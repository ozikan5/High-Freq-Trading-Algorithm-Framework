from dataclasses import dataclass

from src.data_structures.constants import SIDE_BUY, SIDE_SELL


@dataclass
class PendingOrder:
    order_id: str
    side: int        # SIDE_BUY or SIDE_SELL
    price: float
    quantity: int


# A simple class for a position, given initial cash, that tracks num of shares 
# and money spent to return pnl
class Position:
    def __init__(self, initial_cash: float):
        self.initial_cash = initial_cash
        self.cash = float(initial_cash)
        self.shares = 0

    def on_fill(self, price: float, quantity: int, side: int) -> None:
        if side == SIDE_BUY:
            self.cash -= price * quantity
            self.shares += quantity
        elif side == SIDE_SELL:
            self.cash += price * quantity
            self.shares -= quantity

    def total_value(self, current_price: float) -> float:
        return self.cash + self.shares * current_price

    def pnl(self, current_price: float) -> float:
        return self.total_value(current_price) - self.initial_cash

    def __repr__(self) -> str:
        return f"Position(cash={self.cash:.2f}, shares={self.shares})"
