"""
model_opt_sensitivity.py
Modified version of model_opt.py for sensitivity analysis.
Supports variable number of agents and fixed territory modes.
"""

import os

# 1. FORCE SINGLE THREADING FOR NUMPY/SCIPY
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import numpy as np
import h5py
import random
import copy
import math
import json
from datetime import datetime
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon
import mesa
from mesa.datacollection import DataCollector
from scipy.signal import convolve2d
from scipy.ndimage import distance_transform_edt
from scipy import linalg
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
import seaborn as sns
import optuna
from multiprocessing import shared_memory

# ==========================================
# DATA PATHS & LAZY LOADERS
# ==========================================
DATA_DIR = r"D:\itay\ABM\Data"
YEARLY_DATA_PATH = os.path.join(DATA_DIR, "yearly_data_10_25.h5")
PERMANENT_DATA_PATH = os.path.join(DATA_DIR, "per_data_10_25.h5")
EXT_RASTER_PATH = os.path.join(DATA_DIR, "ext_raster.npy")
PLACE_RASTER_PATH = os.path.join(DATA_DIR, "place_raster.npy")
CALIB_SHP_PATH = r'D:\itay\ABM\points_all\P_for_calib.shp'


class LazyYearlyData:
    def __init__(self, filepath):
        self.filepath = filepath
        self._file = None
        if os.path.exists(filepath):
            with h5py.File(self.filepath, 'r') as f:
                self.num_groups = f['metadata'].attrs['num_groups']
        else:
            self.num_groups = 0

    def __len__(self):
        return self.num_groups

    def __getstate__(self):
        state = self.__dict__.copy()
        state['_file'] = None
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._file = None

    @property
    def file(self):
        if self._file is None or not self._file.id.valid:
            self._file = h5py.File(self.filepath, 'r')
        return self._file

    def __getitem__(self, idx):
        group = self.file[f'group_{idx}']
        keys = sorted(group.keys(), key=lambda x: int(x.split('_')[1]))
        arrays = [np.array(group[k]) for k in keys]
        return arrays

    def close(self):
        if self._file is not None:
            self._file.close()
            self._file = None


def load_permanent_data():
    if not os.path.exists(PERMANENT_DATA_PATH):
        return []
    results = []
    with h5py.File(PERMANENT_DATA_PATH, 'r') as f:
        metadata = f['metadata']
        num_groups = metadata.attrs['num_groups']
        arrays_per_group = metadata.attrs['arrays_per_group']
        for i in range(num_groups):
            group = f[f'group_{i + 1}']
            results = [np.array(group[f'array_{j}']) for j in range(arrays_per_group)]
    return results


class SharedDataManager:
    _shm_cache = {}
    _arrays = {}

    @staticmethod
    def create_shared_block(name, array):
        try:
            existing = shared_memory.SharedMemory(name=name)
            existing.close()
            existing.unlink()
        except FileNotFoundError:
            pass
        shm = shared_memory.SharedMemory(create=True, size=array.nbytes, name=name)
        shared_array = np.ndarray(array.shape, dtype=array.dtype, buffer=shm.buf)
        shared_array[:] = array[:]
        return shm

    @staticmethod
    def get_array(name, shape, dtype):
        if name not in SharedDataManager._arrays:
            try:
                shm = shared_memory.SharedMemory(name=name)
                SharedDataManager._shm_cache[name] = shm
                SharedDataManager._arrays[name] = np.ndarray(shape, dtype=dtype, buffer=shm.buf)
            except FileNotFoundError:
                raise RuntimeError(f"Shared memory block '{name}' not found.")
        return SharedDataManager._arrays[name]


class GlobalData:
    y_output = None
    permanent_results = None
    ext_raster = None
    place_raster = None
    loaded = False


def ensure_data_loaded():
    if GlobalData.loaded:
        return
    shape = (318, 280)
    try:
        GlobalData.ext_raster = SharedDataManager.get_array("ext_raster", shape, np.float64)
        GlobalData.place_raster = SharedDataManager.get_array("place_raster", shape, np.float64)
        GlobalData.permanent_results = []
        idx = 0
        while True:
            try:
                arr = SharedDataManager.get_array(f"perm_res_{idx}", shape, np.float64)
                GlobalData.permanent_results.append(arr)
                idx += 1
            except RuntimeError:
                break
    except RuntimeError:
        if os.path.exists(EXT_RASTER_PATH):
            GlobalData.ext_raster = np.load(EXT_RASTER_PATH)[0:318, 0:280]
        else:
            GlobalData.ext_raster = np.ones(shape)
        if os.path.exists(PLACE_RASTER_PATH):
            GlobalData.place_raster = np.load(PLACE_RASTER_PATH)[0:318, 0:280]
        else:
            GlobalData.place_raster = np.ones(shape)
        GlobalData.permanent_results = load_permanent_data()

    if GlobalData.y_output is None:
        GlobalData.y_output = LazyYearlyData(YEARLY_DATA_PATH)
    GlobalData.loaded = True


KERNEL_CACHE = {}
CONV_KERNEL = None


def get_degrade_kernel(r, d_factor):
    key = (r, d_factor)
    if key in KERNEL_CACHE: return KERNEL_CACHE[key]
    y, x = np.ogrid[-r:r + 1, -r:r + 1]
    dist = (np.abs(x) + np.abs(y)) / 2.0
    kernel = d_factor / (dist + 0.001)
    KERNEL_CACHE[key] = kernel
    return kernel


def to_numpy_y(model, mesa_y):
    numpy_y = np.clip(model.grid.height - mesa_y - 1, 0, model.grid.height - 1)
    return numpy_y


def env_mean_val(model, current_pos, r):
    nbr = model.grid.get_neighborhood(current_pos, moore=True, include_center=False, radius=r)
    nbr = [cell for cell in nbr if not model.grid.out_of_bounds(cell) and cell[0] < 280]
    env_values = [
        model.suitability_raster[to_numpy_y(model, pos[1]), np.clip(pos[0], 0, 279)]
        for pos in nbr
    ]
    if not env_values: return 0
    return sum(env_values) / len(env_values)


def pasture_val(model, current_pos, r):
    x, y = current_pos
    numpy_y = to_numpy_y(model, y)
    y_min = max(0, numpy_y - r)
    y_max = min(model.veg_map.shape[0], numpy_y + r + 1)
    x_min = max(0, x - r)
    x_max = min(model.veg_map.shape[1], x + r + 1)
    window = model.veg_map[y_min:y_max, x_min:x_max]
    return np.sum(window)


def set_camp(agent):
    x, y = agent.pos
    agent.surplus -= 1
    agent.model.target_raster[to_numpy_y(agent.model, y), x] += 0.5


def Num_agents():
    total_area_sq_km = 3251.54
    Max_carry_agents = total_area_sq_km / 18
    carry_agents = Max_carry_agents / 20
    return int(np.floor(carry_agents))


def calculate_carrying_capacity(model, suitability_raster, population, needs):
    max_agent_resources = population * needs
    if max_agent_resources == 0: return 0
    carrying_capacity = np.sum(suitability_raster) / max_agent_resources
    return int(np.floor(carrying_capacity))


def eval_neighborhood(model, x, y, household, radius, n):
    nbr = model.grid.get_neighborhood((x, y), moore=True, include_center=False, radius=radius)
    for cell in nbr:
        if model.grid.is_cell_empty(cell) is False:
            n += 1
    numpy_y = model.suitability_raster.shape[0] - y - 1
    start_x = max(0, x - radius)
    stop_x = min(model.suitability_raster.shape[1], x + radius + 1)
    start_numpy_y = max(0, numpy_y - radius)
    stop_numpy_y = min(model.suitability_raster.shape[0], numpy_y + radius + 1)
    subarray = model.suitability_raster[start_numpy_y:stop_numpy_y, start_x:stop_x].copy()
    ret_array = model.return_raster[start_numpy_y:stop_numpy_y, start_x:stop_x]
    if np.any(ret_array >= 2):
        mask2 = ret_array >= 2
        subarray[mask2] += ret_array[mask2]
    eval_env = calculate_carrying_capacity(model, subarray, household.manpower, n)
    return eval_env


def overlap_territory(model, current_agent, nbr):
    for territory in model.territories:
        if current_agent.territory is not None and territory == current_agent.territory:
            continue
        intersection = set(nbr).intersection(set(territory))
        overlap_state = len(intersection) / len(nbr)
        if overlap_state > 0.25:
            return True
    return False


def place_household(model, current_agent, suitability_raster):
    current_agent.update_own_suitability_raster()
    current_agent.own_suitability_raster[current_agent.own_suitability_raster < 0] = 0
    prob_weights = current_agent.own_suitability_raster.flatten() ** 3
    prob_weights = np.nan_to_num(prob_weights, nan=0.0, posinf=0.0, neginf=0.0)
    total_weight = np.sum(prob_weights)
    if total_weight > 0:
        prob = prob_weights / total_weight
    else:
        prob = np.ones_like(prob_weights) / len(prob_weights)
    prob /= prob.sum()

    def get_valid_position():
        while True:
            random_index = np.random.choice(np.arange(len(prob)), p=prob)
            y, x = np.unravel_index(random_index, suitability_raster.shape)
            mesa_y = suitability_raster.shape[0] - y - 1
            if (20 <= x < model.grid.width - 20 and
                    20 <= mesa_y < model.grid.height - 20 and
                    20 <= y < suitability_raster.shape[0] - 20 and
                    20 <= x < suitability_raster.shape[1] - 20 and
                    model.place_raster[y, x] == 1):
                return x, mesa_y

    x, y = get_valid_position()
    nbr = model.grid.get_neighborhood((x, y), moore=True, include_center=False, radius=20)
    while (overlap_territory(model, current_agent, nbr) and
           eval_neighborhood(model, x, y, current_agent, 20, 35) < 1):
        x, y = get_valid_position()
        nbr = model.grid.get_neighborhood((x, y), moore=True, include_center=False, radius=20)
    return (x, y)


def place_members(model, current_agent, ter):
    current_agent.update_own_suitability_raster()
    own_suitability_raster = current_agent.own_suitability_raster
    ter = [cell for cell in ter if model.place_raster[to_numpy_y(model, cell[1]), cell[0]]]
    if not ter: return current_agent.pos
    suitability_values = [
        own_suitability_raster[to_numpy_y(model, cell[1]), cell[0]] for cell in ter
    ]
    prob_weights = np.array(suitability_values) ** 3
    prob_weights = np.nan_to_num(prob_weights, nan=0.0, posinf=0.0, neginf=0.0)
    total_weight = np.sum(prob_weights)
    if total_weight > 0:
        prob = prob_weights / total_weight
    else:
        prob = np.ones(len(ter)) / len(ter)
    prob /= prob.sum()
    selected_index = np.random.choice(len(ter), p=prob)
    return ter[selected_index]


def env_degrade(model, mesa_x, mesa_y, r, d_factor, p_factor):
    numpy_y = model.grid.height - mesa_y - 1
    numpy_x = mesa_x
    kernel = get_degrade_kernel(r, d_factor)
    y_start, y_end = numpy_y - r, numpy_y + r + 1
    x_start, x_end = numpy_x - r, numpy_x + r + 1
    ky_start, ky_end = 0, kernel.shape[0]
    kx_start, kx_end = 0, kernel.shape[1]
    if y_start < 0: ky_start, y_start = -y_start, 0
    if y_end > model.suitability_raster.shape[0]: ky_end -= (y_end - model.suitability_raster.shape[0]); y_end = \
    model.suitability_raster.shape[0]
    if x_start < 0: kx_start, x_start = -x_start, 0
    if x_end > model.suitability_raster.shape[1]: kx_end -= (x_end - model.suitability_raster.shape[1]); x_end = \
    model.suitability_raster.shape[1]
    if y_start < y_end and x_start < x_end:
        view = model.suitability_raster[y_start:y_end, x_start:x_end]
        view[:] = np.maximum(view - kernel[ky_start:ky_end, kx_start:kx_end], 0.0001)
    model.suitability_raster[numpy_y, numpy_x] = max(model.suitability_raster[numpy_y, numpy_x] - p_factor, 0.0001)


def get_agent_enclosures(agent):
    return list(agent.enc_memory)


def Yi_params(year, accumulator, latest_output):
    if year > 0:
        term = latest_output.copy()
        mask2 = term >= 2
        term[mask2] *= 1.5
        new_accumulator = accumulator * 0.5 + term
        global CONV_KERNEL
        if CONV_KERNEL is None:
            radius_cells = 20
            y, x = np.ogrid[-radius_cells:radius_cells + 1, -radius_cells:radius_cells + 1]
            dist = np.sqrt(x * x + y * y)
            weights = 1.0 / np.power(dist + 1, 2)
            CONV_KERNEL = weights / np.sum(weights)
        last_year_output = convolve2d(new_accumulator, CONV_KERNEL, mode='same', boundary='fill', fillvalue=0)
    else:
        last_year_output = np.zeros((318, 280))
        new_accumulator = np.zeros((318, 280))
    mean_value = np.mean(last_year_output)
    if float(mean_value) == 0:
        yi_hu_stressed_z = last_year_output + 10
    else:
        z = np.where(last_year_output == 0, np.nan, last_year_output)

        def fuzzy_linear(x, max_val, min_val):
            normalized = (max_val - x) / (max_val - min_val)
            return np.clip(normalized, 0, 1)

        hs_FuzzyAlgorithm = fuzzy_linear(z, 2, 0)
        yi_hu_stressed_z = hs_FuzzyAlgorithm * 10
        yi_hu_stressed_z = np.where(np.isnan(yi_hu_stressed_z), 10, yi_hu_stressed_z)
    return_arr = new_accumulator * 5
    return return_arr, yi_hu_stressed_z, new_accumulator


def get_suitability_raster(y_output, indices, year, weights, accumulator=None, latest_output=None):
    if GlobalData.permanent_results is None or len(GlobalData.permanent_results) < 6:
        agri_raster = np.zeros((318, 280))
        kb_suitability_raster = np.zeros((318, 280))
        pw_suitability_raster = np.zeros((318, 280))
        veg_fit = np.zeros((318, 280))
        rain_suitability_raster = np.zeros((318, 280))
        slp_suitability_raster = np.zeros((318, 280))
    else:
        agri_raster, kb_suitability_raster, pw_suitability_raster, veg_fit, rain_suitability_raster, slp_suitability_raster = [
            arr.copy() for arr in GlobalData.permanent_results]

    # Use modulo to cycle through available years if simulation exceeds data length
    data_idx = indices[year % len(indices)]
    random_year = [arr.copy() for arr in y_output[data_idx]]
    wp2, wp4, wp6, wp8, ws1, ws2, ws6 = weights
    YrainFuzzyMember_calc, agr_raster, calc_pastoral_Yi = random_year
    return_ras, yi_hu_stressed_z, new_accumulator = Yi_params(year, accumulator, latest_output)
    kb_suitability_raster = np.nan_to_num(kb_suitability_raster, posinf=0, neginf=0)
    pw_suitability_raster = np.nan_to_num(pw_suitability_raster, posinf=0, neginf=0)
    rain_suitability_raster = np.nan_to_num(rain_suitability_raster, posinf=0, neginf=0)
    slp_suitability_raster = np.nan_to_num(slp_suitability_raster, posinf=0, neginf=0)
    return_ras = np.nan_to_num(return_ras, posinf=0, neginf=0)
    yi_hu_stressed_z = np.nan_to_num(yi_hu_stressed_z, posinf=0, neginf=0)
    YrainFuzzyMember_calc = np.nan_to_num(YrainFuzzyMember_calc, posinf=0, neginf=0)
    res = ((wp2 * kb_suitability_raster) + (wp4 * pw_suitability_raster) + (wp6 * rain_suitability_raster) + (
            wp8 * slp_suitability_raster) + (ws1 * return_ras) + (ws2 * yi_hu_stressed_z) + (
                   ws6 * YrainFuzzyMember_calc))
    ext_raster = GlobalData.ext_raster if GlobalData.ext_raster is not None else np.ones((318, 280))
    slp_lim = np.where(slp_suitability_raster < 1, 0, 1)
    suitability_raster = res * slp_lim * ext_raster
    return suitability_raster, new_accumulator, yi_hu_stressed_z


class Household_Agent(mesa.Agent):
    def __init__(self, model, threshold, manpower=None, surplus=None, flock_head=None):
        super().__init__(model)
        if flock_head is None:
            self.flock_head = 0
            for _ in range(10):
                flock_n = np.floor(random.gauss(105, 15))
                self.flock_head += flock_n
        else:
            self.flock_head = flock_head
        if manpower is None:
            self.manpower = max(35, np.floor(self.flock_head / 20))
        else:
            self.manpower = manpower
        if surplus is None:
            self.surplus = 0
        else:
            self.surplus = surplus
        self.territory = None
        self.general_territory_center = None
        self.memory = []
        self.enc_memory = []
        self.threshold = threshold
        self.own_suitability_raster = None
        self.prosperity_index = None
        self.territory_radius = 25

    def step(self):
        self.update_flock_size()
        self.calc_surplus()
        self.manpower -= 10
        herders = (self.flock_head // 75)
        self.manpower -= herders
        existing_enclosure = self.find_recent_enclosure()
        current_env_value = env_mean_val(self.model, self.pos, 20)
        env_quality = current_env_value / 10.0
        denominator = self.manpower + 10 + herders
        if denominator > 0:
            surplus_ratio = self.surplus / denominator
        else:
            surplus_ratio = 0
        prosperity_index = (self.surplus / (denominator * 2)) * env_quality
        self.prosperity_index = copy.copy(prosperity_index)
        is_prosperous = prosperity_index > 0.6
        if is_prosperous and self.model.year > 5:
            if self.manpower >= 15 and self.surplus >= self.threshold:
                if existing_enclosure:
                    xn, yn = existing_enclosure
                    manpower_cost = 10
                    surplus_cost = 6
                    self.manpower = max(self.manpower - manpower_cost, 0)
                    self.surplus = max(self.surplus - surplus_cost, 0)
                    self.model.target_raster[to_numpy_y(self.model, yn), xn] += 1
                    self.model.enclosures.append([existing_enclosure, self.model.year, self])
                    self.enc_memory.append([existing_enclosure, self.model.year])
                    self.manpower += manpower_cost * 0.9
                elif prosperity_index > 0.8 and self.manpower >= 30 and self.surplus >= self.threshold * 3:
                    enc_pos = self.build_enclosure(self.territory, current_env_value)
                    xn, yn = enc_pos
                    manpower_cost = 20
                    surplus_cost = 25
                    enclosure_quality = 1 + (prosperity_index * 2)
                    self.manpower = max(self.manpower - manpower_cost, 0)
                    self.surplus = max(self.surplus - surplus_cost, 0)
                    self.model.target_raster[to_numpy_y(self.model, yn), xn] += enclosure_quality
                    self.model.enclosures.append([enc_pos, self.model.year, self])
                    self.enc_memory.append([enc_pos, self.model.year])
                    self.manpower += manpower_cost * 0.9
        if self.surplus < 10:
            survived = self.handle_survival_crisis(threshold=10)
            if not survived:
                if self.model.fixed_territory:
                    # In fixed territory mode, we "reset" the agent instead of removing it
                    self.flock_head = sum(np.floor(random.gauss(105, 15)) for _ in range(10))
                    self.manpower = max(35, np.floor(self.flock_head / 20))
                    self.surplus = 10
                    self.year_initiation()
                else:
                    if self.territory in self.model.territories:
                        self.model.territories.remove(self.territory)
                    self.model.grid.remove_agent(self)
                    self.model.agents.remove(self)
                    return
        if self.surplus > 80 and self.flock_head < 600:
            investment_amount = min(self.surplus * 0.2, 40)
            self.buy_livestock_with_surplus(investment_amount)
        self.manpower = max(1, self.manpower + 10)
        self.manpower += herders
        if random.uniform(0, 1) > 0.7:
            self.manpower += math.ceil(5 * random.uniform(0, 1))
        if self.manpower > 55 and random.uniform(0, 1) > 0.8:
            self.manpower -= math.ceil(5 * random.uniform(0, 1))
        if self.surplus > 100 and random.random() < 0.3: self.manpower += 1
        if self.surplus > 100:
            base_decay_rate = 0.05
            scaling_factor = 0.001 * (self.surplus - 100)
            decay_rate = min(0.25, base_decay_rate + scaling_factor)
            decay_amount = self.surplus * decay_rate
            self.surplus -= decay_amount
        else:
            decay_rate = 0.01
            decay_amount = self.surplus * decay_rate
            self.surplus -= decay_amount

    def year_initiation(self):
        self.own_suitability_raster = None
        self.memory = [i for i in self.memory if (self.model.year - i[2]) * random.random() < 15]

        if self.model.fixed_territory:
            if self.territory and self.territory not in self.model.territories:
                self.model.territories.append(self.territory)
            set_camp(self)
            for _ in range(9):
                selected_cell = place_members(self.model, self, self.territory)
                env_degrade(self.model, selected_cell[0], selected_cell[1], 11, 0.3, 0.5)
                self.memory.append([selected_cell, env_mean_val(self.model, selected_cell, 5), self.model.year])
                self.model.target_raster[to_numpy_y(self.model, selected_cell[1]), selected_cell[0]] += 0.25
            env_degrade(self.model, self.pos[0], self.pos[1], self.territory_radius, 0.5, 0.9)
            self.memory.append([self.pos, env_mean_val(self.model, self.pos, self.territory_radius), self.model.year])
            return

        if self.general_territory_center is None:
            self.general_territory_center = self.pos
        else:
            self.general_territory_center = (
                0.9 * self.general_territory_center[0] + 0.1 * self.pos[0],
                0.9 * self.general_territory_center[1] + 0.1 * self.pos[1]
            )
        mesa_x, mesa_y = place_household(self.model, self, self.model.suitability_raster)
        self.model.grid.place_agent(self, (mesa_x, mesa_y))

        current_env_value = env_mean_val(self.model, self.pos, 20)
        base_radius = 20
        if current_env_value < 3.5:
            self.territory_radius = base_radius + 10
        elif current_env_value < 5.0:
            self.territory_radius = base_radius + 5
        else:
            self.territory_radius = base_radius

        self.territory = self.model.grid.get_neighborhood(
            (mesa_x, mesa_y), moore=True, include_center=True, radius=self.territory_radius)
        if self.territory not in self.model.territories:
            self.model.territories.append(self.territory)
        set_camp(self)

        for _ in range(9):
            selected_cell = place_members(self.model, self, self.territory)
            env_degrade(self.model, selected_cell[0], selected_cell[1], 11, 0.3, 0.5)
            self.memory.append([selected_cell, env_mean_val(self.model, selected_cell, 5), self.model.year])
            self.model.target_raster[to_numpy_y(self.model, selected_cell[1]), selected_cell[0]] += 0.25

        env_degrade(self.model, mesa_x, mesa_y, self.territory_radius, 0.5, 0.9)
        self.memory.append([self.pos, env_mean_val(self.model, self.pos, self.territory_radius), self.model.year])

    def calc_surplus(self):
        current_surplus = self.surplus
        self.surplus = 0
        ag_values = []
        for cell in self.territory:
            x, y = cell
            ag_values.append(self.model.ag_ras[to_numpy_y(self.model, y), x])
        mean_ag_value = sum(ag_values) / len(ag_values) if ag_values else 0
        ag_benefit = min(0.4, mean_ag_value * 0.04)
        base_need_per_person = 18 * (1 - ag_benefit)
        subsistence_need = self.manpower * base_need_per_person
        env_value = pasture_val(self.model, self.pos, 25)
        neighborhood = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False, radius=25)
        neighborhood_size = len(neighborhood)
        avg_env_value = env_value / neighborhood_size if neighborhood_size > 0 else 0
        quality_factor = avg_env_value / 5.0
        carrying_capacity = neighborhood_size * 1.125 * quality_factor
        stress_ratio = max(0, 1 - (carrying_capacity / self.flock_head)) if self.flock_head > 0 else 0
        buffer_multiplier = 1.5
        stress_multiplier = 1 + (stress_ratio * 0.3)
        total_livestock_needed = subsistence_need * buffer_multiplier * stress_multiplier
        if self.flock_head > 0:
            non_cull_fraction = max(0, (self.flock_head - total_livestock_needed) / self.flock_head)
        else:
            non_cull_fraction = 0
        productive_herd = max(0, self.flock_head - (subsistence_need * non_cull_fraction))
        non_lethal_rate = 0.15
        surplus_from_products = productive_herd * non_lethal_rate
        excess_livestock = max(0, self.flock_head - total_livestock_needed)
        culling_rate = 0.35
        cull_amount = excess_livestock * 0.8
        surplus_from_culling = cull_amount * culling_rate
        self.flock_head -= cull_amount
        total_surplus_generated = surplus_from_products + surplus_from_culling
        decay_rate = 0.3
        preserved_surplus = current_surplus * (1 - decay_rate)
        consumption_per_person = 1.2
        base_consumption = self.manpower * consumption_per_person
        luxury_consumption = (preserved_surplus + total_surplus_generated) * 0.05
        total_consumption = base_consumption + luxury_consumption
        final_surplus = preserved_surplus + total_surplus_generated - total_consumption
        max_surplus_cap = 200 + (self.manpower * 2.5)
        self.surplus = min(max(0, final_surplus), max_surplus_cap)

    def convert_livestock_to_surplus(self, amount_needed):
        conversion_rate = 0.3
        livestock_needed = math.ceil(amount_needed / conversion_rate)
        base_need_per_person = 18
        minimum_reserve = min(self.manpower * base_need_per_person, 100)
        available_livestock = max(0, self.flock_head - minimum_reserve)
        livestock_to_convert = min(available_livestock, livestock_needed)
        if livestock_to_convert > 0:
            self.flock_head -= livestock_to_convert
            surplus_gained = livestock_to_convert * conversion_rate
            self.surplus += surplus_gained
            return surplus_gained
        return 0

    def buy_livestock_with_surplus(self, surplus_to_spend):
        conversion_rate = 0.3
        livestock_per_surplus = 1 / conversion_rate
        livestock_gained = math.floor(surplus_to_spend * livestock_per_surplus)
        actual_cost = livestock_gained / livestock_per_surplus
        if self.surplus >= actual_cost:
            self.surplus -= actual_cost
            self.flock_head += livestock_gained
            return livestock_gained
        return 0

    def update_flock_size(self):
        env_value = pasture_val(self.model, self.pos, 30)
        neighborhood = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False, radius=30)
        neighborhood_size = len(neighborhood)
        avg_env_value = env_value / neighborhood_size if neighborhood_size > 0 else 0
        quality_factor = avg_env_value / 5.0
        goats_per_cell = 1.125 * quality_factor
        carrying_capacity = goats_per_cell * neighborhood_size
        ratio = carrying_capacity / self.flock_head if self.flock_head > 0 else 2.0
        stress_values = []
        for cell in self.territory:
            x, y = cell
            numpy_y = to_numpy_y(self.model, y)
            if 0 <= numpy_y < self.model.stress_ras.shape[0] and 0 <= x < self.model.stress_ras.shape[1]:
                stress_values.append(self.model.stress_ras[numpy_y, x])
        avg_stress = sum(stress_values) / len(stress_values) if stress_values else 0
        stress_factor = 1 - min(0.5, avg_stress / 20)
        small_flock_factor = 1.0
        if self.flock_head < 500:
            small_flock_factor = 2.0 - (self.flock_head / 500)
        if ratio > 1.1:
            max_growth_rate = 0.2 * stress_factor * small_flock_factor
            diminishing_factor = 1 - (self.flock_head / 1500)
            growth_rate = max_growth_rate * diminishing_factor * min(ratio, 2.0) * random.uniform(0.7, 1.3)
            max_sustainable = carrying_capacity * 1.2
            growth_amount = min(self.flock_head * growth_rate, max_sustainable - self.flock_head)
            self.flock_head = np.floor(self.flock_head + max(0, growth_amount))
        elif ratio < 0.9:
            gap = 0.9 - ratio
            base_decline = 0.05 + (gap * 0.5)
            stress_impact = 1 + (avg_stress / 20)
            if self.flock_head < 100:
                base_decline *= max(0.4, self.flock_head / 100)
            decline_rate = base_decline * stress_impact * random.uniform(0.8, 1.2)
            decline_rate = min(decline_rate, 0.3)
            self.flock_head = np.floor(self.flock_head * (1 - decline_rate))

    def find_recent_enclosure(self, r=20):
        recent_enclosures = []
        current_year = self.model.year
        territory_radius = r

        def in_range(pos1, pos2, r):
            return max(abs(pos1[0] - pos2[0]), abs(pos1[1] - pos2[1])) <= r

        for enc in self.enc_memory:
            if in_range(enc[0], self.pos, territory_radius) and (current_year - enc[1]) < 35:
                score = 35 - (current_year - enc[1])
                recent_enclosures.append((enc[0], score))
        for enc in self.model.enclosures:
            if in_range(enc[0], self.pos, territory_radius) and (current_year - enc[1]) < 25 and enc[1] != current_year:
                score = (25 - (current_year - enc[1])) * 0.8
                recent_enclosures.append((enc[0], score))
        enhanced_scores = []
        for pos, score in recent_enclosures:
            x, y = pos
            veg_value = self.model.veg_ras[to_numpy_y(self.model, y), x]
            ag_value = self.model.ag_ras[to_numpy_y(self.model, y), x]
            env_factor = 1.0 + ((veg_value * 0.02) + (ag_value * 0.02))
            final_score = score * env_factor * random.uniform(0.8, 1.2)
            enhanced_scores.append((pos, final_score))
        if not enhanced_scores:
            return None
        selected_idx = random.choices(
            range(len(enhanced_scores)),
            weights=[s[1] for s in enhanced_scores],
            k=1
        )[0]
        return enhanced_scores[selected_idx][0]

    def handle_survival_crisis(self, threshold=10):
        if self.surplus >= threshold:
            if self.flock_head < 25:
                return True
            elif self.surplus > threshold * 10:
                livestock_deficit = 30 - self.flock_head
                self.buy_livestock_with_surplus(livestock_deficit)
                return True
        surplus_deficit = threshold - self.surplus
        self.convert_livestock_to_surplus(surplus_deficit)
        if self.surplus < 0 or self.flock_head < 15 or self.manpower <= 0:
            leftover_resources = {
                'manpower': max(1, self.manpower),
                'surplus': max(0, self.surplus),
                'flock_head': max(0, self.flock_head)
            }
            if not hasattr(self.model, 'scheduled_new_agents'):
                self.model.scheduled_new_agents = []
            self.model.scheduled_new_agents.append(leftover_resources)
            return False
        return True

    def build_enclosure(self, nbr, mean_val):
        bst_cells = []
        for enc in self.enc_memory:
            if enc[0] in nbr:
                age = self.model.year - enc[1]
                xi, yi = enc[0]
                veg_value = self.model.veg_ras[to_numpy_y(self.model, yi), xi]
                ag_value = self.model.ag_ras[to_numpy_y(self.model, yi), xi]
                suit_val = self.model.suitability_raster[to_numpy_y(self.model, yi), xi]
                if age < 15:
                    base_score = 20 - age
                else:
                    base_score = 5 + (20 - min(age, 20)) / 3
                env_factor = 1.0 + (veg_value * 0.02) + (ag_value * 0.02) + (suit_val * 0.02)
                total_score = base_score * env_factor
                ownership_bias = 1.5
                final_score = total_score * ownership_bias
                random_factor = random.uniform(0.9, 1.1)
                bst_cells.append([enc[0], final_score * random_factor])
        for enc_data in self.model.enclosures:
            enc_pos, enc_year, enc_owner = enc_data
            if enc_pos in nbr and enc_pos not in [e[0] for e in self.enc_memory]:
                age = self.model.year - enc_year
                if age > 15:
                    xi, yi = enc_pos
                    veg_value = self.model.veg_ras[to_numpy_y(self.model, yi), xi]
                    ag_value = self.model.ag_ras[to_numpy_y(self.model, yi), xi]
                    suit_val = self.model.suitability_raster[to_numpy_y(self.model, yi), xi]
                    base_score = 10 - (age / 2)
                    env_factor = 1.0 + (veg_value * 0.02) + (ag_value * 0.02) + (suit_val * 0.02)
                    final_score = base_score * env_factor
                    random_factor = random.uniform(0.7, 1.3)
                    bst_cells.append([enc_pos, final_score * random_factor])
        has_reuse_candidates = False
        if bst_cells:
            average_score = sum(cell[1] for cell in bst_cells) / len(bst_cells)
            if average_score > 8:
                has_reuse_candidates = True
        if self.model.enclosures:
            should_consider_new = not has_reuse_candidates or random.random() > 0.7
        else:
            should_consider_new = random.random() > 0.4
        if should_consider_new:
            for cell in nbr:
                if any(e[0] == cell and (self.model.year - e[1]) < 25 for e in self.model.enclosures):
                    continue
                xi, yi = cell
                veg_value = self.model.veg_ras[to_numpy_y(self.model, yi), xi]
                ag_value = self.model.ag_ras[to_numpy_y(self.model, yi), xi]
                suit_val = self.model.suitability_raster[to_numpy_y(self.model, yi), xi]
                env_score = (suit_val * 0.7) + (veg_value * 0.15) + (ag_value * 0.15)
                if env_score > mean_val + 1:
                    base_score = env_score * 0.8
                    random_factor = random.uniform(0.75, 1.25)
                    bst_cells.append([cell, base_score * random_factor])
        if not bst_cells:
            return self.pos
        else:
            weights = [max(0, cell[1]) for cell in bst_cells]
            total_weight = sum(weights)
            if total_weight > 0:
                normalized_weights = [w / total_weight for w in weights]
                selected_idx = random.choices(range(len(bst_cells)), weights=normalized_weights, k=1)[0]
                selected_cell = bst_cells[selected_idx][0]
            else:
                if bst_cells:
                    selected_idx = random.randint(0, len(bst_cells) - 1)
                    selected_cell = bst_cells[selected_idx][0]
        return selected_cell

    @staticmethod
    def create_agents(model, n, threshold, manpower=None, surplus=None, flock_head=None):
        agents = []
        for _ in range(n):
            agent = Household_Agent(model, threshold, manpower, surplus, flock_head)
            agents.append(agent)
        return agents

    def update_own_suitability_raster(self):
        if self.own_suitability_raster is None:
            self.own_suitability_raster = self.model.suitability_raster.copy()
        if self.general_territory_center:
            center_x, center_y = self.general_territory_center
            center_numpy_y = to_numpy_y(self.model, center_y)
            center_numpy_x = center_x
            Y, X = np.ogrid[:self.model.suitability_raster.shape[0], :self.model.suitability_raster.shape[1]]
            dist_from_center = np.sqrt((X - center_numpy_x) ** 2 + (Y - center_numpy_y) ** 2)
            sigma = 50
            pull_strength = 5.0
            territory_bias = pull_strength * np.exp(- (dist_from_center ** 2) / (2 * sigma ** 2))
            self.own_suitability_raster += territory_bias
        if self.territory:
            territory_mask = np.zeros_like(self.own_suitability_raster, dtype=bool)
            for x, y in self.territory:
                numpy_y = to_numpy_y(self.model, y)
                territory_mask[numpy_y, x] = True
            distances = distance_transform_edt(~territory_mask)
            adjustment = np.where(distances <= 20, 2.5 / (distances + 1), 0)
            self.own_suitability_raster += adjustment
        if self.memory:
            for (x, y), value, year in self.memory:
                numpy_cell = (to_numpy_y(self.model, y), x)
                diff_y = self.model.year - year
                if diff_y == 0:
                    self.own_suitability_raster[numpy_cell] -= 0.5
                else:
                    time_factor = 1 / (diff_y ** 0.5)
                    if value >= 5:
                        self.own_suitability_raster[numpy_cell] += value * time_factor * 0.5
                    elif value > 0:
                        self.own_suitability_raster[numpy_cell] -= (1 / value) * time_factor * 0.5


class NomadModel(mesa.Model):
    def __init__(self, suitability_raster, return_raster, stress_ras, inds, place_raster=None, ras_w=None,
                 y_output=None, num_agents=None, fixed_territory=False):
        super().__init__()
        if num_agents is not None:
            self.num_agents = num_agents
        else:
            self.num_agents = Num_agents()
        self.fixed_territory = fixed_territory
        height, width = suitability_raster.shape
        self.grid = mesa.space.MultiGrid(width, height, False)
        self.yearly_outputs = []
        self.suitability_raster = suitability_raster
        self.inds = inds
        self.target_raster = np.zeros_like(self.suitability_raster)
        self.return_raster = return_raster
        if place_raster is None:
            place_raster = GlobalData.place_raster if GlobalData.place_raster is not None else np.ones((318, 280))
        if y_output is None:
            y_output = GlobalData.y_output
        self.y_output = y_output
        self.place_raster = place_raster
        self.ras_control = []
        self.weights = ras_w
        self.year = 0
        self.territories = []
        self.enclosures = []
        self.suitability_raster[np.isnan(self.suitability_raster)] = 0
        self.threshold = 10
        self.scheduled_new_agents = []

        year_0_data = y_output[inds[0 % len(inds)]]
        self.veg_ras = year_0_data[0]
        self.veg_map = year_0_data[0]
        self.ag_ras = year_0_data[1]

        self.stress_ras = stress_ras
        self.ras_control.append(self.suitability_raster.copy())

        for i in range(self.num_agents):
            agent = Household_Agent(self, threshold=self.threshold)
            mesa_x, mesa_y = place_household(self, agent, self.suitability_raster)
            self.grid.place_agent(agent, (mesa_x, mesa_y))
            self.target_raster[to_numpy_y(self, agent.pos[1]), agent.pos[0]] += 0.5

            current_env_value = env_mean_val(self, agent.pos, 20)
            base_radius = 20
            if current_env_value < 3.5:
                territory_radius = base_radius + 10
            elif current_env_value < 5.0:
                territory_radius = base_radius + 5
            else:
                territory_radius = base_radius

            territory = self.grid.get_neighborhood((mesa_x, mesa_y), moore=True, include_center=True,
                                                   radius=territory_radius)
            agent.territory = territory
            agent.territory_radius = territory_radius
            if agent.territory not in self.territories:
                self.territories.append(agent.territory)

            for _ in range(9):
                selected_cell = place_members(self, agent, agent.territory)
                env_degrade(self, selected_cell[0], selected_cell[1], 11, 0.3, 0.5)
                agent.memory.append([selected_cell, env_mean_val(self, selected_cell, 5), self.year])
                self.target_raster[to_numpy_y(self, selected_cell[1]), selected_cell[0]] += 0.25
            env_degrade(self, mesa_x, mesa_y, territory_radius, 0.5, 0.9)
            agent.memory.append([agent.pos, env_mean_val(self, agent.pos, territory_radius), self.year])

        self.datacollector = DataCollector(agent_reporters={"Manpower": "manpower",
                                                            "flocks": "flock_head",
                                                            "surplus": "surplus",
                                                            "proseprity index": "prosperity_index",
                                                            "position": "pos",
                                                            "enclosures": get_agent_enclosures
                                                            })
        self.datacollector.collect(self)

    def step(self):
        self.agents_by_type[Household_Agent].shuffle_do("step")
        self.yearly_outputs.append(self.target_raster.copy())
        self.year += 1
        self.datacollector.collect(self)

    def move_year(self, inds):
        if not self.fixed_territory:
            self.reset_pos()
        self.suitability_raster, self.return_raster, stress_ras = get_suitability_raster(
            self.y_output, inds, self.year, self.weights, accumulator=self.return_raster,
            latest_output=self.yearly_outputs[-1])

        self.ras_control.append(self.suitability_raster.copy())

        # Use modulo to cycle through available years
        data_idx = inds[self.year % len(inds)]
        current_year_data = self.y_output[data_idx]
        self.veg_ras = current_year_data[0]
        self.ag_ras = current_year_data[1]

        self.stress_ras = stress_ras
        stress_safe = np.where(self.stress_ras == 0, 0.01, self.stress_ras)
        inverse_stress = 1 / (stress_safe / 10)
        capped_stress = np.minimum((inverse_stress - 1), 9)
        self.veg_map = np.maximum((self.veg_ras * (1 - (capped_stress * 0.1))), 0)
        self.target_raster = np.zeros_like(self.suitability_raster)
        if hasattr(self, 'scheduled_new_agents') and self.scheduled_new_agents:
            for resources in self.scheduled_new_agents:
                self.create_replacement_agent(resources)
            self.scheduled_new_agents = []
        self.agents_by_type[Household_Agent].shuffle_do("year_initiation")

    def reset_pos(self):
        for agent in self.agents:
            self.grid.remove_agent(agent)

    def create_replacement_agent(self, resources):
        """Creates a new agent to replace one that failed, with a fresh start."""
        additional_flocks = sum(np.floor(random.gauss(90, 15)) for _ in range(10))
        new_agents = Household_Agent.create_agents(
            model=self,
            n=1,
            threshold=self.threshold,
            manpower=resources['manpower'],
            surplus=resources['surplus'],
            flock_head=resources['flock_head'] + additional_flocks
        )
        agent = new_agents[0]
        
        # Even in fixed territory mode, if an agent is replaced (not just reset),
        # we find a new valid location because the previous one was unsustainable.
        # We temporarily place it to allow territory/suitability calculations.
        temp_pos = (self.grid.width // 2, self.grid.height // 2)
        self.grid.place_agent(agent, temp_pos)

        # Override fixed_territory temporarily to ensure the new agent finds a home
        original_fixed = self.fixed_territory
        self.fixed_territory = False
        agent.year_initiation()
        self.fixed_territory = original_fixed


def viz_map(model, suitability_raster, year, run_dir):
    if suitability_raster is None or suitability_raster.size == 0: return
    fig = Figure(figsize=(8, 6))
    canvas = FigureCanvasAgg(fig)
    ax = fig.add_subplot(111)
    im = ax.imshow(suitability_raster, cmap="YlGn", origin="upper", vmin=0, vmax=10)
    cbar = fig.colorbar(im, ax=ax, orientation='vertical', shrink=0.8)
    cbar.set_label('Suitability Index (0-10)')
    height, width = suitability_raster.shape
    agents = model.agents_by_type[Household_Agent]
    palette = sns.color_palette("tab20", n_colors=len(agents))
    household_dict = {}
    hh_x, hh_y, hh_colors = [], [], []
    for idx, agent in enumerate(agents):
        numpy_row = height - 1 - agent.pos[1]
        numpy_column = agent.pos[0]
        color = palette[idx]
        hh_x.append(numpy_column)
        hh_y.append(numpy_row)
        hh_colors.append(color)
        household_dict[agent] = color
    if hh_x:
        ax.scatter(hh_x, hh_y, c=hh_colors, s=20, marker="o", label='Households', zorder=3)
    mem_x, mem_y, mem_colors = [], [], []
    for agent in agents:
        agent_color = household_dict.get(agent, (0.5, 0.5, 0.5))
        for c in agent.memory:
            if c[-1] == year:
                numpy_row = height - 1 - c[0][1]
                numpy_column = c[0][0]
                mem_x.append(numpy_column)
                mem_y.append(numpy_row)
                mem_colors.append(agent_color)
    if mem_x:
        ax.scatter(mem_x, mem_y, c=mem_colors, s=10, marker="o", alpha=1.0, zorder=2)
    for enc in model.enclosures:
        numpy_row = height - 1 - enc[0][1]
        numpy_column = enc[0][0]
        agent = enc[2]
        enc_color = household_dict.get(agent, 'gray')
        if year > 0:
            opc = max(0, 1 - (year - enc[1]) / year)
        else:
            opc = 1.0
        ax.scatter([numpy_column], [numpy_row], color=enc_color, s=15, marker="s", alpha=opc, zorder=1)
    ax.set_title(f"Year {year} Simulated Map", fontsize=14)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.grid(True, linestyle='--', alpha=0.7)
    filename = f'year_{year}_map.png'
    filepath = os.path.join(run_dir, filename)
    os.makedirs(run_dir, exist_ok=True)
    fig.savefig(filepath, dpi=400)


def to_gdf(model_output, lower_left_x=139554.9251999901, lower_left_y=478515.53229999694, cell_size=250):
    yo_sum = sum(model_output.yearly_outputs)
    yo_sum[yo_sum < 0.6] = 0
    yo_sum[yo_sum > 0] = 1
    for enclosure in model_output.enclosures:
        mesa_x, mesa_y = enclosure[0]
        numpy_y = to_numpy_y(model_output, mesa_y)
        yo_sum[numpy_y, mesa_x] = 2
    indices = np.column_stack((np.argwhere(yo_sum > 0), yo_sum[yo_sum > 0]))
    real_world_coords = []
    for (row, col, value) in indices:
        x = lower_left_x + col * cell_size
        y = lower_left_y + (yo_sum.shape[0] - 1 - row) * cell_size
        real_world_coords.append((x, y, value))
    real_world_coords = np.array(real_world_coords)
    if len(real_world_coords) == 0:
        return gpd.GeoDataFrame({'geometry': [], 'value': []}, crs="EPSG:2039")
    geometry = [Point(x, y) for x, y, _ in real_world_coords]
    gdf = gpd.GeoDataFrame({
        'geometry': geometry,
        'value': real_world_coords[:, 2]
    }, crs="EPSG:2039")
    return gdf


def obj_func(gdf, gdf1, run_dir):
    def calculate_ellipse(points):
        if len(points) < 3: return np.mean(points, axis=0), np.median(points, axis=0), 0, 0, 0
        mean_center = np.mean(points, axis=0)
        med_center = np.median(points, axis=0)
        cov = np.cov(points, rowvar=False)
        eigenvalues, eigenvectors = linalg.eigh(cov)
        idx = eigenvalues.argsort()[::-1]
        eigenvalues = eigenvalues[idx]
        eigenvectors = eigenvectors[:, idx]
        std_dev = np.sqrt(np.maximum(eigenvalues, 0)) * 2
        rotation = np.arctan2(eigenvectors[1, 0], eigenvectors[0, 0])
        return mean_center, med_center, std_dev[0], std_dev[1], rotation

    gdf['x'] = gdf['geometry'].x
    gdf['y'] = gdf['geometry'].y
    gdf1['x'] = gdf1['geometry'].x
    gdf1['y'] = gdf1['geometry'].y
    points = gdf[["x", "y"]].values
    points1 = gdf1[["x", "y"]].values
    if len(points1) == 0: return 1.0, 1.0
    mean_center, med_center, major, minor, rotation = calculate_ellipse(points)
    mean_center1, med_center1, major1, minor1, rotation1 = calculate_ellipse(points1)
    fig = Figure(figsize=(10, 8))
    canvas = FigureCanvasAgg(fig)
    ax = fig.add_subplot(111)
    gdf_value1 = gdf[gdf['value'] == 1]
    gdf_value2 = gdf[gdf['value'] == 2]
    ax.scatter(gdf_value1['x'], gdf_value1['y'], color='lightcoral', alpha=0.7, label='archaeology Value 1')
    ax.scatter(gdf_value2['x'], gdf_value2['y'], color='red', alpha=0.7, label='archaeology Value 2')
    gdf1_value1 = gdf1[gdf1['value'] == 1]
    gdf1_value2 = gdf1[gdf1['value'] == 2]
    ax.scatter(gdf1_value1['x'], gdf1_value1['y'], color='lightblue', alpha=0.7, label='simulated Value 1')
    ax.scatter(gdf1_value2['x'], gdf1_value2['y'], color='blue', alpha=0.7, label='simulated Value 2')
    ellipse = Ellipse(xy=mean_center, width=major * 2, height=minor * 2, angle=np.rad2deg(rotation),
                      facecolor="none", edgecolor="red", linestyle="--", linewidth=2)
    ax.add_patch(ellipse)
    ellipse_1 = Ellipse(xy=mean_center1, width=major1 * 2, height=minor1 * 2, angle=np.rad2deg(rotation1),
                        facecolor="none", edgecolor="blue", linestyle="--", linewidth=2)
    ax.add_patch(ellipse_1)
    ax.set_aspect('equal')
    ax.legend(loc='upper right')
    vertices = ellipse.get_verts()
    ellipse_gdf = Polygon(vertices)
    vertices1 = ellipse_1.get_verts()
    ellipse_gdf1 = Polygon(vertices1)
    overlapping_area = ellipse_gdf.intersection(ellipse_gdf1).area
    union_area = ellipse_gdf.union(ellipse_gdf1).area
    iou = overlapping_area / union_area if union_area != 0 else 0
    spatial_error = 1 - iou
    fig.savefig(os.path.join(run_dir, "spatial_similarity.png"))
    t1 = gdf[gdf['value'] == 1].shape[0]
    t2 = gdf[gdf['value'] == 2].shape[0]
    t_ratio = t2 / t1 if t1 != 0 else 0
    t11 = gdf1[gdf1['value'] == 1].shape[0]
    t21 = gdf1[gdf1['value'] == 2].shape[0]
    t1_ratio = t21 / t11 if t11 != 0 else 0
    ratio_error = abs(t_ratio - t1_ratio)
    total_error = (spatial_error + ratio_error) / 2
    return total_error, ratio_error


def run_model_opt(model_years, ras_wts, main_run_directory, trial_number, iteration,
                  permanent_weights_dict=None, yearly_weights_dict=None,
                  y_output_data=None, seed=None, plot=False,
                  num_agents=None, fixed_territory=False):
    if y_output_data is None:
        y_output_data = GlobalData.y_output
    run_directory = os.path.join(main_run_directory, f"trial_{trial_number}", f"iter_{iteration}")
    os.makedirs(run_directory, exist_ok=True)
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    inds = list(range(len(y_output_data)))
    random.shuffle(inds)
    suitability_raster, return_raster, stress_ras = get_suitability_raster(
        y_output_data, inds, year=0, weights=ras_wts
    )
    model = NomadModel(suitability_raster, return_raster, stress_ras, inds, ras_w=ras_wts, y_output=y_output_data,
                       num_agents=num_agents, fixed_territory=fixed_territory)
    plot_y = [10, 20, 30, 40, 50, 60, 70]
    try:
        for i in range(model_years):
            model.step()
            if plot:
                if i in plot_y or i == (model_years - 1):
                    viz_map(model, model.suitability_raster, i, run_directory)
                    plt.close('all')
            if i != (model_years - 1):
                model.move_year(inds)
    finally:
        if hasattr(model, 'datacollector'):
            household_data = model.datacollector.get_agent_vars_dataframe()
            household_data.to_csv(os.path.join(run_directory, "household_data.csv"))
        if permanent_weights_dict:
            with open(os.path.join(run_directory, "permanent_weights_dict.json"), "w") as f:
                json.dump(permanent_weights_dict, f)
                f.flush()
                os.fsync(f.fileno())
        if yearly_weights_dict:
            with open(os.path.join(run_directory, "yearly_weights_dict.json"), "w") as f:
                json.dump(yearly_weights_dict, f)
                f.flush()
                os.fsync(f.fileno())
    return model, run_directory