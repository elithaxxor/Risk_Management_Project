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


# Example usage:
if __name__ == "__main__":
    stock_data = StockData()
    print("\nUser Input Summary:")
    print(stock_data)

    # Convert to a DataFrame if needed
    df = pd.DataFrame(stock_data.to_dataframe())
    print("\nDataFrame Representation:")
    print(df)
