import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import datetime

# Get user input
ticker = input("Enter the ticker symbol (e.g., ^GSPC for S&P 500): ")
end_date_input = input("Enter the end date in YYYY-MM-DD format (or leave blank for today): ")
max_drop_input = input("Enter the maximum amount of points for a significant drop (e.g., 1000): ")
moving_averages_input = input("Enter the moving average periods (e.g., 20,50,200): ")

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
df = yf.download(ticker, start=start_date, end=end_date)

# Check if data was fetched successfully
if df.empty:
    print(f"No data found for ticker '{ticker}' between {start_date.date()} and {end_date.date()}.")
    exit()

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
plt.fill_between(df['Date'], df['Close'], where=df['Significant Drop'], color='red', alpha=0.5, label=f'Drop ≥ {max_drop} points')

# Customize the plot
plt.title(f'{ticker} Price from {start_date.date()} to {end_date.date()}')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.grid(True)
plt.tight_layout()

# Display the plot
plt.show()