import yfinance as yf
import os

# Define the ticker and output directory
ticker_symbol = "GOOG"
output_directory = "financial_documents"

# Create the output directory if it doesn't exist
os.makedirs(output_directory, exist_ok=True)

# Fetch the ticker data
ticker = yf.Ticker(ticker_symbol)

# Download and save financial information
def save_to_csv(data, filename):
    """Save DataFrame to CSV file if data exists."""
    if data is not None and not data.empty:
        file_path = os.path.join(output_directory, filename)
        data.to_csv(file_path, index=True)
        print(f"Saved {filename} to {file_path}")
    else:
        print(f"No data found for {filename}.")

# Financial documents to fetch
financial_data = {
    "balance_sheet": ticker.balance_sheet,
    "income_statement": ticker.financials,
    "cash_flow": ticker.cashflow,
    "earnings": ticker.earnings,
    "quarterly_earnings": ticker.quarterly_earnings,
    "sustainability": ticker.sustainability,
    "recommendations": ticker.recommendations,
}

# Save each type of financial data to CSV
for doc_name, data in financial_data.items():
    save_to_csv(data, f"{ticker_symbol}_{doc_name}.csv")


print("All available financial documents have been downloaded.")