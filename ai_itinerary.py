# ai_itinerary.py

import cohere
import os

COHERE_API_KEY = os.getenv("COHERE_API_KEY")

co = cohere.Client(COHERE_API_KEY)

def generate_itinerary_prompt(data):
    return f'''
You are an expert travel assistant tasked with creating a personalized and efficient travel itinerary based on the following input details:

**Origin:** {data['origin']}
**Destination:** {data['destination']}
**Trip Duration:** {data['trip_length']} days  
**Dates:** {data['start_date']} to {data['end_date']}  
**Budget Level:** {data['budget']}  
**Preferred Transportation:** {data['transportation']}  
**Traveler Interests:** {', '.join(data['activities']) if data['activities'] else 'General'}

### Output Guidelines:
1. Start with a brief and engaging introductory paragraph about the destination (maximum 60 words).
2. For each day, provide a concise itinerary summary (ideally 100–120 words per day) including:
   - A key attraction or theme for the day
   - One recommended meal (lunch or dinner) with venue or local specialty
   - A cultural insight, local tip, or fun fact
3. Use clean and readable Markdown formatting:
   - Use **bold** for day titles and major highlights
   - Use `code` formatting for tips, notes, or important local insights
4. Focus on clarity and value — do not over-describe. Prioritize quality over excessive detail.
5. For trips longer than 3 days, feel free to summarize or group similar days to stay within scope.

### Important:
- The final output should read naturally and professionally.
- Avoid repeating common tourist clichés.
- Return only the formatted itinerary — do not include explanations or disclaimers.

Proceed to generate the itinerary accordingly.
'''

def generate_with_cohere(prompt, model="command-r-plus"):
    try:
        response = co.chat(
            model=model,
            message=prompt,
            temperature=0.7,
            max_tokens=1000,
        )
        return response.text
    except Exception as e:
        return f"Error generating itinerary with Cohere: {str(e)}"

