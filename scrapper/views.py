from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from bs4 import BeautifulSoup
import requests
import json
import html
import bs4

# IPO Data
def scrape_ipo_data(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    table_data = soup.find_all('figure', {'class': 'wp-block-table'})

    ipo_list = []

    for table in table_data:
        rows = table.find_all('tr')[1:8]  # Restrict to the top 7 rows (skip the header row)

        for row in rows:
            cells = row.find_all('td')

            ipo_data = {
                "Name": cells[0].get_text().strip(),
                "Date": cells[1].get_text().strip(),
                "IPOGMP": html.unescape(cells[3].get_text().strip()) if len(cells) > 3 else None,
                "IPOPrice": html.unescape(cells[4].get_text().strip()) if len(cells) > 4 else None,
                "Gain": cells[5].get_text().strip() if len(cells) > 5 else None,
            }

            ipo_list.append(ipo_data)

        # Break out of the loop after processing the first table
        break

    return {"IPOs": ipo_list}



def ipo_api(request):
    screener = requests.get('https://ipowatch.in/ipo-grey-market-premium-latest-ipo-gmp/')
    
    if screener.status_code == 200:
        html_content = screener.text
        ipo_data = scrape_ipo_data(html_content)
        ipo_json = json.dumps(ipo_data, indent=2)

        return HttpResponse(ipo_json, content_type="application/json")
    else:
        return HttpResponse("Failed to fetch data", status=500)



    
def gainers(request):
        screener = requests.get('https://ticker.finology.in/market')
        screener_soup = bs4.BeautifulSoup(screener.text, 'html.parser')

        table_data = screener_soup.find_all('table', {'class': 'screenertable'})

        # Check if there are at least 5 tables with the specified class
        if len(table_data) >= 5:
            target_table = table_data[4]  # Extract the 5th table
            rows = target_table.find_all('tr')[1:8]

            gainers_list = []

            for row in rows:
                cells = row.find_all('td')

                if cells:
                    gainer_data = {
                        "Name": cells[0].get_text().strip(),
                        "Price": float(cells[1].get_text().strip()),
                        "Change": cells[2].get_text().strip()
                    }
                    gainers_list.append(gainer_data)

            response_data = {"gainers": gainers_list}
            return JsonResponse(response_data, json_dumps_params={'indent': 2})
        else:
            return JsonResponse({"error": "Not enough tables with the specified class."})



def losers(request):
        screener = requests.get('https://ticker.finology.in/market')
        screener_soup = bs4.BeautifulSoup(screener.text, 'html.parser')

        table_data = screener_soup.find_all('table', {'class': 'screenertable'})

        # Check if there are at least 5 tables with the specified class
        if len(table_data) >= 6:
            target_table = table_data[5]  # Extract the 5th table
            rows = target_table.find_all('tr')[1:8]

            losers_list = []

            for row in rows:
                cells = row.find_all('td')

                if cells:
                    gainer_data = {
                        "Name": cells[0].get_text().strip(),
                        "Price": float(cells[1].get_text().strip()),
                        "Change": cells[2].get_text().strip()
                    }
                    losers_list.append(gainer_data)

            response_data = {"losers": losers_list}
            return JsonResponse(response_data, json_dumps_params={'indent': 2})
        else:
            return JsonResponse({"error": "Not enough tables with the specified class."})




# Indices data


# def indices(request):
#     screener = requests.get('https://in.investing.com/indices/major-indices')
#     print(screener)
#     screener_soup = BeautifulSoup(screener.text, 'html.parser')

#     table_data = screener_soup.find_all('table', {'class': 'common-table'})
#     indices_data = []

#     for table in table_data:
#         rows = table.find_all('tr')

#         for row in rows:
#             name_cell = row.find('td', {'class': 'col-name'})
#             last_cell = row.find('td', {'class': 'col-last'})
#             high_cell = row.find('td', {'class': 'col-high'})
#             low_cell = row.find('td', {'class': 'col-low'})
#             percent_change = row.find('td', {'class': 'col-chg_pct'})
#             change = row.find('td', {'class': 'col-chg'})
#             time = row.find('td', {'class': 'col-time'})

#             # Check if the element is found before trying to access its attributes
#             if name_cell and last_cell and high_cell and low_cell and percent_change and change and time:
#                 # print(name_cell.get_text().strip(), end='\t')
#                 # print(last_cell.get_text().strip(), end='\t')
#                 # print(high_cell.get_text().strip(), end='\t')
#                 # print(low_cell.get_text().strip(), end='\t')
#                 # print(percent_change.get_text().strip(), end='\t')
#                 # print(change.get_text().strip(), end='\t')
#                 # print(time.get_text().strip(), end='\t')

#                 indices_data.append({
#                     "name": name_cell.get_text().strip(),
#                     "open": float(last_cell.get_text().strip().replace(",", "")),
#                     "high": float(high_cell.get_text().strip().replace(",", "")),
#                     "low": float(low_cell.get_text().strip().replace(",", "")),
#                     "percentChange": float(percent_change.get_text().strip().replace("%", "")),
#                     "change": float(change.get_text().strip().replace(",", "")),
#                     "time": time.get_text().strip()
#                 })
            

#     response_data = {"indices": indices_data}
#     print(response_data)
#     return JsonResponse(response_data)

def indices(request):
    url = 'https://in.tradingview.com/markets/indices/quotes-major/'
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', {'class': 'table-Ngq2xrcG'})
        indices_data = []

        for row in table.find_all('tr'):
            cells = row.find_all('td')
            if cells:
                name = cells[0].get_text().strip()
                price_str = cells[1].get_text().replace(',', '').strip()
                percent_change_str = cells[2].get_text().replace('%', '').strip()
                change_str = cells[3].get_text().replace(',', '').strip()
                high_str = cells[4].get_text().replace(',', '').strip()
                low_str = cells[5].get_text().replace(',', '').strip()
                tech_rating = cells[6].get_text().strip()

                # Replace non-breaking hyphen with regular hyphen
                price_str = price_str.replace('−', '-')
                percent_change_str = percent_change_str.replace('−', '-')
                change_str = change_str.replace('−', '-')
                high_str = high_str.replace('−', '-')
                low_str = low_str.replace('−', '-')

                # Convert strings to float
                price = float(price_str)
                percent_change = float(percent_change_str)
                change = float(change_str)
                high = float(high_str)
                low = float(low_str)

                indices_data.append({
                    "name": name,
                    "price": price,
                    "percentChange": percent_change,
                    "change": change,
                    "high": high,
                    "low": low,
                    "tech_rating": tech_rating
                })

        response_data = {"indices": indices_data}
        return JsonResponse(response_data)

    else:
        return JsonResponse({"error": f"Failed to fetch data. Status code: {response.status_code}"})