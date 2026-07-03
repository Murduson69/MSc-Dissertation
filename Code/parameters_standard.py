"""
===============================================================================
MASTER CONFIGURATION FILE
Centralizes all physical, financial, and logistical parameters for the simulation.
===============================================================================
"""
from WT_data import list_WT

# =============================================================================
# 1. METOCEAN & LOCATION DATA (Copernicus API Integration)
# =============================================================================
PARK_LAT = 57.2139
PARK_LON = -1.9223

COPERNICUS_DATASET_ID = "cmems_mod_glo_wav_anfc_0.083deg_PT3H-i"

# Définition des dates exactes pour tes 3 scénarios (Mets à jour le Base-Case)
WEATHER_SCENARIOS = {
    "Best-Case": {
        "start": "2024-09-15T18:00:00",
        "end":   "2024-09-22T18:00:00"
    },
    "Base-Case": {
        "start": "2024-02-16T03:00:00",  
        "end":   "2024-02-23T03:00:00"   
    },
    "Worst-Case": {
        "start": "2024-01-01T00:00:00",
        "end":   "2024-01-08T00:00:00"
    }
}

# ---> CHANGE CE PARAMÈTRE POUR BASCULER D'UNE SEMAINE À L'AUTRE <---
ACTIVE_WEATHER_SCENARIO = "Base-Case"

# Extraction automatique des variables pour les scripts de simulation
START_DATE = WEATHER_SCENARIOS[ACTIVE_WEATHER_SCENARIO]["start"]
END_DATE = WEATHER_SCENARIOS[ACTIVE_WEATHER_SCENARIO]["end"]
OUTPUT_NC_FILE = f"Hs_Aberdeen_{ACTIVE_WEATHER_SCENARIO}.nc"


# =============================================================================
# 2. WIND FARM & FINANCIAL PARAMETERS
# =============================================================================
MW = 3.6           # Nominal power output of the WT (in MW)
price_MWh = 168    # Price of energy (in EUR/MWh)
Wfactor = 0.9      # Wind factor (ideal conditions)
discount = 0.96    # Discount rate based on industry availability standards

# =============================================================================
# 3. MAINTENANCE TASK PARAMETERS
# =============================================================================
H = 12             # Length of working day (in hours)
TS = 120           # Time to service a WT (in minutes)
TI = 15            # Mobilization time per turbine (in minutes)
h_downtime = 3.5   # Average length of a downtime event (in hours)
MAX_WT_PER_DAY = 6 # Maximum number of WTs to attempt per day

# =============================================================================
# 4. PREDICTIVE AI MODEL PARAMETERS
# =============================================================================
CPST = 500         # Fixed implementation cost for predictive maintenance (in EUR)
# Standardized Membership Scores (Cost-Effectiveness article Table 6)
AI_PROFILE_NAME = "Standard"
MSTP = 0.88        # True Positive score
MSFN = 0.07        # False Negative score

# =============================================================================
# 5. LOGISTICS & VESSEL CONFIGURATION
# =============================================================================
# Base Coordinates Calculation
Base_CTV_coords = {'X': 0, 'Y': 0}
avg_x = sum(wt['X'] for wt in list_WT) / len(list_WT)
avg_y = sum(wt['Y'] for wt in list_WT) / len(list_WT)
Base_SOV_coords = {'X': avg_x, 'Y': avg_y}

# --- VESSEL TOGGLE ---
# Change this to True to simulate an SOV, or False for a CTV
USE_SOV = False  

if USE_SOV:
    # SOV Profile (Service Operation Vessel from Dobbie at Manchester)
    CURRENT_VESSEL_LIMIT = 3.5       # Wave limit (in meters)
    Base_coords = Base_SOV_coords    # Anchored at the offshore barycenter
    Vs = 6.2                         # Average speed (in m/s, approx 12 knots)
    FCV = 35000                      # Fixed vessel cost per day (in EUR)
    COL = 4500                       # Cost of service team per day (in EUR)
    COF = 3000                        # Cost of vessel fuel per day (in EUR/day)
else:
    # CTV Profile (Crew Transfer Vessel from Frederiksen's paper)
    CURRENT_VESSEL_LIMIT = 1.3       # Wave limit (in meters)
    Base_coords = Base_CTV_coords    # Port departure (0, 0)
    Vs = 8.0                         # Average speed (in m/s, approx 15 knots)
    FCV = 3400                       # Fixed vessel cost per day (in EUR)
    COL = 1440                       # Cost of service team per day (in EUR)
    COF = 400                        # Cost of vessel fuel per hour (in EUR/hour)