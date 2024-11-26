import datetime as dt
from datetime import time, datetime, timedelta
from mplfinance.original_flavor import candlestick_ohlc
import pandas_datareader as web
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


class Plot_Candlestick:
    import datetime as dt
    from datetime import time, datetime, timedelta
    from mplfinance.original_flavor import candlestick_ohlc
    import pandas_datareader as web
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates

    def __init__(self, ticker): #
        super(Plot_Candlestick, self).__init__()

        self.timedelta = timedelta(days=365, hours=0, minutes=0) # first create the object, work with it later.
        self.now = dt.datetime.now()
        self.start = (self.now) - self.timedelta
        self.end = dt.datetime.now()
        self.ticker = ticker
        self.data = web.DataReader(self.ticker, f'yahoo', self.start, self.end)
        print(self.data)

        ## pre-processing
        self.data = self.data[['Open', 'High', 'Low', 'Close']]
        self.data.reset_index(inplace=True)
        self.data['Date'] = self.data['Date'].map(mdates.date2num)

    @classmethod
    def from_input(cls):
        return cls(ticker = input('Enter Stock: '))

    def visualization(self):
        print("today is: " + str(self.datetime.now()))
        print(f"Historical Data will span from [{self.now} (today) to: {self.now - self.timedelta} (A year ago)")

        # Preprocessing
        ax = plt.subplot()
        ax.grid(True)
        ax.set_axisbelow(True)
        ax.set_title('{} Share Price'.format(self.ticker), color='white')
        ax.figure.canvas.set_window_title('Basic Window visualizer')
        ax.set_facecolor('black')
        ax.figure.set_facecolor('#121212')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.xaxis_date()  # reformat the date so its readable

        ## display chart
        candlestick_ohlc(ax, self.data.values, width=0.5, colorup='#00ff00')
        plt.show()


def main():
    ticker = Plot_Candlestick.from_input()
    ticker.visualization()

#if '__name__' == '__main__':
main()


import datetime as dt
from datetime import time, datetime, timedelta
from mplfinance.original_flavor import candlestick_ohlc
import pandas_datareader as web
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


class Plot_Candlestick:
    import datetime as dt
    from datetime import time, datetime, timedelta
    from mplfinance.original_flavor import candlestick_ohlc
    import pandas_datareader as web
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates

    def __init__(self, ticker): #
        super(Plot_Candlestick, self).__init__()

        self.timedelta = timedelta(days=365, hours=0, minutes=0) # first create the object, work with it later.
        self.now = dt.datetime.now()
        self.start = (self.now) - self.timedelta
        self.end = dt.datetime.now()
        self.ticker = ticker
        self.data = web.DataReader(self.ticker, f'yahoo', self.start, self.end)
        print(self.data)

        ## pre-processing
        self.data = self.data[['Open', 'High', 'Low', 'Close']]
        self.data.reset_index(inplace=True)
        self.data['Date'] = self.data['Date'].map(mdates.date2num)

    @classmethod
    def from_input(cls):
        return cls(ticker = input('Enter Stock: '))

    def visualization(self):
        print("today is: " + str(self.datetime.now()))
        print(f"Historical Data will span from [{str(self.now())}] (today) to: {str(self.now()) - self.timedelta(days=365)} (A year ago)")

        # Preprocessing
        ax = plt.subplot()
        ax.grid(True)
        ax.set_axisbelow(True)
        ax.set_title('{} Share Price'.format(self.ticker), color='white')
        ax.figure.canvas.set_window_title('Basic Window visualizer')
        ax.set_facecolor('black')
        ax.figure.set_facecolor('#121212')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.xaxis_date()  # reformat the date so its readable

        ## display chart
        candlestick_ohlc(ax, data.values, width=0.5, colorup='#00ff00')
        plt.show()


def main():
    ticker = Plot_Candlestick.from_input()

#if '__name__' == '__main__':
main()




#
#
#
# timedelta(days=365, hours=0, minutes=0)
# print("today is: " + str(datetime.now()))
# print(f"Historical Data will span from [{str(self.dt.now)}] (today) to:  {str(datetime.now() - timedelta(days=365))} (A year ago)")
# start = str(datetime.now() - timedelta(days=365))
# end = dt.datetime.now()
#
# ticker = 'AAPL'
# data = web.DataReader(ticker, 'yahoo', start, end)
# print(type(data))
# print(data)



#
#
#
# timedelta(days=365, hours=0, minutes=0)
# print("today is: " + str(datetime.now()))
# print(f"Historical Data will span from [{str(self.dt.now)}] (today) to:  {str(datetime.now() - timedelta(days=365))} (A year ago)")
# start = str(datetime.now() - timedelta(days=365))
# end = dt.datetime.now()
#
# ticker = 'AAPL'
# data = web.DataReader(ticker, 'yahoo', start, end)
# print(type(data))
# print(data)
