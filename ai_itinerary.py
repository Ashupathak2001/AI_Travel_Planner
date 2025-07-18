# ai_itinerary.py

import cohere
import os

COHERE_API_KEY = os.getenv("COHERE_API_KEY")

co = cohere.Client(COHERE_API_KEY)

def generate_itinerary_prompt(data):
    return f'''
You are a professional travel assistant. Generate a **concise and engaging travel itinerary** using the details below:

**Origin:** {data['origin']}
**Destination:** {data['destination']}
**Trip Duration:** {data['trip_length']} days
**Dates:** {data['start_date']} to {data['end_date']}
**Budget:** {data['budget']}
**Preferred Transportation:** {data['transportation']}
**Interests:** {', '.join(data['activities']) if data['activities'] else 'General'}

### Instructions:
1. Begin with a short, friendly introduction to the destination (max 60 words).
2. For **each day**, return a **brief overview** (max ~120 words/day) including:
   - A main activity or area to explore
   - One food recommendation (either lunch or dinner)
   - A local tip or fun fact
3. Use Markdown formatting:
   - **Bold** day headers and activity names
   - `code` for tips or special notes
4. Keep language engaging and easy to follow.
5. If the trip is more than 3 days, summarize similar days briefly to avoid repetition.

Avoid unnecessary detail — this should fit within a single page output.

Return only the itinerary content — no explanations.
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

