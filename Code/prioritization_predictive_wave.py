from WT_data import list_WT
import parameters as p
from routing import find_optimal_route
from Hs import get_hs_time_series
from weather_check import is_weather_window_safe

# --- 0. PRE-COMPUTATION: Fetch Weather Data ---
print("Fetching Metocean data from Copernicus NetCDF files...")
hs_data = get_hs_time_series(
    folder_path=p.WAVE_DATA_FOLDER,
    file_names=p.WAVE_DATA_FILES,
    target_lat=p.PARK_LAT,
    target_lon=p.PARK_LON
)
print("Weather data successfully loaded!\n")

nb_days = len(list_WT[0]['Pr_Di'])

# We loop through each day
for day_index in range(nb_days):
    current_day = day_index + 1
    print(f"\n{'='*50}")
    print(f"MAINTENANCE PRIORITIES & PLAN - DAY {current_day}")
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
    
    print("Selected Targets for today:")
    for wt in daily_targets:
        print(f" - {wt['ID']} (Risk: {wt['Pr_Di'][day_index]:.2f})")
        
    # =================================================================
    # 5. OPPORTUNISTIC ROUTING & WEATHER CHECK
    # =================================================================
    print("\n[ DYNAMIC WEATHER ROUTING ]")
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
            route_names = [wt['ID'] for wt in optimal_route]
            
            print(f">>> WINDOW FOUND : {shift_time:.1f}h of safe conditions.")
            print(f"Max wave during operations: {max_wave:.2f}m (Limit: {p.CURRENT_VESSEL_LIMIT}m)")
            print(f"Optimal Path : Base -> {' -> '.join(route_names)} -> Base")
            print(f"Total Distance : {distance:.2f} km")
            
            # Validate repairs
            for wt in test_targets:
                wt['repaired'] = True
                wt['day_repaired'] = day_index
            
            # Break out of the fallback loop, we are done for today!
            break 
            
    # If the loop finishes and route_approved is still False, it's a NO-GO
    if not route_approved:
        print(f">>> NO-GO: Operations aborted for today.")
        print(f">>> STATUS: Waves exceed {p.CURRENT_VESSEL_LIMIT}m limit or time is too short even for 1 turbine.")
        print(">>> Turbines remain damaged. Moving targets to tomorrow's queue.")
        
from expected_outcome import evaluate_campaign

evaluate_campaign(list_WT)