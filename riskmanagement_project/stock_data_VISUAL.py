import yfinance as yf
import streamlit as st
import datetime as dt
import altair as alt
from datetime import datetime, timedelta
import pandas as pd
import PIL
from PIL import Image
import pandas_datareader as web
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from yahoo_fin import stock_info as si
from yahoo_fin import news
from yahoo_fin import options
import csv
import pickle

import traceback


image = Image.open('wsb.png')
st.image(image, use_column_width=True)
st.write('''
    #  Why *Invest* when you could **SPECULATE**! [copyleft - all wrongs reserved] - 
    https://github.com/elithaxxor?tab=repositories
    ***  ''')

## preprocessing
# print(tickerDf.columns)
# tickerDf = tickerDf[['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']]
# print(tickerDf.index)
# tickerDf.dropna(how='all')
# tickerDf['Date'] = tickerDf.index[0]
# tickerDf = tickerDf[['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']]
# tickerDf['Date'] = tickerDf['Date'].map(mdates.date2num)
# tickerDf.reset_index(drop=True)
# # tickerDf.reset_index(inplace=False)
# b_chart = alt.Chart(tickerDf).mark_bar().encode(x=tickerDf['Volume'], y=str(tickerDf['Date']))
# b_chart = b_chart.properties(width=alt.Step(80))
# st.write(b_chart)
#
#

def additional_data(tickerSymbol):
    st.subheader(' [5-DAY] Stock Information [DATA FRAME]')
    start = dt.datetime.now() - dt.timedelta(days=365)
    end = dt.datetime.now()

    df = web.DataReader(tickerSymbol, f'yahoo', start, end)
    df['Pct Change'] = df['Adj Close'].pct_change()
    df['Stock Return'] = (df['Pct Change'] + 1).cumprod()

   # st.sidebar.header('User Selections')
    #selected_year = st.sidebar.selectbox('Year', list(reversed(range(2022-1990))))

    #df = df[['Open', 'High', 'Low', 'Close']]
    #df['Date'] = df['Date'].map(mdates.date2num)


    df.reset_index(inplace=True)
    st.subheader(' [5-DAY] Stock Information with PCT change and Return.')
    st.write(df.head())
    print(df.head())

    ## more info (quote table)
    quote_table = si.get_quote_table(tickerSymbol)
    quote_df = pd.DataFrame.from_dict([quote_table])
    financials = si.get_financials(tickerSymbol)
    financials_df = pd.DataFrame.from_dict([financials])
    st.header(f'[Current Stock] {tickerSymbol}---{dt.datetime.now()}]')
    st.write(quote_df.head())
    st.write(dict(quote_table))

    valuation = si.get_stats_valuation(tickerSymbol)
    splits = si.get_splits(tickerSymbol)
    next_earnings = si.get_next_earnings_date(tickerSymbol)
    stat = si.get_stats(tickerSymbol)

    # save csv and let user download (BUTTONS)
    #try:
    df.to_csv(f"pct change + {tickerSymbol} + {dt.date.today()}.csv")  # Write df Object to .CSV
    quote_df.to_csv( f"Stock_Quotes + {tickerSymbol} + {dt.date.today()}.csv")

    # save locations
    saved_df1 = f"pct change + {tickerSymbol} + {dt.date.today()}.csv"
    saved_df2 = f"Stock_Quotes + {tickerSymbol} + {dt.date.today()}.csv"
    table_save_loc = f"quote_table + {tickerSymbol} + {dt.date.today()}.csv"
    financials_loc = f"financials  + {tickerSymbol} + {dt.date.today()}.csv"
    stats_loc =  f"Stock Stats + {tickerSymbol} + {dt.date.today()}.csv"
    splits_loc = f"Stock splits + {tickerSymbol} + {dt.date.today()}.csv"
    valuation_loc = f"Valuation + {tickerSymbol} + {dt.date.today()}.csv"

    try:
        table_colums = []
        financial_columns = []
        with open(table_save_loc, 'w') as csvfile:
            writer = csv.DictWriter(fieldnames=table_colums)
            writer.writeheader()
            for data in table_save_loc:
                writer.writerow(data)

        with open(financials_loc, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=financial_columns)
            writer.writeheader()
            for data in table_save_loc:
                writer.writerow(data)
    except IOError:
        print("I/O error"); pass
    except Exception as e:
        print(f'Exception in Dictionary -- csv writer. \, {str(e)} \n {traceback.format_exc()}')
        pass

    try:
        ## context manager / download-button
        with open(saved_df1, 'rb') as f:
            st.download_button(label='Download Stock Csv',data=f, file_name=saved_df1, on_click=True)
        with open(saved_df2, 'rb') as f2:
            st.download_button(label='Stock Quote Info',data=f2, file_name=saved_df2, on_click=True)

        # write dict to file / download button


        with open(table_save_loc, 'rb') as f4:
            table_save = pickle.dumps(quote_table)
            st.download_button(label='Financials', data=f4, file_name=table_save_loc, on_click=True)

        with open(financials_loc, 'rb') as f5:
            financials = pickle.dumps(financials)
            st.download_button(label='Financial Docs', data=f5, file_name=financials_loc, on_click=True)

    except Exception as e:
        print(f'Data-File Writing \n {str(e)}, {traceback.format_exc()}')
        pass

    print(df.head())
    print(quote_df.head())

    ## earnings, split ratio, stats, valuation
    st.header(f'[{tickerSymbol}] [Equity Info]- **Earnings, Stats, Valuation ') #volume
    st.write("Next Earnings:\n ", si.get_next_earnings_date(tickerSymbol),
             "Split Ratio:\n ", si.get_splits(tickerSymbol),
             "Stats\n", si.get_stats(tickerSymbol))
             #"Valuation\n", si.get_stats_valuation(tickerSymbol))


    try:
        st.subheader('[Open] [Close] [Ask] [Pct Change]')
        st.bar_chart(df['Open'], df['Close'], df['Pct Change'], float(quote_df['Avg. Volume']))
        st.line_chart(df['Open'], df['Close'], quote_df['1y Target Est'], df['Pct Change'])
    except Exception as e:
        print(f'Exception in Open- graph\n {str(e)}, {traceback.format_exc()}')
        pass

    st.subheader(f'[{tickerSymbol}] [Pct Change] [{(df["Pct Change"].count())} Values] ') #volume
    st.line_chart(df['Pct Change'])

    st.subheader(f'[{tickerSymbol}] [Stock Return] [{(df["Stock Return"].count())}] [Values] ') #stock return (df[stock_return]) above
    st.line_chart(df['Stock Return'])
    st.subheader(f'[{tickerSymbol}] [ALL TOGETHER] [{(df["Volume"].count())} Values]') # all days values together.
    st.line_chart(df)

    print(financials_df.head())
    print(type(financials_df))
    st.header(f'[{tickerSymbol}] [Financials] {dt.datetime.now()}]')
    st.write('Financials\n', financials)
    try:
        st.write(financials_df.head())
    except:
        pass


    try:
        moving_averages = [150, 200]
        for ma in moving_averages:
            df['SMA_' + str(ma)] = round(df['Adj Close'].rolling(window=ma).mean())
            quote_df['SMA_' + str(ma)] = round(df['Adj Close'].rolling(window=ma).mean())
            latest_price = df['Adj Close'][-1]
            latest_price1 = quote_df['Adj Close'][-1]
            print(latest_price)
            pe_ratio = float(si.get_quote_table(tickerSymbol)['PE Ratio (TTM)'])
    except Exception as e:
        print(f'Exception in Open- graph\n {str(e)}, {traceback.format_exc()}')
        pass

    ## display ticker news
    st.header(f'[{tickerSymbol}]--News')
    st.text(news.get_yf_rss(tickerSymbol))

def graph_display(tickerSymbol):
    ''' Takes User Input and displays graphs, accordingly '''

    print('Processsing, ', tickerSymbol)
    tickerData = yf.Ticker(tickerSymbol)
    tickerDf = tickerData.history(period='1d', start='2010-5-31', end='2020-5-31')
    tickerDf.to_csv(f"Security_Info + {tickerSymbol} + {dt.date.today()}.csv")  # Write df Object to .CSV

    saved_df=f"Security_Info + {tickerSymbol} + {dt.date.today()}.csv"
    with open(saved_df,'rb') as f:
        st.download_button(label='Download Stock Csv',data=f,  file_name=f"Security Info + {tickerSymbol} + {dt.date.today()}.csv", on_click=True)


    # display basic stock info
    st.header(f'{tickerSymbol} [Stock Information] ')
    print(tickerDf.head())
    st.write(tickerDf.head())

    ## Graphs
    st.subheader(f'{tickerSymbol} [Stock Information -- 5-Year] ')
    st.line_chart(tickerDf)
    st.subheader(f'[{tickerSymbol}] [Stock Information -- 2 -Year] ')
    st.line_chart(tickerDf.head(2))
    st.header(f'[{tickerSymbol}] [Volume] [{(tickerDf["Volume"].count())} Values]') #volume
    st.line_chart(tickerDf.Volume)
    st.header(f'[{tickerSymbol}] [Opening Prices] [{(tickerDf["Open"].count())}] Values') #open
    st.line_chart(tickerDf.Open)
    st.header(f'[{tickerSymbol}] [Closing Prices] [{(tickerDf["Close"].count())} Values ]') #close
    st.line_chart(tickerDf.Close)
    st.header(f'[{tickerSymbol}] [Daily High] [{(tickerDf["High"].count())} Values] ') #volume
    st.line_chart(tickerDf.Volume)

    # call function for added info (financial docs, and Df that require preprocessing
    # additional_data(tickerSymbol) ## call function for addiotnal data



def main():
   # ticker = input('Enter The Stock Symbol, ex: GOOG: ')
    while True:
        stock_input = ">STOCK INPUT \n "
        print(stock_input)
        print(type(stock_input))
        stock = st.text_area('Text Area', stock_input, height=25)
        stock = stock.splitlines()
        stock = stock[1:]  # isolate the the 2nd line on list to retrieve user input
        stock = str(stock)
        stock = stock[1:-1]
        stock = stock[1:-1]
        st.write(''' *** ''')
        print(f'User Entered {stock} \n {type(stock)}')
        if stock != []:
            graph_display(stock)
            additional_data(stock)

main()




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