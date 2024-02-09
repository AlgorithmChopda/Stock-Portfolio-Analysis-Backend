from django.urls import path
from . import views

urlpatterns=[
    path('ipodata/',views.ipo_api),
    path('gainers/',views.gainers),
    path('losers/',views.losers),
    path('indices/',views.indices),
    path('nse',views.fetch_nse_data),
    path('bse',views.fetch_sensex_data),
    path('bank',views.fetch_nifty_bank_data),
    path('it',views.fetch_nifty_it_data),
    path('finance',views.fetch_nifty_fin_data),
    path('fmcg',views.fetch_nifty_fmcg_data),
]