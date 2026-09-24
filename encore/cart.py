
from abc import ABC, abstractmethod
from typing import Dict, Tuple

from .pricing import PricingStrategy, StandardPricing


class Cart:
    """
    Receiver: holds ticket line items and the active pricing strategy.
    """

    def __init__(self, pricing_strategy: PricingStrategy = None):
        self._items: Dict[str, Tuple[int, float]] = {}
        self._pricing_strategy = pricing_strategy or StandardPricing()

    def add_item(self, category: str, qty: int, unit_price: float) -> None:
        current_qty, _ = self._items.get(category, (0, unit_price))
        self._items[category] = (current_qty + qty, unit_price)

    def remove_item(self, category: str, qty: int) -> int:
        if category not in self._items:
            return 0
        current_qty, unit_price = self._items[category]
        removed = min(qty, current_qty)
        remaining = current_qty - removed
        if remaining > 0:
            self._items[category] = (remaining, unit_price)
        else:
            del self._items[category]
        return removed

    def set_pricing_strategy(self, strategy: PricingStrategy) -> PricingStrategy:
        previous = self._pricing_strategy
        self._pricing_strategy = strategy
        return previous

    def items(self) -> Dict[str, Tuple[int, float]]:
        return dict(self._items)

    def quantity(self) -> int:
        return sum(qty for qty, _ in self._items.values())

    def subtotal(self) -> float:
        return sum(qty * unit_price for qty, unit_price in self._items.values())

    def total(self) -> float:
        return self._pricing_strategy.price(self.subtotal(), self.quantity())


class Command(ABC):
    @abstractmethod
    def execute(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def undo(self) -> None:
        raise NotImplementedError


class AddTicketCommand(Command):
    def __init__(self, cart: Cart, category: str, qty: int, unit_price: float):
        self._cart = cart
        self._category = category
        self._qty = qty
        self._unit_price = unit_price
 
    def execute(self) -> None:
        self._cart.add_item(self._category, self._qty, self._unit_price)
 
    def undo(self) -> None:
        self._cart.remove_item(self._category, self._qty)


class RemoveTicketCommand(Command):
    def __init__(self, cart: Cart, category: str, qty: int):
        self._cart = cart
        self._category = category
        self._qty = qty
        self._removed_qty = 0
        self._unit_price = 0.0
     
    def execute(self) -> None:
        line = self._cart.items().get(self._category)
        if line is not None:
            self._unit_price = line[1]
        self._removed_qty = self._cart.remove_item(self._category, self._qty)
     
    def undo(self) -> None:
        if self._removed_qty > 0:
            self._cart.add_item(self._category, self._removed_qty, self._unit_price)
    
    


class SetPricingStrategyCommand(Command):
    def __init__(self, cart: Cart, strategy: PricingStrategy):
        self._cart = cart
        self._strategy = strategy
        self._previous = None
 
    def execute(self) -> None:
        # set_pricing_strategy already returns the old one
        self._previous = self._cart.set_pricing_strategy(self._strategy)
 
    def undo(self) -> None:
        self._cart.set_pricing_strategy(self._previous)


class CartInvoker:
    def __init__(self):
        self._history = []
        self._redo_stack = []
 
    def run(self, command: Command) -> None:
        command.execute()
        self._history.append(command)
        self._redo_stack.clear()
 
    def undo(self, n: int = 1) -> int:
        count = 0
        while count < n and self._history:
            command = self._history.pop()
            command.undo()
            self._redo_stack.append(command)
            count += 1
        return count
 
    def redo(self, n: int = 1) -> int:
        count = 0
        while count < n and self._redo_stack:
            command = self._redo_stack.pop()
            command.execute()
            self._history.append(command)
            count += 1
        return count