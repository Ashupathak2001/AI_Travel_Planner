# main.py 
import streamlit as st
import datetime
from ai_itinerary import generate_itinerary_prompt, generate_with_ollama
from mock_data import generate_mock_flights, generate_mock_hotels, generate_mock_car_rentals
import folium
from streamlit_folium import folium_static
import random  # Added for fallback when scraper fails

# Fallback function when scraper fails
def fallback_hotels(destination, check_in, check_out):
    """Generate backup hotel data if the scraper fails"""
    hotels = []
    hotel_names = {
        "Paris": ["Grand Hôtel de Paris", "Le Marais Suites", "Eiffel View Residence"],
        "Tokyo": ["Shinjuku Plaza Hotel", "Tokyo Bay Resort", "Imperial Garden Inn"],
        "New York": ["Manhattan Skyline Hotel", "Broadway Comfort Inn", "Central Park Lodge"],
        "Dubai": ["Palm Luxury Resort", "Desert Oasis Hotel", "Marina View Suites"]
    }
    
    descriptions = [
        f"Experience the heart of {destination} at this centrally located hotel with modern amenities and exceptional service.",
        f"Situated in the most vibrant district of {destination}, this hotel offers comfort and convenience for all travelers.",
        f"Luxury accommodations with stunning views of {destination}'s most iconic landmarks."
    ]
    
    names = hotel_names.get(destination, ["Luxury Hotel", "City Center Inn", "Plaza Resort"])
    
    for i in range(min(3, len(names))):
        hotels.append({
            "name": names[i],
            "description": descriptions[i % len(descriptions)],
            "url": f"https://example.com/hotels/{destination.lower().replace(' ', '-')}/{i+1}"
        })
    return hotels

# Fallback function for flights
def fallback_flights(origin, destination, departure_date, return_date):
    """Generate backup flight data if the scraper fails"""
    return generate_mock_flights(origin, destination, departure_date, return_date)

# Fallback function for car rentals
def fallback_car_rentals(location, start_date, end_date):
    """Generate backup car rental data if the scraper fails"""
    return generate_mock_car_rentals(location, start_date, end_date)

# Safe scraper function that falls back to mock data
def safe_scrape_hotels(destination, check_in, check_out):
    """Attempt to scrape hotels, fallback to mock data if fails"""
    try:
        from scraper import scrape_hotels
        results = scrape_hotels(destination, check_in, check_out)
        if not results or len(results) == 0:
            return fallback_hotels(destination, check_in, check_out)
        return results
    except Exception as e:
        st.warning(f"Hotel data couldn't be scraped: {str(e)}. Using simulated data instead.")
        return fallback_hotels(destination, check_in, check_out)
    
# New function for scraping flights
def safe_scrape_flights(origin, destination, departure_date, return_date):
    """Attempt to scrape flights, fallback to mock data if fails"""
    try:
        from scraper import scrape_flights
        results = scrape_flights(origin, destination, departure_date, return_date)
        if not results or len(results) == 0:
            return fallback_flights(origin, destination, departure_date, return_date)
        return results
    except Exception as e:
        st.warning(f"Flight data couldn't be scraped: {str(e)}. Using simulated data instead.")
        return fallback_flights(origin, destination, departure_date, return_date)

# New function for scraping car rentals
def safe_scrape_car_rentals(location, start_date, end_date):
    """Attempt to scrape car rentals, fallback to mock data if fails"""
    try:
        from scraper import scrape_car_rentals
        results = scrape_car_rentals(location, start_date, end_date)
        if not results or len(results) == 0:
            return fallback_car_rentals(location, start_date, end_date)
        return results
    except Exception as e:
        st.warning(f"Car rental data couldn't be scraped: {str(e)}. Using simulated data instead.")
        return fallback_car_rentals(location, start_date, end_date)

st.set_page_config(page_title="TravelBuddy - AI Tour Planner", page_icon="✈️", layout="wide")

# Enhanced CSS with modern UI elements
st.markdown("""
    <style>
        /* Main container styling */
        .main {
            padding: 2rem;
            background-color: #1e1e1e;
            color: #f5f5f5;
            transition: all 0.3s ease;
        }
        
        /* Typography */
        h1 {
            font-weight: 900;
            margin-bottom: 2rem;
            color: #FF4081;  /* Savage pink */
            font-size: 3rem;
            letter-spacing: -1px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        
        h2 {
            font-weight: 700;
            margin-bottom: 1rem;
            color: #FF4081;
        }
        
        h3 {
            font-weight: 600;
            margin-bottom: 0.8rem;
            color: #FF4081;
        }
        
        /* Card design with glassmorphism */
        .card {
            background-color: rgba(44, 47, 56, 0.8);
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 32px rgba(255, 64, 129, 0.2);
        }
        
        /* Travel item cards */
        .travel-item {
            background-color: rgba(44, 47, 56, 0.5);
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 16px;
            border-left: 4px solid #FF4081;
            transition: all 0.2s ease;
        }
        
        .travel-item:hover {
            background-color: rgba(44, 47, 56, 0.7);
            transform: translateX(5px);
        }
        
        /* Progress indicators */
        .step-progress {
            display: flex;
            justify-content: space-between;
            margin: 2rem 0;
            position: relative;
        }
        
        .step-progress:before {
            content: '';
            position: absolute;
            background: #444;
            height: 4px;
            width: 100%;
            top: 50%;
            transform: translateY(-50%);
            z-index: 0;
        }
        
        .step {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: #333;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            position: relative;
            z-index: 1;
            border: 2px solid #444;
        }
        
        .step.active {
            background: #FF4081;
            border-color: #FF4081;
        }
        
        .step.completed {
            background: #4CAF50;
            border-color: #4CAF50;
        }
        
        /* Enhanced button styles */
        .primary-btn {
            background: linear-gradient(135deg, #FF4081 0%, #C2185B 100%);
            color: white;
            padding: 10px 20px;
            border-radius: 30px;
            font-weight: bold;
            border: none;
            cursor: pointer;
            box-shadow: 0 4px 10px rgba(255, 64, 129, 0.3);
            transition: all 0.3s ease;
        }
        
        .primary-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(255, 64, 129, 0.4);
        }
        
        .secondary-btn {
            background: rgba(255, 255, 255, 0.1);
            color: white;
            padding: 10px 20px;
            border-radius: 30px;
            font-weight: bold;
            border: 1px solid rgba(255, 255, 255, 0.2);
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .secondary-btn:hover {
            background: rgba(255, 255, 255, 0.2);
        }
        
        /* Destination selection styles */
        .destination-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
            gap: 1rem;
            margin-top: 1.5rem;
        }
        
        .destination-card {
            background-size: cover;
            background-position: center;
            height: 150px;
            border-radius: 12px;
            display: flex;
            align-items: flex-end;
            padding: 1rem;
            position: relative;
            overflow: hidden;
            cursor: pointer;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
        }
        
        .destination-card:before {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 60%;
            background: linear-gradient(to top, rgba(0,0,0,0.7), transparent);
            z-index: 1;
        }
        
        .destination-card:hover {
            transform: scale(1.05);
        }
        
        .destination-name {
            color: white;
            font-weight: bold;
            position: relative;
            z-index: 2;
        }
        
        /* Animation keyframes */
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        .animate-fade {
            animation: fadeIn 0.5s ease-in-out;
        }
        
        /* Loading spinner */
        .loader {
            border: 5px solid #f3f3f3;
            border-top: 5px solid #FF4081;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* Custom selectbox styling */
        div[data-baseweb="select"] {
            background-color: rgba(44, 47, 56, 0.8) !important;
            border-radius: 10px !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: rgba(44, 47, 56, 0.7);
            border-radius: 10px 10px 0 0;
            border: none !important;
            padding: 10px 20px;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: rgba(255, 64, 129, 0.2) !important;
            border-bottom: 3px solid #FF4081 !important;
        }
        
        /* Map container */
        .map-container {
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        }
        
        /* Dark scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #1e1e1e;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #444;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #FF4081;
        }
    </style>
""", unsafe_allow_html=True)

# -------------------- INIT --------------------
if "step" not in st.session_state:
    st.session_state.step = 1
if "form_data" not in st.session_state:
    st.session_state.form_data = {
        "origin": "",
        "destination": "",
        "trip_length": 5,
        "start_date": datetime.date.today(),
        "end_date": datetime.date.today() + datetime.timedelta(days=5),
        "budget": "medium",
        "activities": [],
        "transportation": "public"
    }
if "ai_itinerary" not in st.session_state:
    st.session_state.ai_itinerary = ""
if "travel_data" not in st.session_state:
    st.session_state.travel_data = {"flights": [], "hotels": [], "car_rentals": []}
if "selected_destination" not in st.session_state:
    st.session_state.selected_destination = ""

# -------------------- HEADER --------------------
st.title("✈️ TravelBuddy - Your AI Travel Companion")

# Progress Bar
def show_progress():
    steps = ["Trip Details", "Preferences", "Results"]
    current_step = st.session_state.step
    
    cols = st.columns(len(steps))
    for i, (col, step) in enumerate(zip(cols, steps)):
        with col:
            status = "active" if i+1 == current_step else ("completed" if i+1 < current_step else "")
            st.markdown(f"""
                <div style="display: flex; flex-direction: column; align-items: center;">
                    <div class="step {status}" style="width: 40px; height: 40px; border-radius: 50%; 
                        background: {'#FF4081' if i+1 == current_step else ('#4CAF50' if i+1 < current_step else '#333')}; 
                        display: flex; align-items: center; justify-content: center; color: white; 
                        font-weight: bold; position: relative; z-index: 1;">
                        {i+1}
                    </div>
                    <div style="margin-top: 8px; text-align: center; font-size: 14px; color: {'#FF4081' if i+1 == current_step else 'white'};">
                        {step}
                    </div>
                </div>
            """, unsafe_allow_html=True)
    st.write("")  # Add some space after the progress bar

# -------------------- STEP 1: Destination Selection --------------------
def step_destination_selection():
    st.markdown("### Where are you departing from?")
    origin = st.text_input("Enter your current country/city of departure", value=st.session_state.form_data.get("origin", ""))
    st.session_state.form_data["origin"] = origin

    st.markdown("<div class='animate-fade'>", unsafe_allow_html=True)
    st.subheader("Step 1: Where do you want to go?")
    
    # Destination Cards
    destinations = {
        "Paris": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?q=80&w=2073&auto=format&fit=crop",
        "Tokyo": "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?q=80&w=1971&auto=format&fit=crop",
        "New York": "https://images.unsplash.com/photo-1538970272646-f61fabb3a8a2?q=80&w=1974&auto=format&fit=crop",
        "Dubai": "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?q=80&w=2070&auto=format&fit=crop"
    }
    
    st.markdown("<div class='destination-grid'>", unsafe_allow_html=True)
    
    for dest, img in destinations.items():
        col_html = f"""
        <div class="destination-card" style="background-image: url('{img}');" 
             onclick="document.querySelector('#destination-select').value='{dest}'; 
                     document.querySelector('#destination-select').dispatchEvent(new Event('change'));">
            <div class="destination-name">{dest}</div>
        </div>
        """
        st.markdown(col_html, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Hidden select to capture the click
    dest = st.selectbox("Select destination", list(destinations.keys()), 
                      key="destination-select", label_visibility="collapsed")
    st.session_state.form_data["destination"] = dest
    
    col1, col2 = st.columns(2)
    with col1:
        start = st.date_input("Start Date", value=st.session_state.form_data["start_date"])
    with col2:
        end = st.date_input("End Date", value=st.session_state.form_data["end_date"])

    st.session_state.form_data["start_date"] = start
    st.session_state.form_data["end_date"] = end
    
    # Calculate trip length
    trip_days = (end - start).days
    if trip_days < 1:
        st.error("End date must be after start date")
        trip_days = 1
    
    st.session_state.form_data["trip_length"] = trip_days
    
    # Budget slider with icons
    st.markdown("### Budget Range")
    budget_options = ["budget", "medium", "luxury"]
    budget_icons = ["💰", "💰💰", "💰💰💰"]
    
    cols = st.columns(len(budget_options))
    for i, (col, option, icon) in enumerate(zip(cols, budget_options, budget_icons)):
        with col:
            selected = st.session_state.form_data["budget"] == option
            st.markdown(f"""
                <div style="
                    background-color: {'rgba(255, 64, 129, 0.2)' if selected else 'rgba(44, 47, 56, 0.8)'};
                    border-radius: 12px;
                    padding: 12px;
                    text-align: center;
                    cursor: pointer;
                    border: {f'2px solid #FF4081' if selected else '1px solid rgba(255, 255, 255, 0.1)'};
                    transition: all 0.2s ease;"
                    onclick="document.querySelector('#budget-select').selectedIndex={i};
                            document.querySelector('#budget-select').dispatchEvent(new Event('change'));">
                    <div style="font-size: 24px; margin-bottom: 8px;">{icon}</div>
                    <div style="font-weight: {'bold' if selected else 'normal'}; 
                         color: {'#FF4081' if selected else 'white'};">
                        {option.capitalize()}
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    # Hidden select to capture the click
    budget = st.selectbox("Select budget", budget_options, 
                        index=budget_options.index(st.session_state.form_data["budget"]),
                        key="budget-select", label_visibility="collapsed")
    st.session_state.form_data["budget"] = budget
    
    # Next button
    st.markdown("""
        <div style="display: flex; justify-content: flex-end; margin-top: 2rem;">
            <button class="primary-btn" onclick="
                document.querySelector('#next_step_1').click();">
                Next: Personalize Your Trip
                <span style="margin-left: 8px;">➡️</span>
            </button>
        </div>
    """, unsafe_allow_html=True)
    
    # Hidden button to capture the click
    if st.button("Next", key="next_step_1", help="Proceed to preferences", type="primary", use_container_width=False):
        st.session_state.step = 2
    
    st.markdown("</div>", unsafe_allow_html=True)  # Close animation div

# -------------------- STEP 2: Preferences --------------------
def step_preferences():
    st.markdown("<div class='animate-fade'>", unsafe_allow_html=True)
    st.subheader(f"Step 2: Personalize Your {st.session_state.form_data['destination']} Trip")
    
    # Trip summary
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
            <div class="card">
                <h3>🌍 From</h3>
                <p style="font-size: 18px; font-weight: bold;">{st.session_state.form_data["origin"]}</p>
            </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
            <div class="card">
                <h3>📍 Destination</h3>
                <p style="font-size: 18px; font-weight: bold;">{st.session_state.form_data["destination"]}</p>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="card">
                <h3>📅 Dates</h3>
                <p style="font-size: 16px;">{st.session_state.form_data["start_date"]} to {st.session_state.form_data["end_date"]}</p>
                <p style="font-size: 14px; opacity: 0.8;">{st.session_state.form_data["trip_length"]} days</p>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
            <div class="card">
                <h3>💰 Budget</h3>
                <p style="font-size: 18px; font-weight: bold;">{st.session_state.form_data["budget"].capitalize()}</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### What are you interested in?")
    
    # Interest selection with icons
    activities = {
        "museums": "🏛️ Museums & Culture",
        "beach": "🏖️ Beaches & Relaxation",
        "nature": "🌲 Nature & Outdoors",
        "food": "🍽️ Food & Dining",
        "shopping": "🛍️ Shopping",
        "history": "📜 History & Heritage",
        "nightlife": "🌃 Nightlife",
        "adventure": "🧗‍♂️ Adventure"
    }
    
    # Create a 2x4 grid for activities
    for i in range(0, len(activities), 4):
        cols = st.columns(4)
        for j, col in enumerate(cols):
            if i+j < len(activities):
                key, label = list(activities.items())[i+j]
                with col:
                    selected = key in st.session_state.form_data["activities"]
                    if st.button(
                        label, 
                        key=f"activity_{key}",
                        type="primary" if selected else "secondary",
                        use_container_width=True
                    ):
                        if key in st.session_state.form_data["activities"]:
                            st.session_state.form_data["activities"].remove(key)
                        else:
                            st.session_state.form_data["activities"].append(key)
                        st.rerun()
    
    # Transportation options
    st.markdown("### How do you prefer to get around?")
    transport_options = {
        "public": "🚇 Public Transport",
        "rental car": "🚗 Rental Car",
        "taxi": "🚕 Taxi/Rideshare"
    }
    
    cols = st.columns(len(transport_options))
    for i, (col, (key, label)) in enumerate(zip(cols, transport_options.items())):
        with col:
            selected = st.session_state.form_data["transportation"] == key
            if st.button(
                label,
                key=f"transport_{key}",
                type="primary" if selected else "secondary",
                use_container_width=True
            ):
                st.session_state.form_data["transportation"] = key
                st.rerun()
    
    # Navigation buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Back", help="Go back to Step 1", type="secondary"):
            st.session_state.step = 1
    with col2:
        if st.button("Generate Itinerary ✨", key="generate_itinerary_btn", 
                   help="Generate your AI-powered itinerary", type="primary"):
            with st.spinner("Creating your personalized travel itinerary..."):
                generate_itinerary()
            st.session_state.step = 3
    
    st.markdown("</div>", unsafe_allow_html=True)  # Close animation div

# -------------------- ITINERARY ENGINE --------------------
def generate_itinerary():
    data = st.session_state.form_data
    
    # AI itinerary
    prompt = generate_itinerary_prompt(data)
    st.session_state.ai_itinerary = generate_with_ollama(prompt)

    # Travel data
    st.session_state.travel_data["flights"] = generate_mock_flights(
        data["origin"], data["destination"], data["start_date"], data["end_date"])
    
    st.session_state.travel_data["car_rentals"] = generate_mock_car_rentals(
        data["destination"], data["start_date"], data["end_date"])
    
    # Use safe scraper with fallback
    st.session_state.travel_data["hotels"] = safe_scrape_hotels(
        data["destination"], data["start_date"], data["end_date"])

# -------------------- FINAL DISPLAY --------------------
def show_results():
    st.markdown("<div class='animate-fade'>", unsafe_allow_html=True)
    st.success(f"✨ Your {st.session_state.form_data['destination']} itinerary is ready!")
    
    # Display destination summary card
    origin = st.session_state.form_data["origin"]
    dest = st.session_state.form_data["destination"]
    dest_images = {
        "Paris": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?q=80&w=2073&auto=format&fit=crop",
        "Tokyo": "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?q=80&w=1971&auto=format&fit=crop",
        "New York": "https://images.unsplash.com/photo-1538970272646-f61fabb3a8a2?q=80&w=1974&auto=format&fit=crop",
        "Dubai": "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?q=80&w=2070&auto=format&fit=crop"
    }
    
    dest_image = dest_images.get(dest, "https://images.unsplash.com/photo-1488646953014-85cb44e25828")
    
    st.markdown(f"""
        <div style="
            background-image: linear-gradient(to right, rgba(0,0,0,0.7), rgba(0,0,0,0.4)), url('{dest_image}');
            background-size: cover;
            background-position: center;
            border-radius: 16px;
            padding: 2rem;
            margin-bottom: 2rem;
            color: white;
            height: 200px;
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
        ">
            <h2 style="font-size: 2.5rem; margin-bottom: 0.5rem;">{dest}</h2>
            <p style="font-size: 1.2rem; opacity: 0.9;">
                {st.session_state.form_data["start_date"].strftime('%b %d')} - 
                {st.session_state.form_data["end_date"].strftime('%b %d, %Y')} • 
                {st.session_state.form_data["trip_length"]} days • 
                {st.session_state.form_data["budget"].capitalize()} budget
            </p>
            <div style="margin-top: 1rem;">
                <span style="background: rgba(255,255,255,0.2); padding: 4px 12px; border-radius: 20px; 
                      font-size: 14px; margin-right: 8px;">
                    {st.session_state.form_data["transportation"]}
                </span>
                {' '.join([f'<span style="background: rgba(255,255,255,0.2); padding: 4px 12px; border-radius: 20px; font-size: 14px; margin-right: 8px;">{act}</span>' for act in st.session_state.form_data["activities"][:3]])}
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Create a map for the destination
    try:
        # Get approximate coordinates for each destination
        coordinates = {
            "Paris": [48.8566, 2.3522],
            "Tokyo": [35.6762, 139.6503],
            "New York": [40.7128, -74.0060],
            "Dubai": [25.2048, 55.2708]
        }
        
        lat, lon = coordinates.get(dest, [0, 0])
        
        # Create map
        m = folium.Map(location=[lat, lon], zoom_start=12)
        folium.Marker(
            [lat, lon], 
            popup=dest,
            icon=folium.Icon(color="pink", icon="star")
        ).add_to(m)
        
        # Add some hotel markers
        for i, hotel in enumerate(st.session_state.travel_data["hotels"][:3]):
            # Simulate locations around the center
            hlat = lat + (random.random() - 0.5) * 0.02
            hlon = lon + (random.random() - 0.5) * 0.02
            folium.Marker(
                [hlat, hlon],
                popup=hotel["name"],
                icon=folium.Icon(color="blue", icon="home")
            ).add_to(m)
        
        # Add some attraction locations
        attractions = ["Museum", "Restaurant", "Park", "Shopping"]
        for attr in attractions[:5]:
            alat = lat + (random.random() - 0.5) * 0.03
            alon = lon + (random.random() - 0.5) * 0.03
            folium.Marker(
                [alat, alon],
                popup=f"{attr}",
                icon=folium.Icon(color="green", icon="info-sign")
            ).add_to(m)
            
        # Display map in a custom container
        st.markdown('<div class="map-container">', unsafe_allow_html=True)
        folium_static(m, width=1500, height=300)
        st.markdown('</div>', unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Could not load map: {e}")
    
    # Display tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🗓️ Itinerary", "✈️ Flights", "🏨 Hotels", "🚗 Cars"])

    with tab1:
        st.markdown(st.session_state.ai_itinerary)
        
        # Add download button for itinerary
        st.download_button(
            label="📥 Download Itinerary",
            data=st.session_state.ai_itinerary,
            file_name=f"{dest}_itinerary.md",
            mime="text/markdown",
        )

    with tab2:
    # Enhanced flight display
        for i, f in enumerate(st.session_state.travel_data["flights"]):
            with st.container():
                st.markdown(f"""
                    <div class="travel-item">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <span style="font-size: 18px; font-weight: bold; color: #FF4081;">{f['airline']}</span>
                                <span style="font-size: 14px; opacity: 0.8;"> • Flight {f['flight_number']}</span>
                            </div>
                            <div style="font-size: 18px; font-weight: bold;">
                                ${f['price']}
                            </div>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-top: 12px;">
                            <div>
                                <div style="font-size: 16px; font-weight: bold;">{f['departure_time']}</div>
                                <div style="font-size: 14px; opacity: 0.8;">{f['origin']}</div>
                            </div>
                            <div style="display: flex; flex-direction: column; align-items: center;">
                                <div style="font-size: 12px; opacity: 0.8;">{f['duration']}</div>
                                <div style="width: 100px; height: 2px; background: rgba(255,255,255,0.2); 
                                    position: relative; margin: 8px 0;">
                                    <div style="position: absolute; width: 8px; height: 8px; 
                                        background: #FF4081; border-radius: 50%; 
                                        left: 0; top: -3px;"></div>
                                    <div style="position: absolute; width: 8px; height: 8px; 
                                        background: #FF4081; border-radius: 50%; 
                                        right: 0; top: -3px;"></div>
                                </div>
                                <div style="font-size: 12px; opacity: 0.8;">{f.get('stops', 'Direct')}</div>
                            </div>
                            <div style="text-align: right;">
                                <div style="font-size: 16px; font-weight: bold;">{f['arrival_time']}</div>
                                <div style="font-size: 14px; opacity: 0.8;">{f['destination']}</div>
                            </div>
                        </div>
                        <div style="margin-top: 12px; text-align: right;">
                            <button class="secondary-btn" style="font-size: 14px; padding: 6px 12px;">
                                View Details
                            </button>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

        # Add a note about simulated data
        st.info("Note: Flight information is simulated for demonstration purposes.")

    with tab3:
        # Hotels display
        for hotel in st.session_state.travel_data["hotels"]:
            st.markdown(f"""
                <div class="travel-item">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="font-size: 18px; font-weight: bold; color: #FF4081;">
                            {hotel['name']}
                        </div>
                        <div style="font-size: 16px; font-weight: bold;">
                            ${random.randint(80, 300)}/night
                        </div>
                    </div>
                    <div style="margin-top: 10px; font-size: 14px;">
                        {hotel.get('description', 'No description available')}
                    </div>
                    <div style="margin-top: 12px; display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="background: rgba(255,255,255,0.1); padding: 4px 8px; 
                                border-radius: 4px; font-size: 12px; margin-right: 6px;">
                                Wi-Fi
                            </span>
                            <span style="background: rgba(255,255,255,0.1); padding: 4px 8px; 
                                border-radius: 4px; font-size: 12px; margin-right: 6px;">
                                Breakfast
                            </span>
                            <span style="background: rgba(255,255,255,0.1); padding: 4px 8px; 
                                border-radius: 4px; font-size: 12px;">
                                Pool
                            </span>
                        </div>
                        <button class="secondary-btn" style="font-size: 14px; padding: 6px 12px;">
                            Book Now
                        </button>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        # Add a note about simulated data
        st.info("Note: Hotel information is simulated for demonstration purposes.")

    with tab4:
        # Car rental display
        if st.session_state.form_data["transportation"] == "rental car":
            for car in st.session_state.travel_data["car_rentals"]:
                st.markdown(f"""
                    <div class="travel-item">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="font-size: 18px; font-weight: bold; color: #FF4081;">
                                {car['car_type']}
                            </div>
                            <div style="font-size: 16px; font-weight: bold;">
                                ${car['price_per_day']}/day
                            </div>
                        </div>
                        <div style="margin-top: 10px; font-size: 14px;">
                            {car.get('description', 'Comfortable ride for your trip.')}
                        </div>
                        <div style="margin-top: 12px; display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <span style="background: rgba(255,255,255,0.1); padding: 4px 8px; 
                                    border-radius: 4px; font-size: 12px; margin-right: 6px;">
                                    {car.get('seats', 5)} seats
                                </span>
                                <span style="background: rgba(255,255,255,0.1); padding: 4px 8px; 
                                    border-radius: 4px; font-size: 12px; margin-right: 6px;">
                                    {car.get('transmission', 'Automatic')}
                                </span>
                                <span style="background: rgba(255,255,255,0.1); padding: 4px 8px; 
                                    border-radius: 4px; font-size: 12px;">
                                    {car.get('category', 'Compact')}
                                </span>
                            </div>
                            <button class="secondary-btn" style="font-size: 14px; padding: 6px 12px;">
                                Reserve
                            </button>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info(f"You have selected {st.session_state.form_data['transportation']} as your primary transportation mode. Car rentals are optional.")
            
            if st.button("Browse Available Cars", type="secondary"):
                st.session_state.travel_data["car_rentals"] = generate_mock_car_rentals(
                    st.session_state.form_data["destination"], 
                    st.session_state.form_data["start_date"], 
                    st.session_state.form_data["end_date"])
                st.rerun()
        
        # Add a note about simulated data
        st.info("Note: Car rental information is simulated for demonstration purposes.")

        # Share itinerary buttons
        st.markdown("""
        <div style="margin-top: 2rem; padding: 1rem; background: rgba(44, 47, 56, 0.8); 
            border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.1);">
            <h3 style="margin-bottom: 1rem;">Share your itinerary</h3>
            <div style="display: flex; gap: 12px;">
                <button class="secondary-btn" style="display: flex; align-items: center;">
                    <span style="margin-right: 8px;">📧</span> Email
                </button>
                <button class="secondary-btn" style="display: flex; align-items: center;">
                    <span style="margin-right: 8px;">📱</span> Text
                </button>
                <button class="secondary-btn" style="display: flex; align-items: center;">
                    <span style="margin-right: 8px;">📄</span> PDF
                </button>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Start over button
        if st.button("Create New Trip", type="primary"):
            st.session_state.step = 1
            st.session_state.form_data = {
                "destination": "",
                "trip_length": 5,
                "start_date": datetime.date.today(),
                "end_date": datetime.date.today() + datetime.timedelta(days=5),
                "budget": "medium",
                "activities": [],
                "transportation": "public"
            }
            st.session_state.ai_itinerary = ""
            st.session_state.travel_data = {"flights": [], "hotels": [], "car_rentals": []}
            st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)  # Close animation div

# -------------------- MAIN FLOW --------------------
show_progress()

if st.session_state.step == 1:
    step_destination_selection()
elif st.session_state.step == 2:
    step_preferences()
elif st.session_state.step == 3:
    show_results()

# Footer
st.markdown("""
<div style="margin-top: 4rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1); text-align: center; font-size: 14px; opacity: 0.7;">
    TravelBuddy - Your AI-powered travel companion • © 2025 • Built with Streamlit and AI
</div>
""", unsafe_allow_html=True)