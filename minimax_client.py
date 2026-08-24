import os
import json
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

    def _call_chat(self, messages, system_prompt=None, json_mode=False):
        full_messages = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)

        payload = {
            "model": "MiniMax-Text-01",
            "messages": full_messages,
            "temperature": 0.2
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
            with urllib.request.urlopen(req, timeout=12) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0]["message"]["content"]
                    return content
        except Exception as e:
            print(f"[MiniMaxClient] Chat Error: {e}")
        return None

    def parse_voice_command(self, user_transcript, available_products=None):
        """
        Parses user's voice command into a structured JSON intent using MiniMax LLM.
        """
        product_names = [p["product_type"] for p in available_products] if available_products else []

        system_prompt = (
            "You are an intelligent NLP NLU engine for FreshRoot voice shopping assistant.\n"
            "Your task is to analyze user voice commands (in English, Hindi, Spanish, French, Marathi, etc.) "
            "and extract structured JSON parameters.\n"
            "Identify the primary intent from: ['add_item', 'remove_item', 'search_item', 'get_suggestions', 'clear_list', 'filter_price', 'checkout', 'general_query'].\n"
            "Available products in store: " + ", ".join(product_names) + "\n\n"
            "Output strictly valid JSON only with no markdown wrapping, using this exact schema:\n"
            "{\n"
            '  "intent": "<intent_name>",\n'
            '  "item_name": "<matched or extracted product name or null>",\n'
            '  "quantity": <integer quantity or 1>,\n'
            '  "unit": "<unit if mentioned, e.g. kg, bottles, packs, pieces, or null>",\n'
            '  "category": "<extracted product category if mentioned e.g. Fruits, Vegetables, Grains, Dairy, or null>",\n'
            '  "max_price": <number max price filter if mentioned or null>,\n'
            '  "response_speech": "<friendly confirmation message in user language to speak back>",\n'
            '  "confidence": 0.95\n'
            "}"
        )

        messages = [
            {"role": "user", "content": user_transcript}
        ]

        raw_response = self._call_chat(messages, system_prompt=system_prompt, json_mode=True)
        if raw_response:
            try:
                # Clean response markdown if present
                clean = raw_response.strip()
                if clean.startswith("```json"):
                    clean = clean[7:]
                if clean.startswith("```"):
                    clean = clean[3:]
                if clean.endswith("```"):
                    clean = clean[:-3]
                clean = clean.strip()
                return json.loads(clean)
            except Exception as pe:
                print(f"[MiniMaxClient] JSON parse error: {pe}, Raw: {raw_response}")

        # Fallback heuristic parser if API fails or returns non-JSON
        return self._fallback_parse(user_transcript, available_products)

    def _fallback_parse(self, text, available_products=None):
        text_lower = text.lower()
        intent = "general_query"
        item_name = None
        quantity = 1
        max_price = None

        if "add" in text_lower or "need" in text_lower or "buy" in text_lower or "want" in text_lower:
            intent = "add_item"
        elif "remove" in text_lower or "delete" in text_lower or "take off" in text_lower:
            intent = "remove_item"
        elif "search" in text_lower or "find" in text_lower or "show" in text_lower or "look for" in text_lower:
            intent = "search_item"
        elif "suggest" in text_lower or "recommend" in text_lower or "running low" in text_lower:
            intent = "get_suggestions"

        # Try matching item name
        if available_products:
            for p in available_products:
                p_name = p["product_type"].lower()
                if p_name in text_lower or p["product_title"].lower() in text_lower:
                    item_name = p["product_type"]
                    break

        return {
            "intent": intent,
            "item_name": item_name,
            "quantity": quantity,
            "unit": None,
            "category": None,
            "max_price": max_price,
            "response_speech": f"Processing your request for {item_name or 'items'}.",
            "confidence": 0.7
        }

    def generate_smart_suggestions(self, history_items=None, products_catalog=None):
        """
        Generates smart AI suggestions: personalized recommendations, seasonal items, and substitutes.
        """
        system_prompt = (
            "You are FreshRoot's AI Smart Shopping Advisor.\n"
            "Given shopping context, generate smart recommendations in JSON with three categories:\n"
            "1. 'recommendations': Items based on user history or frequent needs.\n"
            "2. 'seasonal': Fresh seasonal produce currently in peak harvest or discount.\n"
            "3. 'substitutes': Product alternative suggestions (e.g. Almond Milk for Milk, Jaggery for Sugar).\n"
            "Return valid JSON only with keys 'recommendations', 'seasonal', 'substitutes', where each value is an array of objects with fields 'name', 'reason', 'price', 'category'."
        )

        history_str = ", ".join(history_items) if history_items else "Potato, Tomato, Bananas"
        prompt = f"User frequently buys: {history_str}. Suggest 2 recommendations, 2 seasonal picks, and 2 smart substitutes."

        raw = self._call_chat([{"role": "user", "content": prompt}], system_prompt=system_prompt)
        if raw:
            try:
                clean = raw.strip().replace("```json", "").replace("```", "").strip()
                return json.loads(clean)
            except Exception as e:
                print(f"[MiniMaxClient] Suggestions parse error: {e}")

        # Fallback suggestions
        return {
            "recommendations": [
                {"name": "Whole Wheat Bread", "reason": "Looks like you might be running low based on history", "price": 40, "category": "Bakery"},
                {"name": "Fresh Milk", "reason": "Weekly staple recommendation", "price": 30, "category": "Dairy"}
            ],
            "seasonal": [
                {"name": "Ratnagiri Alphonso Mango", "reason": "In peak summer harvest & high demand", "price": 200, "category": "Fruits"},
                {"name": "Mahabaleshwar Strawberry", "reason": "Freshly harvested seasonal favorite", "price": 25, "category": "Fruits"}
            ],
            "substitutes": [
                {"name": "Almond Milk", "reason": "Great plant-based substitute for Regular Milk", "price": 65, "category": "Dairy"},
                {"name": "Brown Rice", "reason": "Healthier high-fiber alternative to White Rice", "price": 85, "category": "Grains"}
            ]
        }

    def generate_speech_audio(self, text):
        """
        Synthesizes text into audio using MiniMax TTS API (`speech-01-turbo` model).
        Returns dict with base64 audio string and format.
        """
        if not text:
            return None

        payload = {
            "model": "speech-01-turbo",
            "text": text[:300],  # keep synthesis snappy
            "stream": False,
            "voice_setting": {
                "voice_id": "male-qn-qingse",
                "speed": 1.0,
                "vol": 1.0,
                "pitch": 0
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
            with urllib.request.urlopen(req, timeout=10) as resp:
                res_data = json.loads(resp.read().decode("utf-8"))
                if res_data.get("base_resp", {}).get("status_code") == 0:
                    audio_hex_or_b64 = res_data.get("data", {}).get("audio", "")
                    if audio_hex_or_b64:
                        return {
                            "status": "success",
                            "audio_b64": audio_hex_or_b64,
                            "format": "mp3"
                        }
        except Exception as e:
            print(f"[MiniMaxClient] TTS Error: {e}")

        return {"status": "error", "message": "TTS synthesis failed"}
