# this file contains data structure models for orders and order books

import time

from src.data_structures.constants import SIDE_BUY, SIDE_SELL, ORDER_TYPE_LIMIT, ORDER_TYPE_MARKET
from collections import deque


# class for representing a single order
class Order:

    def __init__(
        self,
        order_id: str,
        symbol: str,
        price: int,
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
            raise ValueError("price (in ticks) cannot be negative")
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

# class for represeenting a single price level in the order book
class Limit:

    def __init__(self, price: int):
        if price < 0:
            raise ValueError("price (in ticks) cannot be negative")
        self.price = price
        self.orders: deque[Order] = deque[Order]()
        self.total_volume = 0

    def append(self, new_order: Order) -> None:
        self.orders.append(new_order)
        self.total_volume += new_order.quantity

    # match the quanitity with the orders in FIFO basis
    def match(self, quantity: int) -> int:
        if quantity <= 0:
            return 0

        q_left = quantity
        filled = 0

        # fill the orders until we don't have desired quantity left or order left
        while self.orders and self.orders[0].quantity <= q_left:
            order = self.orders.popleft()
            filled += order.quantity
            q_left -= order.quantity
            self.total_volume -= order.quantity

        # if any remaining quantity and orders, also pop that order
        if self.orders and q_left > 0:
            order = self.orders[0]
            filled += q_left
            order.quantity -= q_left
            self.total_volume -= q_left
            if order.quantity <= 0:
                self.orders.popleft()

        # return the number of quantity filled
        return filled

    def cancel(self, order: Order) -> None:
        self.orders.remove(order)
        self.total_volume -= order.quantity

    # helper for looking if this price level have any orders
    def is_empty(self) -> bool:
        return len(self.orders) == 0