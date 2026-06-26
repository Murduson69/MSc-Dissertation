import matplotlib.pyplot as plt
import seaborn as sns
from WT_data import list_WT
import parameters as p

# Configurer le style pour qu'il soit propre et académique (style GGPlot/R comme l'article)
sns.set_theme(style="whitegrid")
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 14,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11
})

# 1. Extraire les coordonnées des turbines (Red Points)
wts_x = [wt['X'] for wt in list_WT]
wts_y = [wt['Y'] for wt in list_WT]
wts_ids = [wt['ID'] for wt in list_WT]

# 2. Récupérer les coordonnées de la base côtière (Blue Point - P0)
# Note : p.Base_coords initiale ou tes coordonnées de dock (0, 0)
dock_x = 0
dock_y = 0

# 3. Récupérer le barycentre du SOV (Green/Orange Point)
# On utilise le dictionnaire qu'on a configuré dans parameters.py
sov_x = p.Base_SOV_coords['X']
sov_y = p.Base_SOV_coords['Y']

# 4. Création de la figure
fig, ax = plt.subplots(figsize=(10, 6), dpi=300) # Haute résolution pour l'impression de la thèse

# Tracé des Éoliennes (Losanges rouges 'D')
ax.scatter(wts_x, wts_y, color='#b23b3b', marker='D', s=50, label='Wind Turbines (WTs)', zorder=3)

# Tracé du Dock/Port (Losange bleu 'D')
ax.scatter(dock_x, dock_y, color='#3b82f6', marker='D', s=60, label='Dock / Port (P0)', zorder=4)

# Tracé de la position d'ancrage du SOV (Losange vert 'D' pour bien le différencier)
ax.scatter(sov_x, sov_y, color='#10b981', marker='D', s=70, label='SOV Offshore Base', zorder=4)

# 5. Ajouter les étiquettes de texte (Labels) à côté de chaque point
# Pour les WTs
for i, name in enumerate(wts_ids):
    # On décale un tout petit peu le texte vers la droite (+0.4) pour que ce soit lisible
    ax.text(wts_x[i] + 0.4, wts_y[i], name, fontsize=10, verticalalignment='center', color='#1f2937')

# Pour le Dock
ax.text(dock_x + 0.4, dock_y, 'P0 (Port)', fontsize=10, verticalalignment='center', fontweight='bold', color='#1f2937')

# Pour le SOV
ax.text(sov_x + 0.4, sov_y, 'SOV Base', fontsize=10, verticalalignment='center', fontweight='bold', color='#065f46')

# 6. Personnalisation des axes et des limites (comme ton image)
ax.set_xlabel('X [km]', fontweight='bold')
ax.set_ylabel('Y [km]', fontweight='bold')
ax.set_title('Case Study - Offshore Wind Farm Layout (20 WTs)', pad=15, fontweight='bold')

# Ajuster les limites pour laisser de l'espace pour les textes
ax.set_xlim(-1, 22)
ax.set_ylim(-1, 16)

# Forcer des graduations principales toutes les 5 unités
ax.set_xticks(range(0, 21, 2))
ax.set_yticks(range(0, 16, 5))

# Afficher la légende de manière élégante
ax.legend(loc='lower right', frameon=True, facecolor='white', edgecolor='#e5e7eb')

# Ajustement parfait des marges
plt.tight_layout()

# Sauvegarder directement l'image en haute qualité pour ton document Word/LaTeX
output_path = 'Case_Study_OWF_Layout.png'
plt.savefig(output_path, bbox_inches='tight')
print(f"Graphique sauvegardé avec succès sous le nom : '{output_path}'")

# Afficher le plot à l'écran
plt.show()