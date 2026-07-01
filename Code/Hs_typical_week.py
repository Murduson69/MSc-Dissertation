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
dataset_id = "cmems_mod_glo_wav_anfc_0.083deg_PT3H-i" 
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

# ---> LA CORRECTION EST ICI : Création du DataFrame "df" <---
# On associe les hauteurs de vagues à leurs dates respectives
df = pd.DataFrame({'Hs': hs_values}, index=time_values)

def get_representative_weeks(data, window=56): 
    # Calcul de la moyenne glissante sur 7 jours
    rolling_mean = data['Hs'].rolling(window=window).mean()
    
    # Trouver l'index (la date) de la semaine la plus calme (été) et la plus agitée (hiver)
    summer_week_start = rolling_mean.idxmin()
    winter_week_start = rolling_mean.idxmax()
    
    return summer_week_start, winter_week_start

# Utilisation avec le df qu'on vient de créer
summer_start, winter_start = get_representative_weeks(df)
summer_end = summer_start + pd.Timedelta(days=7)
winter_end = winter_start + pd.Timedelta(days=7)

print(f"Semaine typique Été : du {summer_start} au {summer_end}")
print(f"Semaine typique Hiver : du {winter_start} au {winter_end}")

# =============================================================================
# 5. CRÉATION DU GRAPHIQUE
# =============================================================================
plt.figure(figsize=(14, 6), dpi=300)

# Tracé des données brutes en arrière-plan
plt.plot(time_values, hs_values, color='lightgray', label='Raw Hs (3-hour steps)', alpha=0.6, linewidth=1)

# Tracé de la tendance (moyenne glissante)
plt.plot(time_values, hs_rolling, color='blue', label='7-Day Rolling Average', linewidth=2)

#Ajout des zones ombrées
plt.axvspan(summer_start, summer_end, color='green', alpha=0.3, label='Semaine Typique Été')
plt.axvspan(winter_start, winter_end, color='red', alpha=0.3, label='Semaine Typique Hiver')

# Lignes de contraintes opérationnelles
plt.axhline(y=1.3, color='green', linestyle='--', linewidth=1.5, label='CTV Limit (1.3m)')
plt.axhline(y=3.5, color='red', linestyle='--', linewidth=1.5, label='SOV Limit (3.5m)')

plt.title("Annual Evolution of Significant Wave Height (Hs) - Aberdeen Wind Farm", fontweight='bold')
plt.xlabel("Date", fontweight='bold')
plt.ylabel("Significant Wave Height - Hs (m)", fontweight='bold')
plt.legend(loc='upper right')
plt.grid(True, linestyle=':', alpha=0.7)
plt.tight_layout()

plt.show()

# Fermeture propre du dataset
ds.close()

