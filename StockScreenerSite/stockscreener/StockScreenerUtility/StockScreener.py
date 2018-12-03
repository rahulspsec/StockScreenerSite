"""
Created on Tue Oct 23 03:00:14 2018

@author: Rahul
"""

import numpy as np
import pandas as pd
import math
import random
import datetime
from logging import info
from .constant import STOCK_LIST

WILLIAM_K_UL = -80
WILLIAM_K_LL = -20
A = [
{'sector' : 'Mining', 'stock' : 'ABIRLANUVO'},
{'sector' : 'Computers', 'stock' : 'MTNL'},
{'sector' : 'Diversified', 'stock' : 'MCDOWELL-N'},
{'sector' : '', 'stock' : 'BANKNIFTY'},]


class StockScreener(object):

    def __init__(self):
        self.stocks = pd.DataFrame()

    def generate_results(self):
        i = 1
        result = list()
        for stock in STOCK_LIST:
            info('stock - {0}'.format(stock['stock']))
            print(str(i) + " - " + stock['stock'])
            i = i+1

            data = StockDetails(stock['stock']).getInfo()
            data['Sector'] = stock['sector']
            result.append(data)

        self.stocks = pd.DataFrame(result)
        return self.stocks

    def get_buyers(self):

        if self.stocks.empty: self.generate_results()
        return self.stocks[self.stocks['Buy'] == True]

    def get_sellers(self):

        if self.stocks.empty: self.generate_results()
        return self.stocks[self.stocks['Sell'] == True]

    def save_results(self, path = None):
        df = self.generate_results()
        if path is None:
            path = "F://Personal Work//Stock Data//Python Code Williams R//williamR_" + datetime.datetime.today().strftime("%Y%m%d") + "_" + str(random.randint(1,1000)) + ".csv"
        self.save_to_csv(df, path)

    def save_to_csv(self, df, path):
        df.to_csv(path)


class StockDetails(object):

    def __init__(self, stock_name, cob = None):
        self.stock_name         = stock_name
        self.historical_prices  = self.get_historical_prices(end_date = cob)
        self.stock_info         = dict()

    def getInfo(self):

        self.stock_info['Stock'] = self.stock_name
        
        # Volume Data
        self.stock_info.update(self.get_avg_vol())
        self.stock_info.update(self.get_last_cob_details())
        
        # William R Details
        self.stock_info.update(self.get_williams_ratio_details(self.stock_info['Average Volume']))
        
        # Moving Averages
        self.stock_info.update(self.calculate_moving_avgs())
        
        # 52W stats
        self.stock_info.update(self.get_52w_stat())
        
        # Add Buy/Sell Suggestion
        self.stock_info.update(self.buy_sell_suggestion())
        
        # Calculate MACD
        self.stock_info.update(self.calculate_macd())
        b = self.historical_prices
        
        return self.stock_info

    @property
    def stock_name(self):
        return self._stock_name

    @stock_name.setter
    def stock_name(self, stock_name):
        self._stock_name = stock_name

    def get_historical_prices(self, end_date = None):
        return getHistoricStockPrices(self.stock_name, end_date = end_date)

    def get_lookback_period(self, avg_vol, std_dev):
        return int(round(math.log(avg_vol, std_dev),0)*2)

    def get_avg_vol(self):
        try:
            avg_vol = round(np.mean(self.historical_prices['Volume']),2)
            avg_vol = 0 if np.isnan(avg_vol) else avg_vol
            return {'Average Volume' : avg_vol}
        except:
            return {'Average Volume' : 0}

    def get_last_cob_details( self ):
        try:
            last_row = self.historical_prices.tail(1)
            return {'Last Close' : round(last_row['Close'][0],2),
                    'Last COB' : last_row.reset_index()['Date'][0].strftime("%d%b%y")}
        except:
            return {'Last Close' : 0,
                    'Last COB' : datetime.datetime.today().strftime("%d%b%y")}
          
    def get_williams_ratio_details( self, avg_vol):
        
        smoothing_period = 5
        
        info = {'Standard Deviation': 0,
                    'Lookback Period'   : 14,
                    'Smoothing Period'  : smoothing_period,
                    '%R'                : 0,
                    '%D'                : 0,
                    'WILLIAM BUY/SELL'  : ''}
        
        try:
            std_dev                     = round(self.get_std_dev(),3)
            info['Standard Deviation']  = std_dev
            lookback_period             = max(self.get_lookback_period(avg_vol, std_dev),14)
            info['Lookback Period']     = lookback_period
            info['%R'], info['%D'], info['WILLIAM BUY/SELL']   = self.calculate_williams_ratio(lookback_period, smoothing_period)
            
        except:
            pass
        
        finally:
            return info
        
    def get_std_dev(self):
        df = self.historical_prices[['High', 'Low']]
        df['SD'] = df.apply(lambda row: (row['High'] - row['Low'])**2, axis = 1)
        return np.mean(df['SD'])**.5

    def calculate_williams_ratio(self, lookback_period, smoothing_period):

        # Append Highest High
        self.historical_prices['HH'] = self.historical_prices[['High']].rolling(window = lookback_period).max()

        # Append Lowest lows
        self.historical_prices['LL'] = self.historical_prices[['Low']].rolling(window = lookback_period).min()

        # Calculate %K
        self.historical_prices['%R'] = self.historical_prices.apply(lambda row: (row['Close'] - row['HH']) * 100 / (row['HH'] - row['LL']) if row['HH'] != 0 else 0, axis = 1)

        # Calculate %D
        self.historical_prices['%D'] = self.historical_prices['%R'].rolling(window = smoothing_period).mean()
        
        # Calculate Buy/Sell using Williams R
        self.historical_prices['WILLIAM BUY/SELL'] = self.historical_prices.apply(lambda row: 'BUY' if row['%D'] < WILLIAM_K_UL and row['%D'] < row['%R'] else 'SELL' if row['%D'] > WILLIAM_K_UL and row['%D'] > row['%R'] else '', axis = 1)

        last_row = self.historical_prices.tail(1)

        return round(last_row['%R'][0],2), round(last_row['%D'][0],2), last_row['WILLIAM BUY/SELL'][0]

    def calculate_moving_avgs(self):
        
        info = {'30D MA' : 0,
                '60D MA' : 0,
                '200D MA': 0}
        try:
            self.historical_prices['30D_MA'] = self.historical_prices['Close'].rolling(window=30).mean()
            info['30D MA'] = round(self.historical_prices.tail(1)['30D_MA'][0],2)
            
            self.historical_prices['60D_MA'] = self.historical_prices['Close'].rolling(window=60).mean()
            info['60D MA'] = round(self.historical_prices.tail(1)['60D_MA'][0],2)
            
            self.historical_prices['200D_MA'] = self.historical_prices['Close'].rolling(window=200).mean()
            info['200D MA'] = round(self.historical_prices.tail(1)['200D_MA'][0],2)
            
        except:
            pass
        finally:
            return info
        
    def calculate_macd( self ):
        ''' function to calculate MACD and Signal Line '''
        
        info = {'MACD'                                  : 0,
                'MACD Signal'                           : 0,
                'MACD To Signal Diff (Value)'           : 0,
                'MACD To Signal Diff (Days)'            : 0,
                'MACD Signal Diff Rolling Peak'         : 0,
                'MACD Signal Diff % to Rolling Peak'    : 0,
                'MACD BUY/SELL'                         : ''
                }
        try:
            self.historical_prices['26D_EMA'] = self.historical_prices[['Close']].apply(ema, args = (26,))
            self.historical_prices['12D_EMA'] = self.historical_prices[['Close']].apply(ema, args = (12,))
            
            self.historical_prices['MACD'] = self.historical_prices.apply(lambda row: row['12D_EMA'] - row['26D_EMA'], axis = 1)
            
            self.historical_prices['MACD Signal'] = self.historical_prices['MACD'].rolling(window=9).mean()
            self.historical_prices['MACD To Signal Diff (Value)'] = self.historical_prices.apply(lambda row: row['MACD'] - row['MACD Signal'], axis = 1)
            self.historical_prices['MACD Signal Diff Rolling Peak'] = self.historical_prices[['MACD To Signal Diff (Value)']].apply(abs)
            self.historical_prices['MACD Signal Diff Rolling Peak'] = self.historical_prices['MACD Signal Diff Rolling Peak'].rolling(window=9).max()
            self.historical_prices['MACD Signal Diff % to Rolling Peak'] = self.historical_prices.apply(lambda row: round(row['MACD To Signal Diff (Value)']*100/row['MACD Signal Diff Rolling Peak'], 2), axis = 1)
            
            self.historical_prices['MACD BUY/SELL'] = self.historical_prices['MACD Signal Diff % to Rolling Peak'].shift(1)
            self.historical_prices['MACD BUY/SELL'] = self.historical_prices[['MACD BUY/SELL', 'MACD Signal Diff % to Rolling Peak']].apply(lambda row: 'BUY' if row['MACD BUY/SELL'] == -100 and row['MACD Signal Diff % to Rolling Peak'] not in (100,-100) else 'SELL' if row['MACD BUY/SELL'] == 100 and row['MACD Signal Diff % to Rolling Peak'] not in (100,-100) else '', axis = 1)
            #self.historical_prices['MACD BUY/SELL'] = self.historical_prices[['MACD Signal Diff % to Rolling Peak']].apply(lambda col: 'BUY' if col.shift(1) == -100 and col not in (100,-100) else 'SELL' if col.shift(1) == 100 and col not in (100,-100) else '')
            
            self.historical_prices['MACD To Signal Diff (Days)'] = self.historical_prices.apply(lambda row: 1 if row['MACD To Signal Diff (Value)'] > 0 else -1 if row['MACD To Signal Diff (Value)'] < 0 else 0, axis = 1)
            self.historical_prices['MACD To Signal Diff (Days)'] = self.historical_prices[['MACD To Signal Diff (Days)']].apply(cum_pattern)
            
            last_row = self.historical_prices.tail(1)
            
            info['MACD']                                = round(last_row['MACD'][0],4)
            info['MACD Signal']                         = round(last_row['MACD Signal'][0],4)
            info['MACD To Signal Diff (Value)']         = round(last_row['MACD To Signal Diff (Value)'][0],4)
            info['MACD To Signal Diff (Days)']          = last_row['MACD To Signal Diff (Days)'][0]
            info['MACD Signal Diff Rolling Peak']       = round(last_row['MACD Signal Diff Rolling Peak'][0],4)
            info['MACD Signal Diff % to Rolling Peak']  = round(last_row['MACD Signal Diff % to Rolling Peak'][0],2)
            info['MACD BUY/SELL']                       = last_row['MACD BUY/SELL'][0]
            
        except:
            pass
        
        finally:
            return info

    def get_52w_stat(self, data = None):
        
        info = {'52W High'          : 0,
                '52W Low'           : 0,
                'Price% 52W'        : 0,
                'Price Band 52W'    : 0}
        
        if data is None: data = self.historical_prices
        
        try:
            _52W_High = data['High'].max()
            info['52W High'] = round(_52W_High,2)
            
            _52W_Low = data['Low'].min()
            info['52W Low'] = round(_52W_Low,2)
            
            last_close = data.tail(1)['Close'][0]
            info['Price% 52W'] = round((last_close - _52W_Low)*100/(_52W_High - _52W_Low),2)
            
            band = math.floor(info['Price% 52W']/10)
            info['Price Band 52W'] = str(band*10) + '% to ' + str((band + 1) * 10) + '%' if band < 10 else '100 %'
        
        except:
            pass
        
        finally:
            return info
        
    def buy_sell_suggestion( self ):
        
        info = {'Buy'   : 'False',
                'Sell'  : 'False'}
        D   = self.stock_info['%D']
        _R  = self.stock_info['%R']
        
        try:
            info['Buy']     = 'True' if D < WILLIAM_K_UL and D < _R else 'False'
            info['Sell']    = 'True' if D > WILLIAM_K_LL and D > _R else 'False'
            
        except:
            pass
        finally:
            return info

def getHistoricStockPrices(stock_name, end_date = None, days = 700):
    ''' wrapper to get historic stock prices 
    :param stock_name: Name of the stock
    :param start_date: Start Date. Defaulted to today.
    :param days: No of past days. Defaulted to 365 days
    :return: Pandas datframe with high, close, AdjClose, volume for each historical date.
    '''
    
    try:
        if end_date is None: end_date = datetime.datetime.today()
        start_date = end_date + datetime.timedelta( days = -1* days )
        
        hist_prices = getHistoricStockPricesFromYahoo(stock_name + '.NS',start_date, end_date)
        if not hist_prices.empty: return hist_prices

        hist_prices = getHistoricStockPricesFromYahoo(stock_name,start_date, end_date)
        if not hist_prices.empty: return hist_prices
    
    except:
        pass
    return pd.DataFrame()
    
    
def getHistoricStockPricesFromYahoo( stock_name, start_date = None, end_date = None):
    '''
    :param stock_name: Name of the stock
    :param start_date: Start Date. Defaulted to today.
    :param days: No of past days. Defaulted to 365 days
    :return: Pandas datframe with high, close, AdjClose, volume for each historical date.
    '''

    import pandas_datareader as pdr

    try:
        if end_date is None: end_date = datetime.datetime.today()
        if start_date is None: start_date = end_date + datetime.timedelta( days = -1* 365 )

        hist_prices = pdr.DataReader(stock_name, 'yahoo',start_date, end_date)
        return hist_prices
        
    except:
        return pd.DataFrame()

def cum_pattern( data ):
    
    prev = 0
    out = []
    for l in data:
        new = l + prev if l*prev > 0 else l
        out.append(new)
        prev = new
    return out

def ema( data, period = 10):
    
    result = [0]*len(data)
    
    for i, j in enumerate(data):
        if i < period-1:
            result[i] = 0
        elif i == period-1:
            result[i] = sum(data[:period])/period
        else:
            result[i] = (j * 2)/(period + 1) + result[i-1]*(1 - 2/(period + 1))
    return result
        

#if __name__ == '__main__':

    #import time
    #start = time.time()
    #a = StockScreener()
    #b = a.save_results()
    #print(time.time() - start)

