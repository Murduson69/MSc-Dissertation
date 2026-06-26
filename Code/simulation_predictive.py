import copy
from WT_data import list_WT as original_list_WT
import parameters as p
from routing import find_optimal_route
from Hs import get_hs_time_series
from weather_check import is_weather_window_safe
from expected_outcome import evaluate_campaign
from financial_evaluation import evaluate_financials, print_mission_status
from visualization import plot_daily_route
from table_exporter import export_financial_table_image, export_downtime_table_image, export_simulation_parameters

CURRENT_SCENARIO = "Predictive_Standard_AI"  # Tu pourras changer ça en "Perfect_AI" plus tard

# --- 0. PRE-COMPUTATION: Fetch Weather Data ---
print("Fetching Metocean data from Copernicus NetCDF files...")
hs_data = get_hs_time_series(
    folder_path=p.WAVE_DATA_FOLDER,
    file_names=p.WAVE_DATA_FILES,
    target_lat=p.PARK_LAT,
    target_lon=p.PARK_LON
)
print("Weather data successfully loaded!\n")

list_WT = copy.deepcopy(original_list_WT)
for wt in list_WT:
    wt['repaired'] = False
    if 'day_repaired' in wt:
        del wt['day_repaired']
        
nb_days = len(list_WT[0]['Pr_Di'])
daily_shift_times = [0.0] * nb_days
mission_end_day = nb_days - 1

# We loop through each day
for day_index in range(nb_days):
    current_day = day_index + 1
    print(f"\n{'='*50}")
    print(f"PREDICTIVE MAINTENANCE PLAN - DAY {current_day}")
    print(f"{'='*50}")
    
    # 1. FILTERING
    turbines_on_hold = [wt for wt in list_WT if not wt['repaired']]
    
    if len(turbines_on_hold) == 0:
        print("All the wind turbines have been repaired. Mission Complete!")
        break
        
    # 2. SORTING
    turbines_sorted = sorted(
        turbines_on_hold, 
        key=lambda x: x['Pr_Di'][day_index], 
        reverse=True
    )
    
    # 3 & 4. SELECTION
    daily_targets = turbines_sorted[:p.MAX_WT_PER_DAY]
    
    print("Selected Targets for today (Riskiest first):")
    for wt in daily_targets:
        print(f" - {wt['ID']} (Risk: {wt['Pr_Di'][day_index]:.2f})")
        
    # =================================================================
    # 5. OPPORTUNISTIC ROUTING & WEATHER CHECK
    # =================================================================
    print("\n[ LOGISTICS & WEATHER CHECK ]")
    route_approved = False
    
    # Loop backwards: Try 3 WTs, if fail try 2, if fail try 1
    for nb_wt_to_try in range(len(daily_targets), 0, -1):
        test_targets = daily_targets[:nb_wt_to_try]
        
        # Calculate logistics for this sub-group
        optimal_route, distance, shift_time = find_optimal_route(
            target_wts=test_targets,
            base_coords=p.Base_coords,
            ts=p.TS,
            ti=p.TI,
            vs=p.Vs
        )
        
        # Check if the shift duration exceeds the absolute daily limit H
        if shift_time > p.H:
            continue # Skip weather check, try with one less turbine
            
        # Check weather window for this specific duration
        is_safe, max_wave = is_weather_window_safe(
            hs_data_list=hs_data,
            day_index=day_index,
            required_hours=shift_time,
            vessel_limit=p.CURRENT_VESSEL_LIMIT
        )
        
        if is_safe:
            # We found a valid opportunistic window!
            route_approved = True
            daily_shift_times[day_index] = shift_time
            route_names = [wt['ID'] for wt in optimal_route]
            
            print(f">>> GO WINDOW FOUND : {shift_time:.1f}h of safe conditions.")
            print(f"Max wave during operations: {max_wave:.2f}m (Limit: {p.CURRENT_VESSEL_LIMIT}m)")
            print(f"Optimal Path : Base -> {' -> '.join(route_names)} -> Base")
            print(f"Total Distance for this tour: {distance:.2f} km")
            
            plot_daily_route(day_index, p.Base_coords, list_WT, optimal_route, p.USE_SOV, scenario_name=CURRENT_SCENARIO)
            # Validate repairs
            for wt in test_targets:
                wt['repaired'] = True
                wt['day_repaired'] = day_index
            
            # Break out of the fallback loop, we are done for today!
            break 
            
    # If the loop finishes and route_approved is still False, it's a NO-GO
    if not route_approved:
        print(f">>> NO-GO: Operations aborted for today.")
        print(f">>> STATUS: Waves exceed {p.CURRENT_VESSEL_LIMIT}m limit (max wave during operations: {max_wave:.2f}m) or time is too short even for 1 turbine.")
        print(">>> Turbines remain damaged. Moving targets to tomorrow's queue.")
        
    # =================================================================
    # VÉRIFICATION DE FIN DE MISSION ANTICIPÉE
    # =================================================================
    turbines_left = [wt for wt in list_WT if not wt['repaired']]
    if len(turbines_left) == 0:
        print(f"\n>>> ALL TURBINES REPAIRED ON DAY {day_index + 1}! Early demobilization of the vessel.")
        mission_end_day = day_index
        break 
        
        
# =================================================================
# 5. EVALUATION FINALE ET EXPORT EN PNG
# =================================================================
# 1. On récupère les 4 résultats de l'IA
daily_expected, daily_predicted, daily_prevented, epsilon_prime = evaluate_campaign(list_WT, strategy="predictive")

# 2. On récupère les 5 résultats financiers
rows, sum_rev, sum_cod, cst, pt = evaluate_financials(daily_expected, daily_prevented, daily_shift_times, epsilon_prime, mission_end_day, strategy="predictive")

print_mission_status(list_WT)

# 3. On ordonne à table_exporter de dessiner les deux PNG
vessel_name = "SOV" if p.USE_SOV else "CTV"

export_downtime_table_image(daily_expected, daily_predicted, daily_prevented, vessel_name, "predictive", CURRENT_SCENARIO)
export_financial_table_image(rows, sum_rev, sum_cod, cst, pt, epsilon_prime, vessel_name, "predictive", CURRENT_SCENARIO)
export_simulation_parameters(strategy_name="predictive", scenario_name=CURRENT_SCENARIO, vessel_type=vessel_name)