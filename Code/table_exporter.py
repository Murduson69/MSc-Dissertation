import matplotlib.pyplot as plt
import pandas as pd
import os
from datetime import datetime

def export_financial_table_image(rows, sum_rev, sum_cod, cst, pt, epsilon_prime, vessel_type, strategy_name, scenario_name):
    df = pd.DataFrame(rows)
    df['rev'] = df['rev'].apply(lambda x: f"€ {x:,.2f}")
    df['dt'] = df['dt'].apply(lambda x: f"{x:.2f}" if x > 0 else "-")
    df['cod'] = df['cod'].apply(lambda x: f"€ {x:,.2f}" if x > 0 else "-")
    df['vt'] = df['vt'].apply(lambda x: f"€ {x:,.2f}" if x > 0 else "-")
    df['fuel'] = df['fuel'].apply(lambda x: f"€ {x:,.2f}" if x > 0 else "-")
    df.columns = ["Day", "Revenue", "Downtimes", "Cost of Downtime", "Vessel + Team", "Fuel Cost"]

    totals = pd.DataFrame([{"Day": "TOTAL", "Revenue": f"€ {sum_rev:,.2f}", "Downtimes": f"ε' = {epsilon_prime:.2f}",
                            "Cost of Downtime": f"€ {sum_cod:,.2f}", "Vessel + Team": "TOTAL CST ->", "Fuel Cost": f"€ {cst:,.2f}"}])
    df = pd.concat([df, totals], ignore_index=True)

    profit = pd.DataFrame([{"Day": "", "Revenue": "", "Downtimes": "", "Cost of Downtime": "", 
                            "Vessel + Team": "NET PROFIT (P_T) ->", "Fuel Cost": f"€ {pt:,.2f}"}])
    df = pd.concat([df, profit], ignore_index=True)

    _draw_and_save_table(df, f"Financial Evaluation ({strategy_name})", vessel_type, strategy_name, scenario_name, "Financial")


def export_downtime_table_image(daily_expected, daily_predicted, daily_prevented, vessel_type, strategy_name, scenario_name):
    nb_days = len(daily_expected)
    days = [f"Day {i+1}" for i in range(nb_days)] + ["TOTAL"]

    exp_total = sum(daily_expected)
    prev_total = sum(daily_prevented)
    
    if strategy_name == "predictive":
        pred_total = sum(daily_predicted)
        pred_col = [f"{x:.2f}" for x in daily_predicted] + [f"{pred_total:.2f}"]
    else:
        pred_col = ["N/A"] * (nb_days + 1)

    df = pd.DataFrame({
        "Day": days,
        "Expected Events": [f"{x:.2f}" for x in daily_expected] + [f"{exp_total:.2f}"],
        "Predicted Events": pred_col,
        "Prevented Events": [f"{x:.2f}" for x in daily_prevented] + [f"{prev_total:.2f}"]
    })

    _draw_and_save_table(df, f"Downtime Events ({strategy_name})", vessel_type, strategy_name, scenario_name, "Downtime")


def _draw_and_save_table(df, title, vessel_type, strategy_name, scenario_name, table_type):
    fig, ax = plt.subplots(figsize=(10, 4), dpi=300)
    ax.axis('tight')
    ax.axis('off')
    
    header_color = '#3b82f6' if table_type == "Financial" else '#10b981' 
    row_colors = ['#f3f4f6', '#ffffff']
    
    table = ax.table(cellText=df.values, colLabels=df.columns, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.8)
    
    for i, key in enumerate(table.get_celld().keys()):
        cell = table.get_celld()[key]
        row, col = key
        
        if row == 0:
            cell.set_text_props(weight='bold', color='white')
            cell.set_facecolor(header_color)
        elif (row >= len(df) - 1 and table_type == "Financial") or (row == len(df) and table_type == "Downtime"):
            cell.set_text_props(weight='bold')
            cell.set_facecolor('#e5e7eb')
        else:
            cell.set_facecolor(row_colors[row % len(row_colors)])
        cell.set_edgecolor('white')

    plt.title(f"{title}: {vessel_type} | Scenario: {scenario_name}", fontweight='bold', pad=20)

    output_dir = 'Figures_Tables'
    os.makedirs(output_dir, exist_ok=True)
    file_name = f'Table_{table_type}_{strategy_name}_{vessel_type}_{scenario_name}.png'
    output_path = os.path.join(output_dir, file_name)
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    
def export_simulation_parameters(strategy_name, scenario_name, vessel_type):
    """
    Exporte l'intégralité des variables de parameters.py dans un fichier texte
    pour conserver un historique strict et propre de chaque simulation.
    """
    import parameters as p  # Import local pour lire les variables à l'instant T
    
    # 1. Création automatique du dossier d'historique s'il n'existe pas
    output_dir = 'Simulation_Logs'
    os.makedirs(output_dir, exist_ok=True)
    
    # 2. Définition du nom du fichier conforme à tes exigences strictes
    # Exemple : Config_predictive_CTV_Standard_AI.txt
    file_name = f'Config_{strategy_name}_{vessel_type}_{scenario_name}.txt'
    output_path = os.path.join(output_dir, file_name)
    
    # 3. Écriture structurée de toutes les variables
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("===============================================================================\n")
        f.write(f"SIMULATION CONFIGURATION LOG - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("===============================================================================\n\n")
        
        f.write(f"MAINTENANCE STRATEGY : {strategy_name.upper()}\n")
        f.write(f"VESSEL PROFILE       : {vessel_type}\n")
        f.write(f"SCENARIO NAME        : {scenario_name}\n\n")
        
        f.write("-------------------------------------------------------------------------------\n")
        f.write("1. METOCEAN & LOCATION DATA\n")
        f.write("-------------------------------------------------------------------------------\n")
        f.write(f"Park Latitude               : {p.PARK_LAT}\n")
        f.write(f"Park Longitude              : {p.PARK_LON}\n")
        f.write(f"Active Wave Limit (Hs)      : {p.CURRENT_VESSEL_LIMIT} meters\n\n")
        
        f.write("-------------------------------------------------------------------------------\n")
        f.write("2. WIND FARM & FINANCIAL BASELINES\n")
        f.write("-------------------------------------------------------------------------------\n")
        f.write(f"Turbine Nominal Power (MW)  : {p.MW} MW\n")
        f.write(f"Energy Market Price         : {p.price_MWh} EUR/MWh\n")
        f.write(f"Wind Efficiency Factor      : {p.Wfactor}\n")
        f.write(f"Availability Discount Rate  : {p.discount}\n\n")
        
        f.write("-------------------------------------------------------------------------------\n")
        f.write("3. MAINTENANCE TASK BASELINES\n")
        f.write("-------------------------------------------------------------------------------\n")
        f.write(f"Working Day Length (H)      : {p.H} hours\n")
        f.write(f"Service Time per WT (TS)    : {p.TS} minutes\n")
        f.write(f"Mobilization Time (TI)      : {p.TI} minutes\n")
        f.write(f"Average Downtime Length     : {p.h_downtime} hours\n")
        f.write(f"Max WTs Attempted / Day     : {p.MAX_WT_PER_DAY}\n\n")
        
        f.write("-------------------------------------------------------------------------------\n")
        f.write("4. AI MODEL PARAMETERS (Only relevant for Predictive)\n")
        f.write("-------------------------------------------------------------------------------\n")
        f.write(f"Implementation Cost (CPST)  : {p.CPST} EUR\n")
        f.write(f"True Positive Score (MSTP)  : {p.MSTP}\n")
        f.write(f"False Negative Score (MSFN) : {p.MSFN}\n\n")
        
        f.write("-------------------------------------------------------------------------------\n")
        f.write("5. ACTIVE VESSEL CHARTER RATES\n")
        f.write("-------------------------------------------------------------------------------\n")
        f.write(f"Vessel Transit Speed (Vs)   : {p.Vs} m/s\n")
        f.write(f"Fixed Vessel Cost / Day(FCV): {p.FCV} EUR/day\n")
        f.write(f"Service Team Cost / Day(COL): {p.COL} EUR/day\n")
        f.write(f"Hourly Fuel Cost (COF)      : {p.COF} EUR/hour\n")
        f.write("===============================================================================\n")
        
    print(f">>> Configuration de simulation archivée : '{output_path}'")