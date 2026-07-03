import matplotlib.pyplot as plt
import seaborn as sns
import os

def plot_daily_route(day_index, base_coords, all_wts, route_wts, use_sov=False, scenario_name="Default"):
    """
    Génère une carte haute résolution de l'itinéraire journalier du navire,
    en respectant la charte graphique de la thèse.
    """
    # Configurer le style académique
    sns.set_theme(style="whitegrid")
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.size': 11,
        'axes.labelsize': 12,
        'axes.titlesize': 14,
        'xtick.labelsize': 11,
        'ytick.labelsize': 11
    })

    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)

    # 1. Tracé de TOUTES les éoliennes (Fond)
    wts_x = [wt['X'] for wt in all_wts]
    wts_y = [wt['Y'] for wt in all_wts]
    ax.scatter(wts_x, wts_y, color='#b23b3b', marker='D', s=50, alpha=0.3, label='Unvisited WTs', zorder=3)

    # 2. Tracé de la Base (CTV ou SOV selon le paramètre)
    base_x, base_y = base_coords['X'], base_coords['Y']
    if use_sov:
        ax.scatter(base_x, base_y, color='#10b981', marker='D', s=70, label='SOV Base', zorder=5)
        ax.text(base_x + 0.4, base_y, 'SOV Base', fontsize=10, va='center', fontweight='bold', color='#065f46')
    else:
        ax.scatter(base_x, base_y, color='#3b82f6', marker='D', s=60, label='Dock / Port (P0)', zorder=5)
        ax.text(base_x + 0.4, base_y, 'P0 (Port)', fontsize=10, va='center', fontweight='bold', color='#1f2937')

    # 3. Noms des turbines (en semi-transparent pour ne pas surcharger)
    for wt in all_wts:
        ax.text(wt['X'] + 0.4, wt['Y'], wt['ID'], fontsize=9, va='center', color='#1f2937', alpha=0.6)

    # =================================================================
    # 4. TRACÉ DYNAMIQUE DE L'ITINÉRAIRE DU JOUR
    # =================================================================
    if route_wts:
        # Coordonnées du chemin complet : Base -> WT1 -> WT2 -> Base
        route_x = [base_x] + [wt['X'] for wt in route_wts] + [base_x]
        route_y = [base_y] + [wt['Y'] for wt in route_wts] + [base_y]

        # Mettre en surbrillance les éoliennes réparées ce jour-là
        visited_x = [wt['X'] for wt in route_wts]
        visited_y = [wt['Y'] for wt in route_wts]
        ax.scatter(visited_x, visited_y, color='#3b82f6', marker='D', s=70, label='Serviced WTs Today', zorder=4)

        # Dessiner les flèches du trajet
        for i in range(len(route_x) - 1):
            ax.annotate(
                '', 
                xy=(route_x[i+1], route_y[i+1]),    # Arrivée de la flèche
                xytext=(route_x[i], route_y[i]),    # Départ de la flèche
                arrowprops=dict(arrowstyle="-|>", color="#1d4ed8", lw=1.8, mutation_scale=15),
                zorder=2
            )

    # =================================================================
    # 5. ESTHÉTIQUE FINALE ET SAUVEGARDE
    # =================================================================
    day_num = day_index + 1
    ax.set_xlabel('X [km]', fontweight='bold')
    ax.set_ylabel('Y [km]', fontweight='bold')
    vessel_name = "SOV" if use_sov else "CTV"
    ax.set_title(f'Vessel Itinerary ({vessel_name}) - Day {day_num}', pad=15, fontweight='bold')

    ax.set_xlim(-1, 22)
    ax.set_ylim(-1, 16)
    ax.set_xticks(range(0, 21, 2))
    ax.set_yticks(range(0, 16, 5))

    ax.legend(loc='lower right', frameon=True, facecolor='white', edgecolor='#e5e7eb')
    plt.tight_layout()

    # --- ARBORESCENCE DYNAMIQUE ---
    # Crée un dossier: Simulation_Results / Nom_Du_Scenario / Routes
    output_dir = os.path.join('Simulation_Results', scenario_name, 'Routes')
    os.makedirs(output_dir, exist_ok=True)
    
    # Le nom du fichier devient juste "Day_1.png", "Day_2.png", car il est déjà dans le bon dossier !
    file_path = os.path.join(output_dir, f'Route_Day_{day_num}.png')
    plt.savefig(file_path)
    plt.close() # N'oublie pas de fermer la figure pour ne pas surcharger la RAM