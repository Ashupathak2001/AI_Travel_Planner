# ai_itinerary.py

import cohere
import os

COHERE_API_KEY = os.getenv("COHERE_API_KEY")

co = cohere.Client(COHERE_API_KEY)

def generate_itinerary_prompt(data):
    return f'''
You are an expert travel assistant creating a professional, well-structured travel itinerary based on these details:
**Origin:** {data['origin']}
**Destination:** {data['destination']}
**Trip Duration:** {data['trip_length']} days  
**Dates:** {data['start_date']} to {data['end_date']}  
**Budget Level:** {data['budget']}  
**Preferred Transportation:** {data['transportation']}  
**Traveler Interests:** {', '.join(data['activities']) if data['activities'] else 'General'}

### Output Requirements:
1. **Introduction:** Brief, engaging paragraph about the destination (50-60 words max)
2. **Daily Structure:** Each day should follow this consistent format (100-120 words per day):
   - **Day X: [Theme/Area]**
   - Main attraction or activity with brief description
   - One food recommendation (restaurant name or local specialty)
   - Practical tip or cultural insight using `code` formatting naturally
3. **Formatting Standards:**
   - Use **bold** for day headers and key attractions
   - Use `code` for practical tips, booking advice, or local insights
   - Keep structure consistent across all days
4. **Professional Guidelines:**
   - Include realistic travel times between locations
   - Mention advance booking requirements where relevant
   - Suggest budget-appropriate options when possible
   - For longer trips (4+ days), group similar activities or highlight key days
   - Ensure geographical accuracy - only suggest day trips within reasonable distance

### Quality Standards:
- Write naturally and professionally
- Avoid tourist clichés and generic descriptions
- Include actionable, specific recommendations
- Maintain consistent tone throughout
- Focus on practical value for travelers

Generate the complete itinerary following these guidelines exactly.
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

