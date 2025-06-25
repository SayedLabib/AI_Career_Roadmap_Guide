# 🧠 AI Personal Guide

**AI Personal Guide** is a sophisticated FastAPI application that leverages AI to detect personality types from survey responses and generate personalized roadmaps for personal growth and career guidance. Using Google's Gemini-2.0 flash model, it provides tailored recommendations to help users achieve their personal and professional goals.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.0-brightgreen)
![Gemini](https://img.shields.io/badge/AI-Gemini--2.0-orange)
![License](https://img.shields.io/badge/license-MIT-yellow)

## 🌟 Features

### 1. 📋 Survey-Based Persona Detection
- Collects answers to 5-10 personality-focused questions
- Uses AI to detect personality type/archetype (analytical, empathetic, aggressive, philosophical, etc.)
- Suggests career alignment (doctor, teacher, artist, athlete, etc.) based on personality profile
- Provides detailed analysis of personality traits and tendencies

### 2. 🗓️ AI-Generated Roadmap
- Generates comprehensive daily task schedules for 3 or 6 months
- Each day is represented as a structured card in JSON format
- Each card contains 4-5 highly specific activities/tasks with scheduled times:
  - Morning activities
  - Afternoon tasks
  - Evening practices
  - Night-time reflection
- Focuses on skills development, personal growth, and continuous learning
- Tasks are tailored to the user's specific personality type

### 3. 🧩 Technical Features
- RESTful API built with FastAPI
- AI-powered content generation using Google's Gemini-2.0 flash model
- Containerized with Docker for easy deployment
- Detailed API documentation with Swagger UI
- Structured data models with Pydantic

## 🛠️ Technology Stack

- **Backend Framework**: FastAPI
- **Data Validation**: Pydantic
- **AI Model**: Google Gemini-2.0 flash
- **Containerization**: Docker
- **Documentation**: Swagger/OpenAPI
- **Language**: Python 3.11
- **Environment Management**: python-dotenv
- **API Server**: Uvicorn

## 🏗️ Project Structure

```
app/
│
├── __init__.py
├── main.py                  # FastAPI application entry point
├── docker-compose.yml       # Docker compose configuration
├── Dockerfile               # Docker configuration
├── requirements.txt         # Project dependencies
│
├── api/                     # API routes
│   ├── __init__.py
│   ├── router.py            # API router configuration
│   └── endpoints/           # API endpoint modules
│       ├── __init__.py
│       ├── roadmap.py       # Roadmap endpoints
│       └── survey.py        # Survey endpoints
│
├── core/                    # Core application components
│   ├── __init__.py
│   └── config.py            # Configuration settings
│
├── models/                  # Data models
│   ├── __init__.py
│   ├── persona.py           # Persona data models
│   ├── roadmap.py           # Roadmap data models
│   └── survey.py            # Survey data models
│
├── services/                # Business logic services
│   ├── __init__.py
│   ├── career_matcher.py    # Career matching service
│   ├── persona_detector.py  # Persona detection service
│   └── roadmap_generator.py # Roadmap generation service
│
└── utils/                   # Utility functions
    ├── __init__.py
    └── gemini_client.py     # Gemini AI client
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+ (Python 3.11 recommended)
- Google AI Studio account with Gemini API access
- Docker and Docker Compose (optional, for containerized deployment)

### Environment Setup

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/ai-personal-guide.git
cd ai-personal-guide
```

2. **Create and activate a virtual environment (optional)**

```bash
# For Windows
python -m venv venv
venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Set up environment variables**

Create a `.env` file in the project root:

```env
# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash

# Optional Database URL
DATABASE_URL=sqlite:///./app.db
```

### Running the Application

#### Option 1: Run with Python

```bash
uvicorn app.main:app --reload
```

#### Option 2: Run with Docker Compose

```bash
docker-compose up -d
```

The API will be accessible at: http://localhost:8000

API documentation will be available at: http://localhost:8000/docs

## 📊 API Endpoints

### Survey Endpoints

#### Get Survey Questions
```
GET /api/survey/questions
```
Returns a predefined set of personality assessment questions.

#### Submit Survey
```
POST /api/survey/submit
```
Submit survey responses and receive personality analysis and career matches.

Request Body:
```json
{
  "user_id": "optional-user-id",
  "responses": [
    {
      "question_id": "q1",
      "answer": "Break it down logically step by step"
    },
    ...
  ]
}
```

Response:
```json
{
  "user_id": "optional-user-id",
  "primary_persona": {
    "type": "analytical",
    "confidence": 0.92,
    "description": "You approach problems methodically..."
  },
  "secondary_persona": {
    "type": "philosophical",
    "confidence": 0.67,
    "description": "You often consider deeper meanings..."
  },
  "career_matches": [
    {
      "career": "Data Scientist",
      "confidence": 0.95,
      "description": "Your analytical nature is perfect for..."
    },
    ...
  ],
  "analysis": "Your responses indicate a strong preference for..."
}
```

### Roadmap Endpoints

#### Generate Roadmap
```
POST /api/roadmap/generate
```
Generate a personalized roadmap based on a persona type.

Query Parameters:
- `persona_type` (string, required): The personality type
- `duration_months` (integer, optional): Duration in months (3 or 6)
- `user_id` (string, optional): User identifier

Response:
```json
{
  "user_id": "optional-user-id",
  "persona_type": "analytical",
  "duration_months": 3,
  "start_date": "2023-06-19",
  "end_date": "2023-09-19",
  "daily_cards": [
    {
      "date": "2023-06-19",
      "focus_area": "Critical Thinking",
      "tasks": [
        {
          "title": "Morning Analysis Exercise",
          "description": "Solve the daily logic puzzle",
          "start_time": "08:00:00",
          "end_time": "08:30:00",
          "time_slot": "morning",
          "estimated_time": "30 minutes",
          "priority": 1,
          "resources": [
            "https://example.com/logic-puzzles"
          ]
        },
        ...
      ],
      "reflection_prompt": "How did today's critical thinking exercises challenge your assumptions?"
    },
    ...
  ],
  "overall_goals": [
    "Develop advanced analytical skills",
    "Improve structured problem-solving approach",
    "Enhance data interpretation abilities"
  ]
}
```

#### Generate Weekly Roadmap
```
POST /api/roadmap/generate-weekly
```
Generate a personalized weekly roadmap for 1 month based on a persona type.

Query Parameters:
- `persona_type` (string, required): The personality type
- `user_id` (string, optional): User identifier

Response:
```json
{
  "user_id": "optional-user-id",
  "persona_type": "analytical",
  "duration_months": 1,
  "start_date": "2023-06-19",
  "end_date": "2023-07-19",
  "weeks": [
    {
      "week_number": 1,
      "tasks": [
        {
          "task_name": "Analytical Problem Solving",
          "resources": [
            "https://example.com/problem-solving",
            "Book: Thinking, Fast and Slow by Daniel Kahneman"
          ],
          "time": "7 hours (day per 1 hour) evening",
          "practice": "Solve one complex logic puzzle each day, analyzing your approach"
        }
      ]
    },
    {
      "week_number": 2,
      "tasks": [
        {
          "task_name": "Data Analysis Fundamentals",
          "resources": [
            "https://example.com/data-analysis",
            "Online Course: Data Analysis with Python"
          ],
          "time": "7 hours (day per 1 hour) morning",
          "practice": "Work with a small dataset each day, drawing different insights"
        }
      ]
    },
    {
      "week_number": 3,
      "tasks": [
        {
          "task_name": "Critical Thinking Development",
          "resources": [
            "https://example.com/critical-thinking",
            "Book: Critical Thinking by Richard Paul"
          ],
          "time": "7 hours (day per 1 hour) evening",
          "practice": "Identify logical fallacies in news articles or social media posts"
        }
      ]
    },
    {
      "week_number": 4,
      "tasks": [
        {
          "task_name": "Systems Thinking Application",
          "resources": [
            "https://example.com/systems-thinking",
            "Video Series: Understanding Complex Systems"
          ],
          "time": "7 hours (day per 1 hour) morning",
          "practice": "Map out a complex system each day and identify leverage points"
        }
      ]
    }
  ],
  "overall_goals": [
    "Develop structured analytical thinking",
    "Enhance problem-solving abilities",
    "Build foundations for data-driven decision making"
  ]
}
```

## 🧪 Testing

Run tests using pytest:

```bash
pytest
```

## 🔄 Development Workflow

1. **Set up development environment**
   - Follow the setup instructions above
   - Ensure you have a valid Gemini API key

2. **Make changes to the codebase**
   - Implement new features or fix bugs
   - Follow the project structure

3. **Test your changes**
   - Run unit tests
   - Test the API endpoints manually

4. **Submit pull requests**
   - Create a new branch for your feature
   - Submit a pull request with your changes

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- [Google Gemini AI](https://ai.google.dev/) for the AI capabilities
- [Pydantic](https://pydantic-docs.helpmanual.io/) for data validation

## ❓ Troubleshooting

### API Key Issues
- Ensure your Gemini API key is correctly set in the `.env` file
- Verify you have sufficient quota/credits in your Google AI Studio account
- Check if the model name is correct (`gemini-1.5-flash`)

### Docker Issues
- Make sure Docker and Docker Compose are properly installed
- If you encounter permission issues, try running Docker commands with `sudo`
- For networking problems, check if port 8000 is available on your machine

### General Issues
- Check the application logs for detailed error messages
- Ensure all dependencies are correctly installed
- Verify your Python version (3.8+ required, 3.11 recommended)

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Contact

For questions, feature requests, or support, please open an issue on GitHub or contact the maintainers.

---

Made with ❤️ by [Your Name/Organization]



## Example User Input:

{
  "user_id": "user123",
  "responses": [
    {
      "question_id": "q1",
      "answer": "Break it down logically step by step"
    },
    {
      "question_id": "q2",
      "answer": "Analyze and provide critical insights"
    },
    {
      "question_id": "q3",
      "answer": "Analyze what went wrong and create a plan"
    },
    {
      "question_id": "q4",
      "answer": "Solving complex problems"
    },
    {
      "question_id": "q5",
      "answer": "Intellectual challenge and expertise"
    },
    {
      "question_id": "q6",
      "answer": "Analyze all data and consider logical consequences"
    },
    {
      "question_id": "q7",
      "answer": "Understand the underlying principles and structure"
    },
    {
      "question_id": "q8",
      "answer": "Quiet, organized, and structured"
    }
  ]
}



## /api/roadmap/generate

persona_type: analytical
  duration_months: 3,
  user_id: user123

## Time  response_time_ms: 7517.58

## response_time_ms: 13812.98 for 3 days