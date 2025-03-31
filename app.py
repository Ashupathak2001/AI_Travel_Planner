import streamlit as st
import ollama
import json
from datetime import date, datetime
import requests
import re

# Set page config must be the first Streamlit command
st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling
def local_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("Custom CSS file not found. Using default styling.")

# Initialize session state
if "conversation" not in st.session_state:
    st.session_state.conversation = []
if "itinerary" not in st.session_state:
    st.session_state.itinerary = None
if "user_info" not in st.session_state:
    st.session_state.user_info = {}

# Load custom CSS
local_css("style.css")

def generate_response(prompt, model="tinyllama"):
    """Generate response using Ollama with better error handling"""
    try:
        response = ollama.generate(
            model=model,
            prompt=prompt,
            options={
                'temperature': 0.7,
                'top_p': 0.9
            }
        )
        return response.get('response', '')
    except Exception as e:
        st.error(f"Error generating response: {str(e)}")
        return None

def parse_natural_language(input_text):
    """Parse natural language input into structured data with robust error handling"""
    prompt = f"""
    The user provided this travel description: "{input_text}"
    
    Extract the following information as valid JSON:
    - destination (string)
    - origin (string or null if not mentioned)
    - start_date (string in YYYY-MM-DD format or null if not mentioned)
    - end_date (string in YYYY-MM-DD format or null if not mentioned)
    - budget (one of: "Budget", "Moderate", "Luxury", or null)
    - travel_style (array of strings from: "Adventure", "Relaxation", "Cultural", "Foodie", "Nature", "Shopping", "History")
    - dietary_restrictions (string or null)
    - mobility_concerns (string or null)
    
    Return ONLY the JSON object, with all property names in double quotes.
    Example:
    {{
        "destination": "Paris",
        "origin": "New York",
        "start_date": "2023-11-15",
        "end_date": "2023-11-22",
        "budget": "Moderate",
        "travel_style": ["Cultural", "Foodie"],
        "dietary_restrictions": "Vegetarian",
        "mobility_concerns": null
    }}
    """
    
    response = generate_response(prompt)
    if not response:
        return {}
    
    try:
        # First try to parse directly
        try:
            parsed_data = json.loads(response)
        except json.JSONDecodeError:
            # If direct parsing fails, try to extract JSON from the response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                parsed_data = json.loads(json_match.group())
            else:
                st.error("Couldn't find valid JSON in the response")
                return {}
        
        # Convert string dates back to date objects
        for date_field in ['start_date', 'end_date']:
            if date_field in parsed_data and parsed_data[date_field]:
                try:
                    parsed_data[date_field] = datetime.strptime(parsed_data[date_field], '%Y-%m-%d').date()
                except ValueError:
                    parsed_data[date_field] = None
        
        return parsed_data
    except Exception as e:
        st.error(f"Couldn't parse response: {str(e)}")
        st.error(f"Problematic response was: {response}")
        return {}

def display_preferences(user_info):
    """Display user preferences in a clean, readable format"""
    st.subheader("Your Travel Preferences")
    
    # Convert dates to readable strings if they exist
    start_date = user_info.get('start_date', 'Not specified')
    if isinstance(start_date, date):
        start_date = start_date.strftime('%B %d, %Y')
    
    end_date = user_info.get('end_date', 'Not specified')
    if isinstance(end_date, date):
        end_date = end_date.strftime('%B %d, %Y')
    
    # Create a clean display of preferences
    preferences = f"""
    **Destination:** {user_info.get('destination', 'Not specified')}  
    **Origin:** {user_info.get('origin', 'Not specified')}  
    **Travel Dates:** {start_date} to {end_date}  
    **Budget Level:** {user_info.get('budget', 'Not specified')}  
    **Travel Style:** {', '.join(user_info.get('travel_style', ['Not specified']))}  
    **Dietary Restrictions:** {user_info.get('dietary_restrictions', 'None')}  
    **Mobility Concerns:** {user_info.get('mobility_concerns', 'None')}
    """
    
    if 'refinements' in user_info:
        preferences += f"\n**Additional Preferences:** {user_info['refinements']}"
    
    st.markdown(preferences)
    st.divider()

def get_clarifying_questions(user_info):
    """Generate questions to clarify vague inputs"""
    prompt = f"""
    Based on this partial travel information:
    {safe_json_dumps(user_info, indent=2)}
    
    Generate 2-3 concise, friendly questions to clarify missing or vague information that would significantly impact itinerary quality.
    Focus on the most important gaps.
    Format as bullet points.
    """
    return generate_response(prompt)

def safe_json_dumps(data, indent=None):
    """Safe JSON dumps that handles date objects"""
    return json.dumps(data, indent=indent, cls=DateTimeEncoder)

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)

def get_user_preferences():
    st.subheader("Tell us about your trip")
    
    input_method = st.radio(
        "How would you like to provide your information?",
        ["Fill out a form", "Describe in natural language"],
        key="input_method"
    )
    
    if input_method == "Fill out a form":
        with st.form("user_info_form"):
            st.session_state.user_info["destination"] = st.text_input("Where do you want to go?")
            st.session_state.user_info["origin"] = st.text_input("Where are you traveling from?")
            
            col1, col2 = st.columns(2)
            with col1:
                st.session_state.user_info["start_date"] = st.date_input("Start date")
            with col2:
                st.session_state.user_info["end_date"] = st.date_input("End date")
            
            st.session_state.user_info["budget"] = st.selectbox(
                "Budget level",
                ["Budget", "Moderate", "Luxury"]
            )
            
            st.session_state.user_info["travel_style"] = st.multiselect(
                "What describes your travel style?",
                ["Adventure", "Relaxation", "Cultural", "Foodie", "Nature", "Shopping", "History"]
            )
            
            st.session_state.user_info["dietary_restrictions"] = st.text_input("Any dietary restrictions?")
            st.session_state.user_info["mobility_concerns"] = st.text_input("Any mobility concerns?")
            
            submitted = st.form_submit_button("Submit Preferences")
            
            if submitted:
                st.session_state.stage = "refine"
                st.rerun()
    
    else:  # Natural language input
        with st.form("natural_lang_form"):
            user_input = st.text_area("Describe your trip plans (e.g., 'I want a moderate budget trip to Paris for 5 days in June, interested in food and history')")
            
            submitted = st.form_submit_button("Submit Description")
            
            if submitted and user_input:
                with st.spinner("Processing your description..."):
                    # Parse the natural language input
                    parsed_info = parse_natural_language(user_input)
                    if parsed_info:
                        st.session_state.user_info.update(parsed_info)
                        
                        # Store the original text for reference
                        st.session_state.user_info["original_input"] = user_input
                        
                        # Check if we have enough info or need clarification
                        required_fields = ["destination", "start_date", "end_date"]
                        missing_fields = [field for field in required_fields if not st.session_state.user_info.get(field)]
                        
                        if missing_fields:
                            st.session_state.stage = "clarify"
                        else:
                            st.session_state.stage = "refine"
                        st.rerun()

def clarify_input():
    st.subheader("Let's clarify a few details")
    st.write("You told us:")
    st.write(st.session_state.user_info.get("original_input", ""))
    
    # Display current preferences in clean format
    display_preferences(st.session_state.user_info)
    
    # Generate clarifying questions based on what's missing/vague
    with st.spinner("Preparing questions..."):
        questions = get_clarifying_questions(st.session_state.user_info)
    
    if questions:
        st.write("To create the best itinerary, we need to know:")
        st.write(questions)
    else:
        st.warning("Couldn't generate clarification questions. Moving to refinement.")
        st.session_state.stage = "refine"
        st.rerun()
    
    with st.form("clarification_form"):
        clarifications = st.text_area("Please provide the additional details:")
        submitted = st.form_submit_button("Submit Clarifications")
        
        if submitted and clarifications:
            with st.spinner("Processing your clarifications..."):
                # Parse the clarifications and update user_info
                prompt = f"""
                Original user info: {safe_json_dumps(st.session_state.user_info, indent=2)}
                
                New clarifications: "{clarifications}"
                
                Update the JSON by incorporating the new information.
                Keep existing fields unless the clarification changes them.
                Return only the updated JSON.
                """
                
                updated_info = generate_response(prompt)
                if updated_info:
                    try:
                        # Extract JSON from response
                        json_start = updated_info.find('{')
                        json_end = updated_info.rfind('}') + 1
                        json_str = updated_info[json_start:json_end]
                        updated_data = json.loads(json_str)
                        
                        # Convert string dates back to date objects
                        for key in ['start_date', 'end_date']:
                            if key in updated_data and updated_data[key]:
                                updated_data[key] = datetime.strptime(updated_data[key], '%Y-%m-%d').date()
                        
                        st.session_state.user_info.update(updated_data)
                        st.session_state.stage = "refine"
                        st.rerun()
                    except Exception as e:
                        st.error(f"Couldn't process your clarifications: {str(e)}")

def refine_preferences():
    st.subheader("Let's refine your preferences")
    
    # Display current preferences in clean format
    display_preferences(st.session_state.user_info)
    
    # For debugging (optional)
    with st.expander("Show raw preference data"):
        st.json(st.session_state.user_info)
    
    # Generate thoughtful refinement questions
    with st.spinner("Preparing refinement questions..."):
        prompt = f"""
        Based on these travel details:
        {safe_json_dumps(st.session_state.user_info, indent=2)}
        
        Generate 2-3 thoughtful questions to refine preferences for a better itinerary.
        Focus on aspects like:
        - Specific interests within their general travel styles
        - Preferred pace (relaxed vs. packed schedule)
        - Special requests not yet mentioned
        - Any other details that would personalize the itinerary
        
        Present questions conversationally.
        """
        
        questions = generate_response(prompt)
    
    if questions:
        st.write("To make your itinerary perfect, please consider:")
        st.write(questions)
    else:
        st.warning("Couldn't generate refinement questions. Proceeding to itinerary generation.")
        st.session_state.stage = "generate"
        st.rerun()
    
    with st.form("refinement_form"):
        refinements = st.text_area("Your refinements:")
        submitted = st.form_submit_button("Submit Refinements")
        
        if submitted and refinements:
            st.session_state.user_info["refinements"] = refinements
            st.session_state.stage = "generate"
            st.rerun()

def generate_itinerary():
    st.subheader("Generating Your Personalized Itinerary")
    
    # Show final preferences
    display_preferences(st.session_state.user_info)
    
    # Create detailed prompt for itinerary generation
    prompt = f"""
    Create a detailed, day-by-day travel itinerary based on:
    {safe_json_dumps(st.session_state.user_info, indent=2)}
    
    Requirements:
    1. Structure logically with morning/afternoon/evening activities
    2. Include both famous attractions and hidden gems
    3. Consider travel time between locations
    4. Accommodate all user preferences and constraints
    5. Suggest appropriate dining options
    6. Provide helpful tips and alternatives
    
    Format with clear headings and brief descriptions for each activity.
    Example format:
    
    Day 1: Arrival in [City]
    - Morning: 
      * Activity 1 (time)
      * Description and details
    - Afternoon:
      * Activity 2 (time)
      * Description and details
    - Evening:
      * Dinner recommendation
      * Evening activity (if applicable)
    """
    
    with st.spinner("Creating your perfect itinerary..."):
        itinerary = generate_response(prompt, model="tinyllama")
        if itinerary:
            st.session_state.itinerary = itinerary
            st.session_state.stage = "display"
            st.rerun()
        else:
            st.error("Failed to generate itinerary. Please try again.")

def display_itinerary():
    st.subheader("✨ Your Personalized Travel Itinerary")
    
    # Header with destination and dates
    destination = st.session_state.user_info.get('destination', 'your destination')
    start_date = st.session_state.user_info.get('start_date', '')
    end_date = st.session_state.user_info.get('end_date', '')
    
    if isinstance(start_date, date):
        date_range = f"{start_date.strftime('%b %d, %Y')} - {end_date.strftime('%b %d, %Y')}"
    else:
        date_range = "your travel dates"
    
    st.markdown(f"""
    <div class="itinerary-header">
        <h2>{destination}</h2>
        <p class="date-range">{date_range}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display itinerary with enhanced formatting
    if st.session_state.itinerary:
        # Split into days if possible - using more robust pattern
        days = re.split(r'(?=\nDay \d+:)', st.session_state.itinerary)
        
        tabs = st.tabs([f"Day {i+1}" for i in range(len(days))])
        
        for i, tab in enumerate(tabs):
            with tab:
                day_content = days[i].strip()
                if not day_content:
                    continue
                    
                # Split into sections (Morning/Afternoon/Evening)
                # Fixed regex pattern - properly closed parentheses
                sections = re.split(r'(?=\n- (?:Morning|Afternoon|Evening):)', day_content)
                
                for section in sections:
                    if not section.strip():
                        continue
                        
                    # Check if it's a section header
                    section_match = re.match(r'- (Morning|Afternoon|Evening):', section)
                    if section_match:
                        time_of_day = section_match.group(1)
                        st.markdown(f"""
                        <div class="time-section">
                            <h4>{time_of_day}</h4>
                        </div>
                        """, unsafe_allow_html=True)
                        continue
                        
                    # Process activities
                    activities = [act.strip() for act in section.split('* ')[1:] if act.strip()]
                    
                    for activity in activities:
                        st.markdown(f"""
                        <div class="activity-card">
                            <div class="activity-content">
                                <p>{activity}</p>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
    
    # Add download and share buttons
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="📥 Download Itinerary",
            data=st.session_state.itinerary,
            file_name=f"{destination}_itinerary.txt",
            mime="text/plain"
        )
    with col2:
        if st.button("🔄 Generate Again"):
            st.session_state.stage = "generate"
            st.rerun()
    
    st.divider()
    
    if st.button("🏠 Start Over"):
        st.session_state.conversation = []
        st.session_state.itinerary = None
        st.session_state.user_info = {}
        st.session_state.stage = "preferences"
        st.rerun()

def main():
    st.title("✈️ AI Travel Itinerary Planner")
    st.markdown("Create your perfect travel plan with AI assistance")
    
    # Check if Ollama is running
    try:
        response = requests.get('http://localhost:11434', timeout=5)
        if response.status_code != 200:
            st.error("Ollama server not running. Please start Ollama first.")
            st.stop()
    except requests.exceptions.RequestException:
        st.error("Couldn't connect to Ollama server. Please make sure Ollama is running.")
        st.stop()
    
    # Initialize stage
    if "stage" not in st.session_state:
        st.session_state.stage = "preferences"
    
    # Show appropriate screen
    if st.session_state.stage == "preferences":
        get_user_preferences()
    elif st.session_state.stage == "clarify":
        clarify_input()
    elif st.session_state.stage == "refine":
        refine_preferences()
    elif st.session_state.stage == "generate":
        generate_itinerary()
    elif st.session_state.stage == "display":
        display_itinerary()

if __name__ == "__main__":
    main()