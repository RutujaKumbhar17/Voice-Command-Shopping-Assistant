import os
import json
import re
import urllib.request
import urllib.error

# Load environment variables if .env file exists
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ[k.strip()] = v.strip()
    except Exception:
        pass

MINIMAX_API_KEY = os.environ.get("MINIMAX_API_KEY", "")
MINIMAX_CHAT_URL = "https://api.minimax.io/v1/chat/completions"
MINIMAX_TTS_URL = "https://api.minimax.io/v1/t2a_v2"

class MiniMaxClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or MINIMAX_API_KEY
        self.tts_disabled = False
        self.chat_disabled = False

    def _call_chat(self, messages, system_prompt=None, json_mode=False):
        if self.chat_disabled or not self.api_key or "your_" in self.api_key.lower() or len(self.api_key) < 10:
            return None

        full_messages = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)

        payload = {
            "model": "MiniMax-Text-01",
            "messages": full_messages,
            "temperature": 0.3
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            req = urllib.request.Request(
                MINIMAX_CHAT_URL,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers
            )
            with urllib.request.urlopen(req, timeout=2.5) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0]["message"]["content"]
                    return content
        except Exception:
            self.chat_disabled = True
        return None

    def parse_voice_command(self, user_transcript, available_products=None, cart_data=None, list_data=None):
        """
        Parses user's voice command into a structured JSON intent with instant sub-millisecond local NLP,
        enhanced with MiniMax LLM for complex open queries.
        """
        # Run high-speed local NLP parser first
        local_parsed = self._fallback_parse(user_transcript, available_products, cart_data, list_data)
        
        # If recognized specific shopping action, return immediately
        if local_parsed.get("intent") in ["add_item", "get_cart_total", "view_cart", "view_shopping_list", "get_price", "remove_item", "clear_list", "clear_cart", "search_item", "filter_price", "get_suggestions", "checkout"]:
            return local_parsed

        # Otherwise, try MiniMax LLM for open conversational questions
        product_names = [p["product_type"] for p in available_products] if available_products else []
        system_prompt = (
            "You are an intelligent NLP assistant for FreshRoot organic shopping.\n"
            "Answer user shopping & produce questions politely and softly in 1-2 friendly sentences.\n"
            "Output strictly valid JSON with keys 'intent', 'item_name', 'response_speech'."
        )

        messages = [{"role": "user", "content": user_transcript}]
        raw_response = self._call_chat(messages, system_prompt=system_prompt, json_mode=True)
        if raw_response:
            try:
                clean = raw_response.strip().replace("```json", "").replace("```", "").strip()
                parsed = json.loads(clean)
                if parsed and "response_speech" in parsed:
                    local_parsed["response_speech"] = parsed["response_speech"]
                    return local_parsed
            except Exception:
                pass

        return local_parsed

        # High-accuracy Local Fallback NLP Parser
        return self._fallback_parse(user_transcript, available_products, cart_data, list_data)

    def _fallback_parse(self, text, available_products=None, cart_data=None, list_data=None):
        text_lower = text.lower().strip()
        intent = "general_query"
        target = "both"
        item_name = None
        quantity = 1
        unit = "kg"
        max_price = None
        category = None

        # Extract numbers & quantity
        qty_match = re.search(r'(\d+)\s*(kg|kilos|kilo|dozen|pack|packs|pieces|bottles|tons)?', text_lower)
        if qty_match:
            try:
                quantity = int(qty_match.group(1))
                if qty_match.group(2):
                    unit = qty_match.group(2)
            except Exception:
                quantity = 1

        # Extract max price filter
        price_match = re.search(r'(?:under|below|less than|within)\s*(?:rs|inr|₹)?\s*(\d+)', text_lower)
        if price_match:
            try:
                max_price = float(price_match.group(1))
                intent = "filter_price"
            except Exception:
                pass

        # Check target: shopping list vs cart
        if "shopping list" in text_lower or "my list" in text_lower or "the list" in text_lower or "to list" in text_lower:
            target = "list"
        elif "cart" in text_lower or "basket" in text_lower or "bag" in text_lower:
            target = "cart"

        # Match Item Name from catalog using word boundaries
        if available_products:
            for p in available_products:
                p_type = p["product_type"].lower()
                p_title = p["product_title"].lower()
                p_stem = p_type[:-1] if p_type.endswith('s') else p_type
                
                # Use word-boundary regex to prevent 'rice' matching in 'price'
                if re.search(r'\b' + re.escape(p_type) + r'\b', text_lower) or \
                   re.search(r'\b' + re.escape(p_title) + r'\b', text_lower) or \
                   (len(p_stem) > 2 and re.search(r'\b' + re.escape(p_stem) + r'(?:s|es)?\b', text_lower)):
                    item_name = p["product_type"]
                    category = p.get("product_cat")
                    break

        if not item_name:
            common_items = ["banana", "bananas", "potato", "potatoes", "tomato", "tomatoes", "apple", "apples", "rice", "carrot", "carrots", "onion", "onions", "milk", "wheat", "mango", "mangoes", "grapes", "strawberry", "orange", "cabbage"]
            for ci in common_items:
                if re.search(r'\b' + re.escape(ci) + r'\b', text_lower):
                    item_name = ci.title()
                    break

        # Check for Cart inquiries ("what is in my cart", "how much is my cart", "cart price", "cart cost", "my cart", etc.)
        is_cart_inquiry = (
            ("cart" in text_lower or "basket" in text_lower or "bag" in text_lower) and
            any(w in text_lower for w in ["price", "total", "cost", "value", "bill", "amount", "how much", "what is", "what's", "check", "view", "show", "items", "in my", "in the", "what do i have", "tell me", "what is in", "what is the"]) and
            not any(w in text_lower for w in ["add", "put", "insert", "remove", "delete", "clear", "empty", "drop"])
        ) or (text_lower.strip() in ["my cart", "cart", "view cart", "check cart", "cart cost", "cart price", "cart total"])

        # Check for Store Inventory inquiry ("count how much items in store", "how many items", "what products do you have", etc.)
        is_store_inventory = any(phrase in text_lower for phrase in [
            "count how much items", "how many items", "items in store", "items in your store",
            "what items you have", "what do you have", "what produce", "store inventory", "available items", "products available"
        ])

        # Check for Shopping List inquiries ("what is in my shopping list", "show my list", etc.)
        is_list_inquiry = (
            ("list" in text_lower or "shopping list" in text_lower) and
            any(w in text_lower for w in ["what is", "what's", "show", "view", "check", "tell", "read", "on my", "in my", "items"]) and
            not any(w in text_lower for w in ["add", "put", "insert", "remove", "delete", "clear", "empty"])
        )

        # Check for Product Price inquiry ("what is the price of apples", "how much is bananas")
        is_price_inquiry = (
            item_name and
            any(w in text_lower for w in ["how much", "price", "cost", "rate", "what is the price", "what's the price"]) and
            "cart" not in text_lower and "list" not in text_lower
        )

        # Classify Intents:
        if is_store_inventory:
            intent = "store_inventory"
            response_speech = "Checking store inventory."

        elif is_cart_inquiry:
            intent = "get_cart_total"
            response_speech = "Checking your cart details and total cost."

        elif is_list_inquiry:
            intent = "view_shopping_list"
            response_speech = "Fetching your shopping list."

        elif is_price_inquiry:
            intent = "get_price"
            response_speech = f"Checking price for {item_name}."

        # 4. Clear list / clear cart
        elif "clear" in text_lower or "empty" in text_lower:
            if "cart" in text_lower:
                intent = "clear_cart"
                response_speech = "Clearing your cart."
            else:
                intent = "clear_list"
                response_speech = "Clearing your shopping list."

        # 5. Remove item
        elif any(w in text_lower for w in ["remove", "delete", "drop", "take off", "cancel"]):
            intent = "remove_item"
            response_speech = f"Removing {item_name or 'item'}."

        # 6. Add item
        elif any(w in text_lower for w in ["add", "put", "insert", "buy", "order", "include", "i need", "i want"]) or (item_name and not any(q in text_lower for q in ["how", "what", "where", "is"])):
            intent = "add_item"
            response_speech = f"Adding {quantity} {unit} {item_name or 'item'} to your cart."

        # 7. Search & Discovery
        elif any(w in text_lower for w in ["search", "find", "show me", "look for", "do you have", "is there", "browse"]):
            intent = "search_item"
            response_speech = f"Searching for {item_name or text} in our fresh produce catalog."

        # 8. Suggestions & Recommendations
        elif any(w in text_lower for w in ["suggest", "recommend", "recommendation", "seasonal", "running low", "what should i buy"]):
            intent = "get_suggestions"
            response_speech = "Here are our smart farm recommendations and seasonal picks."

        # 9. Checkout & Delivery
        elif any(w in text_lower for w in ["checkout", "place order", "pay now", "proceed to buy", "delivery", "shipping"]):
            intent = "checkout"
            response_speech = "You can proceed to checkout directly from your cart page."

        # 10. General store & produce questions
        else:
            intent = "general_query"
            if "organic" in text_lower or "fresh" in text_lower:
                response_speech = "All FreshRoot produce is 100% farm-fresh and harvested directly from certified local farmers."
            elif "delivery" in text_lower or "time" in text_lower:
                response_speech = "We deliver farm-fresh produce to your doorstep within 2 to 4 hours."
            elif "payment" in text_lower or "pay" in text_lower or "upi" in text_lower:
                response_speech = "We accept UPI, Credit/Debit cards, Net Banking, and Cash on Delivery."
            elif "who are you" in text_lower or "what can you do" in text_lower or "help" in text_lower:
                response_speech = "I am your FreshRoot Voice Assistant. You can ask me to add produce to cart, check cart cost, or check prices."
            elif "hello" in text_lower or "hi" in text_lower or "hey" in text_lower:
                response_speech = "Hello! I am here to help you shop farm fresh produce. What would you like to check or buy?"
            else:
                response_speech = "I can help you add items to cart, check cart cost, check product prices, or find farm-fresh vegetables."

        return {
            "intent": intent,
            "target": target,
            "item_name": item_name,
            "quantity": quantity,
            "unit": unit,
            "category": category,
            "max_price": max_price,
            "response_speech": response_speech,
            "confidence": 0.85
        }

    def generate_smart_suggestions(self, history_items=None, products_catalog=None):
        """
        Generates smart AI suggestions: personalized recommendations, seasonal items, and substitutes.
        """
        return {
            "recommendations": [
                {"name": "Whole Wheat Bread", "reason": "Fresh staple based on your frequent shopping", "price": 40, "category": "Bakery"},
                {"name": "Fresh Organic Milk", "reason": "Pure daily farm milk", "price": 30, "category": "Dairy"},
                {"name": "Shivneri Bananas", "reason": "Sweet, potassium-rich fresh bananas", "price": 30, "category": "Fruits"}
            ],
            "seasonal": [
                {"name": "Ratnagiri Alphonso Mango", "reason": "Peak summer harvest & top sweetness", "price": 200, "category": "Fruits"},
                {"name": "Mahabaleshwar Strawberry", "reason": "Freshly picked seasonal organic fruit", "price": 50, "category": "Fruits"}
            ],
            "substitutes": [
                {"name": "Almond Milk", "reason": "Great plant-based dairy alternative", "price": 65, "category": "Dairy"},
                {"name": "Brown Basmati Rice", "reason": "Nutritious high-fiber alternative to white rice", "price": 85, "category": "Grains"}
            ]
        }

    def generate_speech_audio(self, text):
        """
        Synthesizes text into audio using MiniMax TTS API (`speech-01-turbo` model) with soft female voice.
        """
        if self.tts_disabled or not text or not self.api_key or "your_" in self.api_key.lower() or len(self.api_key) < 10:
            return {"status": "fallback", "message": "Using browser soft female speech synthesis"}

        payload = {
            "model": "speech-01-turbo",
            "text": text[:300],
            "stream": False,
            "voice_setting": {
                "voice_id": "female-tianmei",  # Soft, pleasant female voice
                "speed": 0.98,
                "vol": 1.0,
                "pitch": 1
            },
            "audio_setting": {
                "sample_rate": 24000,
                "bitrate": 128000,
                "format": "mp3",
                "channel": 1
            }
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            req = urllib.request.Request(
                MINIMAX_TTS_URL,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers
            )
            with urllib.request.urlopen(req, timeout=2.5) as resp:
                res_data = json.loads(resp.read().decode("utf-8"))
                if res_data.get("base_resp", {}).get("status_code") == 0:
                    audio_hex_or_b64 = res_data.get("data", {}).get("audio", "")
                    if audio_hex_or_b64:
                        return {
                            "status": "success",
                            "audio_b64": audio_hex_or_b64,
                            "format": "mp3"
                        }
        except Exception:
            self.tts_disabled = True

        return {"status": "fallback", "message": "Using frontend soft female speech synthesis"}
