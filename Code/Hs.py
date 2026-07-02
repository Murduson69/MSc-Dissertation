import copernicusmarine
import xarray as xr
import os
import matplotlib.pyplot as plt
import numpy as np

# =============================================================================
# 1. PARAMÈTRES DES SEMAINES TYPIQUES (À REMPLIR AVEC TES RÉSULTATS)
# =============================================================================
# Remplace par les dates exactes issues de ton script précédent
best_case_start = "2024-09-15T18:00:00"
best_case_end   = "2024-09-22T18:00:00"

worst_case_start = "2024-01-01T00:00:00"
worst_case_end   = "2024-01-08T00:00:00"

# Centre du parc d'Aberdeen
center_lat = 57.2139
center_lon = -1.9223

# Deltas spatiaux (20x15 km)
delta_lat = 0.067
delta_lon = 0.175

# Définition des 5 points critiques du parc
test_points = {
    "Center":     (center_lat, center_lon),
    "North-West": (center_lat + delta_lat, center_lon - delta_lon),
    "North-East": (center_lat + delta_lat, center_lon + delta_lon),
    "South-West": (center_lat - delta_lat, center_lon - delta_lon),
    "South-East": (center_lat - delta_lat, center_lon + delta_lon)
}

dataset_id = "cmems_mod_glo_wav_anfc_0.083deg_PT3H-i"

# =============================================================================
# 2. FONCTION DE TÉLÉCHARGEMENT ET D'EXTRACTION SPATIALE
# =============================================================================
def fetch_and_extract_week(start_date, end_date, scenario_name):
    print(f"\n--- TRAITEMENT DU SCÉNARIO : {scenario_name} ---")
    output_filename = f"Hs_Aberdeen_{scenario_name}.nc"
    
    # 1. Téléchargement d'une Bounding Box englobant tout le parc (+ une marge)
    if not os.path.exists(output_filename):
        print(f"Téléchargement des données Copernicus pour {scenario_name}...")
        copernicusmarine.subset(
            dataset_id=dataset_id,
            variables=["VHM0"],
            minimum_longitude=center_lon - (delta_lon + 0.1),
            maximum_longitude=center_lon + (delta_lon + 0.1),
            minimum_latitude=center_lat - (delta_lat + 0.1),
            maximum_latitude=center_lat + (delta_lat + 0.1),
            start_datetime=start_date,
            end_datetime=end_date,
            output_filename=output_filename,
            force_download=True
        )
        print("Téléchargement terminé !")
    else:
        print(f"Fichier {output_filename} déjà existant.")

    # 2. Extraction des 5 points avec Xarray
    print("Extraction des séries temporelles pour les 5 points critiques...")
    ds = xr.open_dataset(output_filename)
    
    results = {}
    for location, (lat, lon) in test_points.items():
        point = ds.sel(latitude=lat, longitude=lon, method="nearest")
        results[location] = point['VHM0'].values.tolist()
        
    ds.close()
    return results

# =============================================================================
# 3. FONCTION DE TRACÉ DU GRAPHIQUE
# =============================================================================
def plot_spatial_variation(results_dict, scenario_name):
    plt.figure(figsize=(12, 6), dpi=300)
    
    markers = ['o', 's', '^', 'v', 'd']
    for i, (location, hs_values) in enumerate(results_dict.items()):
        plt.plot(hs_values, label=location, marker=markers[i], markersize=4, linewidth=1.5, alpha=0.8)
        
    plt.title(f"Spatial Variation of Hs across Wind Farm - {scenario_name}", fontweight='bold')
    plt.xlabel("Time Steps (3-hour intervals over 7 days)", fontweight='bold')
    plt.ylabel("Significant Wave Height - Hs (m)", fontweight='bold')
    
    # Ajout des limites opérationnelles
    plt.axhline(y=1.3, color='green', linestyle='--', linewidth=1.5, label="CTV Limit (1.3m)")
    plt.axhline(y=3.5, color='red', linestyle='--', linewidth=1.5, label="SOV Limit (3.5m)")
    
    plt.legend(loc='upper right')
    plt.grid(True, linestyle=':', alpha=0.7)
    plt.tight_layout()
    
    # Calcul de la différence spatiale maximale
    arr_values = np.array(list(results_dict.values())) 
    max_diffs = np.max(arr_values, axis=0) - np.min(arr_values, axis=0)
    overall_max_diff = np.max(max_diffs)
    
    print("\n" + "="*50)
    print(f"[{scenario_name}] MAXIMUM SPATIAL DIFFERENCE : {overall_max_diff:.3f} meters")
    print("="*50)
    
    plt.show()

# =============================================================================
# 4. EXÉCUTION PRINCIPALE
# =============================================================================
if __name__ == "__main__":
    # Traitement du Best-Case Scenario
    results_best = fetch_and_extract_week(best_case_start, best_case_end, "Best-Case")
    plot_spatial_variation(results_best, "Best-Case")
    
    # Traitement du Worst-Case Scenario
    results_worst = fetch_and_extract_week(worst_case_start, worst_case_end, "Worst-Case")
    plot_spatial_variation(results_worst, "Worst-Case")