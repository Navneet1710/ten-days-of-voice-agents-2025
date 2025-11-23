import logging
import json
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
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


class CoffeeShopBarista(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are a friendly and enthusiastic barista at a specialty coffee shop called "Murf's Coffee House".
            The user is interacting with you via voice to place a coffee order.
            
            Your goal is to take a complete coffee order by gathering the following information:
            - Drink type (e.g., latte, cappuccino, espresso, americano, mocha, macchiato, flat white, etc.)
            - Size (small, medium, or large)
            - Milk preference (whole milk, skim milk, oat milk, almond milk, soy milk, coconut milk, or no milk)
            - Any extras (e.g., extra shot, vanilla syrup, caramel syrup, hazelnut syrup, whipped cream, chocolate drizzle, etc.)
            - Customer's name for the order
            
            Ask clarifying questions in a natural, friendly manner to gather any missing information.
            Don't ask all questions at once - have a natural conversation.
            Once you have all the information, use the complete_order tool to save the order.
            
            Your responses are concise, friendly, and conversational.
            Avoid using complex formatting, emojis, asterisks, or other symbols in your responses.
            Make the customer feel welcome and excited about their coffee!""",
        )
        
        # Initialize order state
        self.order_state = {
            "drinkType": None,
            "size": None,
            "milk": None,
            "extras": [],
            "name": None
        }

    @function_tool
    async def complete_order(
        self, 
        context: RunContext, 
        drink_type: str,
        size: str,
        milk: str,
        extras: str,
        name: str
    ):
        """Complete and save the coffee order when all information has been collected.
        
        This tool should be called only when you have gathered all the required order information from the customer.
        
        Args:
            drink_type: The type of drink ordered (e.g., latte, cappuccino, espresso)
            size: The size of the drink (small, medium, or large)
            milk: The type of milk (whole, skim, oat, almond, soy, coconut, or none)
            extras: Comma-separated list of extras (e.g., "extra shot, vanilla syrup") or "none"
            name: The customer's name for the order
        """
        
        # Update order state
        self.order_state["drinkType"] = drink_type
        self.order_state["size"] = size
        self.order_state["milk"] = milk
        
        # Parse extras
        if extras and extras.lower() != "none":
            self.order_state["extras"] = [e.strip() for e in extras.split(",")]
        else:
            self.order_state["extras"] = []
            
        self.order_state["name"] = name
        
        # Create orders directory if it doesn't exist
        orders_dir = Path(__file__).parent.parent / "orders"
        orders_dir.mkdir(exist_ok=True)
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = orders_dir / f"order_{timestamp}.json"
        
        # Add timestamp to order data
        order_data = {
            **self.order_state,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save order to JSON file
        with open(filename, "w") as f:
            json.dump(order_data, f, indent=2)
        
        logger.info(f"Order saved to {filename}: {order_data}")
        
        # Return confirmation message
        extras_text = ""
        if self.order_state["extras"]:
            extras_text = f" with {', '.join(self.order_state['extras'])}"
        
        return f"Perfect! I've saved your order: {size} {drink_type} with {milk} milk{extras_text} for {name}. Your order has been saved and will be ready soon!"


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    # Logging setup
    # Add any other context you want in all log entries here
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

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
        agent=CoffeeShopBarista(),
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
