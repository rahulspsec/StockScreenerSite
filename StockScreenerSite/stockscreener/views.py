from django.shortcuts import render, redirect

from django.http import HttpResponse, Http404, JsonResponse
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import pandas as pd
import json
from datetime import datetime
import requests
import html.parser
import ast
from .StockScreenerUtility.StockScreener import StockDetails
from .StockScreenerUtility.constant import getStockBySector
from .modelUtil import getSummaryReportFromDB, saveSummaryReportToDB
import time

def index(request):
    return render(
        request,
        'stockscreener/index.html',
        {
            'title':'Stock Screener',
            'message':'This is a webservice for Stock Screener.',
            'year':datetime.now().year,
        }
    )

def viewstockdetails(request, template_name = 'stockscreener/viewstockdetails.html'):
    
    url = "http://localhost:8000" + request.get_full_path().replace('viewstockdetails', 'stockdetails')
    if request.GET.get('stockname',None):
        response = requests.get(url)
        jData = json.loads(response.content.decode('utf-8'))
        summary_data = jData.get('stock_info',[])
        detail_data = jData.get('stock_detail',{})
    else:
        summary_data= []
        detail_data = {}

    # get summary columns
    try:
        summary_col=[]
        summary_col = list(summary_data[0].keys())
    except:
        summary_col = []

    # get detail cols
    try:
        detail_col = []
        for k,v in detail_data.items():
            detail_col = list(v[0].keys())
            break
    except:
        detail_col = []
    #return HttpResponse(pd.read_json(jData).to_html())
    stock_selection = getStockBySector()

    return render(request, 
                  template_name, 
                  {'summary_data'   : summary_data,
                   'detail_data'    : detail_data,
                   'summary_col'    : summary_col,
                   'detail_col'     : detail_col,
                   'stock_selecton' : stock_selection,
                   'year'           : datetime.now().year
                   })

@api_view(["GET","POST"])
def stockdetails(request):
    '''
    Function to fetch Stock Details
    REQUEST:    http://localhost:8000/stockscreener/stockdetails/?stockname=INFY,SBI&cob=20181117
        query_params = {'stockname' : 'INFY,SBI',
                        'cob'       : '20181117' #OPTIONAL. Default to today()
                        }
    '''

    try:
        stock_info = []
        stock_detail = {}
        stockList   = request.query_params.get('stockname',[''])
        stockList   = [l.strip() for l in stockList.split(',')]
        detail      = request.query_params.get('detail','')
        cob         = request.query_params.get('cob', None)
        cob         = datetime(year = int(cob[:4]), month = int(cob[4:6]), day = int(cob[6:])) if cob else datetime.today()
        
        for stock_name in stockList:
            stock_details = StockDetails(stock_name = stock_name, cob = cob)
            stock_info.append(stock_details.getInfo())    #Dict
            if detail.lower() == 'true': stock_detail[stock_name] = stock_details.historical_prices.fillna('').to_dict(orient = 'records')

        #return HttpResponse(pd.DataFrame(stock_info).to_html())
        output = {'stock_info' : pd.DataFrame(stock_info).to_dict(orient = 'records'),
                  'stock_detail' : stock_detail}

        return JsonResponse(output, safe = False)

    except  ValueError as e:
        return Response(e.args[0], status.HTTP_400_BAD_REQUEST)

@api_view(["GET","POST"])
def summaryreport(request):
    '''
    Function to fetch Summary Reports
    REQUEST:    http://localhost:8000/stockscreener/summaryreports/?cob=20181122
        query_params = {'cob'       : '20181117' #OPTIONAL. Default to today()
                        }
    '''

    try:
        cob         = request.query_params.get('cob', None)
        report      = getSummaryReportFromDB(cob)

        output = getSummaryReportFromDB().to_dict(orient = 'records')

        #return HttpResponse(pd.DataFrame(stock_info).to_html())
        return JsonResponse(output, safe = False)

    except  ValueError as e:
        return Response(e.args[0], status.HTTP_400_BAD_REQUEST)

def viewsummary(request, template_name = 'stockscreener/viewsummary.html'):
    
    url = "http://localhost:8000" + request.get_full_path().replace('viewsummary', 'summaryreports')
    cob = request.GET.get('cob',None)
    response = requests.get(url)
    jData = json.loads(response.content.decode('utf-8'))

    # get summary columns
    try:
        summary_col=[]
        summary_col = list(jData[0].keys())
    except:
        summary_col = []

    return render(request, 
                  template_name, 
                  {'summary_data'   : jData,
                   'summary_col'    : summary_col,
                   'year'           : datetime.now().year
                   })

@api_view(["POST"])
def generatesummaryreport(request):
    '''
    Function to fetch Stock Details
    REQUEST:    http://localhost:8000/stockscreener/generatesummaryreport
        query_params = {'stockname' : 'INFY,SBI',
                        'cob'       : '20181117' #OPTIONAL. Default to today()
                        }
    '''

    try:
        start = time.time()
        status = saveSummaryReportToDB()
        print(status)
        print(time.time() - start)

        return JsonResponse(status, safe = False)

    except  ValueError as e:
        return Response(e.args[0], status.HTTP_400_BAD_REQUEST)