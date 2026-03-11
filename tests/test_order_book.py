"""Tests for OrderBook and related data structures.

Run with: python -m pytest tests/ -v -s
"""

from src.data_structures import (
    Order,
    OrderBook,
    Limit,
    Trade,
    ORDER_TYPE_LIMIT,
    ORDER_TYPE_MARKET,
    SIDE_BUY,
    SIDE_SELL,
)


def test_add_sell_order():
    print("\n  → Add sell order, check best_ask and best_bid")
    book = OrderBook("AAPL")
    o = Order("1", "AAPL", 1010, SIDE_SELL, 10, ORDER_TYPE_LIMIT)
    assert book.process_limit_order(o)[0] is True
    assert book.best_ask() == 1010
    assert book.best_bid() is None


def test_buy_crosses_ask():
    print("\n  → Buy order crosses existing ask")
    book = OrderBook("AAPL")
    book.process_limit_order(Order("1", "AAPL", 1010, SIDE_SELL, 10, ORDER_TYPE_LIMIT))
    book.process_limit_order(Order("2", "AAPL", 1010, SIDE_BUY, 5, ORDER_TYPE_LIMIT))
    assert book.best_ask() == 1010


def test_resting_bid():
    print("\n  → Add resting bid below spread")
    book = OrderBook("AAPL")
    book.process_limit_order(Order("1", "AAPL", 1010, SIDE_SELL, 10, ORDER_TYPE_LIMIT))
    book.process_limit_order(Order("2", "AAPL", 1005, SIDE_BUY, 20, ORDER_TYPE_LIMIT))
    assert book.best_bid() == 1005


def test_sell_crosses_bid():
    print("\n  → Sell order crosses existing bid")
    book = OrderBook("AAPL")
    book.process_limit_order(Order("1", "AAPL", 1010, SIDE_SELL, 10, ORDER_TYPE_LIMIT))
    book.process_limit_order(Order("2", "AAPL", 1005, SIDE_BUY, 20, ORDER_TYPE_LIMIT))
    book.process_limit_order(Order("3", "AAPL", 1005, SIDE_SELL, 10, ORDER_TYPE_LIMIT))
    assert book.spread() == 5


def test_spread():
    print("\n  → Check bid-ask spread")
    book = OrderBook("AAPL")
    book.process_limit_order(Order("1", "AAPL", 1010, SIDE_SELL, 10, ORDER_TYPE_LIMIT))
    book.process_limit_order(Order("2", "AAPL", 1005, SIDE_BUY, 20, ORDER_TYPE_LIMIT))
    assert book.spread() == 5


def test_multi_level_book():
    print("\n  → Multi-level book (multiple bid/ask levels)")
    book = OrderBook("AAPL")
    book.process_limit_order(Order("s1", "AAPL", 1010, SIDE_SELL, 5, ORDER_TYPE_LIMIT))
    book.process_limit_order(Order("s2", "AAPL", 1011, SIDE_SELL, 10, ORDER_TYPE_LIMIT))
    book.process_limit_order(Order("b1", "AAPL", 1000, SIDE_BUY, 5, ORDER_TYPE_LIMIT))
    book.process_limit_order(Order("b2", "AAPL", 999, SIDE_BUY, 10, ORDER_TYPE_LIMIT))
    assert book.best_bid() == 1000
    assert book.best_ask() == 1010
    assert book.spread() == 10


def test_buy_sweeps_multiple_levels():
    print("\n  → Buy sweeps multiple ask levels")
    book = OrderBook("AAPL")
    book.process_limit_order(Order("s1", "AAPL", 1010, SIDE_SELL, 3, ORDER_TYPE_LIMIT))
    book.process_limit_order(Order("s2", "AAPL", 1011, SIDE_SELL, 5, ORDER_TYPE_LIMIT))
    book.process_limit_order(Order("b1", "AAPL", 1015, SIDE_BUY, 6, ORDER_TYPE_LIMIT))
    assert book.best_ask() == 1011
    assert book.best_bid() is None


def test_reject_duplicate():
    print("\n  → Reject duplicate order_id")
    book = OrderBook("AAPL")
    o = Order("1", "AAPL", 1010, SIDE_BUY, 5, ORDER_TYPE_LIMIT)
    assert book.process_limit_order(o)[0] is True
    assert book.process_limit_order(o)[0] is False


def test_reject_wrong_symbol():
    print("\n  → Reject order with wrong symbol")
    book = OrderBook("AAPL")
    assert book.process_limit_order(Order("1", "GOOG", 1010, SIDE_BUY, 5, ORDER_TYPE_LIMIT))[0] is False


def test_market_order():
    print("\n  → Market order matches liquidity, no resting")
    book = OrderBook("AAPL")
    book.process_limit_order(Order("s1", "AAPL", 1010, SIDE_SELL, 10, ORDER_TYPE_LIMIT))
    # Market buy (price ignored, use 0 as placeholder)
    success, fills = book.process_market_order(
        Order("m1", "AAPL", 0, SIDE_BUY, 5, ORDER_TYPE_MARKET)
    )
    assert success is True
    assert len(fills) == 1
    assert fills[0].price == 1010
    assert fills[0].quantity == 5
    assert book.best_ask() == 1010  # 5 left
    assert book.best_bid() is None  # no resting


def test_fills_returned():
    print("\n  → Fills returned with price, quantity, maker IDs")
    book = OrderBook("AAPL")
    book.process_limit_order(Order("s1", "AAPL", 1010, SIDE_SELL, 5, ORDER_TYPE_LIMIT))
    success, fills = book.process_limit_order(Order("b1", "AAPL", 1010, SIDE_BUY, 5, ORDER_TYPE_LIMIT))
    assert success is True
    assert len(fills) == 1
    assert fills[0].price == 1010
    assert fills[0].quantity == 5
    assert fills[0].taker_order_id == "b1"
    assert "s1" in fills[0].maker_order_ids
    assert fills[0].timestamp > 0


def test_partial_fill_records_maker():
    print("\n  → Partial fill records maker order_id in Trade")
    book = OrderBook("AAPL")
    book.process_limit_order(Order("s1", "AAPL", 1010, SIDE_SELL, 10, ORDER_TYPE_LIMIT))
    success, fills = book.process_limit_order(Order("b1", "AAPL", 1010, SIDE_BUY, 5, ORDER_TYPE_LIMIT))
    assert success is True
    assert len(fills) == 1
    assert fills[0].quantity == 5
    assert "s1" in fills[0].maker_order_ids  # s1 partially filled (10 -> 5)


def test_limit_partial_fill():
    print("\n  → Limit.match partial fill returns partial_maker")
    lim = Limit(1000)
    o = Order("x", "AAPL", 1000, SIDE_BUY, 10, ORDER_TYPE_LIMIT)
    lim.append(o)
    filled, full, partial_maker = lim.match(5)
    assert filled == 5
    assert len(full) == 0
    assert partial_maker is o
    assert o.quantity == 5
