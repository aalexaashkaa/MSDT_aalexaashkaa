import matplotlib.pyplot as plt
import pandas as pd
from aiohttp import ClientSession
import asyncio

API_KEY = 'T39F3MQYYEQX8PG0'
#Программа асинхронно получает данные об акциях компаний по тикеру и выводит данные в виде графика и информации о статистических показателях

#Функция для получения данных о цене акций компании
async def get_avg_stock_prices(company_name):
    async with ClientSession() as session:
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={company_name}&apikey={API_KEY}'

        async with session.get(url=url) as response:

            stock_prices = await response.json()
            if 'Time Series (Daily)' not in stock_prices:
                print(f"Ошибка API для {company_name}: {stock_prices}")
                return None

            time_series = stock_prices['Time Series (Daily)']
    
            df = pd.DataFrame.from_dict(time_series, orient='index')

            df_avg = pd.DataFrame({
                            'date': df.index,
                            'avg_price': (df['2. high'].astype(float) + df['3. low'].astype(float) + df['4. close'].astype(float)) / 3
                            }).reset_index(drop=True)
            
            df_avg['date'] = pd.to_datetime(df_avg['date'])

            return df_avg

#Функция создает график и добавляет информацию о статистических показателях             
def visualization(df, name):
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(df['date'], df['avg_price'], marker='o', linestyle='-', linewidth=2, markersize=4)
    
    ax.set_xlabel("Дата")
    ax.set_ylabel("Средняя стоимость за день")
    ax.set_title(f"Временной ряд цены акций компании {name} за 100 дней")
    plt.subplots_adjust(left=0.05, right=0.7, top=0.9, bottom=0.1)

    df_stat = analyze_stats(df.sort_values('date'))

    text = ''
    for index, row in df_stat.iterrows():
        text += (f"{row['Показатель']}:  " + f"{row['Значение']}" + "\n")
    
    ax.text(1.05, 0.5, text,
        transform=ax.transAxes, fontsize=12,
        verticalalignment='center')
    
    return fig

#Функция подсчитывает статистические показатели
def analyze_stats(df):
    stats = pd.DataFrame({
        'Показатель': ['Минимальная цена', 'Максимальная цена', 'Средняя цена', 
                       'Медианная цена', 'Ст. отклонение', 'Цена в начале', 'Цена в конце'],
        'Значение': [
            round(df['avg_price'].min(), 2),
            round(df['avg_price'].max(), 2),
            round(df['avg_price'].mean(), 2),
            round(df['avg_price'].median(), 2),
            round(df['avg_price'].std(), 2),
            round(df['avg_price'].iloc[0], 2),
            round(df['avg_price'].iloc[-1], 2)
        ]
    })

    return stats


async def process_company(company):
    df = await get_avg_stock_prices(company)

    if df is not None:
        fig = visualization(df, company)
        return {'company': company, 'figure': fig, 'data': df}
    
    return {'company': company, 'figure': None, 'data': None}

async def main(companies):
    tasks = []

    for company in companies:
        tasks.append(asyncio.create_task(process_company(company)))

        #Существуют ограничение на кол-во запрсов в минуту у бесплатной версии API
        #Чтобы получить информацию о всех компаниях, нужно добавить задержку на 12 секунд
        await asyncio.sleep(12) 
    
    results = await asyncio.gather(*tasks)

    return results



if __name__ == "__main__":
    companies = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'GE']
    results = asyncio.run(main(companies))

    for i in results:
        print(i.get('company'))
        print(i.get('data'))
        if i.get('figure') is not None:
            i.get('figure').show()
    
    plt.show()
