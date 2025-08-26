# Creator Agent Hub - Frontend

A modern, agentic-style frontend for the Creator Agent Hub that provides a one-stop solution for content creators.

## 🎨 Features

### **Modern Agentic Design**
- **Dark theme** with cyberpunk-inspired gradients
- **Glassmorphism effects** with backdrop blur
- **Smooth animations** and transitions
- **Responsive design** for all devices
- **Real-time agent status** monitoring

### **Workflow-Based Interface**
- **4-Step Workflow**: Ideation → Creation → Publishing → Sponsorship
- **Progress tracking** with visual indicators
- **Agent status panel** showing real-time status
- **Interactive idea selection** and content preview

### **Agent Integration**
- **Ideation Agent**: Generate viral content ideas
- **Creation Agent**: Draft posts and scripts
- **Publishing Agent**: Publish content to platforms
- **Analysis Agent**: Analyze YouTube comments
- **Sponsorship Agent**: Send automated sponsorship emails

## 🚀 Getting Started

### **Prerequisites**
- Python server running on `http://127.0.0.1:8000`
- All required environment variables set in `.env`
- `assets.json` file with email lists for sponsorship

### **Running the Frontend**

1. **Start the Python server:**
   ```bash
   python server.py
   ```

2. **Open the frontend:**
   - Main interface: `http://127.0.0.1:8000/static/index.html`
   - Test page: `http://127.0.0.1:8000/static/test.html`

## 📋 Workflow Guide

### **Step 1: Content Ideation**
1. Enter your niche (e.g., "tech reviews", "fitness", "cooking")
2. Select platform (LinkedIn or YouTube)
3. Click "Generate Ideas"
4. Select an idea from the generated list

### **Step 2: Content Creation**
1. Review the selected idea
2. Click "Draft Content"
3. Preview the generated content
4. Proceed to publishing

### **Step 3: Publishing**
1. Click "Publish Content" to publish
2. Use "Analyze YouTube Comments" for YouTube videos
3. Enter YouTube URL for analysis

### **Step 4: Sponsorship**
1. Select target niche from dropdown
2. Click "Send Sponsorship Emails"
3. Review results and email content

## 🎯 Agent Status Indicators

- **🟢 Idle**: Agent is ready
- **🟡 Working**: Agent is processing
- **🟢 Success**: Task completed successfully
- **🔴 Error**: Task failed

## 📱 Responsive Design

The frontend is fully responsive and works on:
- **Desktop**: Full layout with sidebar
- **Tablet**: Stacked layout
- **Mobile**: Optimized for touch interaction

## 🎨 Design System

### **Color Palette**
- **Primary**: `#00d4ff` (Cyan)
- **Secondary**: `#0099cc` (Dark Cyan)
- **Background**: Dark gradient from `#0f0f23` to `#16213e`
- **Text**: `#ffffff` (White) and `#a0a0a0` (Gray)

### **Typography**
- **Font**: Inter (Google Fonts)
- **Weights**: 300, 400, 500, 600, 700

### **Components**
- **Cards**: Glassmorphism with backdrop blur
- **Buttons**: Gradient backgrounds with hover effects
- **Modals**: Centered with backdrop blur
- **Notifications**: Slide-in from right

## 🔧 Customization

### **Modifying Colors**
Edit `static/styles.css`:
```css
:root {
    --primary-color: #00d4ff;
    --secondary-color: #0099cc;
    --background-start: #0f0f23;
    --background-end: #16213e;
}
```

### **Adding New Agents**
1. Add agent to HTML structure
2. Update JavaScript agent list
3. Add corresponding API endpoint

### **Modifying Workflow Steps**
1. Edit step structure in HTML
2. Update progress calculation in JavaScript
3. Add new step logic as needed

## 🐛 Troubleshooting

### **Common Issues**

1. **API Connection Failed**
   - Ensure server is running on port 8000
   - Check CORS settings in server.py
   - Verify API endpoints are working

2. **Agents Not Responding**
   - Check agent status in sidebar
   - Verify environment variables are set
   - Check server logs for errors

3. **Styling Issues**
   - Clear browser cache
   - Check CSS file is loading
   - Verify Font Awesome is accessible

### **Debug Mode**
Open browser console to see:
- API request/response logs
- Agent status updates
- Error messages

## 📁 File Structure

```
static/
├── index.html          # Main frontend interface
├── test.html           # API test page
├── styles.css          # Main stylesheet
└── script.js           # JavaScript functionality
```

## 🔗 API Endpoints Used

- `GET /api/health` - Health check
- `POST /api/generate-ideas` - Generate content ideas
- `POST /api/draft-post` - Draft content
- `POST /api/publish` - Publish content
- `POST /api/youtube/analyze` - Analyze YouTube comments
- `POST /api/sponsorship/send` - Send sponsorship emails

## 🎉 Features in Action

### **Real-time Updates**
- Agent status changes in real-time
- Progress bar updates automatically
- Notifications appear for all actions

### **Interactive Elements**
- Clickable idea cards
- Modal dialogs for YouTube analysis
- Expandable content sections

### **Error Handling**
- Graceful error messages
- Retry mechanisms
- Fallback content

## 🚀 Future Enhancements

- **Real-time streaming** for long-running tasks
- **Drag-and-drop** idea organization
- **Template library** for common content types
- **Analytics dashboard** for performance metrics
- **Multi-language support**
- **Dark/light theme toggle**

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review server logs
3. Test individual API endpoints
4. Verify environment configuration

---

**Built with ❤️ for content creators**
