import pandas as pd
import random
from datetime import datetime, timedelta

def generate_enterprise_data(num_rows=250):
    data = []
    # Start 6 months ago to give the trend chart a nice curve
    start_date = datetime.now() - timedelta(days=180)

    # The exact mappings we built for the Data Entry page
    activities = [
        # Energy
        ("Energy Consumption", "Non-Renewable (Fossil)", "Grid Electricity", "kWh", 0.82, 1000, 5000),
        ("Energy Consumption", "Renewable (Clean)", "Solar Power", "kWh", 0.0, 500, 2000),
        ("Energy Consumption", "Renewable (Clean)", "Wind Power", "kWh", 0.0, 300, 1500),
        ("Energy Consumption", "Non-Renewable (Fossil)", "Diesel Generator", "Liters", 2.68, 300, 3000),
        
        # Waste
        ("Waste Management", "Landfill", "Organic Waste (Landfill)", "kg", 1.5, 20, 150),
        ("Waste Management", "Recycled/Composted", "Organic Waste (Recycled/Composted)", "kg", 0.1, 50, 300),
        ("Waste Management", "Landfill", "Plastic Packaging (Landfill)", "kg", 0.05, 10, 100),
        ("Waste Management", "Recycled/Composted", "Plastic Packaging (Recycled/Composted)", "kg", 0.02, 50, 400),
        ("Waste Management", "Landfill", "Paper/Cardboard (Landfill)", "kg", 0.5, 30, 200),
        ("Waste Management", "Recycled/Composted", "Paper/Cardboard (Recycled/Composted)", "kg", 0.02, 100, 600),
        ("Waste Management", "Landfill", "E-Waste (Landfill)", "kg", 0.1, 5, 50),
        
        # Carbon
        ("Carbon Emissions", "Direct Emission", "Petrol Vehicle Commute", "km", 0.19, 100, 1000),
        ("Carbon Emissions", "Direct Emission", "EV Commute", "km", 0.0, 100, 1000),
        ("Carbon Emissions", "Direct Emission", "Business Flight", "km", 0.25, 1500, 8000),
        ("Carbon Emissions", "Direct Emission", "AC Refrigerant Leak (R410a)", "kg", 2088.0, 0.5, 3.0)
    ]

    for _ in range(num_rows):
        # Pick a random date within the last 6 months
        random_days = random.randint(0, 180)
        entry_date = (start_date + timedelta(days=random_days)).strftime('%Y-%m-%d')
        
        # Pick a random activity, weighting against AC leaks so they don't happen every day
        if random.random() > 0.95:
            item = activities[-1] # AC leak
        else:
            item = random.choice(activities[:-1])
            
        scope, category, activity, unit, factor, min_qty, max_qty = item
        quantity = round(random.uniform(min_qty, max_qty), 2)
        
        data.append({
            "date": entry_date,
            "scope": scope,
            "category": category,
            "activity": activity,
            "quantity": quantity,
            "unit": unit,
            "emission_factor": factor
        })

    # Convert to DataFrame, sort by date, and save
    df = pd.DataFrame(data)
    df = df.sort_values(by='date')
    df.to_csv('gtu_large_dataset.csv', index=False)
    print(f"✅ Generated gtu_large_dataset.csv with {num_rows} rows!")

if __name__ == "__main__":
    generate_enterprise_data(250)