# stock_visualizer_app.py

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import os
from bs4 import BeautifulSoup as bs
import requests
import traceback
import matplotlib.dates as mdates
from mplfinance.original_flavor import candlestick_ohlc


from main import Parameters
from stock_data import StockData, FinancialDataDownloader

class StockVisualizerApp(Parameters, StockData, FinancialDataDownloader):
    def __init__(self):
        super().__init__()
        self.Parameters = Parameters
        self.StockData = StockData()
        self.ticker = StockData.get_stock_ticker()
        self.FinancialDataDownloader = FinancialDataDownloader

        print(f"StockVisualizerApp initialized.\, {self.ticker}, {StockData.get_stock_ticker}")
    def run(self):
        st.title("Stock Visualizer App")
        st.write("Visualize stock data and financial information.")
        ticker = ""
        while (self.StockData.get_stock_ticker == None or self.StockData.get_stock_end_date == None
               or self.StockData.max_drop == None or self.StockData.moving_averages == None):

            ticker = st.text_input("Enter the stock ticker symbol (e.g., AAPL):", value="AAPL")

            end_date_input = st.date_input("Enter the end date:", value=datetime.date.today())
            max_drop_input = st.number_input("Enter the maximum amount of points for a significant drop (e.g., 1000):",
                                             value=1000, step=1)
            moving_averages_input = st.text_input("Enter the moving average periods (e.g., 20,50,200):",
                                                  value="20,50,200")

            if self.StockData.get_stock_ticker:
                st.success(f"Stock ticker symbol set to '{self.StockData.get_stock_ticker}'.")


            if ticker :
                # Process inputs
                stripped_ticker = ticker[1:] if ticker.startswith('^') else ticker

                end_date = end_date_input
                max_drop = max_drop_input
                moving_averages = [int(ma.strip()) for ma in moving_averages_input.split(',') if ma.strip().isdigit()]
                start_date = end_date - datetime.timedelta(days=365)

                # Fetch data
                df = yf.download(ticker, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
                if df.empty:
                    st.error(f"No data found for ticker '{ticker}' between {start_date} and {end_date}.")
                    return
                else:
                    st.success(f"Data fetched for ticker '{ticker}' between {start_date} and {end_date}.")

                # Prepare data
                df['Date'] = df.index
                df['Price'] = df['Close']

                # Calculate indicators
                self.calculate_indicators(df, max_drop, moving_averages)

                # Display data
                st.subheader(f"{ticker} Price Data")
                st.dataframe(df.tail(10))

                # Plot data
                self.plot_data(df, ticker, start_date, end_date, max_drop, moving_averages)
                self.plot_candlestick(df, ticker, moving_averages)

                # Fetch and display additional data
                self.fetch_additional_data(ticker)

                # Scrape and display key statistics
                self.scrape_key_statistics(stripped_ticker)

            if self.StockData.get_stock_ticker:
                # Process inputs
                stripped_ticker = self.StockData.get_stock_ticker[1:] if self.StockData.get_stock_ticker.startswith('^') else self.StockData.get_stock_ticker

                end_date = self.StockData.get_stock_end_date
                max_drop = self.StockData.max_drop
                moving_averages = [int(ma.strip()) for ma in self.StockData.moving_averages.split(',') if ma.strip().isdigit()]
                start_date = end_date - datetime.timedelta(days=365)

                # Fetch data
                df = yf.download(ticker, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
                if df.empty:
                    st.error(f"No data found for ticker '{ticker}' between {start_date} and {end_date}.")
                    return
                else:
                    st.success(f"Data fetched for ticker '{ticker}' between {start_date} and {end_date}.")

                # Prepare data
                df['Date'] = df.index
                df['Price'] = df['Close']

                # Calculate indicators
                self.calculate_indicators(df, max_drop, moving_averages)

                # Display data
                st.subheader(f"{ticker} Price Data")
                st.dataframe(df.tail(10))

                # Plot data
                self.plot_data(df, ticker, start_date, end_date, max_drop, moving_averages)
                self.plot_candlestick(df, ticker, moving_averages)

                # Fetch and display additional data
                self.fetch_additional_data(ticker)

                # Scrape and display key statistics
                self.scrape_key_statistics(stripped_ticker)

    def calculate_indicators(self, df, max_drop, moving_averages):
        """Calculate peaks, drawdowns, significant drops, moving averages."""
        # Ensure 'Close' column is present
        if 'Close' not in df.columns:
            if 'Adj Close' in df.columns:
                df['Close'] = df['Adj Close']
            else:
                st.error("Neither 'Close' nor 'Adj Close' columns are present.")
                return

        # Calculate the cumulative maximum to identify peaks
        df['Peak'] = df['Close'].cummax()

        # Calculate drawdowns from the peaks
        df['Drawdown'] = df['Peak'] - df['Close']

        # Identify periods where the drawdown is equal to or exceeds the max drop
        df['Significant Drop'] = df['Drawdown'] >= max_drop

        # Calculate moving averages
        for ma in moving_averages:
            df[f'MA_{ma}'] = df['Close'].rolling(window=ma).mean()

    def plot_data(self, df, ticker, start_date, end_date, max_drop, moving_averages):
        """Plot the data."""
        plt.figure(figsize=(14, 7))
        plt.plot(df['Date'], df['Close'], label=f'{ticker} Price', color='blue')
        # Plot moving averages
        for ma in moving_averages:
            if f'MA_{ma}' in df.columns:
                plt.plot(df['Date'], df[f'MA_{ma}'], label=f'MA {ma}')

        # Highlight significant drops
        plt.fill_between(df['Date'], df['Close'], where=df['Significant Drop'], color='red', alpha=0.5,
                         label=f'Drop ≥ {max_drop} points')

        # Fetch and highlight earnings dates
        ticker_obj = yf.Ticker(ticker)
        earnings_dates = ticker_obj.calendar.T
        if not earnings_dates.empty:
            earnings_date = earnings_dates.index[0]
            plt.axvline(x=earnings_date, color='green', linestyle='--', alpha=0.7, label='Next Earnings Date')

        # Customize the plot
        plt.title(f'{ticker} Price from {start_date.date()} to {end_date.date()}')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()

        st.subheader(f"{ticker} Price Chart")
        st.pyplot(plt)

    def plot_candlestick(self, df, ticker, moving_averages):
        """Plot candlestick chart with moving averages."""
        if df.empty:
            st.error("[!] No data to plot.")
            return

        # Prepare data
        df['Date_Num'] = mdates.date2num(df.index)
        ohlc_data = df[['Date_Num', 'Open', 'High', 'Low', 'Close']].copy()
        ohlc_data = ohlc_data.dropna()

        fig, ax = plt.subplots(figsize=(14, 7))

        # Plot candlestick chart
        candlestick_ohlc(ax, ohlc_data.values, width=0.6, colorup='green', colordown='red', alpha=0.8)

        # Plot moving averages
        for ma in moving_averages:
            if f'MA_{ma}' in df.columns:
                ax.plot(df['Date_Num'], df[f'MA_{ma}'], label=f'MA {ma}')

        # Format x-axis dates
        ax.xaxis_date()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.xticks(rotation=45)

        # Add grid, legend, and labels
        ax.grid(True)
        ax.legend()
        plt.title(f"{ticker} Candlestick Chart")
        plt.xlabel("Date")
        plt.ylabel("Price")

        plt.tight_layout()

        st.subheader(f"{ticker} Candlestick Chart")
        st.pyplot(fig)

    def fetch_additional_data(self, ticker):
        """Fetch and display additional data."""
        st.subheader(f"{ticker} Additional Data")

        # Create ticker object
        ticker_obj = yf.Ticker(ticker)

        # Fetch financials
        financials = ticker_obj.financials
        if not financials.empty:
            st.write("**Financials:**")
            st.dataframe(financials)
        else:
            st.write("No financials data available.")

        # Fetch balance sheet
        balance_sheet = ticker_obj.balance_sheet
        if not balance_sheet.empty:
            st.write("**Balance Sheet:**")
            st.dataframe(balance_sheet)
        else:
            st.write("No balance sheet data available.")

        # Fetch cashflow
        cashflow = ticker_obj.cashflow
        if not cashflow.empty:
            st.write("**Cash Flow:**")
            st.dataframe(cashflow)
        else:
            st.write("No cash flow data available.")

        # Fetch earnings
        earnings = ticker_obj.earnings
        if not earnings.empty:
            st.write("**Earnings:**")
            st.dataframe(earnings)
        else:
            st.write("No earnings data available.")

        # Fetch sustainability
        sustainability = ticker_obj.sustainability
        if sustainability is not None and not sustainability.empty:
            st.write("**Sustainability:**")
            st.dataframe(sustainability)
        else:
            st.write("No sustainability data available.")

    def scrape_key_statistics(self, stripped_ticker):
        """Scrape key statistics from Yahoo Finance and display."""
        st.subheader(f"Key Statistics for {stripped_ticker}")
        try:
            url = f"https://finance.yahoo.com/quote/{stripped_ticker}/key-statistics?p={stripped_ticker}"
            html_data = requests.get(url).text
            soup = bs(html_data, 'lxml')
            tables = soup.find_all('table')
            df_list = pd.read_html(str(html_data))
            # Combine all the DataFrames in the list
            df_combined = pd.concat(df_list, ignore_index=True)
            st.dataframe(df_combined)
        except Exception as e:
            st.error(f"An error occurred while scraping key statistics: {e}")
            traceback.print_exc()

# Run the app
if __name__ == "__main__":
    app = StockVisualizerApp()
    app.run()