from django.shortcuts import render
from django.http import HttpResponse
from bs4 import BeautifulSoup
import requests
import json
import html

import html



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



