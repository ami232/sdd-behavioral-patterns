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
        # No discount, return subtotal unchanged.
        return subtotal


class EarlyBirdPricing(PricingStrategy):
    """Flat percentage off the subtotal, for shows still far from sold out."""

    def __init__(self, percent: float):
        # Validate at construction time, not at pricing time
        if percent < 0 or percent > 100:
            raise ValueError("percent must be between 0 and 100")
        self.percent = percent

    def price(self, subtotal: float, quantity: int) -> float:
        # Apply the percentage discount, clamped at 0.0
        total = subtotal * (1 - self.percent / 100)
        return max(total, 0.0)


class GroupPricing(PricingStrategy):
    """Per-ticket discount once a party reaches a minimum size."""

    def __init__(self, threshold: int, per_ticket_off: float):
        self.threshold = threshold
        self.per_ticket_off = per_ticket_off

    def price(self, subtotal: float, quantity: int) -> float:
        # Below the threshold: no discount at all
        if quantity < self.threshold:
            return subtotal
        # At or above: per-ticket discount, clamped at 0.0
        total = subtotal - self.per_ticket_off * quantity
        return max(total, 0.0)