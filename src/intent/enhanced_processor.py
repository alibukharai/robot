"""
Enhanced intent processor with better pattern matching and fuzzy string matching
"""

import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class Intent(Enum):
    """Customer intent types."""
    ORDER = "order"
    SUGGEST = "suggest"
    CONFIRM = "confirm"
    CANCEL = "cancel"
    INFO = "info"
    DONE = "done"
    GREETING = "greeting"
    UNKNOWN = "unknown"


class EnhancedIntentProcessor:
    """
    Enhanced intent processor with better NLU capabilities.
    
    Improvements:
    - Fuzzy string matching for menu items
    - Better quantity extraction
    - Context awareness
    - Confidence scoring
    - Multiple intent detection
    """
    
    def __init__(self, fuzzy_threshold: float = 0.6):
        """Initialize the enhanced intent processor."""
        self.fuzzy_threshold = fuzzy_threshold
        self.intent_patterns = self._build_enhanced_patterns()
        self.quantity_patterns = self._build_quantity_patterns()
        logger.info("Enhanced intent processor initialized")
        
    def _build_enhanced_patterns(self) -> Dict[Intent, List[str]]:
        """Build comprehensive regex patterns for intent recognition."""
        return {
            Intent.ORDER: [
                r'\b(i want|i would like|i\'ll have|give me|can i have|may i have|i need)\b',
                r'\b(order|get|take|bring me)\b',
                r'\b(one|two|three|four|five|a|an)\s+\w+',
                r'\b(let me have|how about)\b',
            ],
            Intent.SUGGEST: [
                r'\b(suggest|recommend|what do you suggest|what\'s good|what\'s popular)\b',
                r'\b(what should i|help me choose|what\'s your recommendation)\b',
                r'\b(best|favorite|most popular|top)\b',
                r'\b(what\'s fresh|what\'s new|special)\b',
            ],
            Intent.CONFIRM: [
                r'\b(yes|yeah|yep|yup|sure|okay|ok|correct|right|that\'s right)\b',
                r'\b(confirm|confirmed|sounds good|perfect|exactly)\b',
                r'\b(go ahead|proceed|that works)\b',
            ],
            Intent.CANCEL: [
                r'\b(no|nope|cancel|nevermind|never mind|change|remove|delete)\b',
                r'\b(wrong|mistake|different|not that|scratch that)\b',
                r'\b(take off|take out|remove from)\b',
            ],
            Intent.INFO: [
                r'\b(what is|what\'s|tell me about|info|information|describe)\b',
                r'\b(how much|price|cost|expensive|cheap)\b',
                r'\b(contain|ingredient|allerg|gluten|vegan|vegetarian)\b',
                r'\b(calories|nutrition|healthy)\b',
            ],
            Intent.DONE: [
                r'\b(that\'s all|that\'s it|done|finished|complete|nothing else)\b',
                r'\b(ready|checkout|pay|bill|total|finish)\b',
                r'\b(i\'m done|all set|that\'ll be all)\b',
            ],
            Intent.GREETING: [
                r'\b(hello|hi|hey|good morning|good afternoon|good evening)\b',
                r'\b(how are you|what\'s up)\b',
            ],
        }
        
    def _build_quantity_patterns(self) -> Dict[str, int]:
        """Build patterns for quantity extraction."""
        return {
            # Numbers
            'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
            'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14, 'fifteen': 15,
            'sixteen': 16, 'seventeen': 17, 'eighteen': 18, 'nineteen': 19, 'twenty': 20,
            
            # Articles
            'a': 1, 'an': 1, 'the': 1,
            
            # Pairs/multiples
            'pair': 2, 'couple': 2, 'few': 3, 'several': 4, 'bunch': 5,
            'half': 0.5, 'dozen': 12, 'half dozen': 6,
        }
    
    def fuzzy_match_items(self, text: str, menu_items: List[str]) -> List[Tuple[str, float]]:
        """
        Find menu items using fuzzy string matching.
        
        Args:
            text: Input text
            menu_items: List of menu item names
            
        Returns:
            List of (item_name, confidence) tuples
        """
        matches = []
        text_lower = text.lower()
        
        for item in menu_items:
            item_lower = item.lower()
            
            # Exact match gets highest score
            if item_lower in text_lower:
                matches.append((item, 1.0))
                continue
            
            # Check individual words
            item_words = item_lower.split()
            text_words = text_lower.split()
            
            # All words present
            if all(word in text_lower for word in item_words):
                matches.append((item, 0.9))
                continue
            
            # Fuzzy matching for partial matches
            similarity = SequenceMatcher(None, item_lower, text_lower).ratio()
            if similarity >= self.fuzzy_threshold:
                matches.append((item, similarity))
                continue
                
            # Check for partial word matches
            for item_word in item_words:
                for text_word in text_words:
                    word_similarity = SequenceMatcher(None, item_word, text_word).ratio()
                    if word_similarity >= 0.8:  # High threshold for word matching
                        matches.append((item, word_similarity * 0.7))  # Lower overall confidence
                        break
        
        # Sort by confidence and remove duplicates
        matches = sorted(set(matches), key=lambda x: x[1], reverse=True)
        return matches
    
    def extract_enhanced_quantity(self, text: str) -> int:
        """Enhanced quantity extraction with better pattern matching."""
        text_lower = text.lower()
        
        # Check for explicit quantity patterns
        for pattern, quantity in self.quantity_patterns.items():
            if re.search(rf'\b{re.escape(pattern)}\b', text_lower):
                return int(quantity)
        
        # Check for digits
        digit_matches = re.findall(r'\b(\d+)\b', text_lower)
        if digit_matches:
            return int(digit_matches[0])  # Take first number found
        
        # Default quantity
        return 1
    
    def process(self, text: str, menu_items: List[str]) -> Dict[str, Any]:
        """
        Process text with enhanced NLU capabilities.
        
        Args:
            text: Input text
            menu_items: List of menu item names
            
        Returns:
            Enhanced processing result
        """
        if not text:
            return {
                'intent': Intent.UNKNOWN,
                'entities': {},
                'confidence': 0.0,
                'raw_text': text,
                'alternatives': []
            }
        
        text_lower = text.lower().strip()
        
        # Detect primary intent
        primary_intent = self._detect_intent(text_lower)
        
        # Find menu items with fuzzy matching
        item_matches = self.fuzzy_match_items(text_lower, menu_items)
        
        # Extract quantity
        quantity = self.extract_enhanced_quantity(text_lower)
        
        # Extract modifiers
        modifiers = self._extract_enhanced_modifiers(text_lower)
        
        # Build entities
        entities = {
            'items': [match[0] for match in item_matches[:3]],  # Top 3 matches
            'item_confidences': {match[0]: match[1] for match in item_matches[:3]},
            'quantity': quantity,
            'modifiers': modifiers
        }
        
        # Calculate confidence
        confidence = self._calculate_enhanced_confidence(primary_intent, entities, text_lower)
        
        # Generate alternatives
        alternatives = self._generate_alternatives(text_lower, menu_items)
        
        result = {
            'intent': primary_intent,
            'entities': entities,
            'confidence': confidence,
            'raw_text': text,
            'alternatives': alternatives
        }
        
        logger.info(f"Enhanced processing - Intent: {primary_intent.value}, "
                   f"Items: {entities['items'][:2]}, Confidence: {confidence:.2f}")
        
        return result
    
    def _detect_intent(self, text: str) -> Intent:
        """Enhanced intent detection with weighted scoring."""
        intent_scores = {}
        
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text, re.IGNORECASE))
                score += matches
            intent_scores[intent] = score
        
        # Get intent with highest score
        if max(intent_scores.values()) > 0:
            return max(intent_scores, key=intent_scores.get)
        
        # Fallback logic
        if any(word in text for word in ['hello', 'hi', 'hey']):
            return Intent.GREETING
        
        return Intent.UNKNOWN
    
    def _extract_enhanced_modifiers(self, text: str) -> List[str]:
        """Enhanced modifier extraction."""
        modifiers = []
        
        # Size modifiers
        sizes = ['small', 'medium', 'large', 'extra large', 'xl', 'jumbo']
        for size in sizes:
            if size in text:
                modifiers.append(size)
        
        # Temperature modifiers
        temps = ['hot', 'cold', 'iced', 'frozen', 'warm', 'room temperature']
        for temp in temps:
            if temp in text:
                modifiers.append(temp)
        
        # Dietary modifiers
        dietary = ['no dairy', 'lactose free', 'gluten free', 'vegan', 'vegetarian']
        for diet in dietary:
            if diet in text:
                modifiers.append(diet)
        
        # Preparation modifiers
        prep = ['well done', 'medium rare', 'rare', 'crispy', 'soft', 'extra sauce', 'no sauce']
        for p in prep:
            if p in text:
                modifiers.append(p)
        
        # Negation modifiers
        negations = re.findall(r'no\s+(\w+)', text)
        for neg in negations:
            modifiers.append(f'no {neg}')
        
        # Extra modifiers
        extras = re.findall(r'extra\s+(\w+)', text)
        for extra in extras:
            modifiers.append(f'extra {extra}')
        
        return list(set(modifiers))  # Remove duplicates
    
    def _calculate_enhanced_confidence(self, intent: Intent, entities: Dict, text: str) -> float:
        """Calculate enhanced confidence score."""
        confidence = 0.0
        
        # Base confidence for known intent
        if intent != Intent.UNKNOWN:
            confidence += 0.4
        
        # Boost for found items
        if entities['items']:
            max_item_confidence = max(entities['item_confidences'].values()) if entities['item_confidences'] else 0
            confidence += 0.4 * max_item_confidence
        
        # Boost for quantity
        if entities['quantity'] > 0:
            confidence += 0.1
        
        # Boost for modifiers
        if entities['modifiers']:
            confidence += 0.1
        
        # Text length factor (very short or very long text is less reliable)
        word_count = len(text.split())
        if 3 <= word_count <= 15:
            confidence += 0.1
        elif word_count < 3:
            confidence -= 0.1
        
        return min(1.0, max(0.0, confidence))
    
    def _generate_alternatives(self, text: str, menu_items: List[str]) -> List[Dict]:
        """Generate alternative interpretations."""
        alternatives = []
        
        # Try different intent interpretations
        for intent in Intent:
            if intent == Intent.UNKNOWN:
                continue
            
            alt_score = 0
            for pattern in self.intent_patterns.get(intent, []):
                if re.search(pattern, text, re.IGNORECASE):
                    alt_score += 1
            
            if alt_score > 0:
                alternatives.append({
                    'intent': intent,
                    'confidence': min(0.8, alt_score * 0.3),
                    'reason': f'Pattern match for {intent.value}'
                })
        
        return sorted(alternatives, key=lambda x: x['confidence'], reverse=True)[:3]