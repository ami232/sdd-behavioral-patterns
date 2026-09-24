
from abc import ABC, abstractmethod


class PricingStrategy(ABC):
    """
    Strategy interface: turns a cart's subtotal into its final total.
    """

    @abstractmethod
    def price(self, subtotal: float, quantity: int) -> float:
        raise NotImplementedError


class StandardPricing(PricingStrategy):
    def price(self, subtotal: float, quantity: int) -> float:
        return subtotal


class EarlyBirdPricing(PricingStrategy):
    def __init__(self, percent: float):
        if not (0 <= percent <= 100):
            raise ValueError("percent must be between 0 and 100")
        self.percent = percent

    def price(self, subtotal: float, quantity: int) -> float:
        discounted = subtotal * (1 - self.percent / 100)
        return max(discounted, 0.0)


class GroupPricing(PricingStrategy):
    """Per-ticket discount once a party reaches a minimum size."""

    def __init__(self, threshold: int, per_ticket_off: float):
        self.threshold = threshold
        self.per_ticket_off = per_ticket_off

    def price(self, subtotal: float, quantity: int) -> float:
        if quantity < self.threshold:
            return subtotal
        discounted = subtotal - (self.per_ticket_off * quantity)
        return max(discounted, 0.0)

