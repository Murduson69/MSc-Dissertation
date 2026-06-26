import math

def is_weather_window_safe(hs_data_list, day_index, required_hours, vessel_limit):
    """
    Checks if the sea remains below the vessel's limit for the required time.
    Assumes a 3-hour time step for weather data.
    """
    # Assuming one data point every 3 hours
    start_index = (day_index * 8) + 1  # Assumption: starts at the 2nd value (06:00 AM)
    
    # How many weather blocks are needed to cover the required hours?
    blocks_needed = math.ceil(required_hours / 3)
    end_index = start_index + blocks_needed
    
    # Safety check in case we exceed the end of the data list
    if end_index > len(hs_data_list):
        return False, 99.9 # False flag to block
        
    weather_window = hs_data_list[start_index:end_index]
    max_wave = max(weather_window)
    
    if max_wave <= vessel_limit:
        return True, max_wave
    else:
        return False, max_wave