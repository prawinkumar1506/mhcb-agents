"""
Language detection and multilingual support service
"""
from typing import Dict, List
import re

class LanguageService:
    def __init__(self):
        self.language_patterns = {
            "Hindi": [
                r'[\u0900-\u097F]',  # Devanagari script
                r'\b(मैं|आप|है|हूं|का|की|के|में|से|को|पर|और|या|नहीं|हाँ|क्या|कैसे|कब|कहाँ|क्यों)\b'
            ],
            "Tamil": [
                r'[\u0B80-\u0BFF]',  # Tamil script
                r'\b(நான்|நீங்கள்|இருக்கிறது|உள்ளது|என்|உம்|இல்|से|को|पर|और|या|नहीं|हाँ|क्या|कैसे|कब|कहाँ|क्यों)\b'
            ],
            "Spanish": [
                r'\b(yo|tú|él|ella|nosotros|vosotros|ellos|ellas|soy|eres|es|somos|sois|son|estoy|estás|está|estamos|estáis|están)\b',
                r'\b(que|como|cuando|donde|porque|si|no|sí|hola|gracias|por favor|lo siento)\b'
            ]
        }
        
        self.crisis_translations = {
            "English": {
                "crisis_message": "I'm very concerned about what you've shared. Your life has value and there are people who want to help you right now.",
                "helpline_prompt": "Please reach out to a crisis helpline immediately:",
                "emergency_prompt": "If you're in immediate danger, please call emergency services."
            },
            "Hindi": {
                "crisis_message": "आपने जो साझा किया है उससे मैं बहुत चिंतित हूं। आपका जीवन मूल्यवान है और ऐसे लोग हैं जो अभी आपकी मदद करना चाहते हैं।",
                "helpline_prompt": "कृपया तुरंत क्राइसिस हेल्पलाइन से संपर्क करें:",
                "emergency_prompt": "यदि आप तत्काल खतरे में हैं, तो कृपया आपातकालीन सेवाओं को कॉल करें।"
            },
            "Tamil": {
                "crisis_message": "நீங்கள் பகிர்ந்துகொண்டதைப் பற்றி நான் மிகவும் கவலைப்படுகிறேன். உங்கள் வாழ்க்கைக்கு மதிப்பு உண்டு, இப்போதே உங்களுக்கு உதவ விரும்பும் மக்கள் உள்ளனர்.",
                "helpline_prompt": "தயவுசெய்து உடனடியாக நெருக்கடி உதவி எண்ணை தொடர்பு கொள்ளுங்கள்:",
                "emergency_prompt": "நீங்கள் உடனடி ஆபத்தில் இருந்தால், தயவுசெய்து அவசர சேவைகளை அழைக்கவும்."
            },
            "Spanish": {
                "crisis_message": "Estoy muy preocupado por lo que has compartido. Tu vida tiene valor y hay personas que quieren ayudarte ahora mismo.",
                "helpline_prompt": "Por favor, contacta inmediatamente con una línea de crisis:",
                "emergency_prompt": "Si estás en peligro inmediato, por favor llama a los servicios de emergencia."
            }
        }
    
    def detect_language(self, text: str) -> str:
        """Detect the primary language of the input text"""
        text_lower = text.lower()
        
        for language, patterns in self.language_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return language
        
        # Default to English if no other language detected
        return "English"
    
    def get_crisis_messages(self, language: str) -> Dict[str, str]:
        """Get crisis intervention messages in the specified language"""
        return self.crisis_translations.get(language, self.crisis_translations["English"])
    
    def get_greeting_templates(self, language: str, style: str) -> Dict[str, str]:
        """Get greeting templates for different languages and styles"""
        templates = {
            "English": {
                "formal": "Hello, I'm here to provide mental health support. How can I assist you today?",
                "genz": "Hey there! I'm here to help with whatever's on your mind. What's going on?",
                "empathetic": "Hi, I'm glad you reached out. I'm here to listen and support you. What would you like to talk about?",
                "clinical": "Good day. I'm a mental health support assistant. Please describe your current concerns."
            },
            "Hindi": {
                "formal": "नमस्ते, मैं मानसिक स्वास्थ्य सहायता प्रदान करने के लिए यहाँ हूँ। आज मैं आपकी कैसे सहायता कर सकता हूँ?",
                "genz": "हेलो! मैं यहाँ हूँ आपकी मदद के लिए। क्या बात है?",
                "empathetic": "नमस्ते, मुझे खुशी है कि आपने संपर्क किया। मैं यहाँ सुनने और आपका साथ देने के लिए हूँ। आप किस बारे में बात करना चाहेंगे?",
                "clinical": "नमस्कार। मैं एक मानसिक स्वास्थ्य सहायक हूँ। कृपया अपनी वर्तमान चिंताओं का वर्णन करें।"
            },
            "Tamil": {
                "formal": "வணக்கம், நான் மனநல ஆதரவு வழங்க இங்கே இருக்கிறேன். இன்று நான் உங்களுக்கு எப்படி உதவ முடியும்?",
                "genz": "ஹாய்! உங்கள் மனதில் என்ன இருக்கிறதோ அதற்கு உதவ நான் இங்கே இருக்கிறேன். என்ன நடக்கிறது?",
                "empathetic": "வணக்கம், நீங்கள் தொடர்பு கொண்டதில் மகிழ்ச்சி. நான் கேட்கவும் உங்களுக்கு ஆதரவு அளிக்கவும் இங்கே இருக்கிறேன். எதைப் பற்றி பேச விரும்புகிறீர்கள்?",
                "clinical": "வணக்கம். நான் ஒரு மனநல ஆதரவு உதவியாளர். தயவுசெய்து உங்கள் தற்போதைய கவலைகளை விவரிக்கவும்."
            }
        }
        
        return templates.get(language, templates["English"]).get(style, templates["English"]["empathetic"])

# Global service instance
language_service = LanguageService()
