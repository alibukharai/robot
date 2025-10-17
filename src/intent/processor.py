"""
Intent processor for understanding customer orders
Extracts intents and entities from spoken text
"""

import re
import logging
from typing import Dict, List, Optional, Any
from enum import Enum

logger = logging.getLogger(__name__)


class Intent(Enum):
    """Customer intent types."""
    ORDER = "order"  # Customer wants to order something
    SUGGEST = "suggest"  # Customer wants suggestions
    CONFIRM = "confirm"  # Customer confirms order
    CANCEL = "cancel"  # Customer cancels/changes order
    INFO = "info"  # Customer asks about an item
    DONE = "done"  # Customer is done ordering
    UNKNOWN = "unknown"  # Unknown intent


class IntentProcessor:
    """
    Intent processor for understanding customer orders.
    
    Features:
    - Extract customer intents (order, suggest, confirm, etc.)
    - Identify food/drink items mentioned
    - Extract quantities
    - Simple rule-based NLU (no ML required)
    """
    
    def __init__(self):
        """Initialize the intent processor."""
        self.intent_patterns = self._build_patterns()
        logger.info("Intent processor initialized")
        
    def _build_patterns(self) -> Dict[Intent, List[str]]:
        """
        Build regex patterns for intent recognition.
        
        Returns:
            Dictionary mapping intents to regex patterns
        """
        return {
            Intent.ORDER: [
                r'\b(i want|i would like|i\'ll have|give me|can i have|may i have)\b',
                r'\b(order|get|take)\b',
                r'\b(one|two|three|four|five|a|an)\s+\w+',
            ],
            Intent.SUGGEST: [
                r'\b(suggest|recommend|what do you suggest|what\'s good)\b',
                r'\b(popular|best|favorite)\b',
                r'\b(what should i|help me choose)\b',
            ],
            Intent.CONFIRM: [
                r'\b(yes|yeah|yep|sure|okay|ok|correct|right|that\'s right)\b',
                r'\b(confirm|confirmed)\b',
            ],
            Intent.CANCEL: [
                r'\b(no|nope|cancel|nevermind|never mind|change|remove)\b',
                r'\b(wrong|mistake|different)\b',
            ],
            Intent.INFO: [
                r'\b(what is|what\'s|tell me about|info|information)\b',
                r'\b(how much|price|cost)\b',
                r'\b(contain|ingredient|allerg)\b',
            ],
            Intent.DONE: [
                r'\b(that\'s all|that\'s it|done|finished|complete|nothing else)\b',
                r'\b(ready|checkout|pay)\b',
            ],
        }
        
    def process(self, text: str, menu_items: List[str]) -> Dict[str, Any]:
        """
        Process spoken text to extract intent and entities.
        
        Args:
            text: Spoken text from ASR
            menu_items: List of known menu item names
            
        Returns:
            Dictionary with intent, entities, and confidence
        """
        if not text:
            return {
                'intent': Intent.UNKNOWN,
                'entities': {},
                'confidence': 0.0,
                'raw_text': text
            }
            
        text_lower = text.lower().strip()
        
        # Detect intent
        intent = self._detect_intent(text_lower)
        
        # Extract entities
        entities = {
            'items': self._extract_items(text_lower, menu_items),
            'quantity': self._extract_quantity(text_lower),
            'modifiers': self._extract_modifiers(text_lower)
        }
        
        # Calculate confidence (simple heuristic)
        confidence = self._calculate_confidence(intent, entities)
        
        result = {
            'intent': intent,
            'entities': entities,
            'confidence': confidence,
            'raw_text': text
        }
        
        logger.info(f"Intent: {intent.value}, Items: {entities['items']}, "
                   f"Confidence: {confidence:.2f}")
        
        return result
        
    def _detect_intent(self, text: str) -> Intent:
        """
        Detect the primary intent from text.
        
        Args:
            text: Lowercase text
            
        Returns:
            Detected intent
        """
        # Check each intent pattern
        intent_scores = {}
        
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    score += 1
            intent_scores[intent] = score
            
        # Get intent with highest score
        if max(intent_scores.values()) > 0:
            detected_intent = max(intent_scores, key=intent_scores.get)
            logger.debug(f"Detected intent: {detected_intent.value}")
            return detected_intent
            
        # Default to ORDER if we can't determine intent
        return Intent.UNKNOWN
        
    def _extract_items(self, text: str, menu_items: List[str]) -> List[str]:
        """
        Extract menu items mentioned in text.
        
        Args:
            text: Lowercase text
            menu_items: List of known menu item names
            
        Returns:
            List of found menu items
        """
        found_items = []
        
        for item in menu_items:
            item_lower = item.lower()
            
            # Check for exact match
            if item_lower in text:
                found_items.append(item)
                continue
                
            # Check for word match (all words present)
            item_words = item_lower.split()
            if len(item_words) > 1:
                if all(word in text for word in item_words):
                    found_items.append(item)
                    
        return found_items
        
    def _extract_quantity(self, text: str) -> int:
        """
        Extract quantity from text.
        
        Args:
            text: Lowercase text
            
        Returns:
            Quantity (default: 1)
        """
        # Number words to digits
        number_words = {
            'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
            'a': 1, 'an': 1
        }
        
        # Check for number words
        for word, num in number_words.items():
            if re.search(rf'\b{word}\b', text):
                return num
                
        # Check for digits
        digit_match = re.search(r'\b(\d+)\b', text)
        if digit_match:
            return int(digit_match.group(1))
            
        # Default quantity
        return 1
        
    def _extract_modifiers(self, text: str) -> List[str]:
        """
        Extract modifiers (e.g., "large", "no ice", "extra cheese").
        
        Args:
            text: Lowercase text
            
        Returns:
            List of modifiers
        """
        modifiers = []
        
        # Size modifiers
        sizes = ['small', 'medium', 'large', 'extra large']
        for size in sizes:
            if size in text:
                modifiers.append(size)
                
        # Common modifiers
        common_modifiers = [
            'no ice', 'extra', 'with', 'without', 'hot', 'cold', 'iced'
        ]
        for mod in common_modifiers:
            if mod in text:
                modifiers.append(mod)
                
        return modifiers
        
    def _calculate_confidence(self, intent: Intent, entities: Dict) -> float:
        """
        Calculate confidence score for the interpretation.
        
        Args:
            intent: Detected intent
            entities: Extracted entities
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        confidence = 0.0
        
        # Base confidence for known intent
        if intent != Intent.UNKNOWN:
            confidence += 0.5
            
        # Boost for found items
        if entities['items']:
            confidence += 0.3
            
        # Boost for quantity
        if entities['quantity'] > 0:
            confidence += 0.1
            
        # Boost for modifiers
        if entities['modifiers']:
            confidence += 0.1
            
        return min(1.0, confidence)
        
    def format_order_summary(self, entities: Dict) -> str:
        """
        Format extracted entities into a readable order summary.
        
        Args:
            entities: Extracted entities
            
        Returns:
            Formatted summary string
        """
        items = entities.get('items', [])
        quantity = entities.get('quantity', 1)
        modifiers = entities.get('modifiers', [])
        
        if not items:
            return "No items detected"
            
        summary_parts = []
        
        # Format quantity
        if quantity > 1:
            summary_parts.append(f"{quantity}x")
            
        # Format items
        summary_parts.append(", ".join(items))
        
        # Format modifiers
        if modifiers:
            summary_parts.append(f"({', '.join(modifiers)})")
            
        return " ".join(summary_parts)

