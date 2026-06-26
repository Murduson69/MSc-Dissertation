'''Membership scores of the prediction model used in this case study (Cost Effectiveness)
Expected downtime events and error rates (epsilon)'''

import parameters as p

def evaluate_campaign(wt_list, strategy="predictive"):
    """
    Calcule et affiche les KPIs de la campagne de maintenance.
    strategy : "predictive" (par défaut) ou "preventive"
    """
    title = "Overview of expected, predicted and prevented number of downtime events under predictive maintenance"
    if strategy == "preventive":
        title = "Overview of expected and prevented number of downtime events under preventive maintenance"

    print("\n\n" + "="*115)
    print(title)
    print("="*115)

    nb_days = len(wt_list[0]['Pr_Di'])

    daily_expected = []
    daily_predicted = []
    daily_prevented = []

    # 1. Calcul des métriques pour chaque jour
    for day_index in range(nb_days):
        e_tp_total = 0
        e_fn_total = 0
        prevented_total = 0
        
        for wt in wt_list:
            pr_d = wt['Pr_Di'][day_index]
            
            e_tp = pr_d * p.MSTP
            e_fn = (1.0 - pr_d) * p.MSFN
            
            e_tp_total += e_tp
            e_fn_total += e_fn
            
            if wt.get('repaired') and wt.get('day_repaired') == day_index:
                prevented_total += (e_tp + e_fn)
                
        daily_expected.append(e_tp_total + e_fn_total)
        daily_predicted.append(e_tp_total)
        daily_prevented.append(prevented_total)

    # 2. Calcul des SOMMES TOTALES
    sum_expected = sum(daily_expected)
    sum_predicted = sum(daily_predicted)
    sum_prevented = sum(daily_prevented)

    # 3. Calcul strict des Epsilons
    epsilon = 1.0 - (sum_predicted / sum_expected) if sum_expected > 0 else 0.0
    epsilon_prime = 1.0 - (sum_prevented / sum_expected) if sum_expected > 0 else 0.0

    # =================================================================
    # FORMATAGE DE L'AFFICHAGE
    # =================================================================
    lw = 32
    cw = 10

    header_days = "".join([f"Day {i+1:<{cw-4}}" for i in range(nb_days)])
    header = f"{'':<{lw}}{header_days}{'Sum':<{cw}}"
    separator = "-" * len(header)

    row_exp = f"{'Expected Downtime Events':<{lw}}" + "".join([f"{val:<{cw}.2f}" for val in daily_expected]) + f"{sum_expected:<{cw}.2f}"
    row_prev = f"{'Downtime Events Prevented':<{lw}}" + "".join([f"{val:<{cw}.2f}" for val in daily_prevented]) + f"{sum_prevented:<{cw}.2f}"

    empty_space = " " * (lw + cw * (nb_days - 1))
    sym_eps = "ε"
    sym_eps_prime = "ε'"

    print(header)
    print(separator)
    print(row_exp)

    # Affichage conditionnel selon la stratégie
    if strategy == "predictive":
        row_pred = f"{'Downtime Events Predicted':<{lw}}" + "".join([f"{val:<{cw}.2f}" for val in daily_predicted]) + f"{sum_predicted:<{cw}.2f}"
        print(row_pred)

    print(row_prev)
    print(separator)

    if strategy == "predictive":
        row_eps_labels = empty_space + f"{sym_eps:<{cw}}{sym_eps_prime:<{cw}}"
        row_eps_sep = empty_space + "-" * (cw * 2)
        row_eps_values = empty_space + f"{epsilon:<{cw}.2f}{epsilon_prime:<{cw}.2f}"
    else:
        # En préventif, on masque la colonne de l'erreur de prédiction (ε)
        row_eps_labels = empty_space + f"{'':<{cw}}{sym_eps_prime:<{cw}}"
        row_eps_sep = empty_space + " " * cw + "-" * cw
        row_eps_values = empty_space + f"{'':<{cw}}{epsilon_prime:<{cw}.2f}"

    print(row_eps_labels)
    print(row_eps_sep)
    print(row_eps_values)
    print("="*115 + "\n")
    
    return daily_expected, daily_predicted, daily_prevented, epsilon_prime