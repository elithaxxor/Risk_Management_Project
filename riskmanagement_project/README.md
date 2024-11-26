Below is a sample README.md file for your project, including details about its purpose, functionality, setup, and usage.

Python Stock and Option Data Analysis

Description

This Python project provides tools to analyze stock and option data. It includes scripts for:
	•	Fetching stock and historical data (stock_data.py)
	•	Working with options and their historical price movements (option_data.py)
	•	Running the main application workflow (main.py).

The project uses the yfinance library to retrieve financial data and beautifulsoup4 for web scraping of key statistics. Results are stored in CSV files within a dedicated directory.

Features

	•	Fetch and process stock data, including moving averages and significant drops.
	•	Analyze options data based on strike prices, expiration dates, and types (calls/puts).
	•	Save results in CSV format within a directory (STOCK_RESULTS).
	•	Plot historical stock price data with calculated indicators.
	•	Scrape and save key statistics from Yahoo Finance.

Prerequisites

	•	Python version: 3.8 or higher
	•	Libraries listed in requirements.txt:
	•	numpy
	•	pandas
	•	matplotlib
	•	scipy
	•	tabulate
	•	prettytable
	•	yfinance
	•	requests
	•	beautifulsoup4

Installation

	1.	Clone the repository or download the project files.
	2.	Install dependencies using pip:

pip install -r requirements.txt


	3.	Ensure your environment has write permissions for the current working directory.

Usage

Running Scripts

Main Workflow

Run the main script to interact with the stock and option data tools:

python main.py

Stock Data Analysis

Analyze stock data for a specific ticker:

python stock_data.py

You will be prompted for:
	•	Ticker symbol (e.g., AAPL for Apple Inc.)
	•	End date (YYYY-MM-DD format)
	•	Maximum drop (points considered significant)
	•	Moving average periods (e.g., 20,50,200)

Results:
	•	CSV files with historical data and indicators saved to the STOCK_RESULTS folder.
	•	Visualization of stock price trends and indicators.

Option Data Analysis

Fetch and analyze option data:

python option_data.py

You will be prompted for:
	•	Stock symbol
	•	Expiration date (YYYY-MM-DD)
	•	Option type (call or put)
	•	Strike price

Outputs

Folder Structure

The project creates a folder named STOCK_RESULTS in the same directory. All CSV outputs are saved here:
	•	{TICKER}_historical_data.csv: Historical stock data with indicators.
	•	{TICKER}_key_statistics.csv: Scraped key statistics for the ticker.
	•	Option data files based on user inputs.

Example

Stock Data Analysis

Enter the ticker symbol (e.g., AAPL): AAPL
Enter the end date in YYYY-MM-DD format (or leave blank for today): 2024-12-31
Enter the maximum amount of points for a significant drop (e.g., 100): 50
Enter the moving average periods (e.g., 20,50,200): 20,50,200

Outputs:
	•	CSV files in STOCK_RESULTS/
	•	Visualization of stock price trends.

Option Data Analysis

Enter the stock symbol (e.g., AAPL): TSLA
Enter the option expiration date in YYYY-MM-DD format (or leave blank for the nearest expiration): 2024-10-27
Enter the option type (call/put): call
Enter the strike price (e.g., 200): 300

Output:
	•	Option history and analysis results.

Contributing

	1.	Fork the repository.
	2.	Create a new branch for your feature: git checkout -b feature-name.
	3.	Commit your changes: git commit -m 'Add some feature'.
	4.	Push to the branch: git push origin feature-name.
	5.	Open a Pull Request.

License

This project is licensed under the MIT License.

Acknowledgements

	•	Yahoo Finance for providing data through yfinance.
	•	Contributors to the Python libraries used in this project.

Feel free to modify the README.md to suit your specific requirements or project structure. Let me know if you’d like to add more sections or details!