# Aspire - AI Strategy Generator Backend

A FastAPI backend for generating business strategies using AI.

## Features

- JWT Authentication
- AI Strategy Generation with OpenAI
- Business Consultant Chatbot
- PostgreSQL Database Integration
- Swagger Documentation
- Security Best Practices

## Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL
- OpenAI API Key

### Installation

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Create a `.env` file 
5. Initialize the database:
   ```
   python init_db.py
   ```
6. Run the server:
   ```
   uvicorn app.main:app --reload
   ```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Usage Examples

### Authentication

**Register a new user:**
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "strongpassword", "full_name": "John Doe"}'
```

**Login:**
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "strongpassword"}'
```

### AI Strategy Generation

**Generate a business strategy:**
```bash
curl -X POST "http://localhost:8000/ai/generate-strategy" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"business_name": "EcoTech Solutions", "industry": "Sustainable Technology", "challenges": "Limited funding, need to scale", "goals": "Increase market share by 20% in 12 months"}'
```

**Ask the business consultant chatbot:**
```bash
curl -X POST "http://localhost:8000/ai/chatbot" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"message": "How can I improve customer retention?", "conversation_id": "optional-conversation-id"}'
```
