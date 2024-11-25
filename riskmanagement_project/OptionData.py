import yfinance as yf
import datetime

class OptionData:
    def __init__(self):
        """Initialize the class and prompt the user for input."""
        self.stock_symbol = input("Enter the stock symbol (e.g., AAPL): ").strip().upper()
        self.expiration_date = input("Enter the option expiration date in YYYY-MM-DD format (or leave blank for the nearest expiration): ").strip()
        self.option_type = input("Enter the option type (call/put): ").strip().lower()
        self.strike = input("Enter the strike price (e.g., 170.0): ").strip()

        # Validate and parse the strike price
        try:
            self.strike = float(self.strike)
        except ValueError:
            print("Invalid strike price. Please enter a numerical value.")
            exit()

        # If expiration date is not provided, use the nearest expiration date
        if not self.expiration_date:
            self.expiration_date = None

    def get_option_data(self):
        """Fetch option data based on user input."""
        stock = yf.Ticker(self.stock_symbol)

        # Use the nearest expiration date if none is provided
        if not self.expiration_date:
            expirations = stock.options
            if not expirations:
                print("No option data available for this stock.")
                exit()
            self.expiration_date = expirations[0]
            print(f"No expiration date provided. Using nearest expiration date: {self.expiration_date}")

        # Fetch the option chain for the specified expiration date
        try:
            option_chain = stock.option_chain(self.expiration_date)
        except Exception as e:
            print(f"Error fetching option chain: {e}")
            exit()

        # Select calls or puts based on the option type
        if self.option_type.startswith("call"):
            options = option_chain.calls
        elif self.option_type.startswith("put"):
            options = option_chain.puts
        else:
            print("Invalid option type. Please enter 'call' or 'put'.")
            exit()

        # Filter options by strike price
        option_data = options[options["strike"] == self.strike]
        if option_data.empty:
            print(f"No {self.option_type} options found for strike price {self.strike} on {self.expiration_date}.")
            exit()
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
        for _, od in option_data.iterrows():
            contract_symbol = od["contractSymbol"]
            option_history = self.get_option_history_data(contract_symbol)
            if not option_history.empty:
                first_option_history = option_history.iloc[0]
                first_option_history_date = option_history.index[0]
                first_option_history_close = first_option_history["Close"]
                print(f"For {contract_symbol}, the closing price was ${first_option_history_close:.2f} on {first_option_history_date.strftime('%Y-%m-%d')}.")
            else:
                print(f"No historical data found for option {contract_symbol}.")

if __name__ == "__main__":
    option_data_instance = OptionData()
    option_data_instance.run()
