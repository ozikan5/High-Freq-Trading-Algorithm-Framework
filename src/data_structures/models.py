# this file contains data structure models for orders and order books

import time

from src.data_structures.constants import SIDE_BUY, SIDE_SELL, ORDER_TYPE_LIMIT, ORDER_TYPE_MARKET


# class for represeting a single order
class Order:

    def __init__(
        self,
        order_id: str,
        symbol: str,
        price: float,
        side: int,
        quantity: int,
        order_type: str,
        # timestamp is for testing purposes, since requesting users to input timestamps is not realistic
        # and can lead to time manipulation, we use time.time() to get the current timestamp
        timestamp: float | None = None,
    ):

        # routine checks for validating orders
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        if price < 0:
            raise ValueError("price cannot be negative")
        if side not in (SIDE_BUY, SIDE_SELL):
            raise ValueError(f"side must be {SIDE_BUY} (buy) or {SIDE_SELL} (sell)")
        if order_type not in (ORDER_TYPE_LIMIT, ORDER_TYPE_MARKET):
            raise ValueError(f"order_type must be {ORDER_TYPE_LIMIT} or {ORDER_TYPE_MARKET}")

        self.order_id = order_id
        self.symbol = symbol
        self.price = price
        self.side = side
        self.quantity = quantity
        self.order_type = order_type
        self.timestamp = timestamp if timestamp is not None else time.time()