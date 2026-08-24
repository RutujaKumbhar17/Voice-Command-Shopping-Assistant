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
    return send_from_directory("Frontend", "login_signup.html")

def generate_verbal_cart_suggestions(cart_items, catalog_products):
    """
    Analyzes produce currently in the cart and generates dynamic verbal recommendations.
    """
    if not cart_items:
        return "Your cart is currently empty. I suggest starting with fresh Apples, Bananas, or organic Potatoes."

    cart_types = [item['product_type'].lower() for item in cart_items]
    
    # Contextual Produce Pairing Matrix
    pairings = {
        'potato': ['Tomato', 'Onion', 'Carrot'],
        'potatoes': ['Tomato', 'Onion', 'Carrot'],
        'tomato': ['Potato', 'Onion', 'Cabbage'],
        'tomatoes': ['Potato', 'Onion', 'Cabbage'],
        'onion': ['Potato', 'Tomato', 'Carrot'],
        'onions': ['Potato', 'Tomato', 'Carrot'],
        'carrot': ['Potato', 'Cabbage', 'Tomato'],
        'carrots': ['Potato', 'Cabbage', 'Tomato'],
        'cabbage': ['Carrot', 'Potato', 'Tomato'],
        'banana': ['Apple', 'Strawberry', 'Orange'],
        'bananas': ['Apple', 'Strawberry', 'Orange'],
        'apple': ['Bananas', 'Grapes', 'Orange'],
        'apples': ['Bananas', 'Grapes', 'Orange'],
        'mango': ['Strawberry', 'Grapes', 'Bananas'],
        'grapes': ['Apple', 'Orange', 'Strawberry'],
        'orange': ['Grapes', 'Apple', 'Bananas'],
        'strawberry': ['Bananas', 'Custard Apple', 'Apple'],
        'custard apple': ['Strawberry', 'Mango', 'Apple'],
        'rice': ['Wheat', 'Maize', 'Potato'],
        'wheat': ['Rice', 'Maize', 'Potato'],
        'maize': ['Rice', 'Wheat', 'Carrot'],
        'coconut': ['Rice', 'Bananas', 'Sugarcane'],
        'sugarcane': ['Coconut', 'Mango', 'Bananas']
    }

    candidates = []
    for c_item in cart_types:
        for key, recs in pairings.items():
            if key in c_item:
                for r in recs:
                    if r.lower() not in cart_types and r not in candidates:
                        candidates.append(r)

    # Fallback if no specific pairing found
    if not candidates:
        for p in catalog_products:
            p_name = p['product_type']
            if p_name.lower() not in cart_types and p_name not in candidates:
                candidates.append(p_name)
            if len(candidates) >= 2:
                break

    top_picks = candidates[:2]
    if len(top_picks) == 2:
        return f"Based on items in your cart, I suggest adding fresh {top_picks[0]} and {top_picks[1]}."
    elif len(top_picks) == 1:
        return f"Based on what is in your cart, fresh {top_picks[0]} would pair well."
    else:
        return "Your cart looks great! You can also check out our fresh seasonal fruits."

# -------------------------------------------------------------
# Core Voice Command API Endpoint powered by MiniMax AI
# -------------------------------------------------------------
@app.route("/api/voice-command", methods=["POST"])
def process_voice_command():
    data = request.get_json() or {}
    transcript = data.get("transcript", "").strip()
    session_context = data.get("context", {})

    if not transcript:
        return jsonify({"error": "Transcript is required"}), 400

    products = db.get_all_products()
    current_cart = db.get_cart()
    current_list = db.get_shopping_list()

    # Step 1: Parse intent using MiniMax LLM or Local NLU Engine
    parsed = minimax.parse_voice_command(
        transcript,
        available_products=products,
        cart_data=current_cart,
        list_data=current_list,
        context=session_context
    )
    intent = parsed.get("intent", "general_query")
    target = parsed.get("target", "both")
    item_name = parsed.get("item_name")
    quantity = parsed.get("quantity")
    unit = parsed.get("unit") or "kg"
    max_price = parsed.get("max_price")
    category = parsed.get("category")
    pending_item = None

    response_text = parsed.get("response_speech") or "I processed your request."
    matched_products = []
    suggestions = None

    # Step 2: Execute Intent Actions
    if intent == "ask_quantity":
        pending_item = item_name
        response_text = parsed.get("response_speech") or f"How much {item_name or 'item'} would you like to add? Please specify the quantity, for example 1 kg or 2 kg."
        product = db.get_product_by_name(item_name) if item_name else None
        if product:
            matched_products = [product]

    elif intent == "add_item":
        actual_qty = quantity if (quantity is not None and quantity > 0) else 1
        clean_name = item_name or transcript
        product = db.get_product_by_name(clean_name)

        if product:
            db.add_to_cart(product["product_id"], qty=actual_qty)
            db.add_to_shopping_list(
                item_name=product["product_type"].title(),
                quantity=actual_qty,
                unit=unit,
                category=product.get("product_cat", "General"),
                price=product["product_price"]
            )
            updated_cart = db.get_cart()
            suggestion_verbal = generate_verbal_cart_suggestions(updated_cart, products)
            response_text = f"Added {actual_qty} {unit} {product['product_type']} to your cart. {suggestion_verbal}"
            matched_products = [product]
            pending_item = None
        else:
            # Item is NOT in available farm catalog
            available_samples = [p["product_type"] for p in products[:7]]
            response_text = f"Sorry, '{clean_name}' is not available in our store. We have {', '.join(available_samples)}, and more."
            matched_products = []
            pending_item = None

    elif intent == "store_inventory":
        sample_names = [p["product_type"] for p in products[:7]]
        response_text = f"We have {len(products)} fresh produce items in store including {', '.join(sample_names)}, and more."

    elif intent in ["get_cart_total", "view_cart"]:
        cart_items = db.get_cart()
        if cart_items:
            total_price = sum(item["subtotal"] for item in cart_items)
            item_summaries = [f"{item['qty']} {item['product_type']}" for item in cart_items]
            response_text = f"Your cart has {len(cart_items)} items ({', '.join(item_summaries)}). Total cost: Rs. {total_price}."
            matched_products = cart_items
        else:
            response_text = "Your cart is currently empty. You can ask me to add apples, bananas, or potatoes."

    elif intent == "view_shopping_list":
        list_items = db.get_shopping_list()
        if list_items:
            items_str = ", ".join([f"{item['quantity']} {item['unit']} {item['item_name']}" for item in list_items])
            response_text = f"Shopping list: {items_str}."
        else:
            response_text = "Your shopping list is empty."

    elif intent == "get_price":
        if item_name:
            product = db.get_product_by_name(item_name)
            if product:
                response_text = f"{product['product_type']} is Rs. {product['product_price']} per {unit}."
                matched_products = [product]
            else:
                response_text = f"Fresh {item_name} is around Rs. 30 to 60 per kg."
        else:
            response_text = "Which product price would you like to check?"

    elif intent == "remove_item":
        clean_name = item_name or transcript
        qty_to_remove = quantity if (quantity is not None and quantity > 0) else 1
        success, remaining_qty, product = db.remove_from_cart_by_name(clean_name, qty=qty_to_remove)
        db.remove_from_shopping_list(clean_name)
        
        if success:
            p_name = product["product_type"] if product else clean_name
            p_unit = unit or "kg"
            if remaining_qty > 0:
                response_text = f"Removed {qty_to_remove} {p_unit} {p_name}. You now have {remaining_qty} {p_unit} remaining in your cart."
            else:
                response_text = f"Removed {p_name} from your cart."
        else:
            response_text = f"{clean_name} is not currently in your cart."
        
        matched_products = []
        pending_item = None

    elif intent == "clear_list":
        db.clear_shopping_list()
        response_text = "Shopping list cleared."

    elif intent == "clear_cart":
        with db.get_connection() as conn:
            conn.cursor().execute("DELETE FROM cart WHERE phonenumber = 8169193101")
            conn.commit()
        response_text = "Cart cleared."

    elif intent in ["search_item", "filter_price"]:
        matched_products = db.get_all_products(
            category=category,
            max_price=max_price,
            search_query=item_name or transcript
        )
        if matched_products:
            response_text = f"Found {len(matched_products)} items matching '{item_name or transcript}'."
        else:
            matched_products = db.get_all_products(search_query=item_name or "")
            if matched_products:
                response_text = f"Here are items related to {item_name or transcript}."
            else:
                response_text = "No produce matched your search."

    elif intent == "get_suggestions":
        cart_items = db.get_cart()
        response_text = generate_verbal_cart_suggestions(cart_items, products)
        
        # Also attach structured recommendation objects
        cart_types = [item['product_type'].lower() for item in cart_items]
        rec_products = [p for p in products if p['product_type'].lower() not in cart_types][:3]
        matched_products = rec_products
        suggestions = {
            "recommendations": [{"name": p["product_title"], "price": p["product_price"], "reason": "Recommended based on your cart"} for p in rec_products]
        }

    elif intent == "checkout":
        cart_items = db.get_cart()
        total_price = sum(item["subtotal"] for item in cart_items)
        if cart_items:
            response_text = f"Your order total is ₹{total_price}. Proceeding to checkout."
        else:
            response_text = "Your cart is empty."

    # Step 3: Generate Speech Audio using MiniMax TTS (Soft Female Voice)
    tts_result = minimax.generate_speech_audio(response_text)
    audio_b64 = tts_result.get("audio_b64") if tts_result and tts_result.get("status") == "success" else None

    # Retrieve current updated state
    shopping_list = db.get_shopping_list()
    cart = db.get_cart()

    return jsonify({
        "success": True,
        "intent": intent,
        "pending_item": pending_item,
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
    cart_items = db.get_cart()
    products = db.get_all_products()
    cart_types = [item['product_type'].lower() for item in cart_items]
    
    pairings = {
        'potato': ['Tomato', 'Onion', 'Carrot'],
        'potatoes': ['Tomato', 'Onion', 'Carrot'],
        'tomato': ['Potato', 'Onion', 'Cabbage'],
        'tomatoes': ['Potato', 'Onion', 'Cabbage'],
        'onion': ['Potato', 'Tomato', 'Carrot'],
        'onions': ['Potato', 'Tomato', 'Carrot'],
        'carrot': ['Potato', 'Cabbage', 'Tomato'],
        'carrots': ['Potato', 'Cabbage', 'Tomato'],
        'cabbage': ['Carrot', 'Potato', 'Tomato'],
        'banana': ['Apple', 'Strawberry', 'Orange'],
        'bananas': ['Apple', 'Strawberry', 'Orange'],
        'apple': ['Bananas', 'Grapes', 'Orange'],
        'apples': ['Bananas', 'Grapes', 'Orange'],
        'mango': ['Strawberry', 'Grapes', 'Bananas'],
        'grapes': ['Apple', 'Orange', 'Strawberry'],
        'orange': ['Grapes', 'Apple', 'Bananas'],
        'strawberry': ['Bananas', 'Custard Apple', 'Apple'],
        'custard apple': ['Strawberry', 'Mango', 'Apple'],
        'rice': ['Wheat', 'Maize', 'Potato'],
        'wheat': ['Rice', 'Maize', 'Potato'],
        'maize': ['Rice', 'Wheat', 'Carrot'],
        'coconut': ['Rice', 'Bananas', 'Sugarcane'],
        'sugarcane': ['Coconut', 'Mango', 'Bananas']
    }

    rec_names = []
    reason_map = {}
    for c_item in cart_types:
        for key, recs in pairings.items():
            if key in c_item:
                for r in recs:
                    if r.lower() not in cart_types and r not in rec_names:
                        rec_names.append(r)
                        reason_map[r] = f"Pairs with {c_item.title()} in your cart"

    if not rec_names:
        rec_names = ["Tomato", "Onion", "Carrot", "Bananas"]
        for r in rec_names:
            reason_map[r] = "Popular fresh farm staple"

    recommendations = []
    for r_name in rec_names[:3]:
        p = db.get_product_by_name(r_name)
        if p:
            recommendations.append({
                "name": p["product_title"],
                "price": p["product_price"],
                "reason": reason_map.get(r_name, "Recommended for your cart"),
                "category": p.get("product_cat", "Vegetables")
            })

    seasonal_names = ["Mango", "Strawberry", "Custard Apple"]
    seasonal = []
    for s_name in seasonal_names:
        p = db.get_product_by_name(s_name)
        if p:
            seasonal.append({
                "name": p["product_title"],
                "price": p["product_price"],
                "reason": "Fresh seasonal harvest",
                "category": "Fruits"
            })

    substitute_names = ["Maize", "Rice", "Wheat"]
    substitutes = []
    for sub_name in substitute_names:
        p = db.get_product_by_name(sub_name)
        if p:
            substitutes.append({
                "name": p["product_title"],
                "price": p["product_price"],
                "reason": "Farm-direct grains & produce",
                "category": "Grains"
            })

    return jsonify({
        "suggestions": {
            "verbal_summary": generate_verbal_cart_suggestions(cart_items, products),
            "recommendations": recommendations,
            "seasonal": seasonal,
            "substitutes": substitutes
        }
    })

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

@app.route("/<path:path>")
def serve_frontend_files(path):
    frontend_dir = os.path.join(os.path.dirname(__file__), "Frontend")
    file_path = os.path.join(frontend_dir, path)
    if os.path.exists(file_path):
        return send_from_directory(frontend_dir, path)
    
    # Case-insensitive / fallback resolver for Linux hosting (e.g. Vercel)
    if path.startswith("image/") or path.startswith("image\\"):
        raw_img = os.path.basename(path).lower().replace(" ", "_")
        image_dir = os.path.join(frontend_dir, "image")
        if os.path.exists(image_dir):
            for f in os.listdir(image_dir):
                if f.lower() == raw_img or f.lower() == os.path.basename(path).lower():
                    return send_from_directory(image_dir, f)
    
    return send_from_directory(frontend_dir, "login_signup.html")

if __name__ == "__main__":
    print("[Server] FreshRoot Voice Assistant Server running on http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
 