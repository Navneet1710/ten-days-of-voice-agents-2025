import logging
import json
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

# Catalog and orders paths
CATALOG_PATH = Path("shared-data/day7_food_catalog.json")
ORDERS_DIR = Path("shared-data/orders")
ORDERS_DIR.mkdir(exist_ok=True)


# Cart manager class
class CartManager:
    """Manage shopping cart for food ordering"""
    
    def __init__(self):
        self.catalog = self._load_catalog()
        self.cart = []
        
    def _load_catalog(self):
        """Load the food catalog from JSON"""
        try:
            with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        except Exception as e:
            logger.error(f"Error loading catalog: {e}")
            return {"catalog": [], "recipes": {}}
    
    def find_item_by_name(self, item_name: str):
        """Find item in catalog by name (case-insensitive)"""
        for item in self.catalog.get("catalog", []):
            if item["name"].lower() == item_name.lower():
                return item
        return None
    
    def find_item_by_id(self, item_id: str):
        """Find item in catalog by ID"""
        for item in self.catalog.get("catalog", []):
            if item["id"] == item_id:
                return item
        return None
    
    def add_item(self, item_name: str, quantity: int = 1):
        """Add item to cart"""
        item = self.find_item_by_name(item_name)
        if not item:
            return None, f"Sorry, I couldn't find '{item_name}' in our catalog."
        
        if not item.get("in_stock", False):
            return None, f"Sorry, {item['name']} is currently out of stock."
        
        # Check if item already in cart
        for cart_item in self.cart:
            if cart_item["id"] == item["id"]:
                cart_item["quantity"] += quantity
                cart_item["total"] = cart_item["price"] * cart_item["quantity"]
                return cart_item, f"Updated {item['name']} quantity to {cart_item['quantity']}. Total for this item: ₹{cart_item['total']}"
        
        # Add new item to cart
        cart_item = {
            "id": item["id"],
            "name": item["name"],
            "price": item["price"],
            "quantity": quantity,
            "brand": item.get("brand", ""),
            "size": item.get("size", ""),
            "total": item["price"] * quantity
        }
        self.cart.append(cart_item)
        return cart_item, f"Added {quantity} {item['name']} to your cart. Price: ₹{item['price']} each, Total: ₹{cart_item['total']}"
    
    def remove_item(self, item_name: str):
        """Remove item from cart"""
        item = self.find_item_by_name(item_name)
        if not item:
            return False, f"Sorry, I couldn't find '{item_name}' in our catalog."
        
        for i, cart_item in enumerate(self.cart):
            if cart_item["id"] == item["id"]:
                removed = self.cart.pop(i)
                return True, f"Removed {removed['name']} from your cart."
        
        return False, f"{item['name']} is not in your cart."
    
    def update_quantity(self, item_name: str, new_quantity: int):
        """Update quantity of item in cart"""
        if new_quantity <= 0:
            return self.remove_item(item_name)
        
        item = self.find_item_by_name(item_name)
        if not item:
            return None, f"Sorry, I couldn't find '{item_name}' in our catalog."
        
        for cart_item in self.cart:
            if cart_item["id"] == item["id"]:
                cart_item["quantity"] = new_quantity
                cart_item["total"] = cart_item["price"] * new_quantity
                return cart_item, f"Updated {item['name']} quantity to {new_quantity}. Total: ₹{cart_item['total']}"
        
        return None, f"{item['name']} is not in your cart. Would you like to add it?"
    
    def get_cart(self):
        """Get current cart with summary"""
        if not self.cart:
            return [], 0, "Your cart is empty."
        
        total = sum(item["total"] for item in self.cart)
        cart_summary = "Here's what's in your cart:\n"
        for item in self.cart:
            cart_summary += f"- {item['name']} ({item['quantity']} x ₹{item['price']}) = ₹{item['total']}\n"
        cart_summary += f"\nTotal: ₹{total}"
        
        return self.cart, total, cart_summary
    
    def clear_cart(self):
        """Clear all items from cart"""
        self.cart = []
    
    def get_recipe_items(self, recipe_name: str):
        """Get items for a recipe"""
        recipes = self.catalog.get("recipes", {})
        recipe_name_lower = recipe_name.lower()
        
        # Find matching recipe
        item_ids = recipes.get(recipe_name_lower, [])
        if not item_ids:
            # Try to find partial match
            for key in recipes.keys():
                if recipe_name_lower in key or key in recipe_name_lower:
                    item_ids = recipes[key]
                    break
        
        if not item_ids:
            return None
        
        # Get items from catalog
        items = []
        for item_id in item_ids:
            item = self.find_item_by_id(item_id)
            if item:
                items.append(item)
        return items


# Global cart manager instance
cart_manager = CartManager()


# Function tools for the agent
@function_tool()
async def add_to_cart(item_name: str, quantity: int = 1) -> str:
    """
    Add an item to the shopping cart.
    
    Args:
        item_name: The name of the item to add (e.g., "Bread", "Milk", "Oreo Cookies")
        quantity: The quantity to add (default: 1)
    
    Returns:
        Confirmation message with item details and price
    """
    logger.info(f"Adding to cart: {item_name} x {quantity}")
    cart_item, message = cart_manager.add_item(item_name, quantity)
    return message


@function_tool()
async def remove_from_cart(item_name: str) -> str:
    """
    Remove an item from the shopping cart.
    
    Args:
        item_name: The name of the item to remove
    
    Returns:
        Confirmation message
    """
    logger.info(f"Removing from cart: {item_name}")
    success, message = cart_manager.remove_item(item_name)
    return message


@function_tool()
async def update_cart_quantity(item_name: str, new_quantity: int) -> str:
    """
    Update the quantity of an item in the cart.
    
    Args:
        item_name: The name of the item to update
        new_quantity: The new quantity (use 0 to remove item)
    
    Returns:
        Confirmation message with updated total
    """
    logger.info(f"Updating cart quantity: {item_name} to {new_quantity}")
    cart_item, message = cart_manager.update_quantity(item_name, new_quantity)
    return message


@function_tool()
async def view_cart() -> str:
    """
    View all items currently in the shopping cart.
    
    Returns:
        List of cart items with quantities, prices, and total amount
    """
    logger.info("Viewing cart")
    cart, total, summary = cart_manager.get_cart()
    return summary


@function_tool()
async def order_ingredients_for(meal_or_recipe: str) -> str:
    """
    Add all ingredients needed for a specific meal or recipe to the cart.
    This is a smart function that knows what ingredients are needed for common meals.
    
    Args:
        meal_or_recipe: The name of the meal/recipe (e.g., "peanut butter sandwich", "pasta", "omelette")
    
    Returns:
        Confirmation message listing all ingredients added
    """
    logger.info(f"Ordering ingredients for: {meal_or_recipe}")
    
    items = cart_manager.get_recipe_items(meal_or_recipe)
    
    if not items:
        available_recipes = list(cart_manager.catalog.get("recipes", {}).keys())
        return f"Sorry, I don't have a recipe for '{meal_or_recipe}'. I know recipes for: {', '.join(available_recipes)}"
    
    # Add all items to cart
    added_items = []
    for item in items:
        cart_item, message = cart_manager.add_item(item["name"], 1)
        if cart_item:
            added_items.append(item["name"])
    
    if added_items:
        return f"Great! I've added the ingredients for {meal_or_recipe} to your cart: {', '.join(added_items)}"
    else:
        return f"Sorry, I couldn't add the ingredients for {meal_or_recipe}."


@function_tool()
async def place_order(customer_name: str, delivery_address: str) -> str:
    """
    Place the order with all items in the cart.
    This should only be called when the customer confirms they are done shopping.
    
    Args:
        customer_name: The customer's name
        delivery_address: The delivery address
    
    Returns:
        Order confirmation with order ID and total amount
    """
    logger.info(f"Placing order for {customer_name}")
    
    cart, total, summary = cart_manager.get_cart()
    
    if not cart:
        return "Your cart is empty. Please add some items before placing an order."
    
    # Create order object
    order_id = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}"
    order = {
        "order_id": order_id,
        "customer_name": customer_name,
        "delivery_address": delivery_address,
        "items": cart,
        "total": total,
        "timestamp": datetime.now().isoformat(),
        "status": "placed"
    }
    
    # Save order to JSON file
    order_file = ORDERS_DIR / f"{order_id}.json"
    try:
        with open(order_file, 'w', encoding='utf-8') as f:
            json.dump(order, f, indent=2, ensure_ascii=False)
        logger.info(f"Order saved: {order_file}")
    except Exception as e:
        logger.error(f"Error saving order: {e}")
        return f"Sorry, there was an error placing your order. Please try again."
    
    # Clear the cart
    cart_manager.clear_cart()
    
    return f"Perfect! Your order has been placed successfully.\n\nOrder ID: {order_id}\nTotal Amount: ₹{total}\nDelivery Address: {delivery_address}\n\nYour order will be delivered soon. Thank you for shopping with us, {customer_name}!"


# Food Order Agent class
class FoodOrderAgent(Agent):
    """Voice agent for food and grocery ordering"""
    
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are a friendly and helpful food ordering assistant for a grocery and prepared food delivery service.

Your role:
- Help customers find and add items to their cart
- Answer questions about products, prices, and availability
- Handle intelligent requests like "ingredients for pasta" by adding multiple related items
- Manage the shopping cart (add, remove, update quantities, view cart)
- Place orders when customers are ready to checkout

Key behaviors:
1. GREETING: Start by introducing yourself and explaining you can help with groceries, snacks, prepared foods, and beverages
2. SMART ORDERING: When customers ask for "ingredients for X" or "what I need for Y", use the order_ingredients_for function
3. CART MANAGEMENT: Always confirm additions/removals and read back the updated total
4. HELPFUL: Suggest items, ask about quantities, confirm brand/size preferences
5. CHECKOUT: When customer says "that's all" or "checkout", ask for their name and delivery address, then place the order

Available items include:
- Groceries: Bread, Milk, Eggs, Rice, Pasta, Vegetables (Tomatoes, Onions, Potatoes)
- Dairy: Butter, Cheese, Paneer
- Snacks: Chips, Cookies, Biscuits, Maggi
- Prepared Food: Pizza, Sandwiches, Burgers
- Beverages: Soft drinks, Juices

Recipe bundles you know:
- Peanut butter sandwich (bread + peanut butter)
- Pasta (pasta + pasta sauce + cheese)
- Omelette (eggs + butter + tomatoes + onions)
- Salad (tomatoes + onions + potatoes)

Be conversational, friendly, and efficient. Always confirm actions and keep the customer informed about their cart total."""
        )
    
    @function_tool()
    async def add_to_cart(self, item_name: str, quantity: int = 1) -> str:
        """Add an item to the shopping cart"""
        return await add_to_cart(item_name, quantity)
    
    @function_tool()
    async def remove_from_cart(self, item_name: str) -> str:
        """Remove an item from the shopping cart"""
        return await remove_from_cart(item_name)
    
    @function_tool()
    async def update_cart_quantity(self, item_name: str, new_quantity: int) -> str:
        """Update the quantity of an item in the cart"""
        return await update_cart_quantity(item_name, new_quantity)
    
    @function_tool()
    async def view_cart(self) -> str:
        """View all items currently in the shopping cart"""
        return await view_cart()
    
    @function_tool()
    async def order_ingredients_for(self, meal_or_recipe: str) -> str:
        """Add all ingredients needed for a specific meal or recipe to the cart"""
        return await order_ingredients_for(meal_or_recipe)
    
    @function_tool()
    async def place_order(self, customer_name: str, delivery_address: str) -> str:
        """Place the order with all items in the cart"""
        return await place_order(customer_name, delivery_address)


def prewarm(proc: JobProcess):
    """Prewarm process with VAD model"""
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    """Main agent entrypoint"""
    
    # Create agent session
    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash-lite"),
        tts=murf.TTS(
            voice="en-IN-priya", 
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
    
    # Start with Food Order Agent
    await session.start(
        agent=FoodOrderAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )
    
    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
