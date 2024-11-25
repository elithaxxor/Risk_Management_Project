import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import datetime
from bs4 import BeautifulSoup as bs
import requests

import datetime

class StockData:
    def __init__(self):
        """Initialize the class and prompt the user for input."""
        self.ticker = input("Enter the ticker symbol (e.g., ^GSPC for S&P 500): ")
        self.end_date_input = input("Enter the end date in YYYY-MM-DD format (or leave blank for today): ")
        self.max_drop_input = input("Enter the maximum amount of points for a significant drop (e.g., 1000): ")
        self.moving_averages_input = input("Enter the moving average periods (e.g., 20,50,200): ")
        self.stripped_ticker = self.ticker[1:] if self.ticker.startswith('^') else self.ticker

        self.end_date = self._parse_end_date(self.end_date_input)
        self.max_drop = self._parse_max_drop(self.max_drop_input)
        self.moving_averages = self._parse_moving_averages(self.moving_averages_input)

    def _parse_end_date(self, end_date_input):
        """Parse the end date input and return a datetime object."""
        if end_date_input.strip() == '':
            return datetime.datetime.today()
        try:
            return datetime.datetime.strptime(end_date_input, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Invalid date format. Please enter the date in YYYY-MM-DD format.")

    def _parse_max_drop(self, max_drop_input):
        """Parse the max drop input and return it as a float."""
        try:
            return float(max_drop_input)
        except ValueError:
            raise ValueError("Invalid input for maximum drop amount. Please enter a numerical value.")

    def _parse_moving_averages(self, moving_averages_input):
        """Parse the moving average input and return a list of integers."""
        if not moving_averages_input.strip():
            return []
        moving_averages = []
        for ma in moving_averages_input.split(','):
            try:
                moving_averages.append(int(ma.strip()))
            except ValueError:
                raise ValueError(f"Invalid moving average period: {ma}. Please enter integer values.")
        return moving_averages

    def to_dataframe(self):
        """Convert the user inputs into a DataFrame-friendly dictionary."""
        return {
            "Ticker": [self.ticker],
            "Stripped Ticker": [self.stripped_ticker],
            "End Date": [self.end_date],
            "Max Drop": [self.max_drop],
            "Moving Averages": [', '.join(map(str, self.moving_averages))],
        }

    def __str__(self):
        """Return a string representation of the data."""
        return (
            f"Ticker: {self.ticker}\n"
            f"Stripped Ticker: {self.stripped_ticker}\n"
            f"End Date: {self.end_date.date()}\n"
            f"Max Drop: {self.max_drop}\n"
            f"Moving Averages: {', '.join(map(str, self.moving_averages)) or 'None'}"
        )



def save_data_to_csv(df, ticker, description):
    try:
        csv_filename = f"{ticker}_{description}.csv"
        df.to_csv(csv_filename, index=False)
        print(f"Data saved to {csv_filename}")

    except Exception as e:
        print(f"[!] Error Occured Saving Data to CSV: {e}")

# Validate and parse the end date
if end_date_input.strip() == '':
    end_date = datetime.datetime.today()
else:
    try:
        end_date = datetime.datetime.strptime(end_date_input, '%Y-%m-%d')
    except ValueError:
        print("Invalid date format. Please enter the date in YYYY-MM-DD format.")
        exit()

# Parse the maximum drop value
try:
    max_drop = float(max_drop_input)
except ValueError:
    print("Invalid input for maximum drop amount. Please enter a numerical value.")
    exit()

# Parse moving average periods
moving_averages = []
if moving_averages_input.strip() != '':
    moving_averages_input_list = moving_averages_input.split(',')
    for ma in moving_averages_input_list:
        try:
            ma_period = int(ma.strip())
            moving_averages.append(ma_period)
        except ValueError:
            print(f"Invalid moving average period: {ma}. Please enter integer values.")
            exit()
else:
    print("No moving averages entered. Proceeding without moving averages.")

# Define the start date (one year before the end date)
start_date = end_date - datetime.timedelta(days=365)

# Fetch historical data
try:
    df = yf.download(ticker, start=start_date, end=end_date, timeout=20)

    if df.empty:
        print(f"[-] No data found for ticker '{ticker}' between {start_date.date()} and {end_date.date()}.")

    print(df.head())
    print(df.tail())



    # Fetch historical market data
    historical_data = df.history(start=start_date, end=end_date)  # data for the last year
    print("Historical Data:")
    print(historical_data)

    # Fetch basic financials
    financials = df.financials
    print("\nFinancials:")
    print(financials)

    # Fetch stock actions like dividends and splits
    actions = df.actions
    print("\nStock Actions:")
    print(actions)

    # Get Stock Info
    info = df.info
    print("\nStock Info:")
    print(info)


    # Reset index to make 'Date' a column
    df.reset_index(inplace=True)

    # Calculate the cumulative maximum to identify peaks
    df['Peak'] = df['Close'].cummax()

    # Calculate drawdowns from the peaks
    df['Drawdown'] = df['Peak'] - df['Close']

    # Identify periods where the drawdown is equal to or exceeds the max drop
    df['Significant Drop'] = df['Drawdown'] >= max_drop

    # Calculate moving averages
    for ma in moving_averages:
        df[f'MA_{ma}'] = df['Close'].rolling(window=ma).mean()

    # Plot the index
    plt.figure(figsize=(14, 7))
    plt.plot(df['Date'], df['Close'], label=f'{ticker} Price', color='blue')

    # Plot moving averages
    for ma in moving_averages:
        plt.plot(df['Date'], df[f'MA_{ma}'], label=f'MA {ma}')

    # Highlight periods with significant drops
    plt.fill_between(df['Date'], df['Close'], where=df['Significant Drop'], color='red', alpha=0.5,
                     label=f'Drop ≥ {max_drop} points')

    # Customize the plot
    plt.title(f'{ticker} Price from {start_date.date()} to {end_date.date()}')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Display the plot
    plt.show()


except Exception as e:
    print(f"An error occurred: {e}")
    exit()

try:
    url = f"https://finance.yahoo.com/quote/{stripped_ticker}/key-statistics?p=TSLA"
    html_data = requests.get(url).text
    soup = bs(html_data, 'lxml')  ### or html5lib
    table = soup.find_all('table')
    df = pd.read_html(str(table))

    # Combine all the DataFrames in the list
    df_combined = pd.concat(df, ignore_index=True)

    # Save the DataFrame to a CSV file
    csv_filename = f"{ticker}_key_statistics.csv"
    df_combined.to_csv(csv_filename, index=False)

    print(f"Data saved to {csv_filename}")
    print(df)

except Exception as e:
    print(f"An error occurred: {e}")
    exit()




# Example usage:
if __name__ == "__main__":
    stock_data = StockData()
    print("\nUser Input Summary:")
    print(stock_data)

    # Convert to a DataFrame if needed
    df = pd.DataFrame(stock_data.to_dataframe())
    print("\nDataFrame Representation:")
    print(df)


