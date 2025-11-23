# What to Do Next - Day 2 Setup on Your Device

Hi! Since you've forked this repository, here's exactly what you need to do next to complete Day 2 on your device.

## TL;DR - Quick Answer

1. **Get API keys** (Murf, Google Gemini, Deepgram)
2. **Install dependencies** (Python with uv, Node.js with pnpm, LiveKit)
3. **Configure backend** with your API keys
4. **Run the app** (one command: `./start_app.sh`)
5. **Talk to your barista** and place an order
6. **Record & post** to LinkedIn

**Estimated time:** 30-60 minutes

---

## Step-by-Step Guide

### 📋 What You Need First

Before coding, get these three API keys (all have free tiers):

1. **Murf Falcon API Key**
   - Go to: https://murf.ai
   - Sign up for an account
   - Navigate to API section
   - Create and copy your API key

2. **Google Gemini API Key**
   - Go to: https://aistudio.google.com/apikey
   - Sign in with Google account
   - Click "Create API Key"
   - Copy the key

3. **Deepgram API Key**
   - Go to: https://deepgram.com
   - Sign up for account
   - Go to API Keys section
   - Create and copy a new key

### 💻 Install Required Software

You need these tools installed on your device:

**On macOS:**
```bash
# Install uv for Python package management
pip install uv

# Install pnpm for Node.js package management
npm install -g pnpm

# Install LiveKit server
brew install livekit
```

**On Linux:**
```bash
# Install uv
pip install uv

# Install pnpm
npm install -g pnpm

# Install LiveKit
curl -sSL https://get.livekit.io | bash
```

**On Windows:**
```bash
# Install uv
pip install uv

# Install pnpm
npm install -g pnpm

# Install LiveKit
# Download from: https://github.com/livekit/livekit/releases
```

### 🔧 Configure Your Project

**1. Backend Setup:**

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
uv sync

# Create environment file
cp .env.example .env.local

# Edit .env.local and add your API keys
# Use any text editor (nano, vim, VS Code, etc.)
nano .env.local
```

Your `.env.local` should look like this:
```bash
LIVEKIT_URL=ws://127.0.0.1:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
GOOGLE_API_KEY=your_actual_google_key_here
MURF_API_KEY=your_actual_murf_key_here
DEEPGRAM_API_KEY=your_actual_deepgram_key_here
```

**2. Download Required Models:**

```bash
# Still in backend directory
uv run python src/agent.py download-files
```

This will take a few minutes - it's downloading AI models.

**3. Frontend Setup:**

```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies
pnpm install

# Environment is already configured for local dev
# But you can copy if needed: cp .env.example .env.local
```

### 🚀 Run the Application

**From the root directory of your project:**

```bash
# Make the start script executable (first time only)
chmod +x start_app.sh

# Run everything
./start_app.sh
```

This will start:
- LiveKit server
- Backend agent (your coffee barista)
- Frontend web app

**Wait for the message:** "Frontend started on http://localhost:3000"

### ☕ Test Your Coffee Barista

1. **Open your browser** and go to: http://localhost:3000

2. **Click the "Connect" button**

3. **Grant microphone permission** when asked

4. **Start talking!** Try saying:
   - "Hi, I'd like to order a coffee"
   - "Can I get a latte?"
   - "I'll have a medium cappuccino"

5. **Answer the barista's questions:**
   - What drink? → "Latte"
   - What size? → "Medium"
   - What milk? → "Oat milk"
   - Any extras? → "Vanilla syrup" or "No thanks"
   - Your name? → "Your Name"

6. **Check your order was saved:**
   ```bash
   # In a new terminal
   cd backend/orders
   ls -lt
   # You should see a file like: order_20240123_143025.json
   
   # View it
   cat order_*.json
   ```

### 📹 Complete Day 2

To officially finish Day 2:

1. **Record a video** (1-3 minutes) showing:
   - You connecting to the agent
   - Having a conversation to place an order
   - The order JSON file that was created

2. **Post on LinkedIn** with:
   - "Built a Coffee Shop Barista using Murf Falcon - the fastest TTS API!"
   - "Part of the Murf AI Voice Agent Challenge"
   - Tag: @Murf AI
   - Hashtags: #MurfAIVoiceAgentsChallenge #10DaysofAIVoiceAgents

---

## 📚 Detailed Documentation

Need more help? We've created comprehensive guides:

- **[DAY2_CHECKLIST.md](./DAY2_CHECKLIST.md)** - Complete checklist to track progress
- **[QUICKSTART_DAY2.md](./QUICKSTART_DAY2.md)** - Fast setup guide
- **[SETUP_DAY2.md](./SETUP_DAY2.md)** - Detailed setup instructions
- **[TROUBLESHOOTING_DAY2.md](./TROUBLESHOOTING_DAY2.md)** - Fix common issues
- **[DAY2_SUMMARY.md](./DAY2_SUMMARY.md)** - What was implemented

## ❓ Common Questions

**Q: Do I need to pay for the APIs?**
A: All three APIs (Murf, Google Gemini, Deepgram) have free tiers that are sufficient for Day 2.

**Q: Can I use different AI providers?**
A: Yes, but you'll need to modify `backend/src/agent.py`. The current setup uses the recommended providers.

**Q: What if I get errors during setup?**
A: Check [TROUBLESHOOTING_DAY2.md](./TROUBLESHOOTING_DAY2.md) - it covers most common issues.

**Q: How do I stop the application?**
A: Press `Ctrl+C` in the terminal where you ran `./start_app.sh`

**Q: Can I customize the barista?**
A: Absolutely! Edit `backend/src/agent.py` to change the personality, coffee shop name, etc.

**Q: Where are the order files saved?**
A: In `backend/orders/` directory with timestamps like `order_20240123_143025.json`

## 🎯 What's Different from Day 1?

Day 1 was about getting a basic voice agent running. 

Day 2 adds:
- ☕ Coffee shop barista personality
- 📝 Order state tracking
- 💾 Saving orders to JSON files
- 🤖 Function tools for the LLM
- 💬 Natural conversation flow

## 🎉 You're All Set!

That's it! You now have everything you need to:

1. ✅ Run the coffee barista on your device
2. ✅ Place orders through voice
3. ✅ See orders saved as JSON
4. ✅ Complete Day 2 of the challenge

If you get stuck, check the troubleshooting guide or reach out to the community with #MurfAIVoiceAgentsChallenge on LinkedIn.

**Good luck and happy coding! ☕🚀**

---

*P.S. Want to go further? Check out the Advanced Challenge in [challenges/Day 2 Task.md](./challenges/Day%202%20Task.md) for HTML beverage visualization!*
