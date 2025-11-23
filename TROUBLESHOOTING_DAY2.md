# Day 2 Troubleshooting Guide

Common issues and solutions when running the Coffee Shop Barista agent.

## Installation Issues

### `uv` command not found

**Solution:**
```bash
pip install uv
# or
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### `pnpm` command not found

**Solution:**
```bash
npm install -g pnpm
```

### `livekit-server` command not found

**Solutions by platform:**

**macOS:**
```bash
brew install livekit
```

**Linux:**
```bash
curl -sSL https://get.livekit.io | bash
```

**Windows:**
Download from https://github.com/livekit/livekit/releases

## API Key Issues

### "GOOGLE_API_KEY not found" or similar

**Check:**
1. Make sure you created `.env.local` (not just using `.env.example`)
2. Check the file is in the correct directory (`backend/.env.local`)
3. Verify no extra spaces around the `=` sign
4. Make sure the API key is valid

**Format:**
```bash
GOOGLE_API_KEY=AIzaSy...your_actual_key_here
MURF_API_KEY=your_murf_key_here
DEEPGRAM_API_KEY=your_deepgram_key_here
```

### Getting API Keys

**Google/Gemini:**
- Visit https://aistudio.google.com/apikey
- Click "Create API Key"
- Copy and paste into `.env.local`

**Murf Falcon:**
- Sign up at https://murf.ai
- Navigate to API section in dashboard
- Generate and copy API key

**Deepgram:**
- Sign up at https://deepgram.com
- Go to API Keys section
- Create a new key and copy it

## Connection Issues

### "Connection refused" error

**Causes and Solutions:**

1. **LiveKit server not running**
   ```bash
   # Start in a separate terminal
   livekit-server --dev
   ```

2. **Port already in use**
   ```bash
   # Check what's using port 7880
   lsof -i :7880  # macOS/Linux
   netstat -ano | findstr :7880  # Windows
   
   # Kill the process or use a different port
   livekit-server --dev --port 7881
   ```

3. **Wrong URL in .env.local**
   - Should be: `LIVEKIT_URL=ws://127.0.0.1:7880`
   - NOT: `http://` or `https://`

### Frontend can't connect to backend

**Check:**
1. Both backend and LiveKit server are running
2. Frontend `.env.local` matches backend credentials
3. No firewall blocking localhost connections

## Model Download Issues

### "Models not found" or "Failed to load VAD"

**Solution:**
```bash
cd backend
uv run python src/agent.py download-files
```

**If download fails:**
- Check internet connection
- Try again (sometimes servers are temporarily down)
- Check disk space (models need ~500MB)

### Download is very slow

**Tips:**
- Be patient, first download can take 5-10 minutes
- Models are cached, subsequent runs are fast
- Download on a good internet connection

## Runtime Issues

### Order file not being created

**Check:**
1. `backend/orders/` directory exists
2. You have write permissions
   ```bash
   ls -la backend/orders/
   # Should show directory is writable
   ```

3. The agent actually completed the order
   - Watch backend terminal for "Order saved" log message
   - Make sure you provided all order information

4. Look in the right place
   ```bash
   cd backend/orders
   ls -lt  # List files by date, newest first
   ```

### Agent doesn't respond or takes too long

**Possible causes:**

1. **API rate limits reached**
   - Wait a few minutes
   - Check API dashboard for quotas

2. **Network latency**
   - Check internet connection
   - APIs may be slow during peak hours

3. **Model warming up**
   - First response is always slower
   - Subsequent responses are faster

### Agent doesn't use the `complete_order` tool

**Reasons:**

1. **Not all information collected yet**
   - Agent needs: drink type, size, milk, extras, name
   - Answer all the barista's questions

2. **LLM decides not to call it**
   - The agent should call it automatically
   - Try being explicit: "That's everything, please complete my order"

3. **Error in the tool**
   - Check backend logs for Python errors

## Audio Issues

### Can't hear the agent

**Check:**
1. Browser permissions granted for microphone
2. Correct audio output device selected
3. Volume not muted
4. Check browser console for errors (F12)

### Agent can't hear you

**Check:**
1. Browser has microphone permission
2. Correct microphone selected in browser settings
3. Test microphone in browser settings
4. Check for browser extensions blocking mic access

### Echo or audio feedback

**Solutions:**
- Use headphones
- Mute your speakers
- Check for multiple browser tabs with audio

## Dependency Issues

### `uv sync` fails

**Try:**
```bash
# Clear cache and retry
uv cache clean
uv sync

# Or use pip as fallback
pip install -r requirements.txt  # if it exists
```

### `pnpm install` fails

**Try:**
```bash
# Clear cache
pnpm store prune

# Retry
pnpm install

# Or use npm
npm install
```

## Port Conflicts

### Port 3000 already in use (Frontend)

**Solutions:**

1. Kill the existing process
   ```bash
   # macOS/Linux
   lsof -ti:3000 | xargs kill -9
   
   # Windows
   netstat -ano | findstr :3000
   taskkill /PID <PID> /F
   ```

2. Use a different port
   ```bash
   # Edit frontend/package.json
   # Change dev script to: "next dev -p 3001"
   ```

### Port 7880 already in use (LiveKit)

**Solution:**
```bash
# Use a different port
livekit-server --dev --port 7881

# Update both .env.local files:
# LIVEKIT_URL=ws://127.0.0.1:7881
```

## Testing Issues

### How to test without a full order

**For development:**

You can test the tool directly by modifying the agent code temporarily:

```python
# Add at the end of entrypoint() before ctx.connect()
# For testing only - remove after
logger.info("Testing order creation...")
test_agent = CoffeeShopBarista()
result = await test_agent.complete_order(
    None, 
    "latte", 
    "medium", 
    "oat", 
    "vanilla syrup", 
    "Test"
)
logger.info(f"Test result: {result}")
```

## Performance Issues

### Very slow responses

**Optimizations:**

1. **Use faster models** (edit `agent.py`):
   - Try `gemini-2.0-flash-lite` instead of `gemini-2.5-flash`

2. **Reduce TTS quality** (if needed):
   - Lower quality settings in Murf TTS config

3. **Check system resources**:
   - Close unnecessary applications
   - Check CPU/memory usage

### High CPU usage

**Normal:**
- First run is CPU-intensive (model loading)
- Should stabilize after warmup

**If persistent:**
- Check for infinite loops in logs
- Restart all services
- Check for memory leaks

## Logs and Debugging

### Enable more detailed logging

**Backend:**
```python
# In agent.py, change logging level
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Frontend:**
- Open browser DevTools (F12)
- Check Console and Network tabs

### Where to find logs

**Backend:**
- Terminal output where you ran `uv run python src/agent.py dev`

**Frontend:**
- Browser console (F12)
- Terminal where you ran `pnpm dev`

**LiveKit:**
- Terminal where you ran `livekit-server --dev`

## Getting Help

If you're still stuck:

1. **Check official docs:**
   - LiveKit: https://docs.livekit.io
   - Murf: https://murf.ai/api/docs

2. **Search GitHub issues:**
   - Check if someone else had the same problem

3. **Community:**
   - LiveKit Slack: https://livekit.io/join-slack
   - Challenge participants on LinkedIn (#MurfAIVoiceAgentsChallenge)

4. **Debug checklist:**
   - [ ] All dependencies installed?
   - [ ] All API keys set correctly?
   - [ ] All three services running? (LiveKit, Backend, Frontend)
   - [ ] Checked all terminal outputs for errors?
   - [ ] Tried restarting everything?

## Quick Reset

If nothing works, try a complete reset:

```bash
# Stop all services (Ctrl+C in all terminals)

# Backend
cd backend
rm -rf .venv
uv sync
uv run python src/agent.py download-files

# Frontend  
cd ../frontend
rm -rf node_modules .next
pnpm install

# Restart all services
```

---

Still having issues? Share your error logs and setup details when asking for help!
