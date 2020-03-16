"""
@author: Tomáš Mimra
"""

import requests as rq
import pandas as pd
from bs4 import BeautifulSoup
import plotly.graph_objects as go

#expected dividends for PSE (www.pse.cz) stocks
df_stocks_exp = pd.DataFrame(columns = ['name' , 'isin', 'exp_divi'])
df_stocks_exp.loc[0] = ['AVAST', 'GB00BDD85M81',2.37]
df_stocks_exp.loc[1] = ['CETV', 'BMG200452024',0]
df_stocks_exp.loc[2] = ['ČEZ', 'CZ0005112300',24]
df_stocks_exp.loc[3] = ['KOFOLA', 'CZ0009000121',13.5]
df_stocks_exp.loc[4] = ['KOMERČNÍ BANKA', 'CZ0008019106',58]
df_stocks_exp.loc[5] = ['02', 'CZ0009093209',21]
df_stocks_exp.loc[6] = ['ERSTE', 'AT0000652011',40]
df_stocks_exp.loc[7] = ['PHILIP MORRIS', 'CS0008418869',1600]
df_stocks_exp.loc[8] = ['MONETA', 'CZ0008040318',3.3]
df_stocks_exp.loc[9] = ['PFNONWOVENS', 'LU0275164910',9]
df_stocks_exp.loc[10] = ['TMR', 'SK1120010287',0]
df_stocks_exp.loc[11] = ['VGP', 'BE0003878957',0]
df_stocks_exp.loc[12] = ['VIG', 'AT0000908504',30]

# request for URL for current prices
url = "https://www.pse.cz/udaje-o-trhu/akcie/prime-market"
page = rq.get(url)

# lists creation
labels = []
isins = []
prices = []

# fing my table id='data_online_tab' tr elements as rows
page_content = BeautifulSoup(page.content, 'html.parser')
table = page_content.find('table', class_='sortable')
rows = table.find_all('tr')

# for each row in tr element find td 0 is label, 2 is price
for row in rows:
    try:
        labels.append(str(row.find_all('a')[0].text))
        isins.append(str(row.find_all("div", class_="isin")[0].get_text(strip=True)))
        prices.append(str(row.find_all('td')[2].get_text(strip=True)))
    except IndexError:
        pass
    continue

# get rid of mess in prices list
prices = [price.replace('\xa0','') for price in prices]
prices = [price.replace('Kč','') for price in prices]
prices = [price.replace(',','.') for price in prices]

#create dataframe stock_labels
df_stocks_labels = pd.DataFrame({'label':labels})
#remove mess in 1st row
df_stocks_labels = df_stocks_labels.drop(0,axis=0)
df_stocks_labels = df_stocks_labels.reset_index()

#create dataframe stock_isins
df_stocks_isins = pd.DataFrame({'isin':isins})

#create dataframe stock_prices
df_stocks_prices = pd.DataFrame({'price':prices})
# convert to float64
df_stocks_prices.price = df_stocks_prices.price.astype('float64')


#concat df_stocks_labels, df_stocks_isins,df_stocks_prices in one df_stocks
df_stocks = pd.concat([df_stocks_labels, df_stocks_isins,df_stocks_prices], axis=1)


# join web data and expected dividend data
df_stocks = pd.merge(df_stocks,df_stocks_exp,on='isin')

#yield calculation

df_stocks['yield'] = df_stocks['exp_divi'] / df_stocks['price']

df_stocks = df_stocks.sort_values(by='yield', ascending=True)

# Vizualize data in ploty
# prepare on hover tooltips
#price
y1 = df_stocks['price']
text1 = [f"Current price:{str(v).replace('.', ',')}Kč<br>"  for v in y1]

#expected divi
y2 = df_stocks['exp_divi']
text2 = [f"Expected divi:{str(v).replace('.', ',')}Kč<br>"  for v in y2]

#final tooltip
tooltips = [f"{lab}{val}"  for lab, val in zip(text1,text2)]

#create bar chart
fig = go.Figure(
    data=[go.Bar(x=df_stocks['name'], y=df_stocks['yield'], hovertext=tooltips)]
)
#update bar chart with additional atributes
fig.update_layout(
    title="Prague Stocks Current Divi Yields",
    xaxis_title="PSE Stock",
    xaxis_tickformat = '%',
    yaxis_title="Yield",
    yaxis_tickformat = '%',
    font=dict(
        family="Courier New, monospace",
        size=18,
        color="#7f7f7f")
)
#format traces
fig.update_traces(
    texttemplate='%{value:0.2%  }', textposition='outside',
)

#add target yeild line
fig.add_shape(
        # Line Horizontal
        go.layout.Shape(
            type="line",
            x0=0,
            y0=0.05,
            x1=10,
            y1=0.05,
            line=dict(
                color="LightSeaGreen",
                width=4,
                dash="dashdot",
            ),
        )
)

# create HMTL output with actual divi yeild in bar chart
fig.write_html('first_figure.html', auto_open=True)
