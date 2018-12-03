from django.db import models

# Create your models here.

class ContextKey(models.Model):
    STATUS_CHOICES = (
                        ('Started','Started'),
                        ('Completed', 'Completed'),
                        ('Cancelled', 'Cancelled')
                    )
    cob                 = models.CharField(max_length = 8)
    status              = models.CharField(max_length = 10, default = 'Started', choices = STATUS_CHOICES)
    runtime             = models.DateTimeField('date published')

    def __str__(self):
        try:
            return self.cob + '_' + str(self.id)
        except:
            return self.cob

class SummaryReport(models.Model):
    context                     = models.ForeignKey(ContextKey, on_delete=models.CASCADE)
    stock_symbol                = models.CharField(max_length = 10)
    sector                      = models.CharField(max_length = 20, blank = True)
    last_close                  = models.FloatField(default = 0, null = True, blank = True)
    d_perc                      = models.FloatField(default = 0, null = True, blank = True)
    r_perc                      = models.FloatField(default = 0, null = True, blank = True)
    ma_200d                     = models.FloatField(default = 0, null = True, blank = True)
    ma_30d                      = models.FloatField(default = 0, null = True, blank = True)
    high_52w                    = models.FloatField(default = 0, null = True, blank = True)
    low_52w                     = models.FloatField(default = 0, null = True, blank = True)
    ma_60d                      = models.FloatField(default = 0, null = True, blank = True)
    price_band_52w              = models.CharField(max_length = 20, null = True, default = '', blank = True)
    price_52w_perc              = models.FloatField(default = 0, null = True, blank = True)
    avg_volume                  = models.FloatField(default = 0, null = True, blank = True)
    is_buy                      = models.CharField(max_length = 4, null = True, default = 'False', blank = True)
    lookback_period             = models.IntegerField(default = 0, null = True, blank = True)
    macd                        = models.FloatField(default = 0, null = True, blank = True)
    macd_buy_sell               = models.CharField(max_length = 4, null = True, default = 'False', blank = True)
    macd_signal                 = models.FloatField(default = 0, null = True, blank = True)
    is_sell                     = models.CharField(max_length = 4, null = True, default = 'False', blank = True)
    smoothing_period            = models.IntegerField(default = 0, null = True, blank = True)
    std_deviation               = models.FloatField(default = 0, null = True, blank = True)
    william_buy_sell            = models.CharField(max_length = 4, null = True, default = 'False', blank = True)
    macd_sig_diff_peak_perc     = models.FloatField(default = 0, null = True, blank = True)
    macd_sig_diff_peak_val      = models.FloatField(default = 0, null = True, blank = True)
    macd_sig_diff_days          = models.IntegerField(default = 0, null = True, blank = True)
    macd_sig_diff_val           = models.FloatField(default = 0, null = True, blank = True)
    last_cob                    = models.CharField(max_length = 4, null = True, default = '', blank = True)


    def __str__(self):
        return self.stock_symbol + '_' + str(self.context)

