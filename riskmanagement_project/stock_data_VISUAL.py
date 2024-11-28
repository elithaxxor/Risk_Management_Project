# Import necessary modules and classes
import yfinance as yf
import streamlit as st
import datetime as dt
import altair as alt
from datetime import datetime, timedelta
import pandas as pd
from PIL import Image
import pandas_datareader as web
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from yahoo_fin import stock_info as si
from yahoo_fin import news
import csv
import pickle
import os
import traceback

# Import parent classes
from stock_data import StockData, FinancialDataDownloader
from main import Parameters

class StockVisualizerApp(StockData, FinancialDataDownloader, Parameters):
    def __init__(self):
        super().__init__()
        # Additional initialization if necessary

    def display_header(self):
        """Display the header image and title."""
        image = Image.open('wsb.png')
        st.image(image, use_column_width=True)
        st.write('''
            # Why *Invest* when you could **SPECULATE**!
            [copyleft - all wrongs reserved] - https://github.com/elithaxxor?tab=repositories
            ***  
            ''')

    def additional_data(self, tickerSymbol):
        """Fetch and display additional stock data."""
        st.subheader(f'{tickerSymbol} [1-Year Stock Information]')
        start = dt.datetime.now() - dt.timedelta(days=365)
        end = dt.datetime.now()

        # Fetch data
        df = web.DataReader(tickerSymbol, 'yahoo', start, end)
        df['Pct Change'] = df['Adj Close'].pct_change()
        df['Stock Return'] = (df['Pct Change'] + 1).cumprod()
        df.reset_index(inplace=True)
        st.subheader(f'{tickerSymbol} [Stock Information with PCT Change and Return]')
        st.write(df.head())

        # Fetch additional data
        quote_table = si.get_quote_table(tickerSymbol)
        quote_df = pd.DataFrame.from_dict([quote_table])
        financials = si.get_financials(tickerSymbol)
        financials_df = pd.DataFrame.from_dict([financials])

        st.header(f'[Current Stock] {tickerSymbol} --- {dt.datetime.now()}')
        st.write(quote_df.head())
        st.write(dict(quote_table))

        # Save data to CSV files
        os.makedirs('STOCK_DATA', exist_ok=True)
        df.to_csv(f"STOCK_DATA/{tickerSymbol}_pct_change_{dt.date.today()}.csv", index=False)
        quote_df.to_csv(f"STOCK_DATA/{tickerSymbol}_stock_quotes_{dt.date.today()}.csv", index=False)

        # Display additional stock information
        st.header(f'[{tickerSymbol}] [Equity Info] - Earnings, Stats, Valuation')
        st.write("Next Earnings: ", si.get_next_earnings_date(tickerSymbol))
        st.write("Split Ratio: ", si.get_splits(tickerSymbol))
        st.write("Stats: ", si.get_stats(tickerSymbol))

        # Plotting graphs
        try:
            st.subheader('[Open] [Close] [Pct Change]')
            st.line_chart(df[['Open', 'Close', 'Pct Change']])
        except Exception as e:
            print(f'Exception in Open-Close graph\n {str(e)}, {traceback.format_exc()}')
            pass

        st.subheader(f'[{tickerSymbol}] [Pct Change]')
        st.line_chart(df['Pct Change'])

        st.subheader(f'[{tickerSymbol}] [Stock Return]')
        st.line_chart(df['Stock Return'])

        st.subheader(f'[{tickerSymbol}] [All Data]')
        st.line_chart(df)

        st.header(f'[{tickerSymbol}] [Financials] {dt.datetime.now()}')
        st.write('Financials:', financials)

        # Display news
        st.header(f'[{tickerSymbol}] - News')
        news_list = news.get_yf_rss(tickerSymbol)
        for item in news_list:
            st.write(f"- {item['title']}")

    def graph_display(self, tickerSymbol):
        """Display graphs based on the user input ticker symbol."""
        print('Processing', tickerSymbol)
        stockinfo = StockData()

        tickerData = yf.Ticker(tickerSymbol)
        end_date = dt.datetime.today().strftime('%Y-%m-%d')
        tickerDf = tickerData.history(period='1d', start='2010-05-31', end=end_date)
        tickerDf.to_csv(f"STOCK_DATA/{tickerSymbol}_security_info_{dt.date.today()}.csv", index=False)

        # Download button for CSV
        with open(f"STOCK_DATA/{tickerSymbol}_security_info_{dt.date.today()}.csv", 'rb') as f:
            st.download_button(
                label='Download Stock CSV',
                data=f,
                file_name=f"{tickerSymbol}_security_info_{dt.date.today()}.csv",
                mime='text/csv'
            )

        # Display basic stock info
        st.header(f'{tickerSymbol} [Stock Information]')
        st.write(tickerDf.head())

        # Graphs
        st.subheader(f'{tickerSymbol} [Stock Closing Prices Over Time]')
        st.line_chart(tickerDf['Close'])

        st.header(f'{tickerSymbol} [Volume Over Time]')
        st.line_chart(tickerDf['Volume'])

        st.header(f'{tickerSymbol} [Opening Prices Over Time]')
        st.line_chart(tickerDf['Open'])

        st.header(f'{tickerSymbol} [High Prices Over Time]')
        st.line_chart(tickerDf['High'])

        # Call function for additional data
        self.additional_data(tickerSymbol)

    def run(self):
        """Run the Streamlit app."""
        self.display_header()

        ticker = StockData()
        tickerSymbol = ticker.get_stock_ticker()
        print('Ticker:', tickerSymbol)
        if tickerSymbol:
            self.graph_display(tickerSymbol)


        # Get user input for the stock ticker symbol
        tickerSymbol = st.text_input("Enter the stock ticker symbol", "AAPL")

        if tickerSymbol:
            self.graph_display(tickerSymbol)

# Run the app
if __name__ == "__main__":
    app = StockVisualizerApp()
    app.run()


### scratches
# stock_input01 = ">STOCK INPUT \n "
# stock01 = st.text_area('Text Area', stock_input01, height=25)
# stock01 = stock01.splitlines()
# stock01 = stock01[1:]  # isolate the the 2nd line to retrieve user input
# st.write(''' *** ''')
#
# ## function recursion IF frontend recieves new stock symbol, reload page with new info
# if bool(stock01):
#     graph_display(tickerSymbol)
#     additional_data(tickerSymbol)
#