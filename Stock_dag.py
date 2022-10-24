from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import s3fs 

from bs4 import BeautifulSoup
import requests
import pandas as pd


def run_stock_analysis():
    url = 'https://markets.businessinsider.com/index/components/s&p_500?p='
    titles = []
    prices = []
    percents = []
    for page in range(1,11):
        req = requests.get(url + str(page))
        soup = BeautifulSoup(req.content, 'html.parser')

        everything = soup.find('tbody', attrs={'class':"table__tbody"})

        for items in everything.findAll('td', attrs={'class':"table__td table__td--big"}):
            title = items.find('a').getText()   
            titles.append(title)

        count = 0 
        for items in everything.find_all('td', attrs={'class':"table__td"}):
            count += 1

        for i in range (1,count,8):
            price = everything.find_all('td', attrs={'class':"table__td"})[i].get_text().split("(")[0].strip()
            head, sep, tail = price.partition('\n')
            prices.append(head)
        
        for i in range (3,count,8):
            percent = everything.find_all('td', attrs={'class':"table__td"})[i].get_text().split("(")[0].strip()
            head, sep, tail = percent.partition('\n')
            percents.append(tail)

    df1 = pd.DataFrame(titles, columns = ["S&P 500 Companies"])
    df2 = pd.DataFrame(prices, columns = ["Latest Prices ($)"])
    df3 = pd.DataFrame(percents, columns = ["Change (%)"])
    df4 = pd.concat([df1, df2, df3], axis = 1)
    df4.set_index('S&P 500 Companies', inplace=True)
    df4.to_csv(r's3://<bucket_name>/<file_name>.csv')

with DAG("my_dag", start_date=datetime(2022,10,22),
    schedule_interval="@daily", catchup=False) as dag:

    training_model_A = PythonOperator(
        task_id="run_stock",
        python_callable = run_stock_analysis
    )
