# AI Travel Itinerary Planner ✈️

An intelligent travel planning assistant that creates personalized itineraries using natural language processing.

![Travel Planner Screenshot]("./Screenshot 2025-03-31 223941.png")

## Features

- **Two Input Methods**:
  - Fill out a detailed form
  - Describe your trip in natural language
- **Smart Itinerary Generation**:
  - Day-by-day breakdown
  - Morning/Afternoon/Evening activities
  - Personalized recommendations
- **Beautiful UI**:
  - Clean, responsive interface
  - Tabbed day navigation
  - Printable/downloadable format

## Installation

1. Clone the repository:
   git clone https://github.com/yourusername/ai-travel-planner.git
   cd ai-travel-planner

Install dependencies:

pip install -r requirements.txt
Start Ollama server (required for local AI):

ollama serve
Run the application:

streamlit run app.py
Usage
Choose your preferred input method (form or natural language)

Provide your travel details:

Destination and dates

Budget level

Travel preferences

Any special requirements

Review and refine your preferences

Generate your personalized itinerary

Download or regenerate as needed

Configuration
Ensure you have these models pulled in Ollama:

ollama pull tinyllama

Project Structure

ai-travel-planner/
├── app.py               # Main application
├── requirements.txt     # Python dependencies
├── style.css            # Custom styling
└── README.md            # This documentation

Troubleshooting

Common Issues:

Ollama connection errors:

Ensure Ollama server is running: ollama serve

Check if models are downloaded: ollama list

Date parsing errors:

Use clear date formats (e.g., "June 15-20, 2024")

Try the form input for precise date selection

CSS not loading:

Ensure style.css exists in the same directory

Check browser console for loading errors

Contributing
Pull requests are welcome! For major changes, please open an issue first.

License
MIT

### Important Notes:

1. **Ollama Setup**:
   - You'll need to have Ollama installed and running locally
   - The `tinyllama` model should be pulled before first use:
     ```bash
     ollama pull tinyllama
     ```
