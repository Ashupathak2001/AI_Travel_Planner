# ai_itinerary.py

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


def generate_with_ollama(prompt, system_prompt="", model="tinyllama", host="http://localhost:11434"):
    import requests

    url = f"{host}/api/chat"
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    data = {
        "model": model,
        "messages": messages,
        "stream": False
    }

    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        result = response.json()

        if "message" in result and "content" in result["message"]:
            return result["message"]["content"]
        else:
            return "Error: Unexpected response format from Ollama."

    except requests.exceptions.RequestException as e:
        return f"Error connecting to Ollama: {str(e)}\n\nMake sure Ollama is running and TinyLlama is available."
