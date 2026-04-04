import pandas as pd
import numpy as np
from datetime import date, timedelta
import random

def generate_indian_sme_data():
    start_date = date(2024, 1, 1)
    end_date = date(2026, 4, 4) # Up to current date
    total_days = (end_date - start_date).days
    
    data = []
    
    # Standard Emission Factors (Approximate for India)
    EF_GRID = 0.716        # kgCO2e/kWh (Central Electricity Authority India avg)
    EF_DIESEL = 2.68       # kgCO2e/Liter
    EF_PETROL = 2.31       # kgCO2e/Liter
    EF_LANDFILL = 0.45     # kgCO2e/kg
    EF_RECYCLING = 0.02    # kgCO2e/kg (Transport overhead for scrap)
    EF_R32 = 675.0         # kgCO2e/kg (Modern AC refrigerant)

    for i in range(total_days + 1):
        current_date = start_date + timedelta(days=i)
        month = current_date.month
        year = current_date.year

        # --- 1. ELECTRICITY (Daily) ---
        # Base load for machinery/lights
        base_load = np.random.normal(450, 30) 
        
        # Summer HVAC Spike (March - June)
        if month in [3, 4, 5, 6]:
            base_load += np.random.normal(150, 20)
            
        solar_generation = 0
        # Simulating a CapEx 50kW Solar Rooftop plant commissioned in Jan 2025
        if year >= 2025:
            # Baseline solar generation
            solar_generation = np.random.normal(200, 15)
            # Monsoon cloud cover penalty (July - August)
            if month in [7, 8]:
                solar_generation *= 0.6 
                
        grid_consumption = max(0, base_load - solar_generation)
        data.append([current_date, "Scope 2", "Purchased Electricity", "State Grid", grid_consumption, "kWh", EF_GRID])
        
        if solar_generation > 0:
            data.append([current_date, "Scope 2", "Purchased Electricity", "Rooftop Solar", solar_generation, "kWh", 0.0])

        # --- 2. BACKUP POWER (Sporadic) ---
        # Diesel Generator usage due to local load shedding/power cuts
        # More frequent in summer/monsoon
        if random.random() < (0.15 if month in [5, 6, 7] else 0.05):
            diesel_liters = np.random.normal(15, 5)
            data.append([current_date, "Scope 1", "Stationary Combustion", "DG Set (Diesel)", diesel_liters, "Liter", EF_DIESEL])

        # --- 3. VEHICLE FLEET (Weekly) ---
        if current_date.weekday() == 5: # Every Saturday
            # Company delivery tempo (Diesel)
            data.append([current_date, "Scope 1", "Mobile Combustion", "Delivery Truck (Diesel)", np.random.normal(40, 5), "Liter", EF_DIESEL])
            # Management/Sales cars (Petrol)
            data.append([current_date, "Scope 1", "Mobile Combustion", "Company Cars (Petrol)", np.random.normal(25, 3), "Liter", EF_PETROL])

        # --- 4. WASTE MANAGEMENT (Weekly) ---
        if current_date.weekday() == 4: # Every Friday
            # General facility waste
            data.append([current_date, "Scope 3", "Waste Generated", "Mixed Municipal Waste", np.random.normal(80, 10), "kg", EF_LANDFILL])
            
            # Industrial scrap/cardboard sold to local recyclers
            # Slowly improving recycling separation over time
            recycling_efficiency = 1.0 if year == 2024 else 1.3
            data.append([current_date, "Scope 3", "Waste Generated", "Scrap Metal & Cardboard", np.random.normal(50 * recycling_efficiency, 5), "kg", EF_RECYCLING])

        # --- 5. HVAC MAINTENANCE (Annual) ---
        # Pre-summer AC servicing topping up leaked gas
        if month == 3 and current_date.day == 15:
            data.append([current_date, "Scope 1", "Fugitive Emissions", "AC Refrigerant (R-32)", np.random.normal(1.5, 0.2), "kg", EF_R32])

    df = pd.DataFrame(data, columns=["date", "scope", "category", "activity", "quantity", "unit", "emission_factor"])
    
    df.to_csv("sme_realistic_data.csv", index=False)
    print(f"Generated {len(df)} rows of realistic Indian SME data.")

if __name__ == "__main__":
    generate_indian_sme_data()