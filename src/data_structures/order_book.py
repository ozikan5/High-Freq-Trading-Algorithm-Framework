import bisect

from src.data_structures.constants import ORDER_TYPE_LIMIT, ORDER_TYPE_MARKET, SIDE_BUY, SIDE_SELL
from src.data_structures.models import Limit, Order


# main order book data structure for a symbol
class OrderBook:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.bids: list[int] = []  # prices for bids will be descending
        self.asks: list[int] = []  # prices for asks will be ascending
        self.order_map: dict[str, tuple[Order, Limit]] = {}  # this will map the order_id to an order, limit tuple
        self.price_map: dict[int, Limit] = {}  # this will map any price to its following limit structure

    def process_market_order(self, order : Order) -> bool:
        # routine validation checks
        if order.symbol != self.symbol:
            return False
        if order.order_type != ORDER_TYPE_MARKET:
            return False
        if order.quantity <= 0:
            return False
        if str(order.order_id) in self.order_map:
            return False
        
        quantity = order.quantity

        raise NotImplementedError("Market orders are not implemented yet")

    
    # this is for processing limit orders
    def process_limit_order(self, order: Order) -> bool:
   
        # routine validation checks
        if order.symbol != self.symbol:
            return False
        if order.order_type != ORDER_TYPE_LIMIT:
            return False
        if order.quantity <= 0:
            return False
        if str(order.order_id) in self.order_map:
            return False

        quantity = order.quantity
        # call helper
        self._match_and_rest(order, quantity)
        return True

    # helper for matching both buy and sell orders with limits
    def _match_and_rest(self, order: Order, quantity: int) -> None:
        # create lambad cond functions to crate the while loop 
        if order.side == SIDE_BUY:
            opposite_side = self.asks
            can_cross = lambda: self.asks and order.price >= self.asks[0]
        else:
            opposite_side = self.bids
            can_cross = lambda: self.bids and order.price <= -self.bids[0]

        # match orders with the needs until its not possible, delete the limit objects if they are empty and clear out the dicts
        while can_cross() and quantity > 0:
            if order.side == SIDE_BUY:
                best_price = opposite_side[0]
            else:
                best_price = -opposite_side[0]

            best_limit = self.price_map[best_price]

            filled, fully_filled = best_limit.match(quantity)
            quantity -= filled

            for filled_order in fully_filled:
                self.order_map.pop(str(filled_order.order_id), None)

            if best_limit.is_empty():
                self._remove_level(opposite_side, best_price, order.side == SIDE_SELL)

        if quantity > 0:
            order.quantity = quantity
            self._add_to_book(order)

    # add orders to the book
    def _add_to_book(self, order: Order) -> None:
        price = order.price
        # if this is the first price with this value, create a limit object and add it to the class lists too
        if price not in self.price_map:
            self.price_map[price] = Limit(price)
            if order.side == SIDE_BUY:
                # store bid prices as negative so we can insert in sorted order
                bisect.insort(self.bids, -price)
            else:
                # use bisect to add a new value into the ordered list in O(n)
                bisect.insort(self.asks, price)

        self.price_map[price].append(order)
        self.order_map[str(order.order_id)] = (order, self.price_map[price])

    # removes given price level from the given side
    def _remove_level(self, side: list[int], price: int, is_bid: bool) -> None:
        value_to_remove = -price if is_bid else price
        side.remove(value_to_remove)
        del self.price_map[price]

    # get the best bid from the lists
    def best_bid(self) -> int | None:
        return -self.bids[0] if self.bids else None

    # get the best ask from the lists
    def best_ask(self) -> int | None:
        return self.asks[0] if self.asks else None

    # spread is the difference between the best ask and the best bid
    def spread(self) -> int | None:
        bb, ba = self.best_bid(), self.best_ask()
        return (ba - bb) if (bb is not None and ba is not None) else None

    def cancel_order(self, order_id: str) -> bool:
        raise NotImplementedError("Cancel order is not implemented yet")
