import ccxt
import pandas as pd
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trades.log'),
        logging.StreamHandler()
    ]
)

# Initialize exchanges and load markets
binance = ccxt.binance({'enableRateLimit': True})
binance.load_markets()
coinbase = ccxt.coinbaseexchange({'enableRateLimit': True})
coinbase.load_markets()

symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'ADA/USDT', 'XRP/USDT']  # Added more symbols for variety
hypothetical_position_usd = 1000
fee_rate = 0.0001  # Reduced for demo to trigger on small differences; set to 0.0 for even more
total_simulated_profit = 0.0  # Running total of all simulated net profits

def get_prices(exchange, symbol):
    try:
        ticker = exchange.fetch_ticker(symbol)
        bid = ticker['bid']
        ask = ticker['ask']
        logging.info(f"Fetched {symbol} on {exchange.name}: Bid={bid}, Ask={ask}")
        return bid, ask
    except ccxt.NetworkError as e:
        logging.error(f"Network error fetching {symbol} on {exchange.name}: {e}")
        return None, None
    except ccxt.ExchangeError as e:
        logging.error(f"Exchange error fetching {symbol} on {exchange.name}: {e}")
        return None, None
    except Exception as e:
        logging.error(f"Unexpected error fetching {symbol} on {exchange.name}: {e}")
        return None, None

def check_arbitrage(symbol):
    global total_simulated_profit  # Access the global total
    bin_bid, bin_ask = get_prices(binance, symbol)
    cb_symbol = symbol.replace('USDT', 'USD').replace('/', '-')
    cb_bid, cb_ask = get_prices(coinbase, cb_symbol)
    if None in [bin_bid, bin_ask, cb_bid, cb_ask]:
        return
    fee_adjustment = 1 + fee_rate * 2
    if bin_bid > cb_ask * fee_adjustment:
        profit_pct = (bin_bid - cb_ask) / cb_ask - fee_rate * 2
        if profit_pct > 0:
            logging.info(f"Arbitrage detected! Buy {symbol} on Coinbase @ {cb_ask}, Sell on Binance @ {bin_bid}. Est. Profit: {profit_pct:.4%}")
            amount_crypto = hypothetical_position_usd / cb_ask
            gross_profit = amount_crypto * (bin_bid - cb_ask)
            net_profit = gross_profit - (gross_profit * fee_rate * 2)
            logging.info(f"Simulated: Bought {amount_crypto:.6f} {symbol.split('/')[0]} for ${hypothetical_position_usd}. Net Profit: ${net_profit:.2f}")
            total_simulated_profit += net_profit  # Accumulate to total
    elif cb_bid > bin_ask * fee_adjustment:
        profit_pct = (cb_bid - bin_ask) / bin_ask - fee_rate * 2
        if profit_pct > 0:
            logging.info(f"Arbitrage detected! Buy {symbol} on Binance @ {bin_ask}, Sell on Coinbase @ {cb_bid}. Est. Profit: {profit_pct:.4%}")
            amount_crypto = hypothetical_position_usd / bin_ask
            gross_profit = amount_crypto * (cb_bid - bin_ask)
            net_profit = gross_profit - (gross_profit * fee_rate * 2)
            logging.info(f"Simulated: Bought {amount_crypto:.6f} {symbol.split('/')[0]} for ${hypothetical_position_usd}. Net Profit: ${net_profit:.2f}")
            total_simulated_profit += net_profit  # Accumulate to total

if __name__ == "__main__":
    logging.info("Starting arbitrage bot...")
    while True:
        for symbol in symbols:
            check_arbitrage(symbol)
        logging.warning(f"Current Total Simulated Profit: ${total_simulated_profit:.2f}")  # Log total after all symbols
        time.sleep(5)