import os
import shutil
import re

#scenarios = ["Best-Case", "Base-Case", "Worst-Case"]
scenarios = ["Base-Case"]
vessels = [True, False] # True: SOV, False: CTV
ai_profiles = ["perfect", "standard", "mediocre"]
#ai_profiles = ["standard"]

def update_parameters(scenario, sov_bool):
    """Modifie le fichier parameters.py en cours d'utilisation."""
    with open('parameters.py', 'r') as f:
        content = f.read()
        
    # CORRECTION ICI : Utilisation de re.sub au lieu de replace pour la météo
    content = re.sub(r'ACTIVE_WEATHER_SCENARIO\s*=\s*".*"', f'ACTIVE_WEATHER_SCENARIO = "{scenario}"', content)
    
    # Pour le navire, le replace classique fonctionne très bien
    content = content.replace('USE_SOV = True', 'USE_SOV = TEMP_SOV')
    content = content.replace('USE_SOV = False', 'USE_SOV = TEMP_SOV')
    content = content.replace('TEMP_SOV', str(sov_bool))
    
    with open('parameters.py', 'w') as f:
        f.write(content)

if __name__ == "__main__":
    print("Démarrage de la Matrice de Simulation (24 Itérations)...")
    
    try:
        for sc in scenarios:
            for sov in vessels:
                vessel_name = 'SOV' if sov else 'CTV'
                
                # 1. LANCEMENT PRÉVENTIF (1 seule itération par configuration navire/météo)
                print(f"\n[RUN] {sc} | PREVENTIVE | {vessel_name}")
                shutil.copy('parameters_standard.py', 'parameters.py') # Le choix de l'IA n'a pas d'impact ici
                update_parameters(sc, sov)
                os.system("python simulation_preventive.py")

                # 2. LANCEMENT PRÉDICTIF (3 itérations pour tester la sensibilité de l'IA)
                for ai in ai_profiles:
                    print(f"\n[RUN] {sc} | PREDICTIVE ({ai.upper()}) | {vessel_name}")
                    shutil.copy(f'parameters_{ai}.py', 'parameters.py')
                    update_parameters(sc, sov)
                    os.system("python simulation_predictive.py")
                    
    finally:
        print("\nOrchestration terminée. Nettoyage...")
        if os.path.exists('parameters.py'):
            os.remove('parameters.py')