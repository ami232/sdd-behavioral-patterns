
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
        # TODO: store cart, category, qty and unit_price for later use.
        self.cart = cart
        self.category = category
        self.qty = qty
        self.unit_price = unit_price

    def execute(self) -> None:
        # TODO: add `qty` tickets of `category` at `unit_price` to the cart.
        self.cart.add_item(self.category, self.qty, self.unit_price)

    def undo(self) -> None:
        # TODO: remove exactly the tickets this command added.
        self.cart.remove_item(self.category, self.qty)


class RemoveTicketCommand(Command):
    def __init__(self, cart: Cart, category: str, qty: int):
        # TODO: store cart, category and qty. You'll also need somewhere to
        # remember how many tickets were *actually* removed, and at what
        # price, once execute() runs.
        self.cart = cart
        self.category = category
        self.qty = qty
        self.removed_qty = 0
        self.unit_price = 0.0

    def execute(self) -> None:
        # TODO: remove up to `qty` tickets of `category` from the cart
        # (cart.remove_item returns how many were actually removed), and
        # remember that count plus the unit price so undo() can restore them.
        # Save the price before removal can delete the entire category.
        self.unit_price = self.cart.items().get(self.category, (0, 0))[1]
        self.removed_qty = self.cart.remove_item(self.category, self.qty)

    def undo(self) -> None:
        # TODO: add back exactly the quantity that was actually removed, at
        # the price it was removed at. Do nothing if nothing was removed.
        if self.removed_qty > 0:
            self.cart.add_item(self.category, self.removed_qty, self.unit_price)


class SetPricingStrategyCommand(Command):
    def __init__(self, cart: Cart, strategy: PricingStrategy):
        # TODO: store cart and the new strategy. You'll need somewhere to
        # keep the previous strategy once execute() runs.
        self.cart = cart
        self.strategy = strategy

    def execute(self) -> None:
        # TODO: swap the cart's pricing strategy, remembering the previous one.
        self.previous_strategy = self.cart.set_pricing_strategy(self.strategy)

    def undo(self) -> None:
        # TODO: restore the previous pricing strategy.
        self.cart.set_pricing_strategy(self.previous_strategy)


class CartInvoker:
    def __init__(self):
        # TODO: set up a history stack and a redo stack.
        self.history = []
        self.redo_stack = []

    def run(self, command: Command) -> None:
        # TODO: execute `command`, push it onto the history, and clear the
        # redo stack (a fresh command invalidates any pending redo).
        command.execute()
        self.history.append(command)
        self.redo_stack.clear()

    def undo(self, n: int = 1) -> int:
        # TODO: undo up to `n` commands from the history, moving each onto
        # the redo stack. Return how many were actually undone (fewer than
        # `n` once history runs out).
        undone_count = 0
        for _ in range(n):
            if not self.history:
                break
            command = self.history.pop()
            command.undo()
            self.redo_stack.append(command)
            undone_count += 1
        return undone_count

    def redo(self, n: int = 1) -> int:
        # TODO: redo up to `n` commands from the redo stack, moving each back
        # onto the history. Return how many were actually redone.
        redone_count = 0
        for _ in range(n):
            if not self.redo_stack:
                break
            command = self.redo_stack.pop()
            command.execute()
            self.history.append(command)
            redone_count += 1
        return redone_count
