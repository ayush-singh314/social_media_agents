# Quick Fix Guide - API Connection Issues

## Current Problems
1. **ASGI Factory Warning**: Server shows "WARNING: ASGI app factory detected"
2. **Failed to Fetch**: Frontend can't connect to API endpoints
3. **Generate Ideas Failing**: API calls are not working

## Immediate Solutions

### Option 1: Use Simple Startup Script (Recommended)
```bash
# Use the new simple startup script
python start_simple.py

# OR use the batch file
start_simple.bat
```

### Option 2: Manual Uvicorn Command
```bash
# Stop current server (Ctrl+C)
# Then run this command:
python -m uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

### Option 3: Test with Simple Test Page
1. Start server using Option 1 or 2
2. Open: `http://127.0.0.1:8000/static/test.html`
3. This simple page will test all API endpoints

## What I Fixed

1. **Removed ASGI Factory Warning**: Changed server startup to use `server:app` instead of direct app reference
2. **Added Debug Logging**: All API endpoints now log requests and responses
3. **Better Error Handling**: Frontend shows detailed error messages
4. **Simple Test Page**: Created `test.html` for basic API testing

## Testing Steps

1. **Start Server**: Use `python start_simple.py`
2. **Test API**: Visit `http://127.0.0.1:8000/static/test.html`
3. **Check Console**: Look for detailed logging in server terminal
4. **Test Frontend**: Try the main frontend at `http://127.0.0.1:8000/static/`

## Expected Results

- ✅ No more ASGI factory warning
- ✅ Health check endpoint working
- ✅ Generate ideas endpoint working
- ✅ Frontend connecting successfully
- ✅ Detailed logging in server console

## If Still Having Issues

1. **Check Server Console**: Look for error messages
2. **Use Test Page**: Test individual endpoints
3. **Check Browser Console**: Look for JavaScript errors
4. **Verify Port**: Make sure nothing else is using port 8000

## Quick Commands

```bash
# Kill any process using port 8000 (Windows)
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# Start server
python start_simple.py

# Test API
curl http://127.0.0.1:8000/api/health
```
