import datetime, traceback, requests
from prettytable import PrettyTable
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from bs4 import BeautifulSoup as bs



''' 
    ** Class to fetch stock data: STORING TO MEMORY, TO REFACTOR FOR BETTER READBILITY / ABILITY TO ACCESS DATA AMOUNGST VARYING METHODS/CALLS" 
    
    1. Fetch historical stock data,
    2. Calculate indicators, and plot the data.
    3. The user is prompted to enter the ticker symbol, end date, maximum drop amount, and moving average periods.
    4. The class fetches historical data using yfinance, calculates peaks, drawdowns, significant drops, and moving averages.
    5. The data is then plotted using Matplotlib.
    6. The user can also save the data to a CSV file and fetch additional data like financials, actions, and info.
    7. Key statistics are scraped from Yahoo Finance and saved to a CSV file. 
'''
class StockData:
    def __init__(self):
        """Initialize the class and prompt the user for input."""
        # Get user input
        self.ticker = input("[?] Enter the ticker symbol (e.g., ^GSPC for S&P 500): ")
        self.end_date_input = input("[?] Enter the end date in YYYY-MM-DD format (or leave blank for today): ")
        self.max_drop_input = input("[?] Enter the maximum amount of points for a significant drop (e.g., 1000): ")
        self.moving_averages_input = input("[?] Enter the moving average periods (e.g., 20,50,200): enter to skip:")

        # Strip the ticker symbol if it starts with '^', so it can be used in BS4 / yfinance
        self.stripped_ticker = self.ticker[1:] if self.ticker.startswith('^') else self.ticker

        # MOVING PARTS: Parses data
        self.end_date = self._parse_end_date(self.end_date_input)
        self.max_drop = self._parse_max_drop(self.max_drop_input)
        self.moving_averages = self._parse_moving_averages(self.moving_averages_input)
        self.start_date = self.end_date - datetime.timedelta(days=365)

        ''' 
            1. Initialize the DataFrame ---> REMEMBER NOT TO STORE DATA IN MEMORY, USE METHODS TO ACCESS DATA
            2. DO NOT GET conventianal "df" confused with other dataframes and method calls. 
        '''
        self.df = None


    ''' ----------------- PARSING METHODS ----------------- 
        1. Parse the end date input and return a datetime object.
        2. Parse the max drop input and return it as a float. ( THERE IS A BUG HERE ) 
        3. Parse the moving average input and return a list of integers.
        ----> EXIT SYS IF USER INPUT IS INVALID
    '''


    """ 1. Parse the end date input and return a datetime object."""
    def _parse_end_date(self, end_date_input):
        if end_date_input.strip() == '':
            print(f"[!] No end date entered. Proceeding with today's date.\n")
            return datetime.datetime.today()
        try:
            print(f"[+] End Date: {end_date_input}")
            return datetime.datetime.strptime(end_date_input, '%Y-%m-%d')
        except ValueError:
            print("[!] Invalid date format. Please enter the date in YYYY-MM-DD format. \n Exiting.")
            traceback.print_exc()
            exit()

    """2. Parse the max drop input and return it as a float."""
    def _parse_max_drop(self, max_drop_input):
        try:
            return float(max_drop_input)
        except ValueError:
            print("[-] Invalid input for maximum drop amount. Please enter a numerical value. \n Exiting.")
            traceback.print_exc()
            exit()

    """3. Parse the moving average input and return a list of integers."""
    def _parse_moving_averages(self, moving_averages_input):

        if not moving_averages_input.strip():
            print("[!] No moving averages entered. Proceeding without moving averages.")
            return []

        moving_averages = []
        for ma in moving_averages_input.split(','):
            try:
                moving_averages.append(int(ma.strip()))

            except ValueError:
                print(f"[-] Invalid moving average period: {ma}. Please enter integer values. \n Exiting.")
                traceback.print_exc()
                exit()

        print(f"[!] Moving averages: \n {moving_averages}")
        return moving_averages

    ''' ----------------- FETCH METHODS ----------------- 
        1. Fetch historical data using yfinance. Store in memory AND locally 
        2. Fetch additional data like financials, actions, info. Store Locally 
    '''

    """ (fetch_data) Fetch historical data using yfinance. 
        1. Store in memory 
        2. Store locally 
        3. Display Prettify in console 
    """
    def fetch_data(self):
        try:
            self.df = yf.download(self.ticker, start=self.start_date, end=self.end_date, timeout=20)

            if self.df.empty:
                print(f"[-] No data found for ticker '{self.ticker}' between {self.start_date.date()} and {self.end_date.date()}.\n Exiting.")
                exit()


            print("\n[+] Fetched Data:")
            # Display the first few rows of the DataFrame in console

            fetch_data = PrettyTable()
            fetch_data.field_names = self.df.columns.tolist()
            for row in self.df.itertuples(index=False):
                fetch_data.add_row(row)

            description = 'ticker_data'
            csv_filename = f"{self.ticker}_{description}.csv"
            self.df.to_csv(csv_filename, index=False)
            self.df.reset_index(inplace=True)

        except Exception as e:
            print(f"[!] An error occurred while fetching data: {e}")
            print(f"[-] Exiting")
            traceback.print_exc()
            exit()

    def fetch_additional_data(self):
        try:
            # TICKER OBJECT WILL BE USED THIS METHOD TO GATHER SUBSEQUENT DATA
            ticker_obj = yf.Ticker(self.ticker)

             # Fetch historical market data
            try:
                historical_data = ticker_obj.history(start=self.start_date, end=self.end_date)
                description = 'historical_data'

                csv_filename = f"{self.ticker}_{description}.csv"
                historical_data.to_csv(csv_filename, index=False)

                print("\n[+] Historical Data:")
                historical_data_table = PrettyTable()
                historical_data_table.field_names = historical_data.columns.tolist()
                for row in historical_data.itertuples(index=False):
                    historical_data_table.add_row(row)
                print(f"[!]  Data saved to {csv_filename}")


            except Exception as e:
                print(f"[!] Error Occurred Saving Data to CSV: {e}")
                traceback.print_exc()

            # Fetch financial data
            try:
                description = 'basic_financials'
                financials = ticker_obj.financials

                csv_filename = f"{self.ticker}_{description}.csv"
                financials.to_csv(f"{self.ticker}_{description}.csv", index=False)

                print("\n[+] General Financials:\n")
                financial_data_table = PrettyTable()
                financial_data_table.field_names = financial_data_table.columns.tolist()

                for row in financial_data_table.itertuples(index=False):
                    financial_data_table.add_row(row)

                print(f"[!] General Finances saved to {csv_filename}")

            except Exception as e:
                print(f"[!] Error Occurred Saving Data to CSV: {e}")
                traceback.print_exc()

            try:
                # Fetch quarterly financials
                description = 'quarterly_financials'
                quarterly_financials = ticker_obj.quarterly_financials

                csv_filename = f"{self.ticker}_{description}.csv"
                quarterly_financials.to_csv(f"{self.ticker}_{description}.csv", index=False)

                print("\n[+] Quarterly Financials:\n")
                quarterly_financials_table = PrettyTable()
                quarterly_financials.field_names = quarterly_financials_table.columns.tolist()
                for row in quarterly_financials_table.itertuples(index=False):
                    quarterly_financials_table.add_row(row)

                print(f"[!] Quareterly Financials saved to:  {csv_filename}")

            except Exception as e:
                print(f"[!] Error Occurred Saving Data to CSV: {e}")
                traceback.print_exc()

            try:
                '''1:  Fetch stock info '''
                stock_info = ticker_obj.info
                description = 'stock_info'

                csv_filename = f"{self.ticker}_{description}.csv"
                stock_info.to_csv(f"{self.ticker}_{description}.csv", index=False)
                print("\n[+] Dividends+Stock_Splits:\n")
                stock_info_table = PrettyTable()
                stock_info.field_names = stock_info_table.columns.tolist()
                for row in stock_info_table.itertuples(index=False):
                    stock_info_table.add_row(row)
                print(f"[!] Dividends and Splits  Financials saved to:  {csv_filename}")

                '''2:  Fetch stock actions like dividends and splits '''
                stock_actions = ticker_obj.actions
                description = 'Dividends+Stock_Splits'
                csv_filename = f"{self.ticker}_{description}.csv"
                stock_actions.to_csv(f"{self.ticker}_{description}.csv", index=False)
                print(f"[!] Dividends and Splits  Financials saved to:  {csv_filename}")

                '''3:  Fetch major holders '''
                print("\n[+] Dividends+Stock_Splits:\n")
                stock_actions_table = PrettyTable()
                stock_actions.field_names = stock_actions_table.columns.tolist()
                for row in stock_actions_table.itertuples(index=False):
                    stock_actions_table.add_row(row)

                maj_holder = ticker_obj.major_holders
                description = 'major_holders'
                csv_filename = f"{self.ticker}_{description}.csv"
                maj_holder.to_csv(f"{self.ticker}_{description}.csv", index=False)
                print(f"[!] Major Holders saved to:  {csv_filename}")

                print("\n[+] Major Holders:\n")
                maj_holder_table = PrettyTable()
                maj_holder_table.field_names = maj_holder_table.columns.tolist()
                for row in maj_holder_table.itertuples(index=False):
                    maj_holder_table.add_row(row)

                '''4: Fetch institutional holders '''
                inst_holder = ticker_obj.institutional_holders
                description = 'institutional_holders'
                csv_filename = f"{self.ticker}_{description}.csv"
                inst_holder.to_csv(f"{self.ticker}_{description}.csv", index=False)
                print(f"[!] Institutional Holders saved to:  {csv_filename}")

                print("\n[+] Institutional Holders:\n")
                inst_holder_table = PrettyTable()
                inst_holder_table.field_names = inst_holder_table.columns.tolist()
                for row in inst_holder_table.itertuples(index=False):
                    inst_holder_table.add_row(row)


            except Exception as e:
                print(f"An error occurred while fetching additional data: {e}")
                traceback.print_exc()
                exit()
        except Exception as e:
            print(f"An error occurred while fetching additional data: {e}")
            exit()


    ''' SCRAPING METHODS: 
        1. Financial Docs 
        2. Balance Sheet 
        3. Cash Flow 
    '''
    def scrape_financial_documents(self):
        ticker_obj = yf.Ticker(self.ticker)
        '''1:  Fetch financial documents'''
        try:
            financials = ticker_obj.financials
            description = 'financials'
            csv_filename = f"{self.ticker}_{description}.csv"
            financials.to_csv(f"{self.ticker}_{description}.csv", index=False)
            print("\n[+] Financials:\n")
            financials_table = PrettyTable()
            financials_table.field_names = financials.columns.tolist()
            for row in financials_table.itertuples(index=False):
                financials_table.add_row(row)
            print(f"[!] Financials saved to {csv_filename}")

        except Exception as e:
            print(f"An error occurred while scraping financial documents: {e}")
            traceback.print_exc()

        ''' 2. Fetch balance sheet'''
        try:
            balance_sheet = ticker_obj.balance_sheet
            description = 'balance_sheet'
            csv_filename = f"{self.ticker}_{description}.csv"
            balance_sheet.to_csv(f"{self.ticker}_{description}.csv", index=False)
            print("\n[+] Balance Sheet:\n")
            balance_sheet_table = PrettyTable()
            balance_sheet_table.field_names = balance_sheet.columns.tolist()
            for row in balance_sheet_table.itertuples(index=False):
                balance_sheet_table.add_row(row)
            print(f"[!] Balance Sheet saved to {csv_filename}")


    def scrape_key_statistics(self):
        """Scrape key statistics from Yahoo Finance and save to CSV."""
        try:
            url = f"https://finance.yahoo.com/quote/{self.stripped_ticker}/key-statistics?p={self.stripped_ticker}"
            html_data = requests.get(url).text
            soup = bs(html_data, 'lxml')
            tables = soup.find_all('table')
            df_list = pd.read_html(str(tables))
            # Combine all the DataFrames in the list
            df_combined = pd.concat(df_list, ignore_index=True)
            # Save the DataFrame to a CSV file
            csv_filename = f"{self.ticker}_key_statistics.csv"
            df_combined.to_csv(csv_filename, index=False)
            print(f"Data saved to {csv_filename}")

        except Exception as e:
            print(f"An error occurred while scraping key statistics: {e}")
            exit()


    def calculate_indicators(self):
        """Calculate peaks, drawdowns, significant drops, moving averages."""

        # Ensure 'Close' column is present
        if 'Close' not in self.df.columns:
            if 'Adj Close' in self.df.columns:
                self.df['Close'] = self.df['Adj Close']
            else:
                print("Neither 'Close' nor 'Adj Close' columns are present.")
                exit()
        # Ensure 'Close' is a Series
        if isinstance(self.df['Close'], pd.DataFrame):
            self.df['Close'] = self.df['Close'].iloc[:, 0]
        # Calculate the cumulative maximum to identify peaks
        self.df['Peak'] = self.df['Close'].cummax()
        # Ensure 'Peak' is a Series
        if isinstance(self.df['Peak'], pd.DataFrame):
            self.df['Peak'] = self.df['Peak'].iloc[:, 0]

        # Calculate drawdowns from the peaks
        self.df['Drawdown'] = self.df['Peak'] - self.df['Close']
        # Identify periods where the drawdown is equal to or exceeds the max drop
        self.df['Significant Drop'] = self.df['Drawdown'] >= self.max_drop

        # Calculate moving averages
        for ma in self.moving_averages:
            self.df[f'MA_{ma}'] = self.df['Close'].rolling(window=ma).mean()

    def plot_data(self):
        """Plot the data."""
        plt.figure(figsize=(14, 7))
        plt.plot(self.df['Date'], self.df['Close'], label=f'{self.ticker} Price', color='blue')
        # Plot moving averages
        for ma in self.moving_averages:
            plt.plot(self.df['Date'], self.df[f'MA_{ma}'], label=f'MA {ma}')
        # Highlight significant drops
        plt.fill_between(self.df['Date'], self.df['Close'], where=self.df['Significant Drop'], color='red', alpha=0.5,
                         label=f'Drop ≥ {self.max_drop} points')
        # Customize the plot
        plt.title(f'{self.ticker} Price from {self.start_date.date()} to {self.end_date.date()}')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        # Display the plot
        plt.show()

    def save_data_to_csv(self, description):
        """Save the DataFrame to a CSV file."""
        try:
            csv_filename = f"{self.ticker}_{description}.csv"
            self.df.to_csv(csv_filename, index=False)
            print(f"Data saved to {csv_filename}")
        except Exception as e:
            print(f"[!] Error Occurred Saving Data to CSV: {e}")
            traceback.print_exc()

        """Fetch additional data like financials, actions, info."""


    def run(self):
        print("\nFetched Data:")
        self.fetch_data()
        self.fetch_additional_data()
        self.scrape_key_statistics()

        self.calculate_indicators()
        self.plot_data()

        self.save_data_to_csv(description='historical_data')

# Example usage:
if __name__ == "__main__":
    stock_data = StockData()
    stock_data.run()





def get_option_data(stock_symbol, expiration_date, option_type, strike):
    stock = yf.Ticker(stock_symbol)
    option_chain = stock.option_chain(expiration_date)
    options = getattr(option_chain, "calls" if option_type.startswith("call") else "puts")
    option_data = options[options["strike"] == strike]
    return option_data


def get_option_history_data(contract_symbol, days_before_expiration=30):
    option = yf.Ticker(contract_symbol)
    option_info = option.info
    option_expiration_date = datetime.datetime.fromtimestamp(option_info["expireDate"])

    start_date = option_expiration_date - datetime.timedelta(days=days_before_expiration)
    option_history = option.history(start=start_date)
    return option_history


def main(*args):
    # Example:
    stock_symbol = "AAPL"
    expiration_date = "2023-10-27"
    expiration_date = None
    option_type = "call"
    strike = 170.0

    option_data = get_option_data(stock_symbol, expiration_date, option_type, strike)
    for i, od in option_data.iterrows():
        contract_symbol = od["contractSymbol"]
        option_history = get_option_history_data(contract_symbol)
        first_option_history = option_history.iloc[0]
        first_option_history_date = option_history.index[0]
        first_option_history_close = first_option_history["Close"]
        print("For {}, the closing price was ${:.2f} on {}.".format(
            contract_symbol,
            first_option_history_close,
            first_option_history_date
        ))

