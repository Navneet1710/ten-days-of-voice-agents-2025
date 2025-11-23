# Day 2 Completion Checklist

Use this checklist to track your progress on Day 2 of the Murf AI Voice Agents Challenge.

## Prerequisites Setup

- [ ] Python 3.9+ installed
- [ ] `uv` package manager installed (`pip install uv`)
- [ ] Node.js 18+ installed
- [ ] `pnpm` installed (`npm install -g pnpm`)
- [ ] LiveKit server installed (see SETUP_DAY2.md)
- [ ] Forked repository cloned to your device

## API Keys Obtained

- [ ] Murf API Key (from https://murf.ai)
- [ ] Google/Gemini API Key (from https://aistudio.google.com/apikey)
- [ ] Deepgram API Key (from https://deepgram.com)

## Backend Configuration

- [ ] Navigate to `backend/` directory
- [ ] Run `uv sync` to install dependencies
- [ ] Copy `.env.example` to `.env.local`
- [ ] Add all three API keys to `.env.local`
- [ ] Run `uv run python src/agent.py download-files`
- [ ] Verify no errors in model download

## Frontend Configuration

- [ ] Navigate to `frontend/` directory
- [ ] Run `pnpm install` to install dependencies
- [ ] Copy `.env.example` to `.env.local` (or use defaults)
- [ ] Verify configuration matches backend

## Validate Implementation

- [ ] Run `python3 backend/validate_day2.py`
- [ ] All validation checks pass ✓
- [ ] `backend/orders/` directory exists
- [ ] `backend/orders/example_order.json` exists

## Run the Application

Choose one method:

### Option A: Start Script
- [ ] From root directory, run `chmod +x start_app.sh`
- [ ] Run `./start_app.sh`
- [ ] Wait for all services to start

### Option B: Manual Start
- [ ] Terminal 1: `livekit-server --dev`
- [ ] Terminal 2: `cd backend && uv run python src/agent.py dev`
- [ ] Terminal 3: `cd frontend && pnpm dev`

## Test the Barista

- [ ] Open browser to http://localhost:3000
- [ ] See the frontend interface load
- [ ] Click "Connect" button
- [ ] Grant microphone permissions if asked
- [ ] Hear the agent's greeting

## Place Your First Order

- [ ] Start conversation: "Hi, I'd like to order a coffee"
- [ ] Agent asks about drink type
- [ ] Provide drink type (e.g., "latte")
- [ ] Agent asks about size
- [ ] Provide size (e.g., "medium")
- [ ] Agent asks about milk
- [ ] Provide milk preference (e.g., "oat milk")
- [ ] Agent asks about extras
- [ ] Provide extras or say "no thanks"
- [ ] Agent asks for your name
- [ ] Provide your name
- [ ] Agent confirms order is saved

## Verify Order Saved

- [ ] Navigate to `backend/orders/` directory
- [ ] Find your order JSON file (e.g., `order_20240123_143025.json`)
- [ ] Open the file and verify:
  - [ ] `drinkType` is correct
  - [ ] `size` is correct
  - [ ] `milk` is correct
  - [ ] `extras` array is correct (or empty)
  - [ ] `name` is correct
  - [ ] `timestamp` is present

## Record Demonstration

- [ ] Set up screen recording software
- [ ] Start recording
- [ ] Show yourself opening the browser
- [ ] Connect to the agent
- [ ] Have a natural conversation placing an order
- [ ] Show the agent's responses
- [ ] Show the complete order
- [ ] Navigate to `backend/orders/` directory
- [ ] Open your order JSON file
- [ ] Show the contents clearly
- [ ] Stop recording

## LinkedIn Post

- [ ] Edit/trim your video to 1-3 minutes
- [ ] Prepare post text including:
  - [ ] Brief description of what you built
  - [ ] Mention: "Building with Murf Falcon - the fastest TTS API"
  - [ ] Mention: "Part of the Murf AI Voice Agent Challenge"
  - [ ] Tag: @Murf AI (official handle)
  - [ ] Hashtag: #MurfAIVoiceAgentsChallenge
  - [ ] Hashtag: #10DaysofAIVoiceAgents
- [ ] Upload video to LinkedIn
- [ ] Publish post
- [ ] Share the post link (optional)

## Optional: Advanced Challenge

Only if you want extra credit:

- [ ] Read about HTML beverage visualization in Day 2 Task.md
- [ ] Design HTML/CSS for drink visualization
- [ ] Implement size-based cup rendering
- [ ] Add extras visualization (whipped cream, etc.)
- [ ] Or: Create HTML order receipt instead
- [ ] Test the visualization
- [ ] Include in your LinkedIn post

## Customize (Optional)

- [ ] Change coffee shop name in agent instructions
- [ ] Modify barista personality/tone
- [ ] Add more drink options
- [ ] Add more extras options
- [ ] Customize TTS voice in agent.py
- [ ] Test your customizations

## Clean Up & Prepare for Day 3

- [ ] Stop all running services
- [ ] Commit any custom changes to your fork
- [ ] Back up any important order files
- [ ] Review Day 3 task when available
- [ ] Rest and celebrate! ☕🎉

---

## Troubleshooting

If you get stuck on any step:

1. Check **TROUBLESHOOTING_DAY2.md** for your specific issue
2. Review **SETUP_DAY2.md** for detailed instructions
3. Run `python3 backend/validate_day2.py` to check setup
4. Check terminal outputs for error messages
5. Restart all services and try again

## Success Criteria

You've successfully completed Day 2 when:

✅ The barista agent runs on your device
✅ You can have a natural conversation
✅ Orders are saved as JSON files
✅ Your video is recorded and shows the working agent
✅ Your LinkedIn post is live with proper tags/hashtags

---

**Time estimate:** 30-60 minutes for first-time setup and testing

**Good luck! You've got this! ☕🚀**
