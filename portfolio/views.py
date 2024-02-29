import pandas as pd
from rest_framework import generics
from django.http import JsonResponse
import yfinance
from .constants import fundamental_data, threshold, risk_weights, convert_range

from .models import File
from .serializers import FileUploadSerializer


class UploadFileView(generics.CreateAPIView):
    serializer_class = FileUploadSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data["file"]
        reader = pd.read_csv(file)

        portfolio_response_list = []

        # percetage profit-loss and an response list
        for _, row in reader.iterrows():
            percentage_profit_loss = (row["profit_loss"] / row["invested_value"]) * 100
            portfolio_response_list.append(
                {
                    "name": row["name"],
                    "quantity": row["quantity"],
                    "buy_price": row["buy_price"],
                    "profit_loss_percentage": round(
                        percentage_profit_loss, 1
                    ),  # Round to 1 decimal place
                    "invested_value": row["invested_value"],
                }
            )

        # add .NS for indian stocks
        portfolio_stock = [stock + ".NS" for stock in reader["name"]]
        total_invested = reader["invested_value"].sum()
        profit_loss = float(reader["profit_loss"].sum())

        # stock wise percentage in portfolio
        stock_percentage = {}
        for row in portfolio_response_list:
            stock_name = row["name"]
            percentage = (
                (
                    row["invested_value"]
                    + row["profit_loss_percentage"] * row["invested_value"] / 100
                )
                / total_invested
            ) * 100
            stock_percentage[stock_name] = round(percentage, 2)

        # risk analysis
        stock_risk_analysis, risk_rating = risk_analysis(
            portfolio_stock, stock_percentage
        )

        # portfolio vs nifty
        portfolio_return, nifty_return = comapare_portfolio_nifty(portfolio_stock)
        portfolio_nifty = build_portfolio_nifty_list(
            portfolio_return.index, portfolio_return, nifty_return
        )

        # sector percentage
        sector_percentage = (
            reader.groupby("sector")["invested_value"]
            .sum()
            .add(reader.groupby("sector")["profit_loss"].sum())
            .div(total_invested + profit_loss)
            .mul(100)
            .round(1)
            .reset_index()
            .rename(columns={0: "percentage"})
            .to_dict(orient="records")
        )

        print("type : ", type(total_invested))

        # Market Cap percentage
        market_cap_percentage = (
            reader.groupby("market_cap")["invested_value"]
            .sum()
            .add(reader.groupby("market_cap")["profit_loss"].sum())
            .div(total_invested + profit_loss)
            .mul(100)
            .round(1)
            .reset_index()
            .rename(columns={0: "percentage"})
            .to_dict(orient="records")
        )

        sorted_data = sorted(
            portfolio_response_list,
            key=lambda x: x["profit_loss_percentage"],
            reverse=True,
        )

        top_performers = [
            {
                "name": entry["name"],
                "profit_loss_percentage": entry["profit_loss_percentage"],
            }
            for entry in sorted_data
            if entry["profit_loss_percentage"] > 0
        ][:5]

        response_object = {
            "portfolio_nifty": portfolio_nifty,
            "total_invested": total_invested,
            "profit_loss": profit_loss,
            "sector_percentage": sector_percentage,
            "market_cap_percentage": market_cap_percentage,
            "portfolio": portfolio_response_list,
            "top_performers": top_performers,
            "risk_analysis": stock_risk_analysis,
            "risk_rating": risk_rating,
        }
        return JsonResponse({"status": "success", "data": response_object})


def comapare_portfolio_nifty(stock_list):
    portfolio_returns = get_stock_returns(stock_list)
    nifty_returns = get_nifty_returns()

    return portfolio_returns, nifty_returns


def get_nifty_returns():
    period = "1y"
    nifty_data_close = get_stock_data("^NSEI", period)["Close"]
    nifty_last_close = nifty_data_close.resample("M").last()

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
    monthly_average = stock_close.resample("M").last().sum(axis=1)

    return monthly_average


def calculate_variation(ar):
    result = ar.pct_change() * 100
    return result.iloc[1:]


def build_portfolio_nifty_list(dates, portfolio, nifty):
    response_object = [
        {"date": date.strftime("%b"), "portfolio": portfolio, "nifty": nifty}
        for date, portfolio, nifty in zip(dates, portfolio, nifty)
    ]
    return response_object


def risk_analysis(stock_list, stock_invested_value):
    risk_analysis = {}
    info = ["pe_ratio", "debt_to_equity", "beta", "profit_growth", "sales_growth"]
    risk_analysis = {prop: {"low": 0, "mid": 0, "high": 0} for prop in info}
    risk_analysis_output = []

    # for every parameter
    for prop in info:
        total_risk = 0

        # calculate the low, mid, high percentage of a prop
        for stock in stock_list:
            stock = stock.split(".")[0]
            stock_percentage = stock_invested_value[stock]
            val = fundamental_data[stock][prop]

            risk_level = ""
            if prop == "sales_growth" or prop == "profit_growth":
                risk_level = (
                    "low"
                    if val >= threshold[prop]["low"]
                    else ("mid" if val >= threshold[prop]["mid"] else "high")
                )
            else:
                risk_level = (
                    "low"
                    if val <= threshold[prop]["low"]
                    else ("mid" if val <= threshold[prop]["mid"] else "high")
                )

            risk_analysis[prop][risk_level] += stock_percentage
            total_risk += stock_percentage

        # cal low, mid, high percentage
        for risk_level in risk_analysis[prop]:
            risk_analysis[prop][risk_level] = (
                risk_analysis[prop][risk_level] / total_risk
            ) * 100
            risk_analysis[prop][risk_level] = round(risk_analysis[prop][risk_level], 2)

        # get max level and value
        max_risk_level, max_risk_value = max(
            risk_analysis[prop].items(), key=lambda x: x[1]
        )

        # find all stocks in that level
        stock_output = []
        for stock in stock_list:
            stock = stock.split(".")[0]
            val = fundamental_data[stock][prop]

            risk_level = ""
            if prop == "sales_growth" or prop == "profit_growth":
                risk_level = (
                    "low"
                    if val >= threshold[prop]["low"]
                    else ("mid" if val >= threshold[prop]["mid"] else "high")
                )
            else:
                risk_level = (
                    "low"
                    if val <= threshold[prop]["low"]
                    else ("mid" if val <= threshold[prop]["mid"] else "high")
                )

            if risk_level == max_risk_level:
                stock_output.append({"name": stock, "value": val})

        risk_analysis_output.append(
            {
                "parameter": prop,
                "level": max_risk_level,
                "percentage": max_risk_value,
                "stock": stock_output,
            }
        )

    weighted_risk_score = 0
    for item in risk_analysis_output:
        level = item["level"]
        percentage = item["percentage"]

        # todo handle if more low percentage
        weighted_risk_score += risk_weights[level] * percentage

    print("risk :", weighted_risk_score)
    scaled_risk = convert_range(weighted_risk_score)

    return risk_analysis_output, scaled_risk
