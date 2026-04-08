import pandas as pd

from src.backtester.position import PendingOrder, Position
from src.data_structures.constants import SIDE_BUY, SIDE_SELL
from src.strategy.base import BaseStrategy


class Backtester:
    """
    Replays historical OHLCV bars through a strategy and simulates order fills.

    Fill rules (limit orders, passive side):
      - Buy order fills if bar low  <= order price
      - Sell order fills if bar high >= order price
    """

    def __init__(self, symbol: str, initial_cash: float, strategy: BaseStrategy):
        self.symbol = symbol
        self.position = Position(initial_cash)
        self.strategy = strategy
        self.pending_orders: list[PendingOrder] = []
        self._next_id = 0

    def run(self, bars: pd.DataFrame) -> pd.DataFrame:
        """
        Run the backtest over a DataFrame with columns: open, high, low, close, volume.
        Returns an equity curve DataFrame with columns: timestamp, equity, pnl.
        """
        records = []

        for timestamp, bar in bars.iterrows():
            self._fill_pending(bar)

            new_orders, cancels = self.strategy.on_bar(bar, self.position, list(self.pending_orders))

            # apply cancellations
            cancel_set = set(cancels)
            self.pending_orders = [o for o in self.pending_orders if o.order_id not in cancel_set]

            # register new orders
            for order in new_orders:
                self._next_id += 1
                order.order_id = str(self._next_id)
                self.pending_orders.append(order)

            equity = self.position.total_value(bar["close"])
            records.append({
                "timestamp": timestamp,
                "equity": equity,
                "pnl": equity - self.position.initial_cash,
                "shares": self.position.shares,
                "cash": self.position.cash,
            })

        return pd.DataFrame(records).set_index("timestamp")

    def _fill_pending(self, bar: pd.Series) -> None:
        still_pending = []
        for order in self.pending_orders:
            if order.side == SIDE_BUY and bar["low"] <= order.price:
                self.position.on_fill(order.price, order.quantity, SIDE_BUY)
            elif order.side == SIDE_SELL and bar["high"] >= order.price:
                self.position.on_fill(order.price, order.quantity, SIDE_SELL)
            else:
                still_pending.append(order)
        self.pending_orders = still_pending
