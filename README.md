# Content Ideation Agent Microservice

A modern microservice for generating content ideas and publishing to LinkedIn or YouTube, built with FastAPI and a beautiful React-like frontend.

## Features

- 🚀 **Content Ideation**: Generate engaging content ideas based on your niche
- 📱 **Multi-Platform Support**: LinkedIn posts and YouTube video scripts
- 🎨 **Modern UI**: Beautiful, responsive web interface
- 🔄 **Step-by-Step Workflow**: Guided content creation process
- 📤 **Publishing Integration**: Ready for platform publishing
- 🎯 **Niche Targeting**: Specialized content for your audience

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI       │    │   Ideation      │
│   (HTML/CSS/JS) │◄──►│   Microservice  │◄──►│   Workflow      │
│                 │    │                 │    │   (LangGraph)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file in the root directory:

```env
GROQ_API_KEY=your_groq_api_key_here
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
```

### 3. Start the Server

```bash
python server.py
```

The server will start on `http://localhost:8000`

### 4. Access the Frontend

Open your browser and navigate to:
- **Frontend**: `http://localhost:8000/static/`
- **API Docs**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/api/health`

## API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API information and available endpoints |
| `GET` | `/api/health` | Health check endpoint |
| `POST` | `/api/generate-ideas` | Generate content ideas |
| `POST` | `/api/draft-post` | Create post/script draft |
| `POST` | `/api/publish` | Publish content |

### Request/Response Models

#### Generate Ideas
```json
POST /api/generate-ideas
{
  "user_niche": "Digital Marketing",
  "platform_choice": "linkedin",
  "media_url": "https://example.com/image.jpg"
}
```

#### Draft Post
```json
POST /api/draft-post
{
  "selected_idea": {
    "title": "LinkedIn Post Idea 1",
    "summary": "Post summary..."
  },
  "platform": "linkedin",
  "niche": "Digital Marketing",
  "media_url": "https://example.com/image.jpg"
}
```

#### Publish Content
```json
POST /api/publish
{
  "post_draft": "Post content...",
  "platform": "linkedin",
  "media_url": "https://example.com/image.jpg"
}
```

## Frontend Features

### Step-by-Step Workflow

1. **Setup**: Enter niche, select platform, add media URL
2. **Ideas**: Choose from generated content ideas
3. **Draft**: Review and edit the generated content
4. **Publish**: Send content to the selected platform

### Responsive Design

- Mobile-first approach
- Modern gradient backgrounds
- Interactive platform selection
- Real-time form validation
- Loading states and error handling

## Development

### Project Structure

```
ideation_agent/
├── server.py                 # FastAPI server with API endpoints
├── ideation_workflow_alpha.py # LangGraph workflow logic
├── static/
│   └── index.html           # Frontend client
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

### Adding New Features

1. **New API Endpoint**: Add to `server.py`
2. **Frontend Changes**: Modify `static/index.html`
3. **Workflow Logic**: Update `ideation_workflow_alpha.py`

### Testing

```bash
# Test the API
curl http://localhost:8000/api/health

# Test idea generation
curl -X POST http://localhost:8000/api/generate-ideas \
  -H "Content-Type: application/json" \
  -d '{"user_niche": "AI", "platform_choice": "linkedin"}'
```

## Deployment

### Production Considerations

1. **Environment Variables**: Secure all API keys
2. **CORS**: Restrict origins to your domain
3. **HTTPS**: Use SSL certificates
4. **Rate Limiting**: Implement API rate limiting
5. **Monitoring**: Add health checks and logging

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "server.py"]
```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GROQ_API_KEY` | Groq API key for LLM | Yes |
| `LINKEDIN_CLIENT_ID` | LinkedIn OAuth client ID | No |
| `LINKEDIN_CLIENT_SECRET` | LinkedIn OAuth secret | No |

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Find process using port 8000
   netstat -ano | findstr :8000
   # Kill the process
   taskkill /PID <process_id> /F
   ```

2. **Module Not Found**
   ```bash
   pip install -r requirements.txt
   ```

3. **Frontend Not Loading**
   - Check if server is running
   - Verify static files are in the correct directory
   - Check browser console for errors

### Logs

The server outputs logs to the console. Check for:
- API request logs
- Error messages
- Workflow execution status

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review API documentation at `/docs`
3. Check server logs for errors
4. Open an issue in the repository

---

**Happy Content Creating! 🚀**
