import xarray as xr
import os
import matplotlib.pyplot as plt
import numpy as np

def get_hs_time_series(folder_path, file_names, target_lat, target_lon):
    """
    Extracts the significant wave height (Hs) time series 
    for specific coordinates from NetCDF files.
    """
    # 1. Construct the full file paths
    file_paths = [os.path.join(folder_path, f) for f in file_names]
    
    # 2. Open the datasets
    xrds = xr.open_mfdataset(file_paths, combine='by_coords', parallel=False, chunks={})
    
    # 3. Extract the nearest geographical point
    point = xrds.sel(latitude=target_lat, longitude=target_lon, method="nearest")
    
    # 4. Retrieve the Hs variable (VHM0)
    Hs = point['VHM0']
    
    # 5. Convert to a simple Python list
    hs_list = Hs.values.tolist()
    
    return hs_list

# =============================================================================
# SENSITIVITY TEST: SPATIAL VARIATION ACROSS THE WIND FARM
# =============================================================================
if __name__ == "__main__":
    folder = r'/Users/baptiste/Documents/Heriot Watt/R-SET/Dissertation/Code'
    files = [
        'mfwamglocep_2025060100_R20250602_00H.nc',
        'mfwamglocep_2025060112_R20250602_12H.nc',
        'mfwamglocep_2025060200_R20250603_00H.nc',
        'mfwamglocep_2025060212_R20250603_12H.nc',
        'mfwamglocep_2025060300_R20250604_00H.nc',
        'mfwamglocep_2025060312_R20250604_12H.nc',
        'mfwamglocep_2025060400_R20250605_00H.nc',
        'mfwamglocep_2025060412_R20250605_12H.nc',
        'mfwamglocep_2025060500_R20250606_00H.nc',
        'mfwamglocep_2025060512_R20250606_12H.nc',
        'mfwamglocep_2025060600_R20250607_00H.nc',
        'mfwamglocep_2025060612_R20250607_12H.nc',
        'mfwamglocep_2025060700_R20250608_00H.nc',
        'mfwamglocep_2025060712_R20250608_12H.nc'
    ]
    
    # Centre du parc (Orkney)
    #center_lat = 58.9303
    #center_lon = -3.9335
    
    # Centre du parc (Aberdeen)
    center_lat = 57.2139
    center_lon = -1.9223
    
    # Conversion de km en degrés (Approximation locale pour ~59° Nord)
    # 1° Latitude  = ~111 km.  Donc 15 km total (+/- 7.5 km) = +/- 0.067°
    # 1° Longitude = ~111 * cos(58.9°) = ~57 km. Donc 20 km total (+/- 10 km) = +/- 0.175°
    delta_lat = 0.067
    delta_lon = 0.175
    
    # Définition des 5 points critiques du parc
    test_points = {
        "Center":      (center_lat, center_lon),
        "North-West":  (center_lat + delta_lat, center_lon - delta_lon),
        "North-East":  (center_lat + delta_lat, center_lon + delta_lon),
        "South-West":  (center_lat - delta_lat, center_lon - delta_lon),
        "South-East":  (center_lat - delta_lat, center_lon + delta_lon)
    }
    
    results = {}
    print("Fetching spatial data across the 20x15 km area...")
    
    # Extraction pour chaque point
    for location, (lat, lon) in test_points.items():
        print(f" -> Extracting {location:10} (Lat: {lat:.4f}, Lon: {lon:.4f})")
        results[location] = get_hs_time_series(folder, files, lat, lon)
        
    # --- PLOTTING THE RESULTS ---
    plt.figure(figsize=(12, 6), dpi=300)
    
    # Tracer chaque ligne avec un style différent pour bien les distinguer
    markers = ['o', 's', '^', 'v', 'd']
    for i, (location, hs_values) in enumerate(results.items()):
        plt.plot(hs_values, label=location, marker=markers[i], markersize=4, linewidth=1.5, alpha=0.8)
        
    plt.title("Spatial Variation of Significant Wave Height (Hs) across Wind Farm", fontweight='bold')
    plt.xlabel("Time Steps (Data points from NetCDF)", fontweight='bold')
    plt.ylabel("Significant Wave Height (m)", fontweight='bold')
    plt.axhline(y=1.3, color='r', linestyle='--', label="CTV Limit (1.3m)")
    plt.legend(loc='upper right')
    plt.grid(True, linestyle=':', alpha=0.7)
    plt.tight_layout()
    
    # Calcul de la différence maximale
    arr_values = np.array(list(results.values())) # Matrice (5 points x Time steps)
    max_diffs = np.max(arr_values, axis=0) - np.min(arr_values, axis=0)
    overall_max_diff = np.max(max_diffs)
    
    print("\n" + "="*50)
    print(f"MAXIMUM SPATIAL DIFFERENCE AT ANY GIVEN TIME: {overall_max_diff:.3f} meters")
    print("="*50)
    
    plt.show()
