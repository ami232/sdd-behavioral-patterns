
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
        return subtotal


class EarlyBirdPricing(PricingStrategy):
    """Flat percentage off the subtotal, for shows still far from sold out."""

    def __init__(self, percent: float):
        if percent < 0 or percent > 100:
            raise ValueError("Percent must be between 0 and 100")

        self.percent = percent

    def price(self, subtotal: float, quantity: int) -> float:
        discounted_price = subtotal * (1 - self.percent / 100)
        return max(0.0, discounted_price)


class GroupPricing(PricingStrategy):
    """Per-ticket discount once a paprty reaches a minimum size."""

    def __init__(self, threshold: int, per_ticket_off: float):
        self.threshold = threshold
        self.per_ticket_off = per_ticket_off

    def price(self, subtotal: float, quantity: int) -> float:
        if quantity < self.threshold:
            return subtotal
        discounted_price = subtotal - (self.per_ticket_off * quantity)
        return max(0.0, discounted_price)
