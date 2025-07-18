# ai_itinerary.py

import cohere
import os

COHERE_API_KEY = os.getenv("COHERE_API_KEY")

co = cohere.Client(COHERE_API_KEY)

def generate_itinerary_prompt(data):
    return f'''
You are a professional travel assistant. Create a detailed travel itinerary with the following details:

Origin: {data['origin']}
Destination: {data['destination']}
Trip Duration: {data['trip_length']} days
Dates: {data['start_date']} to {data['end_date']}
Budget: {data['budget']}
Preferred Transportation: {data['transportation']}
Interests: {', '.join(data['activities']) if data['activities'] else 'General'}

Instructions:
1. Give a friendly intro paragraph for the destination.
2. For each day, provide:
   - Day heading (e.g., Day 1: Arrival and Explore Downtown)
   - Morning activity (with timing)
   - Lunch suggestion (restaurant or local food)
   - Afternoon activity
   - Dinner suggestion
   - Transportation tip (if relevant)
   - Bonus: local tip or fun fact

Use Markdown for formatting, like **bold** for highlights, and `code` for special notes.
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

