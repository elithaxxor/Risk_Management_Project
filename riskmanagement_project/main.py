import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm
from prettytable import PrettyTable
import os
import time

import os
import time
import traceback
import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm
from tabulate import tabulate
from prettytable import PrettyTable
from dataclasses import dataclass
import openpyxl as px

import stock_data
from stock_data import StockData
from stock_data import FinancialDataDownloader


# from option_data import OptionData

# from option_data import OptionData
# from stock_data import StockData

# OptionData = option_data.OptionData


@dataclass
class Parameters():
    stock_symbol = None
    initial_equity_price: float
    strike_price_PUT: float
    trigger_price_PUT: float
    time_horizon: int
    time_step: int
    time_horizon_step: int
    annual_expected_return: float
    volatility: float
    risk_free_rate: float
    trigger_price: float
    num_shares: int
    num_puts: int
    margin_requirement: float
    margin_rate: float

    @classmethod
    def from_user_input(cls):
        """Create an instance by taking inputs from the user."""
        print("[!] Enter the following parameters:")
        return cls(
            initial_equity_price=float(input(" [?] Initial Equity Price (e.g., 40.0): ")),
            strike_price_PUT=float(input("[?] Strike Price for PUT (e.g., 35.0): ")),
            trigger_price_PUT=float(input("[?] Trigger Price for PUT (e.g., 40.0): ")),
            time_horizon=int(input("[?] Time Horizon (Days, e.g., 90): ")),
            time_step=252,  # Set to 252 (trading days in a year)
            time_horizon_step=int(input("[?] Time Horizon Step (e.g., 90): ")),
            annual_expected_return=float(input("[?] Annual Expected Return (e.g., 0.05 for 5%): ")),
            volatility=float(input("[?] Volatility (e.g., 0.3 for 30%): ")),
            risk_free_rate=float(input("[?] Risk-Free Rate (e.g., 0.01 for 1%): ")),
            trigger_price=float(input("[?] Trigger Price (e.g., 42.5): ")),
            num_shares=int(input("[?] Number of Shares (e.g., 1000): ")),
            num_puts=int(input("[?] Number of Put Contracts (e.g., 10): ")),
            margin_requirement=float(input("[?] Margin Requirement (e.g., 0.5 for 50%): ")),
            margin_rate=float(input("[?] Margin Rate (e.g., 0.05 for 5%): ")),
        )


class OptionSimulator:
    def __init__(self, parameters):
        self.parameters = parameters
        self.adjusted_time_step = 1 / self.parameters.time_step  # Time step in years (assuming 252 trading days per year)
        self.borrowed_amount = self.parameters.num_shares * self.parameters.initial_equity_price * (
                1 - self.parameters.margin_requirement)
        self.daily_margin_rate = self.parameters.margin_rate / self.parameters.time_step
        self.total_margin_interest = 0

    def simulate_stock_prices(self):
        """Simulate stock prices using geometric Brownian motion."""
        t = np.linspace(0, self.parameters.time_horizon * self.adjusted_time_step, self.parameters.time_horizon_step)
        randomness = np.random.standard_normal(size=self.parameters.time_horizon_step)
        randomness = np.cumsum(randomness) * np.sqrt(self.adjusted_time_step)
        coeff = (self.parameters.annual_expected_return - 0.5 * self.parameters.volatility ** 2) * t \
                + self.parameters.volatility * randomness
        new_stock_price = self.parameters.initial_equity_price * np.exp(coeff)
        return new_stock_price

    def black_scholes_put(self, equity_price, put_strike, time_to_expiration):
        """Calculate the price of a put option using the Black-Scholes model."""
        if time_to_expiration <= 0:
            return max(put_strike - equity_price, 0)
        d1 = (np.log(equity_price / put_strike) + (
                self.parameters.risk_free_rate + 0.5 * self.parameters.volatility ** 2) * time_to_expiration) / (
                     self.parameters.volatility * np.sqrt(time_to_expiration))
        d2 = d1 - self.parameters.volatility * np.sqrt(time_to_expiration)
        put_price = put_strike * np.exp(-self.parameters.risk_free_rate * time_to_expiration) * norm.cdf(-d2) \
                    - equity_price * norm.cdf(-d1)
        return put_price

    def plot_stock_prices(self, prices):
        """Plot the simulated stock prices over time."""
        dates = pd.date_range(start='2023-01-01', periods=len(prices), freq='B')
        df = pd.DataFrame({'Date': dates, 'Price': prices})

        plt.figure(figsize=(12, 6))
        plt.plot(df['Date'], df['Price'], label='Stock Price')
        plt.title(f'Simulated Stock Prices over {self.parameters.time_horizon} Days with Varying Volatility')
        plt.xlabel('Date')
        plt.ylabel('Price ($)')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

        description = 'simulated_stock_prices'
        output_file = f"{description}.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f'[!] Graph saved to {output_file}')

    def run_simulation(self):
        """Run the main simulation logic."""
        # Initialize variables
        position_values = []
        put_strike_prices = []
        put_option_values = []
        actions = []
        margin_interests = []

        borrowed_amount = self.parameters.num_shares * self.parameters.initial_equity_price * (
                1 - self.parameters.margin_requirement)
        daily_margin_rate = self.parameters.margin_rate / self.parameters.time_step
        total_margin_interest = 0

        # Step 1: Simulate Prices
        np.random.seed(42)
        simulated_price_index = self.simulate_stock_prices()

        # Prepare pandas DataFrame
        dates = pd.date_range(start='2023-01-01', periods=self.parameters.time_horizon_step, freq='B')
        df = pd.DataFrame({'Date': dates, 'Stock Price': simulated_price_index})

        # Save simulated stock prices to CSV
        description = "simulated_stock_prices"
        os.makedirs("BLACK_SCHOLES_RESULTS", exist_ok=True)
        csv_filename = os.path.join("BLACK_SCHOLES_RESULTS", f"{description}.csv")
        df.to_csv(csv_filename, index=False)
        print(f"\n[!] Data saved to {csv_filename}\n")

        # Plot stock prices
        self.plot_stock_prices(simulated_price_index)

        # Initial put option
        T_initial = self.parameters.time_horizon * self.adjusted_time_step
        put_price = self.black_scholes_put(
            self.parameters.initial_equity_price,
            self.parameters.strike_price_PUT,
            T_initial
        )
        put_option_value = self.parameters.num_puts * 100 * put_price
        current_put_strike = self.parameters.strike_price_PUT
        action = f'Bought initial puts at {self.parameters.strike_price_PUT}'
        actions.append(action)

        # Main simulation loop
        for day in range(self.parameters.time_horizon_step):
            day_stock = df['Stock Price'].iloc[day]
            adjusted_time_to_expiration = (self.parameters.time_horizon - day) * self.adjusted_time_step
            interest = borrowed_amount * daily_margin_rate
            total_margin_interest += interest

            # Check for trigger to adjust puts
            if day_stock >= self.parameters.trigger_price and current_put_strike == self.parameters.strike_price_PUT:
                print("\n[!] Trigger price reached. Adjusting put options...")
                print("... Selling puts and buying new puts with higher strike price")
                time.sleep(0.1)

                put_price_sell = self.black_scholes_put(day_stock, self.parameters.strike_price_PUT,
                                                        adjusted_time_to_expiration)
                proceeds = self.parameters.num_puts * 100 * put_price_sell
                print(f"\n[+] Sold puts at ${self.parameters.strike_price_PUT} for ${proceeds:.2f}")
                time.sleep(0.25)

                # Buy new puts with higher strike price
                current_put_strike = self.parameters.trigger_price_PUT
                remaining_days = self.parameters.time_horizon - day
                T_new = remaining_days * self.adjusted_time_step
                put_price_buy = self.black_scholes_put(day_stock, self.parameters.trigger_price_PUT, T_new)
                put_option_value = self.parameters.num_puts * 100 * put_price_buy

                print(f".. Bought puts at K=${self.parameters.trigger_price_PUT} for ${put_option_value:.2f}")
                time.sleep(0.25)

                print(
                    f"\n[RESULTS] \n[+] Day {day} Bought puts at ${self.parameters.trigger_price_PUT} for ${put_option_value:.2f}")

                action = (
                    f' [+] DAY: {day} Bought puts at K=${self.parameters.trigger_price_PUT} for ${put_option_value:.2f}, '
                    f'[PRICE ACTION] Sold puts at ${self.parameters.strike_price_PUT}, bought puts at ${self.parameters.trigger_price_PUT}')
                print("[+] Price Action: ", action)
            else:
                # Update put option value
                put_price_current = self.black_scholes_put(day_stock, current_put_strike, adjusted_time_to_expiration)
                put_option_value = self.parameters.num_puts * 100 * put_price_current
                action = '[!] No need for action today'
                print("[+]\n Price Action: ", action)

            # Total position value
            position_value = (self.parameters.num_shares * day_stock) + put_option_value - total_margin_interest

            # Store results
            position_values.append(position_value)
            put_strike_prices.append(current_put_strike)
            put_option_values.append(put_option_value)
            actions.append(action)
            margin_interests.append(total_margin_interest)

        # Add results to DataFrame
        df['Put Strike Price'] = put_strike_prices
        df['Put Option Value'] = put_option_values
        df['Margin Interest'] = margin_interests
        df['Total Position Value'] = position_values
        df['Action'] = actions[1:]  # Skip the initial action
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        df['Value'] = df['Total Position Value'].map('${:,.2f}'.format)

        # Save simulation results
        try:
            description = "simulation_results"
            csv_filename = os.path.join("BLACK_SCHOLES_RESULTS", f"{description}.csv")
            df.to_csv(csv_filename, index=False)

            excel_filename = os.path.join("BLACK_SCHOLES_RESULTS", f"{description}.xlsx")
            df.to_excel(excel_filename, index=False, engine='openpyxl')
            print(f"[!] Data saved to {csv_filename} and {excel_filename}")
        except Exception as e:
            print(f"[-] Error saving data: {e}")
            pass

        # Display the final table
        put_table = PrettyTable()
        put_table.field_names = df.columns.tolist()
        for row in df.itertuples(index=False):
            put_table.add_row(row)
        print(put_table)

        # Plot total position value over time
        plt.figure(figsize=(12, 6))
        plt.plot(df['Date'], df['Total Position Value'], label='Total Position Value')
        plt.title(f"Investor's Total Position Value Over {self.parameters.time_horizon} Days")
        plt.xlabel('Date')
        plt.ylabel('Value ($)')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()

        output_file = 'total_position_value.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f'[!] Graph saved to {output_file}')
        plt.show()

        # Plot stock price and put strike price over time
        print("Plotting the stock price and put strike price over time")
        plt.figure(figsize=(12, 6))
        plt.plot(df['Date'], df['Stock Price'], label='Stock Price')
        plt.plot(df['Date'], df['Put Strike Price'], label='Put Strike Price', linestyle='--')
        plt.title(f'Stock Price and Put Strike Price Over {self.parameters.time_horizon} Days')
        plt.xlabel('Date')
        plt.ylabel('Price ($)')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()

        output_file = 'stock_and_put_strike_price.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f'[!] Graph saved to {output_file}')
        plt.show()


# Assuming Parameters class is defined elsewhere with a from_user_input() method


if __name__ == "__main__":
    parameters = Parameters.from_user_input()
    simulator = OptionSimulator(parameters)
    simulator.run_simulation()


    class StockDataFetch:
        def __init__(self, paramaters):
            self.parameters = parameters
            self.runStock = StockData()
            self.runCalculations = StockData().run()
            self.ticker = paramaters.stock_symbol

        def get_stock_ticker(self):
            return parameters.stock_symbol

        def get_time_horizon(self):
            return parameters.time_horizon

        def get_stock_data(self):
            stock = yf.Ticker(self.ticker)
            data = stock.history(period=self.get_time_horizon())
            return data

        def runClass(self):
            self.runCalculations = StockData().run()
            self.ticker = self.get_stock_ticker()
            self.runStock.run()


    print("ATTEMPTING TO ACCESSS STOCK DATA CLASS")
    run_stock = StockDataFetch(parameters)
    run_stock.runClass()

    current_ticker = run_stock.get_stock_ticker()
    download_fin_data = FinancialDataDownloader
    download_fin_data.download_financial_data(current_ticker)

# import os
# import time
# import traceback
# import yfinance as yf
# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
# from scipy.stats import norm
# from tabulate import tabulate
# from prettytable import PrettyTable
# from dataclasses import dataclass
# import openpyxl as px
#
# #from option_data import OptionData
# #from stock_data import StockData
# # import option_data
# # import stock_data
# #OptionData = option_data.OptionData

#
# '''
#     ------ PARAMETERS CLASS ------
#     To Save to MEMORY the parameters for the simulation.
#     Step 1: Create a class with dataclass decorator
#     Step 2: Create a class method to take user input
#
#     --> This class be be cross called between programs
# '''
# #

# @dataclass
# class Parameters():
#     stock_symbol = None
#     initial_equity_price: float
#     strike_price_PUT: float
#     trigger_price_PUT: float
#     time_horizon: int
#     time_step: int
#     time_horizon_step: int
#     annual_expected_return: float
#     volatility: float
#     risk_free_rate: float
#     trigger_price: float
#     num_shares: int
#     num_puts: int
#     margin_requirement: float
#     margin_rate: float
#
#     @classmethod
#     def from_user_input(cls):
#         """Create an instance by taking inputs from the user."""
#         print("[!] Enter the following parameters:")
#         return cls(
#             initial_equity_price=float(input(" [?] Initial Equity Price (e.g., 40.0): ")),
#             strike_price_PUT=float(input("[?] Strike Price for PUT (e.g., 35.0): ")),
#             trigger_price_PUT=float(input("[?] Trigger Price for PUT (e.g., 40.0): ")),
#             time_horizon=int(input("[?] Time Horizon (Days, e.g., 90): ")),
#             time_step=252,  # Set to 252 (trading days in a year)
#             time_horizon_step=int(input("[?] Time Horizon Step (e.g., 90): ")),
#             annual_expected_return=float(input("[?] Annual Expected Return (e.g., 0.05 for 5%): ")),
#             volatility=float(input("[?] Volatility (e.g., 0.3 for 30%): ")),
#             risk_free_rate=float(input("[?] Risk-Free Rate (e.g., 0.01 for 1%): ")),
#             trigger_price=float(input("[?] Trigger Price (e.g., 42.5): ")),
#             num_shares=int(input("[?] Number of Shares (e.g., 1000): ")),
#             num_puts=int(input("[?] Number of Put Contracts (e.g., 10): ")),
#             margin_requirement=float(input("[?] Margin Requirement (e.g., 0.5 for 50%): ")),
#             margin_rate=float(input("[?] Margin Rate (e.g., 0.05 for 5%): ")),
#         )


# '''   ------ Geometric Brownian Motion -------
#     To Simulate stock prices using
#         step 1:craete Random increments using time ste
#         step 2: Calculate Brownian motion
#         step 3: Calculate stock prices using the formula S = S0 * exp(X)
#         return stock prices (s)
#  '''
#
#
# def simulate_stock_prices(inital_price, annual_expected_return, volatility, time_horizon_annual, adjusted_time_step,
#                           time_step):
#     t = np.linspace(0, time_horizon_annual, time_step)
#     randomness = np.random.standard_normal(size=time_step)
#     randomness = np.cumsum(randomness) * np.sqrt(adjusted_time_step)
#     coeiff = (annual_expected_return - 0.5 * volatility ** 2) * t + volatility * randomness
#     new_stock_price = inital_price * np.exp(coeiff)
#     return new_stock_price
#
#
# '''
#     --- BLACK SHOELS PUT OPTION PRICING MODEL ---
#     step 1: Calculate d1 and d2
#     step 2: Calculate put price using the formula
#     return put price
# '''
#
#
# def black_scholes_put(equity_price, put_strike, time_to_expiration, risk_free_rate, volatility):
#     if time_to_expiration <= 0:
#         return max(put_strike - equity_price, 0)
#     d1 = (np.log(equity_price / put_strike) + (risk_free_rate + 0.5 * volatility ** 2) * time_to_expiration) / (
#                 volatility * np.sqrt(time_to_expiration))
#     d2 = d1 - volatility * np.sqrt(time_to_expiration)
#     put_price = put_strike * np.exp(-risk_free_rate * time_to_expiration) * norm.cdf(-d2) - equity_price * norm.cdf(-d1)
#     return put_price
#
#
# '''
#     ------ PLOTTING METHOD ------
#     Plot the stock prices over time using matplotlib.
#     step 1: Create a DataFrame with dates and prices
#     step 2: Plot the stock prices
#     step 3: Save the plot to a file
#
# '''
#
#
# def plot_stock_prices(prices, periods):
#     dates = pd.date_range(start='2023-01-01', periods=periods, freq='B')
#     df = pd.DataFrame({'Date': dates, 'Price': prices})
#
#     plt.figure(figsize=(12, 6))
#     plt.plot(df['Date'], df['Price'], label='Stock Price')
#     plt.title('Simulated Stock Prices over 90 Days with Varying Volatility')
#     plt.xlabel('Date')
#     plt.ylabel('Price ($)')
#     plt.legend()
#     plt.grid(True)
#     plt.tight_layout()
#     plt.show()
#
#     description = 'simulated_stock_prices'
#     #output_file = os.path.join("BLACK_SHOELS_RESULTS", f"{description}.png")
#     output_file = f"{description}.png"
#
#
#     plt.savefig(output_file, dpi=300, bbox_inches='tight')
#
#     print(f'[!] Graph saved to {output_file}')
#
#     ''' ----------------- RUN METHOD ----------------- '''
#
#
# ''' ----------------- RUN METHOD ----------------- '''
#
#
# def mainBuild():
#     ''' INIT '''
#     parameters = Parameters.from_user_input()
#
#     print("\n[!] User-Defined :")
#     for field, value in parameters.__dict__.items():
#         print(f"{field.replace('_', ' ').title()}: {value}")
#
#     ''' PARAMETERS '''
#     adjusted_time_step = 1 / parameters.time_step  # Time step in years (assuming 252 trading days per year)
#
#     # Initialize variables
#     position_values = []
#     put_strike_prices = []
#     put_option_values = []
#     actions = []
#     margin_interests = []
#
#     borrowed_amount = parameters.num_shares * parameters.initial_equity_price * (1 - parameters.margin_requirement)
#     daily_margin_rate = parameters.margin_rate / parameters.time_step
#     total_margin_interest = 0
#
#     ''' Step 1: Simulate Prices,
#         Step 2: Prepare DataFrames,
#          Step 3: Display Table and save data
#     '''
#     np.random.seed(42)
#
#     time_horizon_in_years = parameters.time_horizon * adjusted_time_step
#     N = parameters.time_horizon_step
#
#     simulated_price_index = simulate_stock_prices(
#         parameters.initial_equity_price,
#         parameters.annual_expected_return,
#         parameters.volatility,
#         time_horizon_in_years,
#         adjusted_time_step,
#         N
#     )
#
#     # Prepare pandas DF, store results, and display table on console
#     dates = pd.date_range(start='2023-01-01', periods=parameters.time_horizon_step, freq='B')  # Business days
#     df = pd.DataFrame({'Date': dates, 'Stock Price': simulated_price_index})
#
#     description = "simulated_stock_prices"
#     csv_filename = os.path.join("BLACK_SHOELS_RESULTS", f"{description}.csv")
#     df.to_csv(csv_filename, index=False)
#     convert_csv_to_excel(csv_filename)
#
#     print(f"\n\n Data saved to simulated_stock_prices.csv\n\n")
#
#     ''' PLOT STOCK PRICES, USING TIME_HORIZON_STEP AND SIMULATED_PRICE_INDEX '''
#     plot_stock_prices(simulated_price_index, parameters.time_horizon_step)
#
#
#     # Display the first few rows of the DataFrame in console
#     stock_table = PrettyTable()
#     stock_table.field_names = df.columns.tolist()
#     for row in df.itertuples(index=False):
#         stock_table.add_row(row)
#    # print(stock_table)
#
#
#     '''  Initial put option '''
#     T_initial = parameters.time_horizon * adjusted_time_step  # Time to expiration in years
#     put_price = black_scholes_put(parameters.initial_equity_price, parameters.strike_price_PUT, T_initial,
#                                   parameters.risk_free_rate, parameters.volatility)
#     put_option_value = parameters.num_puts * 100 * put_price
#     current_put_strike = parameters.strike_price_PUT
#     action = f'Bought initial puts at {parameters.strike_price_PUT}'
#     actions.append(action)
#
#     '''
#           Logic:
#               1. loop through each day,
#               2. check for trigger to adjust puts,
#               3.update put option value,
#               4. calculate total position value
#       '''
#     for day in range(parameters.time_horizon_step):
#         day_stock = df['Stock Price'].iloc[day]
#         adjusted_time_to_expiration = (parameters.time_horizon - day) * adjusted_time_step
#         interest = borrowed_amount * daily_margin_rate
#         total_margin_interest += interest
#
#         # Check for trigger to adjust puts
#         if day_stock >= parameters.trigger_price and current_put_strike == parameters.strike_price_PUT:
#             print("\n[!] Trigger price reached. Adjusting put options...")
#             print("... Selling puts and buying new puts with higher strike price")
#             time.sleep(.1)
#
#             put_price_sell = black_scholes_put(day_stock, parameters.strike_price_PUT, adjusted_time_to_expiration,
#                                                parameters.risk_free_rate, parameters.volatility)
#             proceeds = parameters.num_puts * 100 * put_price_sell
#             print(f"\n[+] Sold puts at ${parameters.strike_price_PUT} for ${proceeds:.2f}")
#             time.sleep(.25)
#
#             # Buy new puts with higher strike price
#             current_put_strike = parameters.trigger_price_PUT
#             remaining_days = parameters.time_horizon - day
#             T_new = remaining_days * adjusted_time_step
#             put_price_buy = black_scholes_put(day_stock, parameters.trigger_price_PUT, T_new, parameters.risk_free_rate,
#                                               parameters.volatility)
#             put_option_value = parameters.num_puts * 100 * put_price_buy
#
#             print(f".. Bought puts at K=${parameters.trigger_price_PUT} for ${put_option_value:.2f}")
#             time.sleep(.25)
#
#             print(
#                 f"\n[RESULTS] \n[+] Day {day} Bought puts at ${parameters.trigger_price_PUT} for ${put_option_value:.2f}")
#
#             action = (f' [+] DAY: {day} Bought puts at K=${parameters.trigger_price_PUT} for ${put_option_value:.2f}, '
#                       f'[PRICE ACTION] Sold puts at ${parameters.strike_price_PUT}, bought puts at ${parameters.trigger_price_PUT}')
#             print("[+] Price Action: ", action)
#         else:
#             # Update put option value
#             put_price_current = black_scholes_put(day_stock, current_put_strike, adjusted_time_to_expiration,
#                                                   parameters.risk_free_rate, parameters.volatility)
#             put_option_value = parameters.num_puts * 100 * put_price_current
#             action = '[!] No need for action today'
#             print("[+]\n Price Action: ", action)
#
#         # Total position value
#         position_value = (parameters.num_shares * day_stock) + put_option_value - total_margin_interest
#
#         # Store results
#         position_values.append(position_value)
#         put_strike_prices.append(current_put_strike)
#         put_option_values.append(put_option_value)
#         actions.append(action)
#         margin_interests.append(total_margin_interest)
#
#     # Add results to DataFrame
#     df['Put Strike Price'] = put_strike_prices
#     df['Put Option Value'] = put_option_values
#     df['Margin Interest'] = margin_interests
#     df['Total Position Value'] = position_values
#     df['Action'] = actions[1:]  # Skip the initial action
#     df['Date'] = pd.to_datetime(df['Date']).dt.date
#     df['Value'] = df['Total Position Value'].map('${:,.2f}'.format)
#
#     try:
#
#         data = {
#             'Date': df['Date'],
#             'Stock Price': df['Stock Price'],
#             'Put Strike Price': df['Put Strike Price'],
#             'Put Option Value': df['Put Option Value'],
#             'Margin Interest': df['Margin Interest'],
#             'Total Position Value': df['Total Position Value'],
#             'Action': df['Action'],
#             'Value': df['Value'],
#             "Position Value": position_values,
#         }
#         df = pd.DataFrame(data)
#         description = "simulation_results.csv"
#
#         csv_filename = os.path.join("BLACK_SHOELS_RESULTS", f"{description}")
#         df.to_csv(csv_filename, index=False)
#
#         excel_filename = os.path.join("BLACK_SHOELS_RESULTS", f"{description}.xlsx")
#         df.to_excel(excel_filename, index=False, engine='openpyxl')
#         print(f"[!] Data saved to {csv_filename}")
#
#     except Exception as e:
#         print(f"[-] Error saving data to CSV: {e}")
#         traceback.print_exc()
#         pass
#
#
#
#     # Display the final table
#     put_table = PrettyTable()
#     put_table.field_names = df.columns.tolist()
#     for row in df.itertuples(index=False):
#         put_table.add_row(row)
#     print(put_table)
#
#     description = "simulation_results"
#     csv_filename = os.path.join("BLACK_SHOELS_RESULTS", f"{description}.csv")
#     df.to_csv(csv_filename, index=False)
#     convert_csv_to_excel(csv_filename)
#
#     print(f"[!] Data saved to {csv_filename}")
#
#     plt.figure(figsize=(12, 6))
#     plt.plot(df['Date'], df['Total Position Value'], label='Total Position Value')
#     plt.title('Investor\'s Total Position Value Over {} Days'.format(parameters.time_horizon))
#     plt.xlabel('Date')
#     plt.ylabel('Value ($)')
#     plt.legend()
#     plt.grid(True)
#     plt.tight_layout()
#
#     output_file = 'total_position_value.png'
#     plt.savefig(output_file, dpi=300, bbox_inches='tight')
#     print(f'[!] Graph saved to {output_file}')
#     plt.show()
#
#     print("Plotting the stock price and put strike price over time")
#     plt.figure(figsize=(12, 6))
#     plt.plot(df['Date'], df['Stock Price'], label='Stock Price')
#     plt.plot(df['Date'], df['Put Strike Price'], label='Put Strike Price', linestyle='--')
#     plt.title('Stock Price and Put Strike Price Over {} Days'.format(parameters.time_horizon))
#     plt.xlabel('Date')
#     plt.ylabel('Price ($)')
#     plt.legend()
#     plt.grid(True)
#     plt.tight_layout()
#
#     output_file = '90_day_position_value.png'
#     plt.savefig(output_file, dpi=300, bbox_inches='tight')
#     print(f'[!] Graph saved to {output_file}')
#
#     plt.show()
#
#
# def main():
#     ''' INIT '''
#     # Input_Paramaters = Parameters.from_user_input()
#
#     ''' PARAMETERS '''
#     initial_equity_price = 40.0
#     strike_price_PUT = 35.0
#     trigger_price_PUT = 40.0
#     time_horizon = 90
#     time_step = 252
#     time_horizon_step = time_horizon
#     annual_expected_return = 0.05
#     volatility = 0.3
#     risk_free_rate = 0.01
#     trigger_price = 42.5
#     num_shares = 1000
#     num_puts = 10
#     margin_requirement = 0.5
#     margin_rate = 0.05
#
#     adjusted_time_step = 1 / time_step  # Time step in years (assuming 252 trading days per year)
#
#     # adjusted_time_step = 1 / parameters.time_step  # Time step in years (assuming 252 trading days per year)
#
#     # Initialize variables
#     position_values = []
#     put_strike_prices = []
#     put_option_values = []
#     actions = []
#     margin_interests = []
#     borrowed_amount = num_shares * initial_equity_price * (1 - margin_requirement)
#     daily_margin_rate = margin_rate / 252
#     total_margin_interest = 0
#
#     ''' Step 1: Simulate Prices, Step 2: Prepare DataFrames, Step 3: Display Table and save data  '''
#     # Simulate Prices
#     np.random.seed(42)  # For reproducibility
#     simulated_price_index = simulate_stock_prices(initial_equity_price, annual_expected_return, volatility,
#                                                   time_horizon * adjusted_time_step, adjusted_time_step,
#                                                   time_horizon_step)
#
#     # Prepare pandas DF, store results, and display table on console
#     dates = pd.date_range(start='2023-01-01', periods=time_horizon_step, freq='B')  # Business days
#     df = pd.DataFrame({'Date': dates, 'Stock Price': simulated_price_index})
#
#     description = "simulated_stock_prices"
#     csv_filename = os.path.join("BLACK_SHOELS_RESULTS", f"{description}.csv")
#     df.to_csv(csv_filename, index=False)
#     convert_csv_to_excel(csv_filename)
#
#     print(f"\n\n [!] Data saved to simulated_stock_prices.csv\n\n")
#
#     # Display the first few rows of the DataFrame
#     stock_table = PrettyTable()
#     stock_table.field_names = df.columns.tolist()
#
#     for stock in df.itertuples(index=False):
#         stock_table.add_row(stock)
#     print(stock_table)
#
#     ''' PLOT STOCK PRICES, USING TIME_HORIZON_STEP AND SIMULATED_PRICE_INDEX '''
#     plot_stock_prices(simulated_price_index, time_horizon_step)
#
#     # Initial put option
#     expiration_T_annualized = time_horizon * adjusted_time_step  # Time to expiration in years
#     put_price = black_scholes_put(initial_equity_price, strike_price_PUT, expiration_T_annualized, risk_free_rate,
#                                   volatility)
#     put_option_value = num_puts * 100 * put_price
#     current_put_strike = strike_price_PUT
#     action = f'Bought initial puts at {strike_price_PUT}'
#     actions.append(action)
#
#     '''
#         Logic:
#             1. loop through each day,
#             2. check for trigger to adjust puts,
#             3.update put option value,
#             4. calculate total position value
#     '''
#     for day in range(time_horizon_step):
#         day_stock = df['Stock Price'].iloc[day]
#         adjusted_time_to_expiration = (time_horizon - day) * adjusted_time_step  # Remaining time to expiration
#         interest = borrowed_amount * daily_margin_rate
#         total_margin_interest += interest
#
#         # Check for trigger to adjust puts
#         if day_stock >= trigger_price and current_put_strike == strike_price_PUT:
#             print("\n[!] Trigger price reached. Adjusting put options...")
#             print("... Selling puts and buying new puts with higher strike price")
#             time.sleep(.1)
#
#             put_price_sell = black_scholes_put(day_stock, strike_price_PUT, adjusted_time_to_expiration, risk_free_rate,
#                                                volatility)
#             proceeds = num_puts * 100 * put_price_sell
#             print(f"\n[+] Sold puts at ${strike_price_PUT} for ${proceeds:.2f}")
#             time.sleep(.25)
#
#             # Buy new puts with higher strike price
#             print(f".. Bought puts at K=${trigger_price_PUT} for ${put_option_value:.2f}")
#             time.sleep(.25)
#
#             current_put_strike = trigger_price_PUT
#             remaining_days = time_horizon - day
#             T_new = remaining_days * adjusted_time_step
#             put_price_buy = black_scholes_put(day_stock, trigger_price_PUT, T_new, risk_free_rate, volatility)
#             put_option_value = num_puts * 100 * put_price_buy
#
#             print(f"\n[RESULTS] \n[+] day {day} Bought puts at ${trigger_price_PUT} for ${put_option_value:.2f}")
#
#             action = (f' [+] DAY: {day} Bought puts at K=${trigger_price_PUT} for ${put_option_value:.2f}, '
#                       f'[PRICE ACTION] Sold puts at ${strike_price_PUT}, bought puts at ${trigger_price_PUT}')
#             print("[+] Price Action: ", action)
#         else:
#             # Update put option value
#             put_price_current = black_scholes_put(day_stock, current_put_strike, adjusted_time_to_expiration,
#                                                   risk_free_rate, volatility)
#             put_option_value = num_puts * 100 * put_price_current
#             action = '[!] No need for action today'
#             print("[+]\n Price Action: ", action)
#
#         # Total position value
#         position_value = (num_shares * day_stock) + put_option_value - total_margin_interest
#
#         # Store results
#         position_values.append(position_value)
#         put_strike_prices.append(current_put_strike)
#         put_option_values.append(put_option_value)
#         actions.append(action)
#         margin_interests.append(total_margin_interest)
#
#     # Add results to DataFrame
#
#     df['Put Strike Price'] = put_strike_prices
#     df['Put Option Value'] = put_option_values
#     df['Margin Interest'] = margin_interests
#     df['Total Position Value'] = position_values
#     df['Action'] = actions[1:]  # Skip the initial action
#
#     put_table = PrettyTable()
#     put_table.field_names = df.columns.tolist()
#     for stock in df.itertuples(index=False):
#         put_table.add_row(stock)
#     print(put_table)
#
#     description = "simulation_results"
#     csv_filename = os.path.join("BLACK_SHOELS_RESULTS", f"{description}.csv")
#     df.to_csv(csv_filename, index=False)
#     convert_csv_to_excel(csv_filename)
#
#
#     df = pd.DataFrame({
#         'Stock Price': simulated_price_index,
#         'Date': dates,
#         'Put Strike Price': put_strike_prices,
#         'Put Option Value': put_option_values,
#         'Margin Interest': margin_interests,
#         'Total Position Value': position_values,
#         'Action': actions[1:],  # Skip the initial action, if needed
#     })
#
#     description = "simulation_results2"
#     csv_filename = os.path.join("BLACK_SHOELS_RESULTS", f"{description}.csv")
#     csv_filename = df.to_csv(csv_filename, index=False)
#
#     convert_csv_to_excel(csv_filename)
#
#     print(f"[!] Data saved to {csv_filename}")
#
#     print("\n[!] Plotting the total position value over time")
#     plt.figure(figsize=(12, 6))
#     plt.plot(df['Date'], df['Total Position Value'], label='Total Position Value')
#     plt.title('Investor\'s Total Position Value Over 90 Days')
#     plt.xlabel('Date')
#     plt.ylabel('Value ($)')
#     plt.legend()
#     plt.grid(True)
#     plt.tight_layout()
#     plt.show()
#
#     output_file = '90_day_position_value.png'
#    # output_file = os.path.join("BLACK_SHOELS_RESULTS", f"{description}.png")
#     plt.savefig(output_file, dpi=300, bbox_inches='tight')
#     print(f"[!] Data saved to {output_file}")
#
#     print("\n[!] Plotting the stock price and put strike price over time")
#     plt.figure(figsize=(12, 6))
#     plt.plot(df['Date'], df['Stock Price'], label='Stock Price')
#     plt.plot(df['Date'], df['Put Strike Price'], label='Put Strike Price', linestyle='--')
#     plt.title('Stock Price and Put Strike Price Over 90 Days')
#     plt.xlabel('Date')
#     plt.ylabel('Price ($)')
#     plt.legend()
#     plt.grid(True)
#     plt.tight_layout()
#     plt.show()
#
#     description = 'stock+put_price_plot.png'
#     output_file = os.path.join("BLACK_SHOELS_RESULTS", f"{description}.png")
#
#     plt.savefig(description, dpi=300, bbox_inches='tight')
#     print(f"[!] Data saved to {output_file}")
#
#     plt.savefig(output_file, dpi=300, bbox_inches='tight')
#     print(f"[!] Data saved to {output_file}")
#
#
# '''--------------- HELPER FUNCTIONS ----------------
#
#     1. Convert CSV to Excel
#     2. Create Results Folder
#     3. Main Method to run the program
# '''
#
#
# def convert_csv_to_excel(csv_file_path, excel_file_path=None):
#     """ Convert a CSV file to an Excel file using pandas.
#     :param csv_file_path: Path to the input CSV file.
#     :param excel_file_path: Path to save the output Excel file. If None, saves in the same directory as the CSV.
#     """
#     try:
#         ''' Check if the CSV file exists '''
#         if not os.path.exists(csv_file_path):
#             print(f"Error: The file '{csv_file_path}' does not exist.")
#             return
#
#         df = pd.read_csv(csv_file_path)
#
#         # Generate Excel file path if not provided
#         if excel_file_path is None:
#             base_name = os.path.splitext(csv_file_path)[0]
#             excel_file_path = f"{base_name}.xlsx"
#
#         df.to_excel(excel_file_path, index=False, engine='openpyxl')
#         print(f"[!] Successfully converted '{csv_file_path}' to '{excel_file_path}'")
#
#     except Exception as e:
#         print(f"[-] An error in converting .CVS  to EXCEL : {e}")
#         traceback.print_exc()
#
#
# def create_results_folder():
#     ''' 2.  CREATE RESULTS FOLDER '''
#     folder_name = "BLACK_SHOELS_RESULTS"
#
#     try:
#         os.makedirs(folder_name, exist_ok=True)
#         print(f"[+] Folder '{folder_name}'\n created with read and write permissions.")
#         os.chmod(folder_name, 0o777)
#
#     except Exception as e:
#         print(f"[!] An error occurred while creating the folder: {e}")
#         traceback.print_exc()
#
#
# ''' -------------------------------------------------------- '''
# '''
#     MAIN METHOD TO RUN THE PROGRAM '''
# ''''
#    -----  MAIN METHOD TO RUN THE PROGRAM -----
#     1. Create a results folder
#     2. main() to run the program with hard coded variables
#     3. mainBuild() to take user inputs and store them in memory
#  func main() will remain commented out, unless debugging is needed
# '''
# if __name__ == "__main__":
#
#     create_results_folder()
#     if not os.path.exists("BLACK_SHOELS_RESULTS"):
#         print("[!] Error: No STOCK_RESULTS folder found. Exiting.")
#
#
#     # R = RocketAnimation()
#     # R.run()  # Run the Rocket Animation
#
#     mainBuild()
#
#     class StockData:
#         def __init__(self, stock_symbol):
#             self.stock_symbol = stock_symbol
#             self.data = self.get_stock_data()
#
#         @staticmethod
#         def get_stock_ticker():
#             return input("Enter Stock: ")
#
#         def get_stock_data(self):
#             stock = yf.Ticker(self.stock_symbol)
#             data = stock.history(period="1y")
#             return data
#
#         def run(self):
#             StockData.__init__(self, stock_symbol=StockData.get_stock_ticker()) # get the stock ticker
#             print("\n" , self.data)
#
#         def __repr__(self):
#             return str(self.data)
#
#         def __str__(self):
#             return str(self.data)
#
#
#         runStockData = StockData(stock_symbol="AAPL")
#

#
#
#
#     # main()  # Uncomment to run the program with hard-coded variables
#
