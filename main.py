import matplotlib.pyplot as plt
from config import api, secret
import numpy as np
from pybit.unified_trading import HTTP
from talib import abstract
import time

client = HTTP(
    testnet=False,
    api_key=api,
    api_secret=secret
)

symbol = 'ETHUSDT'
threshold_percentage = 0.12
interval = '5'


def get_klines(symbol, interval):
    klines = client.get_kline(category='linear', symbol=symbol, interval=interval)
    klines = klines['result']['list']
    return klines


# print(get_klines(symbol, interval))

def get_close_data(klines):
    close = [float(i[4]) for i in klines]
    close = close[::-1]
    close = np.array(close)
    return close

# print(get_close_data(get_klines(symbol, interval)))

def get_sma(close):
    SMA = abstract.Function('sma')
    data = SMA(close, timeperiod=20)
    return data


def show_data():
        """
        Function to plot Close prices and SMA (Simple Moving Average) over time.
        """

        # Create a new figure with a specific size
        plt.figure(figsize=(14, 7))

        # Plot Close prices with blue color
        plt.plot(close, label='Close prices', color='blue')

        # Plot SMA with orange color
        plt.plot(data, label='SMA', color='orange')

        # Set the title of the plot
        plt.title('Close Prices and SMA 20')

        # Label the x-axis
        plt.xlabel('Time')

        # Label the y-axis
        plt.ylabel('Price')

        # Display legend
        plt.legend()

        # Display the plot
        plt.show()

# show_data()

while True:
    close = get_close_data(get_klines(symbol, interval))
    data = get_sma(close)
    last_close = close[-1]
    last_sma = data[-1]
    print(f'last_close; {last_close}, last_sma: {last_sma}')

    if last_sma is not None:
        deviation = abs((last_close - last_sma) / last_sma) * 100
        print(f'deviation: {deviation}')

        if deviation < threshold_percentage:
            if last_close <= last_sma:
                print('Open sell order(short)')
                order = client.place_active_order(
                    category='linear',
                    symbol=symbol,
                    side='sell',
                    order_type='market',
                    qty=0.5,
                    time_in_force='post_only',
                    reduce_only=True
                )
                print(order)

                while True:
                    close = get_close_data(get_klines(symbol, interval))
                    data = get_sma(close)
                    last_close = close[-1]
                    last_sma = data[-1]
                    print(f'last_close; {last_close}, last_sma: {last_sma}')

                    if last_sma is not None:
                        deviation = abs((last_close - last_sma) / last_sma) * 100
                        print(f'deviation: {deviation}')

                        if deviation > threshold_percentage:
                            if last_close >= last_sma:
                                print('Open buy order(short)')
                                order = client.place_active_order(
                                    category='linear',
                                    symbol=symbol,
                                    side='buy',
                                    order_type='market',
                                    qty=0.5,
                                    time_in_force='post_only',
                                    reduce_only=True
                                )
                                print(order)
                                break
                            else:
                                print('Waiting for next close price...')
                                print(f'last_close; {last_close}, last_sma: {last_sma}')
                                time.sleep(20)
                        break
                else:
                    print('Insufficient data to calculate SMA')
                    print(f'Sleep {interval} min')
                    time.sleep(interval)

