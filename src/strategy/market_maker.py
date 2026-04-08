import pandas as pd

from src.backtester.position import PendingOrder, Position
from src.data_structures.constants import SIDE_BUY, SIDE_SELL
from src.strategy.base import BaseStrategy


class MarketMakerStrategy(BaseStrategy):
    """
    Simple market-making strategy.

    On each bar, cancels all resting orders and posts a fresh pair:
      - A bid at  close * (1 - spread_pct)
      - An ask at close * (1 + spread_pct)

    If both fill, we collect the spread as profit. Position limits prevent
    the strategy from accumulating an unbounded directional position.
    """

    def __init__(
        self,
        quantity: int = 10,
        spread_pct: float = 0.01,
        max_position: int = 50,
    ):
        self.quantity = quantity
        self.spread_pct = spread_pct  # 0.01 = 1% on each side of mid
        self.max_position = max_position

    def on_bar(
        self,
        bar: pd.Series,
        position: Position,
        pending_orders: list[PendingOrder],
    ) -> tuple[list[PendingOrder], list[str]]:
        # cancel all resting orders at the start of each bar
        cancels = [o.order_id for o in pending_orders]

        mid = bar["close"]
        bid_price = round(mid * (1 - self.spread_pct), 2)
        ask_price = round(mid * (1 + self.spread_pct), 2)

        new_orders: list[PendingOrder] = []

        # only post a bid if we have room to buy more
        if position.shares < self.max_position:
            new_orders.append(PendingOrder(
                order_id="",    # assigned by the engine
                side=SIDE_BUY,
                price=bid_price,
                quantity=self.quantity,
            ))

        # only post an ask if we have shares to sell
        if position.shares > -self.max_position:
            new_orders.append(PendingOrder(
                order_id="",
                side=SIDE_SELL,
                price=ask_price,
                quantity=self.quantity,
            ))

        return new_orders, cancels
