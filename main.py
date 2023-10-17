import requests
from flask import Flask
from pymongo import MongoClient
from datetime import datetime
from bson import json_util


# set app and mongo details
app = Flask(__name__)
client = MongoClient('localhost', 27017)
db = client.PolygonAPIArchive
collection = db.get_price_of_stock


date_format = "%Y-%m-%d"
# key for the polygon api
api_key = ''


def validate_date(date_text):
    try:
        if date_text != datetime.strptime(date_text, "%Y-%m-%d").strftime('%Y-%m-%d'):
            raise ValueError
        return True
    except ValueError:
        return False


def get_price_of_stock(symbol, date):

    query_string = f"https://api.polygon.io/v1/open-close/{symbol}/{date}?adjusted=true&apiKey={api_key}"
    if validate_date(date):
        response = requests.get(query_string)
        print('query string: ', query_string)
        print('response: ', response)
        print('response code: ', response.status_code)
        return response
    else:
        print('incorrect date: ', date)
        raise ValueError


@app.route('/price/<symbol>/<date>', methods=['GET'])
def get_price(symbol, date):
    # symbol is stock symbol, date is the date lookup in yyyy-mm-dd
    try:
        response = get_price_of_stock(symbol, date)
        print(f"{type(response.text)}response:", response.text)
        if response.status_code:
            response_json = response.json()
            print(f"{type(response_json)}response_json:", response_json)

        else:
            raise ValueError

        collection.replace_one({'from': date}, response_json, upsert=True)
        return json_util.dumps(response_json)

    except Exception as e:
        return {'message': f"something went wrong: {type(e).__name__}"}


if __name__ == '__main__':
    app.run()
