import arcpy
import numpy as np
import os
import math
import copy
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from arcpy.sa import *
from model import (
    try_NomadModel, Household_Agent, household_member,
    Num_agents, place_household, env_degrade, env_mean_val,
    get_suitability_raster, viz_map
)

# Check out the ArcGIS Spatial Analyst extension license
arcpy.CheckOutExtension("Spatial")

class ModelVisualization:
    def __init__(self):
        # Initialize the model with dummy data
        suitability_raster, return_raster, stress_ras = get_suitability_raster()
        
        self.model = try_NomadModel(suitability_raster, return_raster, stress_ras)
        
        # Set up the figure and animation
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(15, 6))
        self.fig.suptitle('Nomadic Household Model Visualization')
        
    def update(self, frame):
        self.ax1.clear()
        self.ax2.clear()
        
        # Update model
        self.model.step()
        
        # Plot grid state
        grid_state = np.zeros((self.model.grid.height, self.model.grid.width))
        for agent in self.model.schedule.agents:
            if isinstance(agent, Household_Agent):
                x, y = agent.pos
                grid_state[y][x] = agent.surplus
        
        # Plot agents and environment
        im = self.ax1.imshow(self.model.suitability_raster, cmap='YlOrRd')
        self.fig.colorbar(im, ax=self.ax1)
        
        # Plot households
        for agent in self.model.schedule.agents:
            if isinstance(agent, Household_Agent):
                x, y = agent.pos
                self.ax1.scatter(x, y, c='blue', s=100, label='Household')
            elif isinstance(agent, household_member):
                if agent.status == 'leader':
                    x, y = agent.pos
                    self.ax1.scatter(x, y, c='red', s=50, label='Leader')
        
        # Plot metrics
        household_data = self.model.datacollector.get_agent_vars_dataframe()
        if not household_data.empty:
            avg_surplus = household_data.xs('surplus', level="Variable")['surplus'].mean()
            self.ax2.bar(['Average Surplus'], [avg_surplus])
        
        self.ax1.set_title('Model State')
        self.ax2.set_title('Metrics')
        
        return self.ax1, self.ax2

    def animate(self, frames=100):
        anim = FuncAnimation(self.fig, self.update, frames=frames, interval=500, blit=True)
        plt.show()

if __name__ == '__main__':
    viz = ModelVisualization()
    viz.animate(frames=10)  # Run for 10 steps
