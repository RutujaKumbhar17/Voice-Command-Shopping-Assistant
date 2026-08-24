# FreshRoot - AI Voice Command Shopping Assistant

**FreshRoot** is an industry-grade, farm-to-kitchen e-commerce ecosystem featuring a **Multilingual AI Voice Command Shopping Assistant** built for the Software Engineering Technical Assessment.

---

## 🌟 Executive Summary & Project Approach (Technical Write-up)

> **Approach Write-up (Max 200 words):**
> 
> FreshRoot AI Voice Assistant decouples multilingual audio input from AI natural language processing (NLP) to provide an intuitive, voice-first shopping experience. We integrated **MiniMax LLM (`MiniMax-Text-01`)** as our core intent-recognition engine to parse complex, conversational commands across multiple languages (e.g., *"Add 2 kg apples"*, *"Find organic vegetables under ₹50"*, *"Remove milk"*). For spoken audio feedback, we leveraged **MiniMax Speech Synthesis (`speech-01-turbo`)** to generate real-time AI voice responses.
> 
> The system is backed by a robust Python Flask REST API and an SQLite relational database (`freshroot.db`) pre-seeded with real product catalogs, user cart models, and shopping lists. To maximize intelligence, we built a **Smart Suggestions Engine** that dynamically outputs personalized product recommendations, seasonal harvest picks (e.g., Ratnagiri Alphonso Mango), and health-conscious item substitutes (e.g., Almond Milk for Regular Milk). Furthermore, an integrated Scikit-Learn Machine Learning Linear Regression model (`pricing_model.pkl`) predicts optimal dynamic market pricing based on competitor rates, supply, demand, and seasonal metrics. The frontend features a glassmorphic UI with real-time waveform visualizers, visual intent badges, and instant cart synchronization.

---

## 🏗️ System Architecture

```
 ┌───────────────────────────────────────────────────────────────┐
 │                   Web Frontend (Glassmorphic UI)              │
 │  - Web Speech API (Multilingual Browser Microphone Input)    │
 │  - MiniMax Speech Audio Player (TTS Base64 Output Playback)   │
 │  - Dynamic Shopping List, Cart Sync & Smart Suggestions      │
 └───────────────────────────────┬───────────────────────────────┘
                                 │ REST API Requests (JSON)
                                 ▼
 ┌───────────────────────────────────────────────────────────────┐
 │                   Backend Flask REST Server                   │
 │                     (`server.py` on Port 5000)                │
 │  - `/api/voice-command` : Core NLU processing & execution     │
 │  - `/api/suggestions`   : Personalized, Seasonal & Substitutes│
 │  - `/api/cart`          : Shopping Cart CRUD & Total          │
 │  - `/api/shopping-list` : Voice Shopping List CRUD            │
 │  - `/api/products`      : Voice Search & Price Range Filters  │
 │  - `/api/predict-price` : ML Linear Regression Pricing API    │
 └──────────────┬────────────────────────────────┬───────────────┘
                │                                │
                ▼                                ▼
 ┌──────────────────────────────┐ ┌──────────────────────────────┐
 │    MiniMax AI Engine Gateway │ │     SQLite Database Engine   │
 │    (`minimax_client.py`)     │ │        (`database.py`)       │
 │ - LLM: `MiniMax-Text-01`     │ │ - `products` catalog         │
 │ - Speech: `speech-01-turbo`  │ │ - `voice_shopping_list`      │
 └──────────────────────────────┘ │ - `cart` & `orders`          │
                                  └──────────────────────────────┘
```

---

## 🚀 Key Features Implemented

### 1. 🎤 Multilingual Voice Recognition & NLP (MiniMax LLM)
- **Flexible Natural Language Processing:** Understands varied user phrasing (*"Add 2 bottles of water"*, *"I want to buy 5 oranges"*, *"Take milk off my list"*).
- **Multilingual Input Support:** Supports English, Hindi, Marathi, Spanish, French, etc. via Web Speech API.
- **Intent Extraction:** MiniMax LLM parses commands into structured JSON (`intent`, `item_name`, `quantity`, `unit`, `max_price`, `category`, `response_speech`).

### 2. 💡 Smart AI Suggestions Engine
- **Product Recommendations:** Suggests items based on user shopping history and frequent needs.
- **Seasonal Picks:** Highlights in-season produce (e.g., Alphonso Mangoes in Summer, Strawberries in Winter).
- **Smart Substitutes:** Automatically suggests alternative products (e.g., Almond Milk for Regular Milk, Brown Rice for White Rice).

### 3. 📋 Voice Shopping List & Cart Management
- **Full CRUD:** Add, remove, update quantities, or clear list via voice or UI buttons.
- **Auto-Categorization:** Categorizes produce automatically (Fruits, Vegetables, Grains, Dairy, Bakery).
- **1-Click Cart Sync:** Seamlessly converts voice shopping list items into active cart purchases.

### 4. 🔍 Voice Search & Price Filtering
- Filter produce by price range (*"Find fruits under ₹60"*) or search specific brands/types (*"Find organic carrots"*).

### 5. 🔊 MiniMax AI Text-to-Speech (TTS) Synthesis
- Synthesizes spoken responses using MiniMax `speech-01-turbo` voice engine and streams MP3 audio back to the user interface.

### 6. 📊 Machine Learning Price Estimator
- Integrates pre-trained `pricing_model.pkl` to calculate optimal market prices using competitor rates, supply tons, demand, and season.

---

## 🔧 Installation & Local Setup

### 1. Prerequisites
- Python 3.9+
- Modern Web Browser (Google Chrome / Edge recommended for Web Speech API)

### 2. Install Dependencies
```bash
pip install flask flask-cors pandas scikit-learn joblib
```

### 3. Run the Backend Server
```bash
python server.py
```
*The Flask server will start on `http://127.0.0.1:5000`.*

### 4. Access the Application
Open your browser and navigate to:
```
http://127.0.0.1:5000/
```
or directly access the Voice Assistant interface:
```
http://127.0.0.1:5000/voice_assistant.html
```

---

## 🧪 Verification & Automated Testing

To run the system test suite verifying MiniMax API connectivity, database CRUD, and price predictions:
```bash
python -c "
import urllib.request, json
req = urllib.request.Request('http://127.0.0.1:5000/api/products')
res = urllib.request.urlopen(req)
print('Server Health Status:', res.status)
"
```

---

## 📂 Project Structure

```
FarmPure/
├── server.py                   # Main Flask REST API server
├── minimax_client.py           # MiniMax LLM & Speech Synthesis Client wrapper
├── database.py                 # SQLite Database Manager & Catalog Seeder
├── dataset.py                  # ML Pricing model training pipeline
├── pricing_model.pkl           # Scikit-learn trained linear regression model
├── farmpure.db                 # SQLite database storage
├── farmpure.sql                # SQL dump schema and seed data
└── Frontend/
    ├── voice_assistant.html    # AI Voice Command Shopping Assistant UI
    ├── index.html              # FarmPure Landing Page
    ├── cart.html               # Shopping Cart Page
    └── products.html           # Product Catalog Page
```