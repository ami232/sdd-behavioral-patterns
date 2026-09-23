
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
        return max(0.0, subtotal)


class EarlyBirdPricing(PricingStrategy):
    def __init__(self, percent: float):
        if not 0 <= percent <= 100:
            raise ValueError("percent must be between 0 and 100")
        self._percent = percent

    def price(self, subtotal: float, quantity: int) -> float:
        return max(0.0, subtotal * (1 - self._percent / 100))


class GroupPricing(PricingStrategy):
    def __init__(self, threshold: int, per_ticket_off: float):
        self._threshold = threshold
        self._per_ticket_off = per_ticket_off

    def price(self, subtotal: float, quantity: int) -> float:
        if quantity < self._threshold:
            return max(0.0, subtotal)
        return max(0.0, subtotal - self._per_ticket_off * quantity)