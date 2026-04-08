from abc import ABC, abstractmethod

import pandas as pd

from src.backtester.position import PendingOrder, Position


class BaseStrategy(ABC):
    """
    Base class for all strategies.

    on_bar() is called once per bar (e.g. once per day for daily data).
    It receives the current bar, your position, and any orders still waiting to fill.
    It returns a list of new orders to place and a list of order IDs to cancel.
    """

    @abstractmethod
    def on_bar(
        self,
        bar: pd.Series,
        position: Position,
        pending_orders: list[PendingOrder],
    ) -> tuple[list[PendingOrder], list[str]]:
        """
        Returns:
            new_orders  — list of PendingOrder to submit (order_id will be assigned by engine)
            cancels     — list of order_id strings to cancel
        """
        ...
