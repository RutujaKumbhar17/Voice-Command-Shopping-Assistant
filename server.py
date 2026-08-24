import os
import json
import joblib
import pandas as pd
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from database import Database
from minimax_client import MiniMaxClient

app = Flask(__name__, static_folder="Frontend", static_url_path="")
CORS(app)

db = Database()
minimax = MiniMaxClient()

# Load Scikit-Learn Pricing Model if available
PRICING_MODEL_PATH = os.path.join(os.path.dirname(__file__), "pricing_model.pkl")
pricing_model = None
if os.path.exists(PRICING_MODEL_PATH):
    try:
        pricing_model = joblib.load(PRICING_MODEL_PATH)
        print("[Server] Pricing ML model loaded successfully.")
    except Exception as e:
        print(f"[Server] Failed to load pricing model: {e}")

@app.route("/")
def index():
    return send_from_directory("Frontend", "home.html")

# -------------------------------------------------------------
# Core Voice Command API Endpoint powered by MiniMax AI
# -------------------------------------------------------------
@app.route("/api/voice-command", methods=["POST"])
def process_voice_command():
    data = request.get_json() or {}
    transcript = data.get("transcript", "").strip()

    if not transcript:
        return jsonify({"error": "Transcript is required"}), 400

    products = db.get_all_products()

    # Step 1: Parse intent using MiniMax LLM
    parsed = minimax.parse_voice_command(transcript, available_products=products)
    intent = parsed.get("intent", "general_query")
    item_name = parsed.get("item_name")
    quantity = parsed.get("quantity", 1)
    max_price = parsed.get("max_price")
    category = parsed.get("category")

    response_text = parsed.get("response_speech") or "I processed your request."
    matched_products = []
    suggestions = None

    # Step 2: Execute Intent Actions
    if intent == "add_item":
        if item_name:
            product = db.get_product_by_name(item_name)
            price = product["product_price"] if product else 25
            cat = product["product_cat"] if product else (category or "General")

            # Add to DB shopping list and cart
            db.add_to_shopping_list(
                item_name=item_name.title(),
                quantity=quantity,
                unit=parsed.get("unit") or "items",
                category=cat,
                price=price
            )
            if product:
                db.add_to_cart(product_id=product["product_id"], qty=quantity)

            response_text = f"Added {quantity} {item_name} to your shopping list and cart."
        else:
            # Fallback: add raw item
            db.add_to_shopping_list(item_name=transcript.title(), quantity=quantity, price=30)
            response_text = f"Added {transcript} to your shopping list."

    elif intent == "remove_item":
        if item_name:
            success = db.remove_from_shopping_list(item_name)
            if success:
                response_text = f"Removed {item_name} from your shopping list."
            else:
                response_text = f"Could not find {item_name} in your list."
        else:
            response_text = "Please specify which item to remove."

    elif intent in ["search_item", "filter_price"]:
        matched_products = db.get_all_products(
            category=category,
            max_price=max_price,
            search_query=item_name or transcript
        )
        if matched_products:
            response_text = f"Found {len(matched_products)} items matching your request."
        else:
            # If search yields empty, fallback search by query
            matched_products = db.get_all_products(search_query=item_name or "")
            if matched_products:
                response_text = f"Here are items related to {item_name}."
            else:
                response_text = "Sorry, no products matched your search parameters."

    elif intent == "get_suggestions":
        history = [item["item_name"] for item in db.get_shopping_list()]
        suggestions = minimax.generate_smart_suggestions(history_items=history)
        response_text = "Here are smart recommendations, seasonal picks, and substitutes for you."

    elif intent == "clear_list":
        db.clear_shopping_list()
        response_text = "Cleared all items from your shopping list."

    # Step 3: Generate Speech Audio using MiniMax TTS
    tts_result = minimax.generate_speech_audio(response_text)
    audio_b64 = tts_result.get("audio_b64") if tts_result and tts_result.get("status") == "success" else None

    # Retrieve current state
    shopping_list = db.get_shopping_list()
    cart = db.get_cart()

    return jsonify({
        "success": True,
        "intent": intent,
        "parsed_nlu": parsed,
        "response_speech": response_text,
        "audio_b64": audio_b64,
        "matched_products": matched_products,
        "suggestions": suggestions,
        "shopping_list": shopping_list,
        "cart": cart
    })

# -------------------------------------------------------------
# REST API Endpoints for Shopping List, Cart & Products
# -------------------------------------------------------------
@app.route("/api/shopping-list", methods=["GET", "POST", "DELETE"])
def handle_shopping_list():
    if request.method == "GET":
        return jsonify({"shopping_list": db.get_shopping_list()})

    elif request.method == "POST":
        data = request.get_json() or {}
        item_name = data.get("item_name")
        if not item_name:
            return jsonify({"error": "item_name is required"}), 400
        qty = int(data.get("quantity", 1))
        unit = data.get("unit", "items")
        category = data.get("category", "General")
        price = int(data.get("price", 0))

        item_id = db.add_to_shopping_list(item_name, qty, unit, category, price)
        return jsonify({"success": True, "item_id": item_id, "shopping_list": db.get_shopping_list()})

    elif request.method == "DELETE":
        item_id = request.args.get("id")
        if item_id:
            with db.get_connection() as conn:
                conn.cursor().execute("DELETE FROM voice_shopping_list WHERE id = ?", (item_id,))
                conn.commit()
        else:
            db.clear_shopping_list()
        return jsonify({"success": True, "shopping_list": db.get_shopping_list()})

@app.route("/api/cart", methods=["GET", "POST", "DELETE"])
def handle_cart():
    if request.method == "GET":
        cart = db.get_cart()
        total = sum(item["subtotal"] for item in cart)
        return jsonify({"cart": cart, "total": total})

    elif request.method == "POST":
        data = request.get_json() or {}
        product_id = data.get("product_id")
        qty = int(data.get("qty", 1))
        if not product_id:
            return jsonify({"error": "product_id required"}), 400

        db.add_to_cart(product_id=product_id, qty=qty)
        cart = db.get_cart()
        total = sum(item["subtotal"] for item in cart)
        return jsonify({"success": True, "cart": cart, "total": total})

    elif request.method == "DELETE":
        cart_id = request.args.get("id")
        if cart_id:
            db.remove_from_cart(cart_id)
        cart = db.get_cart()
        total = sum(item["subtotal"] for item in cart)
        return jsonify({"success": True, "cart": cart, "total": total})

@app.route("/api/products", methods=["GET"])
def get_products():
    category = request.args.get("category")
    max_price = request.args.get("max_price")
    query = request.args.get("query")
    if max_price:
        max_price = float(max_price)

    products = db.get_all_products(category=category, max_price=max_price, search_query=query)
    return jsonify({"products": products})

@app.route("/api/suggestions", methods=["GET"])
def get_suggestions():
    history = [item["item_name"] for item in db.get_shopping_list()]
    products = db.get_all_products()
    suggestions = minimax.generate_smart_suggestions(history_items=history, products_catalog=products)
    return jsonify({"suggestions": suggestions})

@app.route("/api/predict-price", methods=["POST"])
def predict_price():
    if not pricing_model:
        return jsonify({"error": "Pricing model not available"}), 500

    data = request.get_json() or {}
    try:
        input_df = pd.DataFrame([{
            "Competitor Price (₹)": float(data.get("competitor_price", 50)),
            "Supply Quantity (Tons)": float(data.get("supply", 20)),
            "Demand (Number of Buyers)": float(data.get("demand", 1500)),
            "Season": data.get("season", "Summer")
        }])
        predicted_price = float(pricing_model.predict(input_df)[0])
        return jsonify({
            "success": True,
            "predicted_price": round(predicted_price, 2),
            "input": data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/tts", methods=["POST"])
def text_to_speech():
    data = request.get_json() or {}
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "Text is required"}), 400

    tts_res = minimax.generate_speech_audio(text)
    return jsonify(tts_res)

if __name__ == "__main__":
    print("[Server] FreshRoot Voice Assistant Server running on http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
