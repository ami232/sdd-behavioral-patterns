
from abc import ABC, abstractmethod


class PricingStrategy(ABC):
    """
    Strategy interface: turns a cart's subtotal into its final total.
    """

    @abstractmethod
    def price(self, subtotal: float, quantity: int) -> float:
        raise NotImplementedError


class StandardPricing(PricingStrategy):
    """No discount: the total is just the subtotal."""

    def price(self, subtotal: float, quantity: int) -> float:
        # TODO: no discount, return subtotal unchanged.

        return subtotal



class EarlyBirdPricing(PricingStrategy):
    """Flat percentage off the subtotal, for shows still far from sold out."""

    def __init__(self, percent: float):
        # TODO: store `percent`, raising ValueError if it isn't between 0
        # and 100 (inclusive).
        if not 0 <= percent <= 100:
            raise ValueError("Percent must be between 0 and 100.")
        self.percent = percent

    def price(self, subtotal: float, quantity: int) -> float:
        # TODO: apply the percentage discount to `subtotal`. The result must
        # never be negative (clamp at 0.0).
        discount = subtotal * (self.percent / 100)
        final_price = subtotal - discount
        return max(final_price, 0.0)            


class GroupPricing(PricingStrategy):
    """Per-ticket discount once a party reaches a minimum size."""

    def __init__(self, threshold: int, per_ticket_off: float):
        # TODO: store `threshold` and `per_ticket_off`.
        self.threshold = threshold
        self.per_ticket_off = per_ticket_off  

    def price(self, subtotal: float, quantity: int) -> float:
        # TODO: if `quantity` is below `threshold`, return subtotal
        # unchanged. Otherwise subtract `per_ticket_off * quantity` from
        # `subtotal`, clamped at 0.0.
        if quantity < self.threshold:
            return subtotal
        else:
            discount = self.per_ticket_off * quantity
            final_price = subtotal - discount
            return max(final_price, 0.0)