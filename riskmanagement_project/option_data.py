import os
import traceback

import yfinance as yf
import datetime
import pandas as pd

import main

''' CLASS - OptionData 
    1. Fetch option data based on user input
    2. Fetch historical data for a specific option contract
    3. Execute the workflow to fetch and display option data
[BUG] 4. Validate and parse the strike price (If expiration date is not provided, use the nearest expiration date_
    5. Fetch the option chain for the specified expiration date
    6. Select calls or puts based on the option type
    7. Filter options by strike price
    8. Fetch historical data for a specific option contract
    10. Display the option data
[TODO]
    1. Add error handling for invalid user input
    2. Plot the historical data for the option contract
    3. Add support for fetching option data for multiple contracts
    4. Add plotting and analysis of option data
'''
import main
import stock_data

StockData = stock_data.StockData()
OptionInfo = main.Parameters

''' SUBCLASS - OptionData AND StockData to get the stock ticker and end date '''
# class OptionData:
class OptionData(OptionInfo, StockData):
    def __init__(self):  #, stock_symbol=None, expiration_date=None, option_type=None, strike=None):
        super().__init__()
        self.stock_symbol = StockData.get_stock_ticker()
        self.strike = OptionInfo.strike_price_PUT#  input("[?] Enter the strike price (e.g., 170.0): ").strip()
        self.expiration_date = StockData.get_stock_end_date()  #input("[?] Enter the option expiration date in YYYY-MM-DD format (or leave blank for the nearest expiration): ").strip()
        self.option_type = input("[?] Enter the option type (call/put): ").strip().lower()

        # Validate and parse the strike price
        #try:
            #self.strike = float(self.strike)
        #except ValueError:
         #   print("Invalid strike price. Please enter a numerical value.")
          #  exit()

        # If expiration date is not provided, use the nearest expiration date
        if not self.expiration_date:
            self.expiration_date = None


    ''' FETCH DATA 
        1. Fetch option data based on user input
        2. Fetch historical data for a specific option contract
    '''
    def get_option_data(self):
        """1. Fetch option data based on user input."""
        stock = yf.Ticker(self.stock_symbol)

        # Use the nearest expiration date if none is provided
        if not self.expiration_date:
            expirations = stock.options
            print(f"[!] Available expiration dates: {expirations}")
            if not expirations:
                print("No option data available for this stock., program will not work right ")

            self.expiration_date = expirations[0]
            print(f"[!] No expiration date provided. \n...Using nearest expiration date: {self.expiration_date}")

        ''' Fetch the option chain for the specified expiration date '''
        try:
            option_chain = stock.option_chain(self.expiration_date)
            description = f"option_data+{self.stock_symbol}+{self.expiration_date}+{self.option_type}+{self.strike}"
            csv_filename = os.path.join("OPTIONS_DATA", f"{description}.csv")


            print(f"Fetching option data for {self.stock_symbol} with expiration date {self.expiration_date}...")
            print(f"Option type: {self.option_type}, Strike price: {self.strike}")
            print(f"Option chain: {option_chain}")
        except Exception as e:
            print(f"Error fetching option chain: {e}")
            traceback.print_exc()
            exit()

        # Select calls or puts based on the option type
        if self.option_type.startswith("call"):
            options = option_chain.calls
            print(f"Call Options: {options}")
        elif self.option_type.startswith("put"):
            options = option_chain.puts
            print(f"Put Options: {options}")

        else:
            print("Invalid option type. Please enter 'call' or 'put'.")
            traceback.print_exc()
            exit()

        # Filter options by strike price
        option_data = options[options["strike"] == self.strike]
        if option_data.empty:
            print(f"No {self.option_type} options found for strike price {self.strike} on {self.expiration_date}.")
            exit()

        print(option_data.to_string(index=False))

        return option_data

    def get_option_history_data(self, contract_symbol, days_before_expiration=30):
        """Fetch historical data for a specific option contract."""
        option = yf.Ticker(contract_symbol)
        option_info = option.info

        # Get the option's expiration date
        option_expiration_timestamp = option_info.get("expireDate")
        if not option_expiration_timestamp:
            print(f"Expiration date not found for contract {contract_symbol}.")
            exit()
        option_expiration_date = datetime.datetime.fromtimestamp(option_expiration_timestamp)

        # Calculate the start date for historical data
        start_date = option_expiration_date - datetime.timedelta(days=days_before_expiration)
        option_history = option.history(start=start_date)
        return option_history

    def run(self):
        """Execute the workflow to fetch and display option data."""
        option_data = self.get_option_data()
        print(f"[!] Fetching historical data for {len(option_data)} option contracts...")
        print(f"[!] Parsing option data: {option_data}")
        for _, od in option_data.iterrows():
            contract_symbol = od["contractSymbol"]
            option_history = self.get_option_history_data(contract_symbol)

            if not option_history.empty:
                first_option_history = option_history.iloc[0]
                first_option_history_date = option_history.index[0]
                first_option_history_close = first_option_history["Close"]
                print(f"For {contract_symbol}, the closing price was ${first_option_history_close:.2f} on {first_option_history_date.strftime('%Y-%m-%d')}.")
            else:
                print(f"[-] No historical data found for option {contract_symbol}.")
                #break

        print("[!] Option data retrieval complete.\n\n")

        print(option_data.to_string(index=False)) # Display the option data
        description = f"option_data+{self.stock_symbol}+{self.expiration_date}+{self.option_type}+{self.strike}"
        csv_filename = os.path.join("OPTIONS_DATA", f"{description}.csv")
        option_data.to_csv(csv_filename)
        convert_csv_to_excel(csv_filename)
        df = pd.DataFrame(option_data)
        df.to_csv(csv_filename, 'option_dataII.csv')
        df.to_excel('option_dataII.xlsx')
        print(f"Option data saved to {csv_filename}")
        return option_data


def create_results_folder():
    ''' 2.  CREATE RESULTS FOLDER '''
    folder_name = "OPTION_DATA"

    try:
        os.makedirs(folder_name, exist_ok=True)
        print(f"[+] Folder '{folder_name}'\n created with read and write permissions.")
        os.chmod(folder_name, 0o777)

    except Exception as e:
        print(f"[!] An error occurred while creating the folder: {e}")
        traceback.print_exc()

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


def main():

    create_results_folder()
    option_data_instance = OptionData()
    option_data_instance.run()

if __name__ == "__main__":
    main()