import parameters as p
from table_exporter import export_financial_table_image

def evaluate_financials(daily_expected, daily_prevented, daily_shift_times, epsilon_prime, mission_end_day, strategy="predictive"):
    """
    Calcule et affiche le bilan financier (Tableau 11) en couplant la logistique et la finance.
    Le coût du carburant est calculé dynamiquement : shift_time * p.COF
    """
    # Sécurité : On s'assure que toutes les listes couvrent la même période
    assert len(daily_expected) == len(daily_prevented) == len(daily_shift_times), \
        "Erreur : Toutes les listes (expected, prevented, shift_times) doivent avoir la même taille."
    
    nb_days = len(daily_expected)

    # Équation (2) : Revenu d'une éolienne pour 1 heure (calculé via parameters.py)
    rev_per_hour_per_wt = p.MW * p.price_MWh * p.Wfactor * p.discount
    rev_per_day = rev_per_hour_per_wt * 24

    # Coût fixe journalier = Navire (FCV) + Équipe (COL)
    base_vessel_team_cost = p.FCV + p.COL 
    cpst = p.CPST if strategy == "predictive" else 0.0

    # Détection du dernier jour d'activité réelle pour la démobilisation anticipée
    last_active_day = -1
    for i in range(nb_days):
        if daily_prevented[i] > 0:
            last_active_day = i

    sum_rev = 0
    sum_cod = 0
    sum_vessel_team = 0
    sum_fuel = 0
    
    rows = []
    
    for i in range(nb_days):
        # A. Manque à gagner (Cost of Downtime)
        downtimes = max(0, daily_expected[i] - daily_prevented[i])
        cod = downtimes * p.h_downtime * rev_per_hour_per_wt
        
        # B. Logique d'activation des coûts selon le statut de la mission
        if i <= mission_end_day:
            daily_vt_cost = base_vessel_team_cost
            # CALCUL DYNAMIQUE DU FUEL : Temps de mer effectif * Coût horaire
            fuel = daily_shift_times[i] * p.COF
        else:
            # Mission terminée, le navire est rentré au port, coûts stoppés
            daily_vt_cost = 0.0
            fuel = 0.0
        
        rows.append({
            "day": f"Day {i+1}",
            "rev": rev_per_day,
            "dt": downtimes,
            "cod": cod,
            "vt": daily_vt_cost,
            "fuel": fuel
        })
        
        sum_rev += rev_per_day
        sum_cod += cod
        sum_vessel_team += daily_vt_cost
        sum_fuel += fuel

    # Équation (1) : Totaux généraux et Profit net
    cst = sum_vessel_team + sum_fuel
    pt = sum_rev - sum_cod - cst - cpst

    # =================================================================
    # MISE EN FORME CONFORME AU TABLEAU 11
    # =================================================================
    cw_day = 8
    cw_rev = 18
    cw_dt = 12
    cw_cod = 18
    cw_vt = 18
    cw_fuel = 15

    print("\n\n" + "="*115)
    print(f"Potential revenue and costs for the service mission under {strategy} maintenance with ε' = {epsilon_prime:.2f}.")
    print("=" * 115)
    
    header = (f"{'':<{cw_day}}{'Rev':^{cw_rev}}{'Downtimes':^{cw_dt}}"
              f"{'CoD':^{cw_cod}}{'Vessel + Team':^{cw_vt}}{'Fuel':^{cw_fuel}}")
    print(header)
    print("-" * 115)
    
    for r in rows:
        rev_str = f"EUR {r['rev']:.2f}"
        dt_str = f"{r['dt']:.2f}" if r['dt'] > 0 else "0"
        cod_str = f"EUR {r['cod']:.2f}" if r['cod'] > 0 else "EUR -"
        vt_str = f"EUR {r['vt']:.2f}" if r['vt'] > 0 else "EUR -"
        fuel_str = f"EUR {r['fuel']:.2f}" if r['fuel'] > 0 else "EUR -"
        
        line = (f"{r['day']:<{cw_day}}{rev_str:^{cw_rev}}{dt_str:^{cw_dt}}"
                f"{cod_str:^{cw_cod}}{vt_str:^{cw_vt}}{fuel_str:^{cw_fuel}}")
        print(line)
        
    print("-" * 115)
    
    rev_tot_str = f"EUR {sum_rev:.2f}"
    cod_tot_str = f"EUR {sum_cod:.2f}"
    cst_tot_str = f"EUR {cst:.2f}"
    sym_eps = "ε'"
    
    tot_line1 = (f"{'Rev_T':<{cw_day}}{rev_tot_str:^{cw_rev}}{f'CoD_T({sym_eps})':^{cw_dt}}"
                 f"{cod_tot_str:^{cw_cod}}{f'CS_T({sym_eps})':^{cw_vt}}{cst_tot_str:^{cw_fuel}}")
    print(tot_line1)
    
    pt_str = f"EUR {pt:.2f}"
    sym_eps_double = "ε, ε'" if strategy == "predictive" else "ε'"
    
    tot_line2 = (f"{'':<{cw_day}}{'':^{cw_rev}}{'':^{cw_dt}}"
                 f"{'':^{cw_cod}}{f'P_T({sym_eps_double})':^{cw_vt}}{pt_str:^{cw_fuel}}")
    print(tot_line2)
    print("=" * 115 + "\n")
    return rows, sum_rev, sum_cod, cst, pt
    
def print_mission_status(wt_list):
    """
    Affiche un bilan critique de la campagne à l'attention du management.
    """
    total_wts = len(wt_list)
    repaired_wts = sum(1 for wt in wt_list if wt.get('repaired', False))
    success_rate = (repaired_wts / total_wts) * 100

    print("=" * 100)
    print(f"                   OPERATIONAL CAMPAIGN REPORT: {repaired_wts}/{total_wts} WTs SERVICED")
    print("=" * 100)
    
    if success_rate == 100:
        print(f">>> [SUCCESS] Mission completed! All {total_wts} turbines have been successfully serviced.")
    elif success_rate >= 70:
        print(f">>> [WARNING] Mission partially successful. {repaired_wts}/{total_wts} WTs serviced ({success_rate:.1f}%).")
        print(f"    Remaining targets ({total_wts - repaired_wts} WTs) must be rescheduled for the next weather window.")
    else:
        print(f">>> [CRITICAL FAILURE] Mission aborted due to harsh weather conditions!")
        print(f"    Only {repaired_wts}/{total_wts} WTs could be serviced ({success_rate:.1f}%).")
        print(f"    The vessel was gridlocked at port for the majority of the campaign.")
        print(f"    CRITICAL IMPACT: Severe accumulation of unmitigated risk and high Cost of Downtime (CoD).")
    
    print("=" * 100 + "\n")
    
