
from django.utils import timezone
from datetime import datetime
from .StockScreenerUtility.StockScreener import StockScreener
from collections import OrderedDict

import pandas as pd

def saveSummaryReportToDB():

    from stockscreener.models import ContextKey, SummaryReport

    try:
        ctxModel = ContextKey(cob       = datetime.today().strftime('%Y%m%d'),
                              runtime   = timezone.now()
                              )
        ctxModel.save()

        report = StockScreener().generate_results()
        for stock in report.to_dict(orient = 'records'):
            print(stock['Stock'])
            stkReport = SummaryReport(context                   = ctxModel,
                                    stock_symbol                = stock['Stock'],
                                    sector                      = stock['Sector'],
                                    last_close                  = stock['Last Close'],
                                    d_perc                      = stock['%D'],
                                    r_perc                      = stock['%R'],
                                    ma_200d                     = stock['200D MA'],
                                    ma_30d                      = stock['30D MA'],
                                    high_52w                    = stock['52W High'],
                                    low_52w                     = stock['52W Low'],
                                    ma_60d                      = stock['60D MA'],
                                    price_band_52w              = stock['Price Band 52W'],
                                    price_52w_perc              = stock['Price% 52W'],
                                    avg_volume                  = stock['Average Volume'],
                                    is_buy                      = stock['Buy'],
                                    lookback_period             = stock['Lookback Period'],
                                    macd                        = stock['MACD'],
                                    macd_buy_sell               = stock['MACD BUY/SELL'],
                                    macd_signal                 = stock['MACD Signal'],
                                    is_sell                     = stock['Sell'],
                                    smoothing_period            = stock['Smoothing Period'],
                                    std_deviation               = stock['Standard Deviation'],
                                    william_buy_sell            = stock['WILLIAM BUY/SELL'],
                                    macd_sig_diff_peak_perc     = stock['MACD Signal Diff % to Rolling Peak'],
                                    macd_sig_diff_peak_val      = stock['MACD Signal Diff Rolling Peak'],
                                    macd_sig_diff_days          = stock['MACD To Signal Diff (Days)'],
                                    macd_sig_diff_val           = stock['MACD To Signal Diff (Value)'],
                                    last_cob                    = stock['Last COB'],
                                      
                                      )
                                    
            stkReport.save()

        ctxModel.status = 'Completed'
        ctxModel.save()

        return True

    except:
        return False

def getSummaryReportFromDB(cob = None, format = 'dataframe'):
    '''
        Funtion to fetch Summary Reports from DB
        INPUT:
            :param cob = '20181122'
            :param format = 'dataframe'
    '''
    from stockscreener.models import ContextKey, SummaryReport

    if format == 'dataframe':
        output = pd.DataFrame()
    else:
        output = []

    try:
        if cob:
            contextList = ContextKey.objects.filter(cob = cob, status = 'Completed')
        else:
            contextList = ContextKey.objects.filter(status = 'Completed')
            contextList = contextList.order_by('-id')

        context = contextList[0]

        if context.id > 0:
            objList = SummaryReport.objects.filter(context = context)

            # start creating dataframe
            outputdictlist = []
            for obj in objList:
                outputdictlist.append(
                    OrderedDict({'Stock Symbol'                         : obj.stock_symbol,
                                 'Sector'                               : obj.sector,
                                 'Last Close'                           : obj.last_close,
                                 'Last COB'                             : obj.last_cob,
                                 'Average Volume'                       : obj.avg_volume,
                                 'Standard Deviation'                   : obj.std_deviation,
                                 '52W High'                             : obj.high_52w,
                                 '52W Low'                              : obj.low_52w,
                                 'Price% 52W'                           : obj.price_52w_perc,
                                 'Price Band 52W'                       : obj.price_band_52w,
                                 '30D MA'                               : obj.ma_30d,
                                 '60D MA'                               : obj.ma_60d,
                                 '200D MA'                              : obj.ma_200d,
                                 'Lookback Period'                      : obj.lookback_period,
                                 'Smoothing Period'                     : obj.smoothing_period,
                                 '%D'                                   : obj.d_perc,
                                 '%R'                                   : obj.r_perc,
                                 'WILLIAM BUY/SELL'                     : obj.william_buy_sell,
                                 'MACD'                                 : obj.macd,
                                 'MACD Signal'                          : obj.macd_signal,
                                 'MACD Signal Diff Rolling Peak'        : obj.macd_sig_diff_peak_val,
                                 'MACD Signal Diff % to Rolling Peak'   : obj.macd_sig_diff_peak_perc,
                                 'MACD To Signal Diff (Days)'           : obj.macd_sig_diff_days,
                                 'MACD To Signal Diff (Value)'          : obj.macd_sig_diff_val,
                                 'MACD BUY/SELL'                        : obj.macd_buy_sell,
                                 'Buy'                                  : obj.is_buy,
                                 'Sell'                                 : obj.is_sell
                        }))

            output = pd.DataFrame(outputdictlist)
            # end creating dataframe
        return output

    except:
        return output
