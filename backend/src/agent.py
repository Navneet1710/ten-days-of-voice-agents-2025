import logging
import json
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Annotated
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    MetricsCollectedEvent,
    RoomInputOptions,
    WorkerOptions,
    cli,
    metrics,
    tokenize,
    function_tool,
    RunContext
)
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("agent")

load_dotenv(".env.local")

WELLNESS_LOG_FILE = "wellness_log.json"


@dataclass
class WellnessLog:
    """Manages wellness check-in history"""
    
    def load_history(self) -> list:
        """Load previous check-ins from JSON file"""
        if Path(WELLNESS_LOG_FILE).exists():
            with open(WELLNESS_LOG_FILE, 'r') as f:
                return json.load(f)
        return []
    
    def get_last_checkin(self) -> dict | None:
        """Get the most recent check-in"""
        history = self.load_history()
        return history[-1] if history else None
    
    def save_checkin(self, entry: dict) -> None:
        """Append a new check-in entry to the log"""
        history = self.load_history()
        history.append(entry)
        with open(WELLNESS_LOG_FILE, 'w') as f:
            json.dump(history, f, indent=2)


class Assistant(Agent):
    def __init__(self, wellness_log: WellnessLog) -> None:
        # Get context from previous check-in if available
        last_checkin = wellness_log.get_last_checkin()
        context_note = ""
        if last_checkin:
            date = last_checkin.get('date', 'last time')
            mood = last_checkin.get('mood', 'N/A')
            context_note = f"\n\nPrevious check-in context: On {date}, the user's mood was '{mood}'."  
        
        super().__init__(
            instructions=f"""You are a supportive Health & Wellness Voice Companion. The user is interacting with you via voice for their daily check-in.

Your role is to:
1. Be warm, empathetic, and non-judgmental
2. Ask about their current mood and energy level
3. Inquire about their intentions/objectives for the day (1-3 things)
4. Offer simple, realistic, and actionable advice (no medical claims or diagnosis)
5. Recap the conversation and confirm understanding

IMPORTANT GUIDELINES:
- Ask ONE question at a time naturally
- Keep responses concise and conversational
- No complex formatting, emojis, or asterisks
- Suggestions should be small, practical, and grounded (e.g., "take a short walk", "break it into smaller steps")
- Always acknowledge previous check-ins when relevant
- Once you have mood, energy level, and objectives, use the save_checkin tool{context_note}""",
        )
        self.wellness_log = wellness_log= wellness_log

    @function_tool
    async def save_checkin(
        self,
        context: RunContext,
        mood: Annotated[str, Field(description="User's current mood or emotional state")],
        energy_level: Annotated[str, Field(description="User's energy level (e.g., high, medium, low)")],
        objectives: Annotated[list[str], Field(description="List of 1-3 intentions or goals for the day")],
        stressors: Annotated[str, Field(description="Any current stressors or concerns")] = "None mentioned",
    ):
        """Save the daily wellness check-in to wellness_log.json.
        
        Args:
            mood: Current mood/emotional state
            energy_level: Energy level
            objectives: Daily intentions/goals (1-3 items)
            stressors: Current stressors (optional)
        """
        entry = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M:%S"),
            "mood": mood,
            "energy_level": energy_level,
            "objectives": objectives,
            "stressors": stressors,
            "timestamp": datetime.now().isoformat()
        }
        
        self.wellness_log.save_checkin(entry)
        
        logger.info(f"Wellness check-in saved: {entry}")
        
        # Create a natural recap
        objectives_text = ", ".join(objectives) if objectives else "no specific objectives"
        return f"Great! I've recorded your check-in. Today you're feeling {mood} with {energy_level} energy, and your main focus is: {objectives_text}. Take care of yourself!"


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    # Logging setup
    # Add any other context you want in all log entries here
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Initialize wellness log
    wellness_log = WellnessLog()

    # Set up a voice AI pipeline using OpenAI, Cartesia, AssemblyAI, and the LiveKit turn detector
    session = AgentSession(
        # Speech-to-text (STT) is your agent's ears, turning the user's speech into text that the LLM can understand
        # See all available models at https://docs.livekit.io/agents/models/stt/
        stt=deepgram.STT(model="nova-3"),
        # A Large Language Model (LLM) is your agent's brain, processing user input and generating a response
        # See all available models at https://docs.livekit.io/agents/models/llm/
        llm=google.LLM(
                model="gemini-2.5-flash",
            ),
        # Text-to-speech (TTS) is your agent's voice, turning the LLM's text into speech that the user can hear
        # See all available models as well as voice selections at https://docs.livekit.io/agents/models/tts/
        tts=murf.TTS(
                voice="en-US-matthew", 
                style="Conversation",
                tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
                text_pacing=True
            ),
        # VAD and turn detection are used to determine when the user is speaking and when the agent should respond
        # See more at https://docs.livekit.io/agents/build/turns
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        # allow the LLM to generate a response while waiting for the end of turn
        # See more at https://docs.livekit.io/agents/build/audio/#preemptive-generation
        preemptive_generation=True,
    )

    # To use a realtime model instead of a voice pipeline, use the following session setup instead.
    # (Note: This is for the OpenAI Realtime API. For other providers, see https://docs.livekit.io/agents/models/realtime/))
    # 1. Install livekit-agents[openai]
    # 2. Set OPENAI_API_KEY in .env.local
    # 3. Add `from livekit.plugins import openai` to the top of this file
    # 4. Use the following session setup instead of the version above
    # session = AgentSession(
    #     llm=openai.realtime.RealtimeModel(voice="marin")
    # )

    # Metrics collection, to measure pipeline performance
    # For more information, see https://docs.livekit.io/agents/build/metrics/
    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")

    ctx.add_shutdown_callback(log_usage)

    # # Add a virtual avatar to the session, if desired
    # # For other providers, see https://docs.livekit.io/agents/models/avatar/
    # avatar = hedra.AvatarSession(
    #   avatar_id="...",  # See https://docs.livekit.io/agents/models/avatar/plugins/hedra
    # )
    # # Start the avatar and wait for it to join
    # await avatar.start(session, room=ctx.room)

    # Start the session, which initializes the voice pipeline and warms up the models
    await session.start(
        agent=Assistant(wellness_log=wellness_log),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            # For telephony applications, use `BVCTelephony` for best results
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Join the room and connect to the user
    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
