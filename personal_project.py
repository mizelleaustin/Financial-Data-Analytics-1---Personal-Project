import pandas as pd
import numpy as np
import pygame
import random
import time

# --- Generate Realistic Stock Data ---
def generate_realistic_stock_data(num_stocks=5, num_days=100):
    """
    Generate realistic stock prices using a random walk with drift and volatility.
    """
    stocks = []
    for i in range(num_stocks):
        # Set initial price and parameters
        dates = pd.date_range('2023-01-01', periods=num_days, freq='D')
        initial_price = random.uniform(50, 150)  # Starting price between $50 and $150
        drift = 0.0005  # Average daily drift (0.05% per day)
        volatility = 0.02  # Daily volatility (2%)

        prices = [initial_price]
        for _ in range(1, num_days):
            # Random walk with drift and volatility
            shock = np.random.normal(drift, volatility)
            new_price = prices[-1] * (1 + shock)
            new_price = max(new_price, 1)  # Ensure price doesn't go below $1
            prices.append(new_price)

        stock_data = pd.DataFrame({
            "Date": dates,
            "Price": prices,
            "Ticker": f"Stock {i+1}"
        })
        stocks.append(stock_data)
    
    return pd.concat(stocks, ignore_index=True)

# --- Portfolio Class ---
class Portfolio:
    def __init__(self, initial_balance=10000):
        self.balance = initial_balance
        self.stocks = {}  # Holds stock ticker and quantity owned
        self.transaction_history = []

    def buy_stock(self, ticker, price, quantity):
        total_cost = price * quantity
        if total_cost <= self.balance:
            self.balance -= total_cost
            self.stocks[ticker] = self.stocks.get(ticker, 0) + quantity
            self.transaction_history.append((ticker, "Buy", quantity, price))
            return f"Bought {quantity} shares of {ticker} at ${price:.2f}"
        return "Not enough balance to complete the transaction."

    def sell_stock(self, ticker, price, quantity):
        if ticker in self.stocks and self.stocks[ticker] >= quantity:
            self.stocks[ticker] -= quantity
            self.balance += price * quantity
            self.transaction_history.append((ticker, "Sell", quantity, price))
            return f"Sold {quantity} shares of {ticker} at ${price:.2f}"
        return "Not enough shares to sell."

    def summary(self):
        stock_summary = ", ".join([f"{ticker}: {qty} shares" for ticker, qty in self.stocks.items() if qty > 0])
        return f"Balance: ${self.balance:.2f} | {stock_summary if stock_summary else 'No stocks owned'}"

# --- Update Stock Prices ---
def simulate_prices(stock_data, current_day):
    """
    Simulate stock prices for a given day.
    """
    return stock_data[stock_data['Date'] == stock_data['Date'].unique()[current_day]]

# --- PyGame Setup ---
pygame.init()
screen = pygame.display.set_mode((1000, 600))
pygame.display.set_caption("Stock Market Simulation Game")
font = pygame.font.Font(None, 32)
clock = pygame.time.Clock()

# --- Game Loop ---
def game_loop():
    running = True
    portfolio = Portfolio()
    stock_data = generate_realistic_stock_data(num_stocks=5, num_days=100)
    stock_tickers = stock_data['Ticker'].unique()
    current_day = 0
    message = ""
    selected_stock = 0  # Index of currently selected stock

    while running:
        screen.fill((200, 220, 255))  # Light blue background

        # Simulate Stock Prices
        stock_today = simulate_prices(stock_data, current_day % 100)

        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b:  # Buy selected stock
                    ticker = stock_tickers[selected_stock]
                    price = stock_today[stock_today['Ticker'] == ticker]['Price'].iloc[0]
                    message = portfolio.buy_stock(ticker, price, 1)
                elif event.key == pygame.K_s:  # Sell selected stock
                    ticker = stock_tickers[selected_stock]
                    price = stock_today[stock_today['Ticker'] == ticker]['Price'].iloc[0]
                    message = portfolio.sell_stock(ticker, price, 1)
                elif event.key == pygame.K_RIGHT:  # Switch to next stock
                    selected_stock = (selected_stock + 1) % len(stock_tickers)
                elif event.key == pygame.K_LEFT:  # Switch to previous stock
                    selected_stock = (selected_stock - 1) % len(stock_tickers)

        # Display Portfolio Summary
        portfolio_text = portfolio.summary()
        screen.blit(font.render(portfolio_text, True, (0, 0, 0)), (10, 10))

        # Display Stock Prices
        y_offset = 50
        for idx, ticker in enumerate(stock_tickers):
            price = stock_today[stock_today['Ticker'] == ticker]['Price'].iloc[0]
            color = (0, 128, 0) if idx == selected_stock else (0, 0, 0)
            text = f"{ticker}: ${price:.2f}"
            screen.blit(font.render(text, True, color), (10, y_offset))
            y_offset += 30

        # Display Instructions
        instructions = "Press B to Buy, S to Sell | Use Left/Right to Switch Stocks"
        screen.blit(font.render(instructions, True, (0, 0, 0)), (10, 500))

        # Display Message
        if message:
            screen.blit(font.render(message, True, (255, 0, 0)), (10, 550))

        # Update Display
        pygame.display.flip()
        clock.tick(1)  # Simulate 1 second per day
        current_day += 1

    pygame.quit()

# --- Start the Game ---
if __name__ == "__main__":
    game_loop()
