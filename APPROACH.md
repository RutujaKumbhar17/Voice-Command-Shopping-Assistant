# Voice Command Shopping Assistant - Approach Write-up

**FreshRoot** is centered around an intelligent **AI Voice Assistant** that delivers an entirely hands-free shopping experience for farm produce.

### Voice Assistant Architecture & Approach

1. **Speech Recognition & Speech Interruption:** Utilizing the Web Speech API, the assistant activates instantly with a soft audio cue. When the microphone is triggered, an interruption handler immediately cancels active speech synthesis so the assistant never talks over the user.
2. **Natural Language Understanding (NLU):** A low-latency NLP engine transforms natural, varied user speech into structured actions. It accurately resolves shopping intents (adding/removing items, price queries, cart cost calculations, inventory counts) while extracting product names, quantities, and units (e.g., *"Add 2 kg apples to cart"*).
3. **Voice-Driven Cart & Catalog Validation:** Voice actions are strictly verified against the store catalog in real time, adding only available produce to the database while recommending seasonal alternatives for unavailable items.
4. **Natural Speech Synthesis & Visual Feedback:** Spoken responses are generated via clear, natural female text-to-speech synthesis (TTS) accompanied by an animated floating widget and interactive in-chat cart summary cards.
 