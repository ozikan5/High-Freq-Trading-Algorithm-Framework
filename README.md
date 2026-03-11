# HFT_Algo

A high-frequency trading (HFT) algorithmic trading project with core data structures, matching engine, and extensible strategy framework.

## Project Structure

```
HFT_Algo/
├── src/                    # Source code
│   ├── data_structures/    # Order book, orders, trades
│   ├── engine/             # Matching engine, trading logic
│   ├── strategies/         # Trading strategies
│   └── utils/              # Shared utilities and types
├── config/                 # Configuration
├── tests/                  # Unit and integration tests
├── scripts/                # Runner and simulation scripts
└── data/                   # Market data (gitignored)
```

## Setup

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Running Tests

```bash
# Run all tests with pytest (verbose, show print output)
python -m pytest tests/ -v -s

# Run a specific test
python -m pytest tests/test_order_book.py::test_market_order -v -s

# Run tests matching a pattern
python -m pytest tests/ -v -s -k "fill"

# Alternative: run without pytest
python scripts/run_tests.py
```

## License

MIT
