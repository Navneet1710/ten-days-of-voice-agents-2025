# Day 2 Setup Guide - Coffee Shop Barista Agent

This guide will help you set up and run the Day 2 Coffee Shop Barista Agent on your local device.

## Prerequisites

Before starting Day 2, make sure you have completed Day 1 and have the following installed:

- **Python 3.9+** with [uv](https://docs.astral.sh/uv/) package manager
- **Node.js 18+** with pnpm
- **LiveKit Server** (for local development)
- **Git** (to work with your forked repository)

## Step 1: Ensure Your Fork is Up to Date

If you've already forked the repository, make sure your fork has the latest Day 2 code:

```bash
# Navigate to your repository directory
cd ten-days-of-voice-agents-2025

# Pull the latest changes
git pull origin main
```

## Step 2: Backend Setup

### Install Dependencies

```bash
cd backend

# Install Python dependencies using uv
uv sync
```

### Configure Environment Variables

1. Copy the example environment file:
```bash
cp .env.example .env.local
```

2. Edit `.env.local` and add your API keys:

```bash
# For local development with LiveKit server
LIVEKIT_URL=ws://127.0.0.1:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret

# Required API keys - get these from the respective providers
GOOGLE_API_KEY=your_google_api_key_here
MURF_API_KEY=your_murf_api_key_here
DEEPGRAM_API_KEY=your_deepgram_api_key_here
```

**Getting API Keys:**

- **Murf API Key**: Sign up at [murf.ai](https://murf.ai) and get your API key from the dashboard
- **Google API Key**: Get Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey)
- **Deepgram API Key**: Sign up at [deepgram.com](https://deepgram.com) for speech-to-text services

### Download Required Models

```bash
uv run python src/agent.py download-files
```

This will download the Silero VAD model and LiveKit turn detector models needed for voice processing.

## Step 3: Frontend Setup

```bash
cd ../frontend

# Install dependencies
pnpm install

# Copy environment file
cp .env.example .env.local
```

Edit `frontend/.env.local` with the same LiveKit credentials:

```bash
LIVEKIT_URL=ws://127.0.0.1:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
```

## Step 4: Install LiveKit Server

### On macOS:
```bash
brew install livekit
```

### On Linux:
```bash
curl -sSL https://get.livekit.io | bash
```

### On Windows:
Download from [LiveKit Releases](https://github.com/livekit/livekit/releases)

## Step 5: Run the Application

You have two options to run the application:

### Option A: Using the Convenience Script (Recommended)

From the root directory:

```bash
# Make the script executable (first time only)
chmod +x start_app.sh

# Run all services
./start_app.sh
```

This will start:
- LiveKit Server (on port 7880)
- Backend agent (Coffee Shop Barista)
- Frontend app (at http://localhost:3000)

### Option B: Run Services Individually

Open **three separate terminal windows**:

**Terminal 1 - Start LiveKit Server:**
```bash
livekit-server --dev
```

**Terminal 2 - Start Backend Agent:**
```bash
cd backend
uv run python src/agent.py dev
```

**Terminal 3 - Start Frontend:**
```bash
cd frontend
pnpm dev
```

## Step 6: Test Your Coffee Shop Barista

1. Open your browser and go to http://localhost:3000

2. Click "Connect" to start a conversation with the barista

3. Try placing an order! Say something like:
   - "Hi, I'd like to order a coffee"
   - "Can I get a large latte?"
   - "I'll have a medium cappuccino with oat milk"

4. The barista will ask clarifying questions to complete your order:
   - Drink type (latte, cappuccino, espresso, etc.)
   - Size (small, medium, large)
   - Milk preference (whole, skim, oat, almond, etc.)
   - Extras (whipped cream, extra shot, vanilla syrup, etc.)
   - Your name for the order

5. Once the order is complete, check the `backend/orders/` directory for your order JSON file

## Step 7: Verify Your Order

After placing an order, you should see a JSON file created in `backend/orders/` with a timestamp filename like `order_20240123_143025.json`:

```json
{
  "drinkType": "latte",
  "size": "medium",
  "milk": "oat",
  "extras": ["vanilla syrup"],
  "name": "John",
  "timestamp": "2024-01-23T14:30:25.123456"
}
```

## Step 8: Record and Share (Complete Day 2)

To complete Day 2:

1. **Record a video** of yourself placing a coffee order with the barista agent
2. **Show the JSON file** that was created with your order details
3. **Post on LinkedIn** with:
   - Description of your Day 2 experience
   - Mention: "Building voice agents using the fastest TTS API - Murf Falcon"
   - Mention: "Part of the Murf AI Voice Agent Challenge"
   - Tag: @Murf AI (official handle)
   - Hashtags: `#MurfAIVoiceAgentsChallenge` `#10DaysofAIVoiceAgents`

## Troubleshooting

### "Models not found" error
Run: `uv run python src/agent.py download-files` from the backend directory

### "Connection refused" error
Make sure LiveKit server is running: `livekit-server --dev`

### "API key not found" error
Double-check your `.env.local` files have all required API keys

### Port already in use
- Frontend (3000): Change port in `frontend/package.json`
- LiveKit (7880): Use a different port with `livekit-server --dev --port 7881`

### Order files not being created
Check that the `backend/orders/` directory exists and has write permissions

## What's Next?

After completing Day 2, you can:
- Customize the barista's personality and brand
- Add more drink options and customizations
- Implement the optional HTML beverage visualization (Advanced Challenge)
- Prepare for Day 3 tasks!

## Resources

- [LiveKit Agents Documentation](https://docs.livekit.io/agents)
- [Murf Falcon TTS API](https://murf.ai/api/docs/text-to-speech/streaming)
- [Day 2 Task Details](./challenges/Day%202%20Task.md)
- [LiveKit Tools Documentation](https://docs.livekit.io/agents/build/tools/)

---

Happy coding! ☕️🤖
