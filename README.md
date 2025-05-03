FastAPI backend for generating business strategies using AI.

- 🔐 JWT Authentication
- 🧠 AI Strategy Generation with OpenAI
- 💬 Business Consultant Chatbot
- 🗄️ PostgreSQL Database Integration
- 🔒 Security

Register a new user -->

POST "http://localhost:8000/auth/register" \
'{"email": "user@example.com", "password":"strongpassword","full_name": "John Doe"}'


Login -->

POST "http://localhost:8000/auth/login" \
'{"email": "user@example.com", "password": "strongpassword"}'

# AI Strategy Generation

Generate a business strategy -->

POST "http://localhost:8000/ai/generate-strategy" \
  -H "Content-Type: application/json" \
'{"business_name": "EcoTech Solutions", "industry": "Sustainable Technology", "challenges": "Limited funding, need to scale", "goals": "Increase market share by 20% in 12 months"}'


Ask the business consultant chatbot --> 

POST "http://localhost:8000/ai/chatbot" 
"Authorization: Bearer YOUR_TOKEN" 
  -d '{"message": "How can I improve customer retention?", "conversation_id": "optional-conversation-id"}'
