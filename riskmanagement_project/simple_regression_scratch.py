''' Simple linear regression from scratch overview
OptionSimulator
--> simulated price index'''


import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import yfinance as yf
import datetime
from stock_data import StockData
from main import Parameters



class SimpleLinearRegressor:
    def __init__(self):
        self.model = None
        self.X = None
        self.y = None

    def fit(self, X, y):
        """Fit the linear regression model using the provided data."""
        self.X = np.array(X).reshape(-1, 1)
        self.y = np.array(y)

        self.model = LinearRegression()
        self.model.fit(self.X, self.y)
        print("Model training completed.")

    def predict(self, X_new):
        """Predict using the linear regression model."""
        if self.model is None:
            raise ValueError("Model has not been trained yet. Call the 'fit' method first.")

        X_new_reshaped = np.array(X_new).reshape(-1, 1)
        predictions = self.model.predict(X_new_reshaped)
        return predictions

    def plot_regression_line(self):
        """Plot the regression line along with the data points."""
        if self.model is None or self.X is None or self.y is None:
            raise ValueError("Model has not been trained yet. Call the 'fit' method first.")

        y_pred = self.model.predict(self.X)

        plt.scatter(self.X, self.y, color='blue', label='Actual Data')
        plt.plot(self.X, y_pred, color='red', linewidth=2, label='Regression Line')
        plt.title('Simple Linear Regression')
        plt.xlabel('Day Number')
        plt.ylabel('Stock Price')
        plt.legend()
        plt.show()

    def get_coefficients(self):
        """Get the coefficients of the linear regression model."""
        if self.model is None:
            raise ValueError("Model has not been trained yet. Call the 'fit' method first.")

        slope = self.model.coef_[0]
        intercept = self.model.intercept_
        return slope, intercept

class StockPredictor(StockData, Parameters):
    def __init__(self):
        super().__init__()
        self.regressor = SimpleLinearRegressor()
        self.X = None
        self.y = None
        self.ticker = Parameters.stock_symbol

    def prepare_data(self):
        """Prepare the data for regression analysis."""
        super().prepare_data()
        if self.df is not None:
            self.X = self.df['Day'].values
            self.y = self.df['Close'].values
        else:
            print("Dataframe is empty. Cannot prepare data.")
            reg = StockData.simple_regression
            self.X, self.Y = StockData.simple_regression
            print("[!] Data has been prepared for regression analysis.")
            print(f"X: {self.X}\n Y: {self.Y}")

    def fit_model(self):
        """Fit the regression model using the prepared data."""
        if self.X is not None and self.y is not None:
            self.regressor.fit(self.X, self.y)
        else:
            print("Data not prepared. Cannot fit model.")

    def predict_future_prices(self, days_ahead=3):
        """Predict future stock prices for the next 'days_ahead' days."""
        if self.X is None:
            print("Model has not been trained or data not prepared.")
            return

        last_day = self.X[-1]
        X_future = [last_day + i for i in range(1, days_ahead + 1)]
        predictions = self.regressor.predict(X_future)
        print(f"Predicted prices for days {X_future}: {predictions}")
        return X_future, predictions

    def plot_regression_line(self):
        """Plot the regression line along with the data points."""
        self.regressor.plot_regression_line()

    def run(self):
        """Execute the workflow of fetching data, training the model, and making predictions."""
        data_fetched = self.fetch_regression_data(start_date=self.start_date,
                                       end_date=self.end_date_input)

        print("[!] Fetching for regression data...\n dates are: ", self.start_date, self.end_date_input)


        if data_fetched:
            self.prepare_data()
            self.fit_model()
            self.predict_future_prices(days_ahead=3)
            self.plot_regression_line()
        else:
            print("Data fetching failed. Exiting.")
