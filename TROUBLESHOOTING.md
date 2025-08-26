# Troubleshooting Guide

## Issue: Frontend shows "Server not running" when using Live Server

### Problem Description
The frontend is running on Live Server (port 5501) but cannot connect to the API server running on port 8000.

### Solutions

#### 1. **Verify Server is Running**
First, make sure your server is actually running:

```bash
# In your terminal where you started the server
python server.py
```

You should see:
```
Starting Content Ideation Agent API Server...
Server will be available at:
  - Local: http://127.0.0.1:8000
  - Network: http://0.0.0.0:8000
  - Frontend: http://127.0.0.1:8000/static/
  - API Docs: http://127.0.0.1:8000/docs
```

#### 2. **Test Server Manually**
Open a new terminal and test the server:

```bash
python test_server.py
```

This will test all API endpoints and show you exactly what's working.

#### 3. **Check Browser Console**
Open your browser's Developer Tools (F12) and check the Console tab for error messages.

#### 4. **Test API Directly in Browser**
Try visiting these URLs directly in your browser:
- `http://127.0.0.1:8000/api/health`
- `http://127.0.0.1:8000/`

#### 5. **Use the Test Connection Button**
The frontend now has a "Test API Connection" button. Click it to test the connection manually.

#### 6. **Common Issues and Fixes**

##### Issue: Port Already in Use
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# Mac/Linux
lsof -i :8000
kill -9 <process_id>
```

##### Issue: Firewall Blocking
Make sure your firewall allows connections on port 8000.

##### Issue: CORS Problems
The server is configured to allow all origins, but if you still have issues, try:
- Restart the server after making changes
- Check that the CORS middleware is properly loaded

#### 7. **Alternative Solutions**

##### Option A: Use the Built-in Frontend
Instead of Live Server, access the frontend directly through the server:
```
http://127.0.0.1:8000/static/
```

##### Option B: Change Frontend Port
If you must use Live Server, you can change the API_BASE in the frontend to match your server:
```javascript
const API_BASE = 'http://127.0.0.1:8000';
```

##### Option C: Use Different Ports
Start your server on a different port:
```python
# In server.py, change the port
uvicorn.run(app_fastapi, host="0.0.0.0", port=8001)
```

Then update the frontend:
```javascript
const API_BASE = 'http://127.0.0.1:8001';
```

#### 8. **Debugging Steps**

1. **Check Server Logs**: Look at the terminal where you started the server
2. **Check Browser Network Tab**: See if requests are being made and what responses you get
3. **Test with curl**: Use the test script or curl commands to test the API
4. **Verify File Structure**: Make sure all files are in the correct locations

#### 9. **Final Verification**

After making changes:
1. Restart the server
2. Clear browser cache
3. Test the connection button
4. Check browser console for errors

### Still Having Issues?

If none of the above solutions work:
1. Check if Python and all dependencies are properly installed
2. Verify your `.env` file is configured correctly
3. Try running the server on a different port
4. Check if antivirus or security software is blocking the connection

### Quick Test Commands

```bash
# Test if server is responding
curl http://127.0.0.1:8000/api/health

# Test if server is accessible
curl -v http://127.0.0.1:8000/

# Test the full workflow
python test_server.py
```
