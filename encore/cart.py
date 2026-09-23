
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
        self._removed = 0
        self._unit_price = 0.0

    def execute(self) -> None:
        items = self._cart.items()
        if self._category in items:
            _, self._unit_price = items[self._category]
        self._removed = self._cart.remove_item(self._category, self._qty)

    def undo(self) -> None:
        if self._removed:
            self._cart.add_item(self._category, self._removed, self._unit_price)


class SetPricingStrategyCommand(Command):
    def __init__(self, cart: Cart, strategy: PricingStrategy):
        self._cart = cart
        self._strategy = strategy
        self._previous = None

    def execute(self) -> None:
        self._previous = self._cart.set_pricing_strategy(self._strategy)

    def undo(self) -> None:
        if self._previous is not None:
            self._cart.set_pricing_strategy(self._previous)


class CartInvoker:
    def __init__(self):
        self._history = []
        self._redo = []

    def run(self, command: Command) -> None:
        command.execute()
        self._history.append(command)
        self._redo.clear()

    def undo(self, n: int = 1) -> int:
        undone = 0
        while undone < n and self._history:
            command = self._history.pop()
            command.undo()
            self._redo.append(command)
            undone += 1
        return undone

    def redo(self, n: int = 1) -> int:
        redone = 0
        while redone < n and self._redo:
            command = self._redo.pop()
            command.execute()
            self._history.append(command)
            redone += 1
        return redone