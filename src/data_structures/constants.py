# this file contains all the constants for the data structures

# sides for buying and selling
SIDE_BUY = 0
SIDE_SELL = 1

# order types
ORDER_TYPE_LIMIT = "LIMIT"
ORDER_TYPE_MARKET = "MARKET"

# minimum price increment; price is stored as int in ticks (display_price = price_ticks * TICK_SIZE)
TICK_SIZE = 0.01