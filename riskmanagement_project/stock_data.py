import datetime, traceback, requests
import os

from prettytable import PrettyTable
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from bs4 import BeautifulSoup as bs
import stock_visiual_candlestick

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

    def __str__(self):
        return str(self.ticker) + str(self.end_date) + str(self.max_drop) + str(self.moving_averages) + str(
            self.df.head())

    def get_stock_ticker(self):
        return self.ticker

    def get_stock_end_date(self):
        return self.end_date

    def get_stock_max_drop(self):
        return self.max_drop

    def get_stock_moving_averages(self):
        return self.moving_averages

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
            print(f"[+] Maximum Drop Amount: {max_drop_input}")
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
                print(f"[+] Moving Average: {ma}")


            except ValueError:
                print(f"[-] Invalid moving average period: {ma}. Please enter integer values. \n Exiting.")
                traceback.print_exc()
                exit()

        # Create a DataFrame from the moving averages

        try:
            description = 'moving_averages'
            csv_file_name = os.path.join("STOCK_RESULTS", f"{self.ticker}_{description}.csv")
            excel_file_name = os.path.join("STOCK_RESULTS", f"{self.ticker}_{description}.xlsx")

            df = pd.DataFrame(moving_averages, columns=["Moving Average"])
            df.to_csv(f"{csv_file_name}", index=False)
            df.to_excel(f"{excel_file_name}.xlsx", index=False, engine='openpyxl')

            print("Moving averages saved as 'moving_averages.csv' and 'moving_averages.xlsx'.")
            print(f"[!] Moving averages: \n {moving_averages}")

        except Exception as e:
            print(f"\n\n[-] An error occurred while saving moving averages: {e}")
            traceback.print_exc()

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
                print(
                    f"[-] No data found for ticker '{self.ticker}' between {self.start_date.date()} and {self.end_date.date()}.\n Exiting.")
                exit()

            print("\n[+] Fetched Data:")
            # Display the first few rows of the DataFrame in console

            description = 'ticker_data'
            csv_filename = os.path.join("STOCK_RESULTS", f"{self.ticker}_{description}.csv")
            self.df.to_csv(csv_filename, index=False)
            convert_csv_to_excel(csv_filename)
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

                csv_filename = os.path.join("STOCK_RESULTS", f"{self.ticker}_{description}.csv")
                historical_data.to_csv(csv_filename, index=False)
                convert_csv_to_excel(csv_filename)

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

                csv_filename = os.path.join("STOCK_RESULTS", f"{self.ticker}_{description}.csv")
                financials.to_csv(csv_filename, index=False)
                convert_csv_to_excel(csv_filename)

                print("\n[+] General Financials:\n")

                print(f"[!] General Finances saved to {csv_filename}")

            except Exception as e:
                print(f"[!] Error Occurred Saving Data to CSV: {e}")
                traceback.print_exc()

            try:
                # Fetch quarterly financials
                description = 'quarterly_financials'
                quarterly_financials = ticker_obj.quarterly_financials

                csv_filename = os.path.join("STOCK_RESULTS", f"{self.ticker}_{description}.csv")
                quarterly_financials.to_csv(csv_filename, index=False)
                convert_csv_to_excel(csv_filename)

                print("\n[+] Quarterly Financials:\n")
                print(f"[!] Quareterly Financials saved to:  {csv_filename}")

            except Exception as e:
                print(f"[!] Error Occurred Saving Data to CSV: {e}")
                traceback.print_exc()

            try:
                '''1:  Fetch stock info '''
                stock_info = ticker_obj.info
                description = 'stock_info'

                csv_filename = os.path.join("STOCK_RESULTS", f"{self.ticker}_{description}.csv")
                stock_info.to_csv(csv_filename, index=False)
                convert_csv_to_excel(csv_filename)

                print("\n[+] Dividends+Stock_Splits:\n")
                stock_info_table = PrettyTable()
                stock_info.field_names = stock_info_table.columns.tolist()

                for row in stock_info_table.itertuples(index=False):
                    stock_info_table.add_row(row)
                print(f"[!] Dividends and Splits  Financials saved to:  {csv_filename}")

            except Exception as e:
                pass  # Do nothing

            try:
                '''2:  Fetch stock actions like dividends and splits '''
                stock_actions = ticker_obj.actions
                description = 'Dividends+Stock_Splits'
                csv_filename = os.path.join("STOCK_RESULTS", f"{self.ticker}_{description}.csv")
                stock_actions.to_csv(csv_filename, index=False)
                convert_csv_to_excel(csv_filename)

                print(f"[!] Dividends and Splits  Financials saved to:  {csv_filename}")

                print("\n[+] Dividends+Stock_Splits:\n")

                '''3:  Fetch major holders '''

                maj_holder = ticker_obj.major_holders
                description = 'major_holders'
                csv_filename = os.path.join("STOCK_RESULTS", f"{self.ticker}_{description}.csv")
                maj_holder.to_csv(csv_filename, index=False)
                convert_csv_to_excel(csv_filename)

                print(f"[!] Major Holders saved to:  {csv_filename}")
                print("\n[+] Major Holders:\n")

                '''4: Fetch institutional holders '''
                inst_holder = ticker_obj.institutional_holders
                description = 'institutional_holders'
                csv_filename = os.path.join("STOCK_RESULTS", f"{self.ticker}_{description}.csv")
                inst_holder.to_csv(csv_filename, index=False)

                print(f"[!] Institutional Holders saved to:  {csv_filename}")

                print("\n[+] Institutional Holders:\n")


            except Exception as e:
                print(f"[-] An error occurred while fetching additional data: {e}")
                traceback.print_exc()
                exit()

        except Exception as e:
            print(f"[-]An error occurred while fetching additional data: {e}")
            exit()

    '''
        ------- SCRAPING METHODS---------
        1. Financial Docs 
        2. Balance Sheet 
        3. Cash Flow 
    '''

    def scrape_financial_documents(self):
        ticker_docs_obj = yf.Ticker(self.ticker)
        '''1:  Fetch financial documents '''
        try:
            financials = ticker_docs_obj.financials
            description = 'financials'
            csv_filename = os.path.join("STOCK_RESULTS", f"{self.ticker}_{description}.csv")
            financials.to_csv(csv_filename, index=False)
            convert_csv_to_excel(csv_filename)

            print("\n[+] Financials:\n")

            print(f"[!] Financials saved to {csv_filename}")

        except Exception as e:
            print(f"An error occurred while scraping financial documents: {e}")
            traceback.print_exc()

        ''' 2. Fetch balance sheet'''
        try:
            balance_sheet = ticker_docs_obj.balance_sheet
            description = 'balance_sheet'
            csv_filename = os.path.join("STOCK_RESULTS", f"{self.ticker}_{description}.csv")
            balance_sheet.to_csv(csv_filename, index=False)
            convert_csv_to_excel(csv_filename)

            print("\n[+] Balance Sheet:\n")

            print(f"[!] Balance Sheet saved to {csv_filename}")

        except Exception as e:
            print(f"An error occurred while scraping balance sheet: {e}")
            traceback.print_exc()

        ''' 3. Fetch cash flow '''
        try:
            cash_flow = ticker_docs_obj.cashflow
            description = 'cash_flow'
            csv_filename = os.path.join("STOCK_RESULTS", f"{self.ticker}_{description}.csv")
            cash_flow.to_csv(csv_filename, index=False)
            convert_csv_to_excel(csv_filename)


        except Exception as e:
            print(f"[-] An error occurred while scraping cash flow: {e}")
            traceback.print_exc()

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

            description = "key_statistic"
            csv_filename = os.path.join("STOCK_RESULTS", f"{self.ticker}_{description}.csv")
            df_combined.to_csv(csv_filename, index=False)
            convert_csv_to_excel(csv_filename)

            print(f"Data saved to {csv_filename}")

        except Exception as e:
            print(f"[+] an error occurred while scraping key statistics: {e}")
            exit()

    ''' ----------------- Calculation METHODS ----------------- 
        1. Calculate peaks, drawdowns, significant drops, moving averages.
        2. Plot the data.
        3. Save the DataFrame to a CSV file.
    '''

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
            convert_csv_to_excel(csv_filename)

            print(f"Data saved to {csv_filename}")
        except Exception as e:
            print(f"[!] Error Occurred Saving Data to CSV: {e}")
            traceback.print_exc()

    ''' ----------------- RUN METHOD ----------------- '''

    def run(self):
        print("\nFetched Data:")
        self.fetch_data()
        self.fetch_additional_data()
        self.scrape_financial_documents()
        self.scrape_key_statistics()

        self.calculate_indicators()
        self.plot_data()

        # self.save_data_to_csv(description='historical_data')


''' ----------------- Helper Methods ----------------- 

    1. Create a results folder to store the data.
    2. Covert CSV to Excel 
    '''


def create_results_folder():
    folder_name = "STOCK_RESULTS"
    try:
        # Create the folder if it doesn't exist
        os.makedirs(folder_name, exist_ok=True)

        # Set read and write permissions
        os.chmod(folder_name, 0o777)

        print(f"Folder '{folder_name}' created with read and write permissions.\n {os.getcwd()}/{folder_name}\n\n ")
    except Exception as e:
        print(f"An error occurred while creating the folder: {e}")


def convert_csv_to_excel(csv_file_path, excel_file_path=None):
    """ Convert a CSV file to an Excel file using pandas.
    :param csv_file_path: Path to the input CSV file.
    :param excel_file_path: Path to save the output Excel file. If None, saves in the same directory as the CSV.
    """
    try:
        ''' Check if the CSV file exists '''
        if not os.path.exists(csv_file_path):
            print(f"Error: The file '{csv_file_path}' does not exist.")
            return

        df = pd.read_csv(csv_file_path)

        # Generate Excel file path if not provided
        if excel_file_path is None:
            base_name = os.path.splitext(csv_file_path)[0]
            excel_file_path = f"{base_name}.xlsx"

        df.to_excel(excel_file_path, index=False, engine='openpyxl')
        print(f"[!] Successfully converted '{csv_file_path}' to '{excel_file_path}'")

    except Exception as e:
        print(f"[-] An error in converting .CVS  to EXCEL : {e}")
        traceback.print_exc()


# ----------------- MAIN -----------------

# Example usage:
if __name__ == "__main__":
    create_results_folder()
    if not os.path.exists("STOCK_RESULTS"):
        print("[!] Error: No STOCK_RESULTS folder found. Exiting.")
        exit()

    # os.makedirs("STOCK_RESULTS", exist_ok=True)

    stock_data = StockData()
    stock_data.run()
    candle_stick = stock_visiual_candlestick.Plot_Candlestick(stock_data.get_stock_ticker())
