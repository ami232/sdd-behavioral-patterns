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
        self.cart = cart
        self.category = category
        self.qty = qty
        self.unit_price = unit_price

    def execute(self) -> None:
        self.cart.add_item(self.category, self.qty, self.unit_price)

    def undo(self) -> None:
        self.cart.remove_item(self.category, self.qty)


class RemoveTicketCommand(Command):
    def __init__(self, cart: Cart, category: str, qty: int):
        self.cart = cart
        self.category = category
        self.qty = qty
        self.removed_qty = 0
        self.removed_unit_price = None

    def execute(self) -> None:
        item = self.cart.items().get(self.category)
        self.removed_unit_price = item[1] if item is not None else None
        self.removed_qty = self.cart.remove_item(self.category, self.qty)

    def undo(self) -> None:
        if self.removed_qty > 0 and self.removed_unit_price is not None:
            self.cart.add_item(
                self.category,
                self.removed_qty,
                self.removed_unit_price,
            )


class SetPricingStrategyCommand(Command):
    def __init__(self, cart: Cart, strategy: PricingStrategy):
        self.cart = cart
        self.strategy = strategy
        self.previous_strategy = None

    def execute(self) -> None:
        self.previous_strategy = self.cart.set_pricing_strategy(self.strategy)

    def undo(self) -> None:
        if self.previous_strategy is not None:
            self.cart.set_pricing_strategy(self.previous_strategy)


class CartInvoker:
    def __init__(self):
        self.history = []
        self.redo_stack = []

    def run(self, command: Command) -> None:
        command.execute()
        self.history.append(command)
        self.redo_stack.clear()

    def undo(self, n: int = 1) -> int:
        undone = 0
        for _ in range(n):
            if not self.history:
                break
            command = self.history.pop()
            command.undo()
            self.redo_stack.append(command)
            undone += 1
        return undone

    def redo(self, n: int = 1) -> int:
        redone = 0
        for _ in range(n):
            if not self.redo_stack:
                break
            command = self.redo_stack.pop()
            command.execute()
            self.history.append(command)
            redone += 1
        return redone
