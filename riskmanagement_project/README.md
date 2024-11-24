Stock Price Simulation and Option Pricing

This Python program simulates stock prices using Geometric Brownian Motion, calculates put option prices using the Black-Scholes formula, and evaluates the total position value over a specified time horizon. It also generates visualizations of the stock prices and total position value over time.

Table of Contents

	•	Features
	•	Prerequisites
	•	Installation
	•	Usage
	•	Parameters
	•	Running the Program
	•	Output
	•	Sample Graphs
	•	Examples
	•	Dependencies
	•	License
 
Features

	•	Simulates stock prices over a given time horizon using Geometric Brownian Motion.
	•	Calculates put option prices using the Black-Scholes formula.
	•	Allows dynamic adjustment of put options based on a trigger price.
	•	Computes the total position value considering margin interest.
	•	Generates plots for:
	•	Simulated stock prices over time.
	•	Investor’s total position value over time.
	•	Stock price and put strike price over time.
	•	Stores simulation results in CSV files for further analysis.

Prerequisites

	•	Python 3.x installed on your system.
	•	Basic understanding of financial concepts like stock pricing, options, and margin trading.


Installation

	1.	Clone the Repository:
    
    $ git clone https://github.com/yourusername/stock-option-simulation.git

	2.	Navigate to the Project Directory:
        
        $ cd stock-option-simulation

	3.	Install Required Python Packages:
        You can install the required packages using pip:
        pip install -r requirements.txt



Usage


Output:

 Graphs:
    •	simulated_stock_prices.png: Plot of simulated stock prices over time.
    •	total_position_value.png: Plot of the investor’s total position value over time.
    •	stock_put_price_plot.png: Plot showing both stock price and put strike price over time.

 CSV Files
	•	simulated_stock_prices.csv: Simulated stock prices over time.
	•	simulation_results.csv: Detailed simulation results including stock price, put option value, margin interest, total position value, and actions.

 Console Output
	•	Displays user-defined parameters.
	•	Shows simulation data in tabular form.
	•	Provides actions taken during the simulation (e.g., adjusting put options).

The program generates the following outputs:
	•	Console Output:
	•	Displays user-defined parameters.
	•	Shows simulation data in tabular form.
	•	Provides actions taken during the simulation (e.g., adjusting put options).
	•	CSV Files:
	•	simulated_stock_prices.csv: Contains simulated stock prices over time.
	•	simulation_results.csv: Contains detailed simulation results, including stock price, put option value, margin interest, total position value, and actions.
	•	Graphs:
	•	simulated_stock_prices.png: Plot of simulated stock prices over time.
	•	total_position_value.png: Plot of the investor’s total position value over time.
	•	stock_put_price_plot.png: Plot showing both stock price and put strike price over time.
The graphs are saved in the same directory as the script.


Parameters

The program requires several input parameters to perform the simulation. You can either input them manually when prompted or modify the default values in the code.
	•	Initial Equity Price (initial_equity_price): The starting price of the stock (e.g., $40.0).
	•	Strike Price for PUT (strike_price_PUT): The strike price of the initial put option (e.g., $35.0).
	•	Trigger Price for PUT (trigger_price_PUT): The stock price at which you adjust the put option (e.g., $40.0).
	•	Time Horizon (time_horizon): Total number of days to simulate (e.g., 90).
	•	Time Step (time_step): Number of trading days in a year (typically 252).
	•	Annual Expected Return (annual_expected_return): Expected annual return of the stock (e.g., 0.05 for 5%).
	•	Volatility (volatility): Annual volatility of the stock price (e.g., 0.3 for 30%).
	•	Risk-Free Rate (risk_free_rate): Annual risk-free interest rate (e.g., 0.01 for 1%).
	•	Trigger Price (trigger_price): Stock price at which you adjust your strategy (e.g., $42.5).
	•	Number of Shares (num_shares): Number of shares purchased (e.g., 1000).
	•	Number of Put Contracts (num_puts): Number of put option contracts (e.g., 10).
	•	Margin Requirement (margin_requirement): Percentage of the stock purchase price that must be covered by cash (e.g., 0.5 for 50%).
	•	Margin Rate (margin_rate): Annual interest rate charged on borrowed funds (e.g., 0.05 for 5%).

Example:
    
    Sample Console Output:
    [!] Enter the following parameters:
    [?] Initial Equity Price (e.g., 40.0): 40.0
    [?] Strike Price for PUT (e.g., 35.0): 35.0
    [?] Trigger Price for PUT (e.g., 40.0): 40.0
    [?] Time Horizon (Days, e.g., 90): 90
    [?] Time Horizon Step (e.g., 90): 90
    [?] Annual Expected Return (e.g., 0.05 for 5%): 0.05
    [?] Volatility (e.g., 0.3 for 30%): 0.3
    [?] Risk-Free Rate (e.g., 0.01 for 1%): 0.01
    [?] Trigger Price (e.g., 42.5): 42.5
    [?] Number of Shares (e.g., 1000): 1000
    [?] Number of Put Contracts (e.g., 10): 10
    [?] Margin Requirement (e.g., 0.5 for 50%): 0.5
    [?] Margin Rate (e.g., 0.05 for 5%): 0.05
    
    [!] User-Defined Parameters:
    Initial Equity Price: 40.0
    Strike Price Put: 35.0
    Trigger Price Put: 40.0
    Time Horizon: 90
    Time Step: 252
    Time Horizon Step: 90
    Annual Expected Return: 0.05
    Volatility: 0.3
    Risk Free Rate: 0.01
    Trigger Price: 42.5
    Num Shares: 1000
    Num Puts: 10
    Margin Requirement: 0.5
    Margin Rate: 0.05
    
    [!] Data saved to simulated_stock_prices.csv
    
    ...
    
    [!] Graph saved to simulated_stock_prices.png
