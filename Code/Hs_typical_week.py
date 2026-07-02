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
start_date = "2024-01-01T00:00:00"
end_date = "2024-12-31T23:59:59"

# ID du dataset Copernicus (Global Ocean Wave Analysis and Forecast)
dataset_id = "cmems_mod_glo_wav_anfc_0.083deg_PT3H-i" 
output_filename = "Hs_1Year_Aberdeen_2024.nc"

# =============================================================================
# 2. TÉLÉCHARGEMENT VIA L'API SUBSET
# =============================================================================
if not os.path.exists(output_filename):
    print("Lancement du téléchargement Subset Copernicus. Cela peut prendre quelques minutes...")
    copernicusmarine.subset(
        dataset_id=dataset_id,
        variables=["VHM0"],
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

# Création du DataFrame "df"
df = pd.DataFrame({'Hs': hs_values}, index=time_values)

def get_representative_weeks(data, window=56): 
    # Calcul de la moyenne glissante sur 7 jours
    rolling_mean = data['Hs'].rolling(window=window, center=True).mean()
    
    # 1. Extrêmes (idxmin/idxmax trouvent le MILIEU de la semaine)
    summer_center = rolling_mean.idxmin()
    winter_center = rolling_mean.idxmax()
    
    # 2. Scénario Médian (Base-Case)
    annual_median = rolling_mean.median()
    mid_center = (rolling_mean - annual_median).abs().idxmin()
    
    return summer_center, mid_center, winter_center

# Utilisation
summer_center, mid_center, winter_center = get_representative_weeks(df)

# On recule de 3.5 jours et on avance de 3.5 jours pour encadrer la semaine
half_week = pd.Timedelta(days=3.5)

summer_start = summer_center - half_week
summer_end = summer_center + half_week

mid_start = mid_center - half_week
mid_end = mid_center + half_week

winter_start = winter_center - half_week
winter_end = winter_center + half_week

print(f"Best-Case Scenario: from {summer_start} to {summer_end}")
print(f"Base-Case Scenario: from {mid_start} to {mid_end}")
print(f"Worst-Case Scenario: from {winter_start} to {winter_end}")

# =============================================================================
# 5. CRÉATION DU GRAPHIQUE
# =============================================================================
plt.figure(figsize=(14, 6), dpi=300)

# Tracé des données brutes en arrière-plan
plt.plot(time_values, hs_values, color='lightgray', label='Raw Hs (3-hour steps)', alpha=0.6, linewidth=1)

# Tracé de la tendance (moyenne glissante)
plt.plot(time_values, hs_rolling, color='blue', label='7-Day Rolling Average', linewidth=2)

# Ajout des zones ombrées (Vert, Orange, Rouge)
plt.axvspan(summer_start, summer_end, color='green', alpha=0.3, label='Best-Case Scenario')
plt.axvspan(mid_start, mid_end, color='orange', alpha=0.4, label='Base-Case Scenario')
plt.axvspan(winter_start, winter_end, color='red', alpha=0.3, label='Worst-Case Scenario')

# Lignes de contraintes opérationnelles
plt.axhline(y=1.3, color='green', linestyle='--', linewidth=1.5, label='CTV Limit (1.3m)')
plt.axhline(y=3.5, color='red', linestyle='--', linewidth=1.5, label='SOV Limit (3.5m)')

plt.title("Annual Evolution of Significant Wave Height (Hs) - Aberdeen Wind Farm", fontweight='bold')
plt.xlabel("Date", fontweight='bold')
plt.ylabel("Significant Wave Height - Hs (m)", fontweight='bold')

# Ajustement de la légende pour éviter qu'elle ne prenne trop de place
plt.legend(loc='upper right', fontsize='small')
plt.grid(True, linestyle=':', alpha=0.7)
plt.tight_layout()

plt.show()

# Fermeture propre du dataset
ds.close()