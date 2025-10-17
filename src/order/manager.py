"""
Order manager for tracking and saving customer orders
"""

import json
import yaml
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class OrderItem:
    """Single item in an order."""
    name: str
    quantity: int
    price: float
    modifiers: List[str] = None
    category: str = ""
    
    def __post_init__(self):
        if self.modifiers is None:
            self.modifiers = []
            
    def total_price(self) -> float:
        """Calculate total price for this item."""
        return self.price * self.quantity
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class Order:
    """Complete customer order."""
    order_id: str
    timestamp: str
    items: List[OrderItem]
    customer_name: Optional[str] = None
    table_number: Optional[int] = None
    notes: str = ""
    
    def total_price(self) -> float:
        """Calculate total order price."""
        return sum(item.total_price() for item in self.items)
        
    def item_count(self) -> int:
        """Get total number of items."""
        return sum(item.quantity for item in self.items)
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'order_id': self.order_id,
            'timestamp': self.timestamp,
            'customer_name': self.customer_name,
            'table_number': self.table_number,
            'notes': self.notes,
            'items': [item.to_dict() for item in self.items],
            'total_price': self.total_price(),
            'item_count': self.item_count()
        }


class OrderManager:
    """
    Order manager for tracking and saving customer orders.
    
    Features:
    - Track current order
    - Add/remove items
    - Calculate totals
    - Save orders to file (JSON/YAML)
    - Generate order IDs
    """
    
    def __init__(self, save_directory: str, file_format: str = "json"):
        """
        Initialize the order manager.
        
        Args:
            save_directory: Directory to save orders
            file_format: File format ("json" or "yaml")
        """
        self.save_directory = Path(save_directory)
        self.file_format = file_format.lower()
        self.current_order: Optional[Order] = None
        
        # Create save directory if it doesn't exist
        self.save_directory.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Order manager initialized (save to: {self.save_directory})")
        
    def start_new_order(self, customer_name: Optional[str] = None, 
                       table_number: Optional[int] = None) -> str:
        """
        Start a new order.
        
        Args:
            customer_name: Customer name (optional)
            table_number: Table number (optional)
            
        Returns:
            Order ID
        """
        order_id = self._generate_order_id()
        timestamp = datetime.now().isoformat()
        
        self.current_order = Order(
            order_id=order_id,
            timestamp=timestamp,
            items=[],
            customer_name=customer_name,
            table_number=table_number
        )
        
        logger.info(f"New order started: {order_id}")
        return order_id
        
    def add_item(self, item_name: str, quantity: int, price: float,
                category: str = "", modifiers: List[str] = None) -> bool:
        """
        Add item to current order.
        
        Args:
            item_name: Item name
            quantity: Quantity
            price: Unit price
            category: Item category
            modifiers: List of modifiers
            
        Returns:
            True if successful
        """
        if self.current_order is None:
            logger.error("No active order. Call start_new_order() first.")
            return False
            
        order_item = OrderItem(
            name=item_name,
            quantity=quantity,
            price=price,
            category=category,
            modifiers=modifiers or []
        )
        
        self.current_order.items.append(order_item)
        logger.info(f"Added to order: {quantity}x {item_name} @ ${price:.2f}")
        return True
        
    def remove_item(self, item_name: str) -> bool:
        """
        Remove item from current order by name.
        
        Args:
            item_name: Item name to remove
            
        Returns:
            True if item was removed
        """
        if self.current_order is None:
            logger.error("No active order")
            return False
            
        original_count = len(self.current_order.items)
        self.current_order.items = [
            item for item in self.current_order.items 
            if item.name.lower() != item_name.lower()
        ]
        
        removed = len(self.current_order.items) < original_count
        if removed:
            logger.info(f"Removed from order: {item_name}")
        else:
            logger.warning(f"Item not found in order: {item_name}")
            
        return removed
        
    def clear_order(self) -> None:
        """Clear all items from current order."""
        if self.current_order:
            self.current_order.items.clear()
            logger.info("Order cleared")
            
    def get_current_order(self) -> Optional[Order]:
        """
        Get current order.
        
        Returns:
            Current order or None
        """
        return self.current_order
        
    def get_order_summary(self) -> str:
        """
        Get formatted summary of current order.
        
        Returns:
            Formatted order summary
        """
        if not self.current_order or not self.current_order.items:
            return "No items in order"
            
        lines = [f"Order {self.current_order.order_id}"]
        lines.append("-" * 40)
        
        for item in self.current_order.items:
            item_line = f"{item.quantity}x {item.name} - ${item.total_price():.2f}"
            if item.modifiers:
                item_line += f" ({', '.join(item.modifiers)})"
            lines.append(item_line)
            
        lines.append("-" * 40)
        lines.append(f"Total: ${self.current_order.total_price():.2f}")
        lines.append(f"Items: {self.current_order.item_count()}")
        
        return "\n".join(lines)
        
    def save_order(self, notes: str = "") -> Optional[str]:
        """
        Save current order to file.
        
        Args:
            notes: Additional notes to add to order
            
        Returns:
            Path to saved file, or None if failed
        """
        if not self.current_order:
            logger.error("No active order to save")
            return None
            
        if not self.current_order.items:
            logger.warning("Cannot save empty order")
            return None
            
        # Add notes
        if notes:
            self.current_order.notes = notes
            
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"order_{self.current_order.order_id}_{timestamp}.{self.file_format}"
        filepath = self.save_directory / filename
        
        try:
            # Convert order to dictionary
            order_dict = self.current_order.to_dict()
            
            # Save to file
            with open(filepath, 'w') as f:
                if self.file_format == 'json':
                    json.dump(order_dict, f, indent=2)
                elif self.file_format == 'yaml':
                    yaml.dump(order_dict, f, default_flow_style=False)
                else:
                    logger.error(f"Unsupported file format: {self.file_format}")
                    return None
                    
            logger.info(f"Order saved to: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Failed to save order: {e}")
            return None
            
    def load_order(self, filepath: str) -> Optional[Order]:
        """
        Load order from file.
        
        Args:
            filepath: Path to order file
            
        Returns:
            Loaded Order object, or None if failed
        """
        try:
            with open(filepath, 'r') as f:
                if filepath.endswith('.json'):
                    data = json.load(f)
                elif filepath.endswith('.yaml') or filepath.endswith('.yml'):
                    data = yaml.safe_load(f)
                else:
                    logger.error("Unsupported file format")
                    return None
                    
            # Reconstruct Order object
            items = [OrderItem(**item_data) for item_data in data['items']]
            order = Order(
                order_id=data['order_id'],
                timestamp=data['timestamp'],
                items=items,
                customer_name=data.get('customer_name'),
                table_number=data.get('table_number'),
                notes=data.get('notes', '')
            )
            
            logger.info(f"Order loaded from: {filepath}")
            return order
            
        except Exception as e:
            logger.error(f"Failed to load order: {e}")
            return None
            
    def _generate_order_id(self) -> str:
        """
        Generate unique order ID.
        
        Returns:
            Order ID string
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"ORD-{timestamp}"
        
    def __repr__(self) -> str:
        """String representation."""
        if self.current_order:
            return (f"OrderManager(order={self.current_order.order_id}, "
                   f"items={len(self.current_order.items)})")
        return "OrderManager(no active order)"

