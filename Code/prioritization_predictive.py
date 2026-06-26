from WT_data import list_WT
import parameters as p
from routing import find_optimal_route

nb_days = len(list_WT[0]['Pr_Di'])

# We loop through each day (index 0 to 6 for days 1 to 7)
for day_index in range(nb_days):
    current_day = day_index + 1
    print(f"\n{'='*40}")
    print(f"MAINTENANCE PRIORITIES & PLAN - DAY {current_day}")
    print(f"{'='*40}")
    
    # 1. FILTERING: Only wind turbines that have not yet been repaired are kept
    turbines_on_hold = [wt for wt in list_WT if not wt['repaired']]
    
    # Condition for stopping if everything is repaired
    if len(turbines_on_hold) == 0:
        print("All the wind turbines have been repaired.")
        break
        
    # 2. SORT: Sort in descending order according to the current day's Pr_Di.
    turbines_sorted = sorted(
        turbines_on_hold, 
        key=lambda x: x['Pr_Di'][day_index], 
        reverse=True
    )
    
    # 3. TEST DISPLAY OF THE QUEUE
    # print(f"Top priorities (Prediction Score Pr_Di) :")
    # for position, wt in enumerate(turbines_sorted):
    #     score_of_the_day = wt['Pr_Di'][day_index]
    #     print(f" {position + 1}. {wt['ID']} | Risk : {score_of_the_day:.2f} | Coordinates : ({wt['X']}, {wt['Y']})")
        
    # 4. SELECTION (Take the top N most critical turbines)
    daily_targets = turbines_sorted[:p.MAX_WT_PER_DAY]
    
    print("Selected Targets for today:")
    for wt in daily_targets:
        print(f" - {wt['ID']} (Risk: {wt['Pr_Di'][day_index]:.2f})")
        
    # 5. ROUTING & SCHEDULING
    optimal_route, distance, shift_time = find_optimal_route(
        target_wts=daily_targets,
        base_coords=p.Base_coords,
        ts=p.TS,
        ti=p.TI,
        vs=p.Vs
    )
    
    route_names = [wt['ID'] for wt in optimal_route]
    print(f"\nOptimal Path : Base -> {' -> '.join(route_names)} -> Base")
    print(f"Total Distance : {distance:.2f} km")
    print(f"Shift Duration : {shift_time:.2f} hours (Max allowed: {p.H}h)")
    
    # 6. VALIDATION
    if shift_time <= p.H:
        print(">>> STATUS: Route APPROVED.")
        # We mark them as repaired so they disappear tomorrow
        for wt in daily_targets:
            wt['repaired'] = True
    else:
        print(">>> STATUS: FAILED! Shift duration exceeds the limit H.")
        # Here, in the future, you could tell the code to drop the last WT 
        # and try again, but for now, it just warns you.
