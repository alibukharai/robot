"""
Menu manager for loading and searching menu items
"""

import yaml
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class MenuManager:
    """
    Menu manager for handling restaurant menu items.
    
    Features:
    - Load menu from YAML file
    - Search items by name
    - Get items by category
    - Get popular items
    - Fuzzy matching for item names
    """
    
    def __init__(self, menu_file: str):
        """
        Initialize the menu manager.
        
        Args:
            menu_file: Path to menu YAML file
        """
        self.menu_file = menu_file
        self.menu_data: Dict[str, Any] = {}
        self.all_items: List[Dict[str, Any]] = []
        
        self._load_menu()
        
    def _load_menu(self) -> None:
        """Load menu from YAML file."""
        try:
            menu_path = Path(self.menu_file)
            if not menu_path.exists():
                logger.error(f"Menu file not found: {self.menu_file}")
                raise FileNotFoundError(f"Menu file not found: {self.menu_file}")
                
            with open(menu_path, 'r') as f:
                self.menu_data = yaml.safe_load(f)
                
            # Build flat list of all items with category info
            self.all_items = []
            for category in self.menu_data.get('categories', []):
                category_name = category.get('name', 'Unknown')
                for item in category.get('items', []):
                    item_with_category = item.copy()
                    item_with_category['category'] = category_name
                    self.all_items.append(item_with_category)
                    
            logger.info(f"Menu loaded: {len(self.all_items)} items from "
                       f"{len(self.menu_data.get('categories', []))} categories")
            
        except Exception as e:
            logger.error(f"Failed to load menu: {e}")
            raise
            
    def get_all_items(self) -> List[Dict[str, Any]]:
        """
        Get all menu items.
        
        Returns:
            List of all menu items with their details
        """
        return self.all_items.copy()
        
    def get_categories(self) -> List[str]:
        """
        Get all category names.
        
        Returns:
            List of category names
        """
        return [cat['name'] for cat in self.menu_data.get('categories', [])]
        
    def get_items_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get all items in a specific category.
        
        Args:
            category: Category name
            
        Returns:
            List of items in the category
        """
        return [item for item in self.all_items 
                if item.get('category', '').lower() == category.lower()]
                
    def search_item(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Search for an item by name (case-insensitive, partial match).
        
        Args:
            query: Search query (item name or partial name)
            
        Returns:
            Best matching item, or None if not found
        """
        query_lower = query.lower().strip()
        
        if not query_lower:
            return None
            
        # First, try exact match
        for item in self.all_items:
            if item['name'].lower() == query_lower:
                logger.info(f"Exact match found: {item['name']}")
                return item
                
        # Then, try partial match (contains)
        for item in self.all_items:
            if query_lower in item['name'].lower():
                logger.info(f"Partial match found: {item['name']}")
                return item
                
        # Try matching individual words
        query_words = query_lower.split()
        for item in self.all_items:
            item_name_lower = item['name'].lower()
            if all(word in item_name_lower for word in query_words):
                logger.info(f"Word match found: {item['name']}")
                return item
                
        logger.debug(f"No match found for: '{query}'")
        return None
        
    def search_items(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for multiple items matching the query.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of matching items
        """
        query_lower = query.lower().strip()
        
        if not query_lower:
            return []
            
        results = []
        
        # Exact matches first
        for item in self.all_items:
            if item['name'].lower() == query_lower:
                results.append(item)
                
        # Then partial matches
        for item in self.all_items:
            if query_lower in item['name'].lower() and item not in results:
                results.append(item)
                if len(results) >= max_results:
                    break
                    
        return results[:max_results]
        
    def get_popular_items(self, max_items: int = 3) -> List[Dict[str, Any]]:
        """
        Get popular menu items.
        
        Args:
            max_items: Maximum number of items to return
            
        Returns:
            List of popular items
        """
        popular = [item for item in self.all_items if item.get('popular', False)]
        return popular[:max_items]
        
    def get_items_by_dietary(self, dietary_filter: str) -> List[Dict[str, Any]]:
        """
        Get items matching a dietary requirement.
        
        Args:
            dietary_filter: Dietary requirement (e.g., "vegetarian", "vegan", "gluten-free")
            
        Returns:
            List of matching items
        """
        return [item for item in self.all_items 
                if dietary_filter.lower() in [d.lower() for d in item.get('dietary', [])]]
                
    def get_item_info(self, item: Dict[str, Any]) -> str:
        """
        Get formatted information about an item.
        
        Args:
            item: Menu item dictionary
            
        Returns:
            Formatted string with item details
        """
        name = item.get('name', 'Unknown')
        description = item.get('description', '')
        price = item.get('price', 0)
        category = item.get('category', 'Unknown')
        
        info = f"{name} - ${price:.2f}"
        if description:
            info += f"\n  {description}"
        info += f"\n  Category: {category}"
        
        dietary = item.get('dietary', [])
        if dietary:
            info += f"\n  Dietary: {', '.join(dietary)}"
            
        return info
        
    def reload(self) -> None:
        """Reload the menu from file."""
        logger.info("Reloading menu...")
        self._load_menu()
        
    def __len__(self) -> int:
        """Return number of items in menu."""
        return len(self.all_items)
        
    def __repr__(self) -> str:
        """String representation."""
        return (f"MenuManager(items={len(self.all_items)}, "
                f"categories={len(self.get_categories())})")

