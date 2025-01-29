## Import Packages ##

import yfinance as yf
import streamlit as st
from prophet import Prophet     
import pandas as pd
import matplotlib.pyplot as plt

## Defining Functions ##

# Downloading Data From yFinance #
def get_stock_data(ticker, start_date='1998-01-01'):                  
    stock_df = yf.download(ticker, start=start_date)                  
    stock_df['MA_50'] = stock_df['Close'].rolling(window=50).mean()   
    stock_df['MA_100'] = stock_df['Close'].rolling(window=100).mean()
    stock_df['MA_200'] = stock_df['Close'].rolling(window=200).mean()  
    stock_df = stock_df.dropna()                                      
    return stock_df

# Prepping Stock Data Frame into Prophet Data Frame #
def prepare_prophet_stock_data(stock_df):          
    prophet_df = stock_df[['Close']].reset_index() 
    prophet_df.columns = ['ds', 'y']               
    return prophet_df

# Main Function #
def main():
    # Set Streamlit page configuration for theme
    st.set_page_config(
        page_title="JXS Prophet Stock Prediction App",
        page_icon="📈",
        layout="wide"
    )

    # Custom CSS for black and purple theme with Google Sans font
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&display=swap');
    
    .stApp {
        background-color: black;
        color: white;
        font-family: 'Google Sans', sans-serif;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: purple;
        font-family: 'Google Sans', sans-serif;
        font-weight: 700;
    }
    
    .stButton>button {
        background-color: purple;
        color: white;
        border-radius: 5px;
        border: 1px solid purple;
        font-family: 'Google Sans', sans-serif;
    }
    
    .stTextInput>div>div>input {
        background-color: black;
        color: white;
        border: 1px solid purple;
        font-family: 'Google Sans', sans-serif;
    }
    
    .stSlider>div>div>div>div {
        background-color: purple;
    }
    
    .stDataFrame {
        font-family: 'Google Sans', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("JXS Prophet Stock Prediction App")
    
    # Introductory Paragraph
    st.write("""
    ### How the Model Works
    This app uses **Facebook's Prophet** model to predict stock prices. Prophet is a time series forecasting tool that decomposes data into trend, seasonality, and holiday effects. It uses an additive model to fit non-linear trends and incorporates seasonality (yearly, weekly, and daily) to make predictions. The model is particularly useful for stock price forecasting because it handles missing data and outliers well, and it provides confidence intervals for predictions.

    The app also calculates **moving averages (50-day, 100-day, and 200-day)** to provide additional insights into stock trends. These moving averages help identify long-term and short-term trends in the stock's performance.
    """)
    
    # Disclaimer
    st.warning("""
    ### Disclaimer
    **These stock value predictions are for testing and educational purposes only.** They should not be used for making real-world financial decisions. Stock markets are highly volatile, and predictions are inherently uncertain. Always consult with a qualified financial advisor before making any investment decisions.
    """)
    
    # User Input
    ticker = st.text_input('Enter Stock Ticker (e.g., XYZ):', 'XYZ')
    
    # Add a range slider for prediction days
    prediction_days = st.slider('Select number of days to predict (0-730):', 0, 730, 365)
    
    if st.button('Predict'):
        with st.spinner('Fetching data and making predictions...'):
            # Get data and calculate moving averages
            df = get_stock_data(ticker)
            
            # Display Stock Data section
            st.subheader(f"{ticker} Raw Stock Data")
            st.write(f"Data from {df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')}")
            
            # Modified dataframe with renamed date column
            display_df = df.reset_index().rename(columns={'Date': 'Dates'})
            st.dataframe(display_df)
            
            # Prepare Prophet data
            prophet_df = prepare_prophet_stock_data(df)
            
            # Create and fit model
            model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=False,
                daily_seasonality=False,
                changepoint_prior_scale=0.5
            )
            model.fit(prophet_df)
            
            # Create future dataframe with dynamic periods based on slider
            future = model.make_future_dataframe(periods=prediction_days, freq='B')
            
            # Generate forecast
            forecast = model.predict(future)
            
            # Create plots
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
            
            # Modified historical data plot title
            ax1.plot(df['Close'], label='Close Price', color='purple')
            ax1.plot(df['MA_50'], label='50-day MA', color='orange')
            ax1.plot(df['MA_100'], label='100-day MA', color='green')
            ax1.plot(df['MA_200'], label='200-day MA', color='red')
            ax1.set_title(f'{ticker} Historical Prices & Moving Averages', color='black')
            ax1.set_facecolor('white')
            ax1.legend()
            ax1.tick_params(colors='black')
            ax1.spines['bottom'].set_color('black')
            ax1.spines['left'].set_color('black')
            
            # Prophet forecast plot
            model.plot(forecast, ax=ax2)
            ax2.set_title(f'{ticker} {prediction_days}-Day Price Prediction', color='black')
            ax2.set_xlabel('Date', color='black')
            ax2.set_ylabel('Price', color='black')
            ax2.set_facecolor('white')
            ax2.tick_params(colors='black')
            ax2.spines['bottom'].set_color('black')
            ax2.spines['left'].set_color('black')
            
            st.pyplot(fig)
            
            # Show components
            st.subheader('Forecast Components')
            components_fig = model.plot_components(forecast)
            st.pyplot(components_fig)
            
            # Additional Graphs for Insights
            st.subheader('Additional Insights')
            
            # Plot Historical vs Predicted
            fig2, ax3 = plt.subplots(figsize=(12, 6))
            ax3.plot(df['Close'], label='Historical Close Price', color='purple')
            ax3.plot(forecast.set_index('ds')['yhat'], label='Predicted Close Price', color='orange')
            ax3.fill_between(forecast.set_index('ds').index, forecast['yhat_lower'], forecast['yhat_upper'], color='orange', alpha=0.2)
            ax3.set_title(f'{ticker} Historical vs Predicted Prices', color='white')
            ax3.set_xlabel('Date', color='black')
            ax3.set_ylabel('Price', color='black')
            ax3.set_facecolor('white')
            ax3.legend()
            ax3.tick_params(colors='black')
            ax3.spines['bottom'].set_color('black')
            ax3.spines['left'].set_color('black')
            st.pyplot(fig2)
            
            # Plot Confidence Intervals
            fig3, ax4 = plt.subplots(figsize=(12, 6))
            ax4.plot(forecast.set_index('ds')['yhat'], label='Predicted Close Price', color='purple')
            ax4.fill_between(forecast.set_index('ds').index, forecast['yhat_lower'], forecast['yhat_upper'], color='purple', alpha=0.2)
            ax4.set_title(f'{ticker} {prediction_days}-Day Price Prediction with Confidence Intervals', color='white')
            ax4.set_xlabel('Date', color='black')
            ax4.set_ylabel('Price', color='black')
            ax4.set_facecolor('white')
            ax4.legend()
            ax4.tick_params(colors='black')
            ax4.spines['bottom'].set_color('black')
            ax4.spines['left'].set_color('black')
            st.pyplot(fig3)
            
            # Combined Table of Historical and Predicted Values
            st.subheader('Combined Historical and Predicted Values')
            combined_df = pd.concat([
                df[['Close']].rename(columns={'Close': 'Historical Close'}),
                forecast.set_index('ds')[['yhat', 'yhat_lower', 'yhat_upper']].rename(columns={
                    'yhat': 'Predicted Close',
                    'yhat_lower': 'Predicted Lower Bound',
                    'yhat_upper': 'Predicted Upper Bound'
                })
            ], axis=1)
            st.dataframe(combined_df)
            
            # Forecast Summary Analysis
            st.subheader("Forecast Summary and Insights")
            
            # Convert pandas elements to native Python types
            last_close = float(df['Close'].iloc[-1])
            last_forecast = forecast.iloc[-1]
            predicted_close = float(last_forecast['yhat'])
            lower_bound = float(last_forecast['yhat_lower'])
            upper_bound = float(last_forecast['yhat_upper'])
            trend_change = ((float(last_forecast['trend']) - float(forecast['trend'].iloc[0])) / float(forecast['trend'].iloc[0])) * 100
            
            summary = f"""
            **Key Forecast Insights for {ticker}:**
            - **Final Historical Close**: ${last_close:.2f}
            - **{prediction_days}-Day Price Prediction**: ${predicted_close:.2f} 
            - **Prediction Range**: ${lower_bound:.2f} - ${upper_bound:.2f}
            - **Trend Direction**: {'Bullish' if trend_change > 0 else 'Bearish'} ({abs(trend_change):.1f}% {'increase' if trend_change > 0 else 'decrease'})
            - **Seasonality Impact**: {'Significant' if abs(forecast['yearly'].mean()) > 0.5 else 'Moderate'} yearly seasonality detected
            - **Moving Average Status**: {'Golden Cross' if df['MA_50'].iloc[-1] > df['MA_200'].iloc[-1] else 'Death Cross'} pattern identified
            
            **Analysis Summary:**
            The forecast suggests a {trend_change:.1f}% {'growth' if trend_change > 0 else 'decline'} over the next {prediction_days} days. 
            Historical moving averages indicate {'strong upward' if df['MA_50'].iloc[-1] > df['MA_200'].iloc[-1] else 'downward'} momentum. 
            Investors should consider the {upper_bound - lower_bound:.2f} price range volatility when evaluating potential positions.
            """
            
            st.markdown(summary)
            st.success('Prediction completed!')

if __name__ == '__main__':
    main()
