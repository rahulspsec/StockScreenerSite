from django.conf.urls import url

from stockscreener import views

urlpatterns = [
    url(r'^stockdetails/', views.stockdetails, name='stockdetailsws'),
    url(r'^summaryreports/', views.summaryreport, name='summaryreportsws'),
    url(r'^viewstockdetails/', views.viewstockdetails, name='viewstockdetails'),
    url(r'^viewsummary$', views.viewsummary, name='viewsummary'),
    url(r'^generatesummaryreport/', views.generatesummaryreport, name='generatesummaryreport'),
    url(r'^$', views.index, name='index'),
]
