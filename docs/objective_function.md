# Calibration objective — code-level walkthrough

> This document is the **code-level** explanation of the calibration
> objective function as implemented in `model.obj_func`. For
> the **conceptual / mathematical** statement of the objective, see
> §4.6.3 of the thesis (Chapter 4) and §A4.3 of the appendix.
>
> Mapping: in the equations, `p` is the proportion of enclosed
> compounds among classified sites; in the code below, that
> corresponds to `ratio_enc` (computed as the ratio of `value == 2`
> counts to `value == 1` counts). The spatial component (IoU on the
> standard deviational ellipses) is captured by the `overlap_func`
> term.

---

## Detailed Explanation of the NumPy/SciPy Version

This function calculates a similarity score between two GeoDataFrames (`gdf` and `gdf1`) by comparing their spatial distribution patterns and value distributions. Let me break down each part:

## Steps 1-3: Value Ratio Analysis

```python
# Step 1: Calculate t_ratio for gdf
t1 = gdf[gdf['value'] == 1].shape[0]  # Count of value == 1
t2 = gdf[gdf['value'] == 2].shape[0]  # Count of value == 2
t_ratio = t2 / t1 if t1 != 0 else 0  # Avoid division by zero

# Step 2: Calculate t1_ratio for gdf1
t11 = gdf1[gdf1['value'] == 1].shape[0]  # Count of value == 1
t21 = gdf1[gdf1['value'] == 2].shape[0]  # Count of value == 2
t1_ratio = t21 / t11 if t11 != 0 else 0  # Avoid division by zero

# Step 3: Calculate ratio_enc
ratio_enc = (t1_ratio / t_ratio) if t_ratio != 0 else 0  # Avoid division by zero
```

This part calculates the ratio of points with value=2 to points with value=1 in each GeoDataFrame, then compares these ratios by dividing one by the other. This creates a measure of how similar the value distributions are between the two datasets.

- `ratio_enc` will be close to 1 if both datasets have similar proportions of value=1 and value=2 points
- `ratio_enc` will diverge from 1 if the proportions are very different

## Step 4: Coordinate Extraction

```python
# Step 4: Extract x and y coordinates from geometry
gdf['x'] = gdf['geometry'].x
gdf['y'] = gdf['geometry'].y
gdf1['x'] = gdf1['geometry'].x
gdf1['y'] = gdf1['geometry'].y
```

This extracts the x and y coordinates from the geometry objects in each GeoDataFrame for easier processing.

## Steps 5-6: Ellipse Calculation

```python
# Function to calculate ellipse properties
def calculate_ellipse(points):
    mean_center = np.mean(points, axis=0)
    med_center = np.median(points, axis=0)
    
    # Calculate covariance matrix
    cov = np.cov(points, rowvar=False)
    
    # Calculate eigenvalues and eigenvectors
    eigenvalues, eigenvectors = linalg.eigh(cov)
    
    # Sort by eigenvalues in decreasing order
    idx = eigenvalues.argsort()[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]
    
    # Calculate standard deviations along axes (for 95% confidence ellipse)
    std_dev = np.sqrt(eigenvalues) * 2
    
    # Calculate rotation angle
    rotation = np.arctan2(eigenvectors[1, 0], eigenvectors[0, 0])
    
    return mean_center, med_center, std_dev[0], std_dev[1], rotation

# Step 5: Calculate ellipse properties for gdf
points = gdf[["x", "y"]].values
mean_center, med_center, major, minor, rotation = calculate_ellipse(points)

# Step 6: Calculate ellipse properties for gdf1
points1 = gdf1[["x", "y"]].values
mean_center1, med_center1, major1, minor1, rotation1 = calculate_ellipse(points1)
```

The `calculate_ellipse` function performs a standard statistical analysis to create a standard deviational ellipse:

1. It calculates the mean center (average of all x,y coordinates)
2. It calculates the median center (median of all x,y coordinates)
3. It computes the covariance matrix of the points
4. It finds the eigenvalues and eigenvectors of this matrix
5. The eigenvalues determine the length of the major and minor axes
6. The eigenvectors determine the orientation of the ellipse
7. The rotation angle is calculated from the first eigenvector

This creates a standard deviational ellipse that represents the spatial distribution and orientation of the points. The ellipse is sized to encompass approximately 95% of the points (multiplying by 2 gives roughly 2 standard deviations).

## Steps 7-8: Ellipse Creation and Overlap Analysis

```python
# Step 7: Create ellipse polygons
ellipse = Ellipse(
    xy=mean_center, 
    width=major * 2, 
    height=minor * 2,
    angle=np.rad2deg(rotation), 
    facecolor="none",
    edgecolor="red",
    linestyle="--",
    label="Std. Ellipse (Mean)"
)
vertices = ellipse.get_verts()  # Get the vertices from the ellipse object
ellipse_gdf = Polygon(vertices)

ellipse_1 = Ellipse(
    xy=mean_center1, 
    width=major1 * 2, 
    height=minor1 * 2,
    angle=np.rad2deg(rotation1), 
    facecolor="none",
    edgecolor="blue",
    linestyle="--",
    label="Std. Ellipse (Mean) (gdf1)"
)
vertices1 = ellipse_1.get_verts()  # Get the vertices from the ellipse object
ellipse_gdf1 = Polygon(vertices1)

# Step 8: Calculate areas and overlap
area_gdf = ellipse_gdf.area
area_gdf1 = ellipse_gdf1.area
total_non_overlapping_area = ellipse_gdf.symmetric_difference(ellipse_gdf1).area
overlapping_area = ellipse_gdf.intersection(ellipse_gdf1).area
```

This part:
1. Creates matplotlib Ellipse objects for visualization
2. Converts these to Shapely Polygon objects for spatial analysis
3. Calculates the area of each ellipse
4. Calculates the overlapping area between the ellipses
5. Calculates the non-overlapping area (symmetric difference)

## Steps 9-10: Final Score Calculation

```python
# Step 9: Calculate overlap function
overlap_func = (abs(overlapping_area - total_non_overlapping_area)) / (overlapping_area + total_non_overlapping_area) if (overlapping_area + total_non_overlapping_area) != 0 else 0  # Avoid division by zero

# Step 10: Calculate total score
total = ((1 - overlap_func) + ratio_enc) / 2
```

Here's where the final score is calculated:

1. `overlap_func` measures how different the overlapping and non-overlapping areas are. It's normalized to be between 0 and 1:
   - If the ellipses completely overlap, `overlap_func` will be close to 0
   - If the ellipses are completely separate, `overlap_func` will be close to 1
   - Values in between indicate partial overlap

2. `(1 - overlap_func)` inverts this, so a higher value means better spatial overlap

3. `total` is the average of two components:
   - `(1 - overlap_func)`: measures spatial similarity (higher is better)
   - `ratio_enc`: measures value distribution similarity (closer to 1 is better)

## What the Total Score Means

The `total` score is a composite measure of how similar the two GeoDataFrames are, considering both:

1. **Spatial distribution similarity**: How similar the point patterns are in terms of their spatial arrangement, measured by the overlap of their standard deviational ellipses.

2. **Value distribution similarity**: How similar the proportions of different values (1 and 2) are between the datasets.

The score ranges from 0 to 1, where:
- Values closer to 1 indicate high similarity between the datasets
- Values closer to 0 indicate low similarity between the datasets

This function appears to be measuring how well one spatial point pattern (possibly a model) represents another (possibly observed data), taking into account both the spatial arrangement of points and their attribute values.