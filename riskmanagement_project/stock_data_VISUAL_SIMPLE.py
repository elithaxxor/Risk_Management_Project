import yfinance as yf
import streamlit as st
import pandas as pd
import pil
import pandas_datareader as web


image = Image.open('wsb.jpg')
st.write('''
    * Simple webapp to display *opening* and **closing** of stock prices.
    ***  ''')

#get user input for stocks
stock_input = ">STOCK INPUT \n "
stock = st.text_area('Text Area', stock_input, height=25)
stock = stock.splitlinse()
stock = stock[1:] # isolate the the 2nd line to retrieve user input
st.write(''' *** ''')

## display dataframe:
stock_info = {}
st.subheader('Stock Information [DATA FRAME]')
df = pd.DataFrame.from_dict(stock_info, orient=index)
df.reset_index(inPlace=True)
st.write(df)
st.write(''' *** ''')

## display barchart
st.subheader('Bar Chart')
b_chart = alt.Chart(df).mark_bar().encode(x = 'Volume', y = 'Date')
p = pd.properties(width=alt.step(80))
st.write(p)
#braker line
st.write('''***''')

def additional_data(tickerSymbol):
    web.DataReader(self.ticker, f'yahoo', self.start, self.end)


def graph_display(tickerSymbol):
    ''' Takes User Input and displays graphs, accordingly '''
    # establish ticker  symbol and fetch data
    tickerData = yf.Ticker(tickerSymbol)
    tickerDf = tickerData.history(period='1d', start='2010-5-31', end='2020-5-31')
    ## Graphs
    st.header('Closing Prices')
    st.line_chart(tickerDf.Close)
    st.header('Trading Volume')
    st.line_chart(tickerDf.Volume)


ticker = input('Enter The Stock Symbol, ex: GOOG: ')
additional_data(ticker)
graph_display(ticker)