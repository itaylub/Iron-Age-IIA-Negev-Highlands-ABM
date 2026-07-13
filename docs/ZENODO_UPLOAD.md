# Uploading the Nomad ABM data bundle to Zenodo

This is the one-time procedure that turns the local `Data/` snapshot
into a citable, versioned, DOI-backed archive that
`scripts/download_data.py` can fetch on a fresh clone. Follow it
once; subsequent updates (a corrected raster, an additional file)
re-use the same Zenodo *record* through the "New version" flow and
keep the DOI lineage intact.

Time budget: ~30 minutes if everything is set up, ~60 minutes if you
also need to create a Zenodo / ORCID account.

---

## Step 0 — One-time accounts (skip if you already have them)

1. **ORCID** (optional but strongly recommended for academic
   publishing). Free at <https://orcid.org/register>. Gives you a
   permanent author identifier that Zenodo and journals link to.

2. **Zenodo** account. Free at <https://zenodo.org/signup>. The
   easiest path is *Sign up with ORCID* — it links the two for you.
   Alternatively use GitHub or email/password.

> **Optional dry-run:** Zenodo also runs a sandbox at
> <https://sandbox.zenodo.org/>. Records published there are
> throw-away and use fake DOIs (prefix `10.5072` instead of
> `10.5281`). Useful if you want to walk through the upload flow
> once before doing the real thing. If you skip the sandbox, just
> double-check the metadata in the production form before clicking
> *Publish* — once a record is published you can no longer delete
> it (you can only supersede it with a new version).

## Step 1 — Build the bundle locally

In **Anaconda Prompt**, with your env active and cwd = `D:\itay\ABM`:

```cmd
git pull
python scripts\build_data_bundle.py
```

This produces `nomad-abm-data-v1.0.zip` in the current directory
(about 65 MB) and prints two values you'll need shortly:

```
Bundle path : D:\itay\ABM\nomad-abm-data-v1.0.zip
Zip bytes   : 67,xxx,xxx
SHA-256     : 6e3a... (64 hex chars)
```

**Copy the SHA-256 somewhere — you'll send it to me at the end.**

What's in the bundle (flat layout, all at the same level):

- `yearly_data_10_25.h5`
- `per_data_10_25.h5`
- `ext_raster.npy`
- `place_raster.npy`
- `P_for_calib.shp` + `.shx` + `.dbf` + `.prj`

The legacy `.h5` / `.pkl` / `.tif` files are **excluded** — see
`docs/DATA.md` for why.

## Step 2 — Create the Zenodo upload

1. Log in to <https://zenodo.org/>.
2. Click **New Upload** (top right, or "Upload" in the navbar).
3. Drag-and-drop `nomad-abm-data-v1.0.zip` into the file area. Wait
   for the upload to finish (a green check appears).

## Step 3 — Fill the metadata form

The fields below are the minimum for a clean, citable archive.
Fields not listed can stay empty.

| Field | Suggested value |
|---|---|
| **Resource type** | `Dataset` |
| **Title** | `Nomad ABM input data — Iron Age IIA Negev Highlands settlement model` |
| **Creators** | `Lubel, Itay` — add your ORCID iD, affiliation `The Hebrew University of Jerusalem` |
| **Description** | See template below |
| **Additional notes** | optional |
| **Publication date** | today |
| **Version** | `1.0` |
| **License** | `Creative Commons Attribution 4.0 International (CC-BY-4.0)` — standard for open data; allows reuse with attribution |
| **Keywords** | `agent-based model`, `archaeology`, `Iron Age IIA`, `Negev Highlands`, `pastoralism`, `palimpsest`, `Mesa`, `Optuna`, `Israel` |
| **Related/alternate identifiers** | Add `https://github.com/itaylub/ABM` with relation type `is supplement to` |
| **Communities** | Optional. Search for `CoMSES` and add it if you plan to submit to the CoMSES model library |

### Description template (copy-paste, edit as you like)

> Input data for the Nomad ABM, an agent-based simulation of
> Iron Age IIA household mobility and palimpsest formation in the
> Negev Highlands, c. 980–830 BCE. The bundle contains the
> environmental rasters (HDF5), valid-placement masks (NumPy), and
> archaeological calibration points (ESRI shapefile, EPSG:2039 /
> Israel Transverse Mercator) consumed by the model code at
> https://github.com/itaylub/ABM.
>
> A complete data dictionary and reproducibility instructions are in
> the `docs/` directory of the code repository, and the model
> description is in the accompanying thesis chapter under `thesis/`.
> The download utility
> `scripts/download_data.py` in that repository fetches this
> archive and verifies its SHA-256 before extracting into
> `Data/`.
>
> Released alongside Chapter 5 of Itay Lubel's MA thesis
> (forthcoming), The Hebrew University of Jerusalem.

## Step 4 — Save draft, sanity-check, publish

1. Click **Save draft** at the bottom of the form. Zenodo validates
   the metadata and surfaces any missing required fields.
2. Read your draft top-to-bottom one last time. **Publication is
   irreversible** — you can supersede with a new version later, but
   you cannot delete the record.
3. Click **Publish**.

Zenodo issues the DOI immediately. You'll see something like:

```
DOI: 10.5281/zenodo.14123456
URL: https://zenodo.org/records/14123456
```

## Step 5 — Send me three values

Paste these into our conversation:

1. **Zenodo record ID** (the digits at the end of the URL,
   e.g. `14123456`)
2. **Bundle filename** (should be exactly `nomad-abm-data-v1.0.zip`
   unless you renamed it during upload)
3. **SHA-256** from `build_data_bundle.py` Step 1

I will then:

- Fill those three values into `scripts/download_data.py` (currently
  has placeholders).
- Add the Zenodo DOI badge to `README.md`.
- Add the `doi:` field to `CITATION.cff`.
- Update `docs/DATA.md` to point at the published archive.
- Commit + push. Phase 9 done.

## Future updates ("v1.1", "v1.2", ...)

When you regenerate data:

1. Re-run `python scripts\build_data_bundle.py` after bumping
   `BUNDLE_VERSION` in that script (e.g. to `v1.1`).
2. On the Zenodo record page, click **New version** (top right of the
   record).
3. Replace the file with the new zip; bump the **Version** field.
4. Publish. Zenodo issues a new DOI for the new version and a
   "concept DOI" that always points at the latest version.
5. Send me the new record ID + SHA-256; I update
   `scripts/download_data.py` (one commit).
