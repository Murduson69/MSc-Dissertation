import copernicusmarine
import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt
import os

# =============================================================================
# 1. PARAMÈTRES DE TÉLÉCHARGEMENT
# =============================================================================
# Coordonnées du centre de ton parc (Aberdeen Wind Farm)
center_lat = 57.2139
center_lon = -1.9223

# Période souhaitée (Année complète)
start_date = "2025-01-01T00:00:00"
end_date = "2025-12-31T23:59:59"

# ID du dataset Copernicus (Global Ocean Wave Analysis and Forecast)
# Vérifie sur le catalogue si tu utilises un autre produit spécifique
dataset_id = "cmems_mod_glo_wav_anfc_0.083_deg_PT3H-i" 
output_filename = "Hs_1Year_Aberdeen.nc"

# =============================================================================
# 2. TÉLÉCHARGEMENT VIA L'API SUBSET
# =============================================================================
if not os.path.exists(output_filename):
    print("Lancement du téléchargement Subset Copernicus. Cela peut prendre quelques minutes...")
    copernicusmarine.subset(
        dataset_id=dataset_id,
        variables=["VHM0"],
        # On définit une très petite bounding box autour de ton point central
        minimum_longitude=center_lon - 0.05,
        maximum_longitude=center_lon + 0.05,
        minimum_latitude=center_lat - 0.05,
        maximum_latitude=center_lat + 0.05,
        start_datetime=start_date,
        end_datetime=end_date,
        output_filename=output_filename,
        force_download=True
    )
    print("Téléchargement terminé !")
else:
    print(f"Le fichier {output_filename} existe déjà, passage au traitement.")

# =============================================================================
# 3. TRAITEMENT ET EXTRACTION AVEC XARRAY
# =============================================================================
print("Traitement des données...")
ds = xr.open_dataset(output_filename)

# Sélection du point géographique le plus proche (au sein de la bounding box)
point = ds.sel(latitude=center_lat, longitude=center_lon, method="nearest")

# Extraction des valeurs de temps et de Hs
time_values = point['time'].values
hs_values = point['VHM0'].values

# =============================================================================
# 4. ANALYSE ET LISSAGE (MOYENNE GLISSANTE)
# =============================================================================
# Utilisation de pandas pour calculer la moyenne glissante sur 7 jours.
# Comme les données sont au pas de 3h, 1 jour = 8 points. 7 jours = 56 points.
window_size = 56 
hs_series = pd.Series(hs_values)
hs_rolling = hs_series.rolling(window=window_size, center=True).mean()

# =============================================================================
# 5. CRÉATION DU GRAPHIQUE
# =============================================================================
plt.figure(figsize=(14, 6), dpi=300)

# Tracé des données brutes en arrière-plan
plt.plot(time_values, hs_values, color='lightgray', label='Raw Hs (3-hour steps)', alpha=0.6, linewidth=1)

# Tracé de la tendance (moyenne glissante)
plt.plot(time_values, hs_rolling, color='blue', label='7-Day Rolling Average', linewidth=2)

# Lignes de contraintes opérationnelles
plt.axhline(y=1.5, color='green', linestyle='--', linewidth=1.5, label='CTV Limit (1.5m)')
plt.axhline(y=3.0, color='red', linestyle='--', linewidth=1.5, label='SOV Limit (3.0m)')

plt.title("Annual Evolution of Significant Wave Height (Hs) - Aberdeen Wind Farm", fontweight='bold')
plt.xlabel("Date", fontweight='bold')
plt.ylabel("Significant Wave Height - Hs (m)", fontweight='bold')
plt.legend(loc='upper right')
plt.grid(True, linestyle=':', alpha=0.7)
plt.tight_layout()

plt.show()

# Fermeture propre du dataset
ds.close()