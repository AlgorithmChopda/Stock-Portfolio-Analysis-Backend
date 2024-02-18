import pandas as pd
from rest_framework import generics
from django.http import JsonResponse
import yfinance
import json


from .models import File
from .serializers import FileUploadSerializer


class UploadFileView(generics.CreateAPIView):
    serializer_class = FileUploadSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data["file"]
        reader = pd.read_csv(file)

        # TODO: store in DB
        portfolio = []
        portfolio_stock = []
        total_invested = 0
        profit_loss = 0
        
        for _, row in reader.iterrows():
            portfolio.append(
                {
                    "name": row["name"],
                    "sector": row["sector"],
                    "buy_price": row["buy_price"],
                    "quantity": row["quantity"],
                    "profit_loss": row["profit_loss"],
                    "invested_value": row["invested_value"],
                }
            )
            portfolio_stock.append(row["name"] + ".NS")
            total_invested += row["invested_value"]
            profit_loss += row["profit_loss"]

        portfolio_return, nifty_return = comapare_portfolio_nifty(portfolio_stock)
        
        portfolio_nifty = build_response_object(portfolio_return.index, portfolio_return, nifty_return)
        response_object = {"portfolio_nifty": portfolio_nifty, "total_invested": total_invested, "profit_loss": profit_loss}
        
        return JsonResponse({"status": "success", "data": response_object})


# print(
#     row["name"],
#     row["sector"],
#     row["buy_price"],
#     row["quantity"],
#     row["profit_loss"],
#     row["invested_value"],
# )
# new_file = File(
#     name=row["name"],
#     sector=row["sector"],
#     quantity=row["quantity"],
#     buy_price=row["buy_price"],
#     invested_value=row["invested_value"],
#     profit_loss=row["profit_loss"],
# )
# new_file.save()

def comapare_portfolio_nifty(stock_list):
    portfolio_returns = get_stock_returns(stock_list)
    nifty_returns = get_nifty_returns()

    return portfolio_returns, nifty_returns


def get_nifty_returns():
    period = "1y"
    nifty_data_close = get_stock_data("^NSEI", period)["Close"]
    nifty_last_close = nifty_data_close.resample('M').last()
    
    return calculate_variation(nifty_last_close)


def get_stock_returns(stock_list):
    stock_close = pd.DataFrame()
    period = "1y"
    
    for stock in stock_list:
        data = get_stock_data(stock, period)
        stock_close[stock] = data["Close"]

    porfolio_cumulative_returns = cal_cumulative_returns_by_month(stock_close)
    return calculate_variation(porfolio_cumulative_returns)


def get_stock_data(ticker, period):
    data = yfinance.download(tickers=ticker, period=period, interval="1d")
    return data


def cal_cumulative_returns_by_month(stock_close):
    stock_close.index = pd.to_datetime(stock_close.index)
    monthly_average = stock_close.resample('M').last().sum(axis = 1)

    return monthly_average


def cal_cumulative_returns(stock_close):
    ret_df = stock_close.pct_change()
    cumul_ret = (ret_df + 1).cumprod() - 1
    pf_cumul_ret = cumul_ret.mean(axis = 1)
    
    return pf_cumul_ret


def calculate_variation(ar):
    result = ar.pct_change() * 100
    return result.iloc[1:]

def build_response_object(dates, portfolio, nifty):
    response_object = [
        {
            'date': date.strftime('%b'),
            'portfolio': portfolio,
            'nifty': nifty
        }
        for date, portfolio, nifty in zip(dates, portfolio, nifty)
    ]

    return response_object
