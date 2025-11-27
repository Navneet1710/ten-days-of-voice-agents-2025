import logging
import json
import sqlite3
from pathlib import Path
from datetime import datetime

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

# Database path
DB_PATH = Path("shared-data/fraud_cases.db")

# Fraud case management
class FraudCaseManager:
    """Manage fraud case data from SQLite database"""
    
    def __init__(self):
        self.current_case = None
        self.user_verified = False
    
    def load_case_by_username(self, username: str):
        """Load fraud case from database by username"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, userName, securityIdentifier, cardEnding, case_status,
                       transactionName, transactionAmount, transactionTime, 
                       transactionCategory, transactionSource, transactionLocation,
                       securityQuestion, securityAnswer
                FROM fraud_cases 
                WHERE LOWER(userName) = LOWER(?) AND case_status = 'pending_review'
                LIMIT 1
            """, (username,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                self.current_case = {
                    "id": row[0],
                    "userName": row[1],
                    "securityIdentifier": row[2],
                    "cardEnding": row[3],
                    "case_status": row[4],
                    "transactionName": row[5],
                    "transactionAmount": row[6],
                    "transactionTime": row[7],
                    "transactionCategory": row[8],
                    "transactionSource": row[9],
                    "transactionLocation": row[10],
                    "securityQuestion": row[11],
                    "securityAnswer": row[12]
                }
                logger.info(f"Loaded fraud case for {username}: ID {self.current_case['id']}")
                return True
            else:
                logger.warning(f"No pending fraud case found for username: {username}")
                return False
                
        except Exception as e:
            logger.error(f"Error loading fraud case: {e}")
            return False
    
    def update_case_status(self, status: str, outcome_note: str):
        """Update fraud case status in database"""
        if not self.current_case:
            logger.error("No current case to update")
            return False
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE fraud_cases 
                SET case_status = ?, outcome_note = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (status, outcome_note, self.current_case["id"]))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Updated case ID {self.current_case['id']}: {status} - {outcome_note}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating fraud case: {e}")
            return False


class FraudAgent(Agent):
    """Fraud Detection Agent for HDFC Bank - handles suspicious transaction verification"""
    
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are a professional and calm Fraud Detection Representative from HDFC Bank's Security Department.

Your role is to help customers verify suspicious transactions on their account.

CALL FLOW:
1. INTRODUCTION: Greet warmly and introduce yourself as calling from HDFC Bank Fraud Detection Team
2. ASK FOR NAME: Ask "May I know your name please?" to identify the customer
3. LOAD CASE: Use get_fraud_case tool with their name to load their pending fraud case
4. VERIFICATION: Ask the security question from the loaded case using ask_security_question tool
5. VERIFY ANSWER: Use verify_security_answer tool to check if answer is correct
6. IF VERIFIED:
   - Read transaction details using read_transaction_details tool
   - Ask: "Did you make this transaction? Please say yes or no."
   - Use confirm_transaction tool with their yes/no response
7. IF NOT VERIFIED:
   - Politely say you cannot proceed without proper verification
   - Use end_verification_failed tool to close the case
8. CLOSING: Thank them and confirm what action was taken

IMPORTANT GUIDELINES:
- Speak in a calm, professional, and reassuring tone
- NEVER ask for full card numbers, PINs, CVV, or passwords
- Only use the security question from the database for verification
- Keep responses concise and clear
- Use the function tools in the correct sequence
- Be empathetic - customers may be worried about fraud
- Always confirm the action taken before ending

You are here to protect customers, be professional and trustworthy!
""",
            tts=murf.TTS(
                voice="en-IN-priya",
                style="Conversation",
                tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=8)
            )
        )
        self.case_manager = FraudCaseManager()
    
    async def on_enter(self) -> None:
        """Called when fraud call starts"""
        await self.session.generate_reply(
            instructions="Greet the customer warmly. Introduce yourself as calling from HDFC Bank's Fraud Detection Team regarding a suspicious transaction on their account. Ask for their name to proceed."
        )
    
    @function_tool
    async def get_fraud_case(self, context: RunContext, username: str):
        """Load pending fraud case from database for the given username
        
        Args:
            username: Customer's full name to look up their fraud case
        """
        success = self.case_manager.load_case_by_username(username)
        
        if success:
            case = self.case_manager.current_case
            return f"""Found fraud case for {case['userName']}.
            
Case ID: {case['id']}
Card ending: **** {case['cardEnding']}
Status: Pending review

I need to verify your identity before proceeding. I'll ask you a security question."""
        else:
            return f"I'm sorry, I couldn't find any pending fraud cases for {username}. Please make sure you've provided your full name as registered with the bank."
    
    @function_tool
    async def ask_security_question(self, context: RunContext):
        """Get the security question for verification
        
        No arguments needed - uses the currently loaded fraud case
        """
        if not self.case_manager.current_case:
            return "No fraud case is currently loaded. Please provide your name first."
        
        question = self.case_manager.current_case.get("securityQuestion")
        return f"For verification purposes: {question}"
    
    @function_tool
    async def verify_security_answer(self, context: RunContext, user_answer: str):
        """Verify the user's answer to the security question
        
        Args:
            user_answer: The user's response to the security question
        """
        if not self.case_manager.current_case:
            return "No fraud case is currently loaded."
        
        correct_answer = self.case_manager.current_case.get("securityAnswer", "").lower().strip()
        user_answer_cleaned = user_answer.lower().strip()
        
        if correct_answer == user_answer_cleaned:
            self.case_manager.user_verified = True
            return "Thank you, your identity has been verified. Let me now share the details of the suspicious transaction."
        else:
            self.case_manager.user_verified = False
            return "I'm sorry, that answer doesn't match our records. For security reasons, I cannot proceed without proper verification."
    
    @function_tool
    async def read_transaction_details(self, context: RunContext):
        """Read the suspicious transaction details to the customer
        
        No arguments needed - uses the currently loaded fraud case
        """
        if not self.case_manager.user_verified:
            return "Please complete verification first before I can share transaction details."
        
        case = self.case_manager.current_case
        amount_formatted = f"₹{float(case['transactionAmount']):,.2f}"
        
        return f"""Here are the details of the suspicious transaction:

Merchant: {case['transactionName']}
Amount: {amount_formatted}
Card ending: **** {case['cardEnding']}
Time: {case['transactionTime']}
Location: {case['transactionLocation']}
Source: {case['transactionSource']}
Category: {case['transactionCategory']}

Did you make this transaction? Please say yes or no."""
    
    @function_tool
    async def confirm_transaction(self, context: RunContext, user_confirmed: str):
        """Process the user's confirmation whether they made the transaction
        
        Args:
            user_confirmed: User's response - should contain "yes" or "no"
        """
        if not self.case_manager.user_verified:
            return "Please complete verification first."
        
        if not self.case_manager.current_case:
            return "No fraud case is currently loaded."
        
        user_response = user_confirmed.lower().strip()
        case = self.case_manager.current_case
        amount_formatted = f"₹{float(case['transactionAmount']):,.2f}"
        
        if "yes" in user_response:
            # Customer confirms - mark as safe
            outcome = f"Customer confirmed transaction as legitimate on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            self.case_manager.update_case_status("confirmed_safe", outcome)
            
            return f"""Thank you for confirming. I've marked this transaction as safe in our system.

Transaction to {case['transactionName']} for {amount_formatted} is now cleared.

Your card ending in {case['cardEnding']} remains active. 

Is there anything else I can help you with regarding this case?"""
        
        elif "no" in user_response:
            # Customer denies - mark as fraudulent
            outcome = f"Customer denied making this transaction. Reported as fraud on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            self.case_manager.update_case_status("confirmed_fraud", outcome)
            
            return f"""Thank you for informing us. I've immediately taken the following actions:

1. Marked this transaction to {case['transactionName']} for {amount_formatted} as fraudulent
2. Blocked your card ending in {case['cardEnding']} to prevent further unauthorized charges
3. Initiated a dispute with the merchant
4. A replacement card will be sent to your registered address within 5-7 business days

You will NOT be charged for this fraudulent transaction.

Our fraud investigation team will contact you within 24 hours. Is there anything else you need assistance with?"""
        
        else:
            return "I didn't quite catch that. Did you make this transaction? Please say yes or no."
    
    @function_tool
    async def end_verification_failed(self, context: RunContext):
        """End the call when verification fails
        
        No arguments needed
        """
        if self.case_manager.current_case:
            outcome = f"Verification failed on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}. Customer could not answer security question correctly."
            self.case_manager.update_case_status("verification_failed", outcome)
        
        return """For your security, I cannot proceed without proper verification.

Please visit your nearest HDFC Bank branch with a valid government ID to resolve this fraud alert, or call our customer care at 1800-267-3333 for further assistance.

Thank you for your time. Goodbye."""



def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    # Logging setup
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }
    
    # Create main session - each agent will configure its own TTS
    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash-lite"),
        tts=murf.TTS(
            voice="en-US-matthew", 
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=8)
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
    )
    
    # Metrics
    usage_collector = metrics.UsageCollector()
    
    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)
    
    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")
    
    ctx.add_shutdown_callback(log_usage)
    
    # Start with Fraud Agent
    await session.start(
        agent=FraudAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )
    
    await ctx.connect()




if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
    

