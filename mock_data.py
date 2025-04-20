# mock_data.py
import random

def generate_mock_flights(origin, destination, departure_date, return_date=None, max_results=3):
    airlines = ["SkyWings", "OceanAir", "Global Express"]
    flight_times = ["06:30", "10:15", "14:45"]
    results = []
    for _ in range(max_results):
        dep_time = random.choice(flight_times)
        duration_hours = random.randint(2, 6)
        duration_mins = random.choice([0, 30])
        arr_hour = (int(dep_time[:2]) + duration_hours) % 24
        arr_time = f"{arr_hour:02}:{dep_time[3:]}"
        results.append({
            "airline": random.choice(airlines),
            "flight_number": f"SK{random.randint(100,999)}",
            "departure": {"airport": origin, "time": dep_time},
            "arrival": {"airport": destination, "time": arr_time},
            "duration": f"{duration_hours}h {duration_mins}m",
            "price": f"{random.randint(200, 700)}",
            "stops": random.choice([0, 1]),
            "departure_time": dep_time,
            "arrival_time": arr_time,
            "origin": origin,
            "destination": destination
        })
    return results


def generate_mock_hotels(destination, check_in, check_out, max_results=3):
    names = ["Comfort Inn", "Luxury Suites", "Seaside Resort"]
    results = []
    for name in names[:max_results]:
        results.append({
            "name": f"{name} {destination}",
            "price_per_night": f"${random.randint(90, 250)}",
            "location": f"Central {destination}",
            "rating": f"{random.uniform(7.5, 9.5):.1f}/10",
            "amenities": ["Wi-Fi", "Breakfast", "Pool"]
        })
    return results

def generate_mock_car_rentals(location, pickup_date, return_date, max_results=2):
    types = ["Economy", "SUV", "Convertible"]
    categories = ["Compact", "SUV", "Luxury"]
    results = []
    for _ in range(max_results):
        results.append({
            "company": random.choice(["Hertz", "Avis"]),
            "car_type": random.choice(types),
            "model": "Ford Focus",
            "price_per_day": f"${random.randint(30, 80)}",
            "total_price": f"${random.randint(100, 250)}",
            "pickup_location": f"{location} Downtown",
            "features": ["Automatic", "GPS"],
            "description": f"Comfortable and reliable {random.choice(types)} car for city and highway driving.",
            "seats": random.choice([4, 5, 7]),
            "transmission": random.choice(["Automatic", "Manual"]),
            "category": random.choice(categories)
        })
    return results
