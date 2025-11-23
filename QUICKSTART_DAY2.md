# Quick Start Guide - Day 2 on Your Device

This is a condensed guide to help you quickly get Day 2 running on your local device.

## What You Need

1. **API Keys** - Get these first:
   - Murf API Key: https://murf.ai (sign up for Falcon TTS)
   - Google API Key: https://aistudio.google.com/apikey (for Gemini)
   - Deepgram API Key: https://deepgram.com (for speech-to-text)

2. **Software Installed**:
   - Python 3.9+ with `uv` (install: `pip install uv`)
   - Node.js 18+ with `pnpm` (install: `npm install -g pnpm`)
   - LiveKit server (install: `brew install livekit` on Mac or see https://livekit.io)

## Setup Steps (5 minutes)

### 1. Backend Setup

```bash
cd backend

# Install dependencies
uv sync

# Create environment file
cp .env.example .env.local

# Edit .env.local and add your API keys:
# GOOGLE_API_KEY=your_key_here
# MURF_API_KEY=your_key_here
# DEEPGRAM_API_KEY=your_key_here

# Download required models
uv run python src/agent.py download-files
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
pnpm install

# Environment is already set for local dev
# (or copy: cp .env.example .env.local)
```

## Running the App (Choose One Method)

### Option A: Use the Start Script (Easiest)

```bash
# From root directory
chmod +x start_app.sh
./start_app.sh
```

This starts everything at once!

### Option B: Run Manually (3 Terminals)

**Terminal 1:**
```bash
livekit-server --dev
```

**Terminal 2:**
```bash
cd backend
uv run python src/agent.py dev
```

**Terminal 3:**
```bash
cd frontend
pnpm dev
```

## Test Your Barista

1. Open http://localhost:3000 in your browser
2. Click "Connect"
3. Say: "Hi, I'd like to order a coffee"
4. Follow the barista's questions
5. Check `backend/orders/` for your order JSON file!

## Example Conversation

```
You: Hi, I'd like a coffee
Barista: Welcome to Murf's Coffee House! What kind of drink would you like?
You: I'll have a latte
Barista: Great choice! What size would you like - small, medium, or large?
You: Medium please
Barista: Perfect! What type of milk would you prefer?
You: Oat milk
Barista: Excellent! Would you like any extras like an extra shot, vanilla syrup, or whipped cream?
You: Yes, add vanilla syrup
Barista: Sounds delicious! And what name should I put on the order?
You: Alex
Barista: Perfect! [Order saved]
```

Your order will be saved as `backend/orders/order_YYYYMMDD_HHMMSS.json`

## Complete Day 2

To finish Day 2:

1. ✅ Get the agent running
2. ✅ Place a coffee order
3. ✅ Find your order JSON file
4. 📹 Record a video showing:
   - You talking to the barista
   - The complete order conversation
   - The JSON file with your order
5. 📱 Post on LinkedIn:
   - Describe your Day 2 experience
   - Mention: "Building with Murf Falcon - the fastest TTS API"
   - Tag: @Murf AI
   - Hashtags: #MurfAIVoiceAgentsChallenge #10DaysofAIVoiceAgents

## Troubleshooting

**Can't connect?**
- Make sure LiveKit server is running: `livekit-server --dev`
- Check backend terminal for errors

**No API key error?**
- Double-check `.env.local` has all three API keys
- Make sure keys are valid (test them individually)

**Models not found?**
- Run: `cd backend && uv run python src/agent.py download-files`

**Port already in use?**
- Kill existing processes on ports 3000 or 7880
- Or change ports in config files

## What's Different in Day 2?

The agent is now a **Coffee Shop Barista** that:
- Has a friendly coffee shop persona
- Asks you about your drink preferences
- Maintains state of your order
- Saves complete orders to JSON files
- Uses natural conversation to gather all info

## File Locations

- **Agent Code**: `backend/src/agent.py`
- **Orders**: `backend/orders/order_*.json`
- **Setup Guide**: `SETUP_DAY2.md` (detailed version)
- **Example Order**: `backend/orders/example_order.json`

## Next Steps

After completing Day 2:
- Customize the barista's personality
- Add more drink options
- Try the Advanced Challenge (HTML visualization)
- Get ready for Day 3!

---

Need help? Check the full `SETUP_DAY2.md` guide or the Day 2 task description in `challenges/Day 2 Task.md`

Happy coding! ☕️
