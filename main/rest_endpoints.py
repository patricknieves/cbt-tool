from flask import Flask, request
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
import calendar
import json
import MySQLdb
import Currency_apis

app = Flask(__name__)
api = Api(app)
shapeshift_main_address_ETH = "0x70faa28a6b8d6829a4b1e649d26ec9a2a39ba413"

class Exchange_address_from(Resource):
    def get(self, address_from):
        result = query_db("SELECT * FROM cross_block.exchanges WHERE address_from = %s", (address_from,))
        return json.dumps(result)

class Exchange_address_to(Resource):
    def get(self, address_to):
        result = query_db("SELECT * FROM cross_block.exchanges WHERE address_to = %s", (address_to,))
        return json.dumps(result)

class Exchange_hash_from(Resource):
    def get(self, hash_from):
        result = query_db("SELECT * FROM cross_block.exchanges WHERE hash_from = %s", (hash_from,))
        return json.dumps(result)

class Exchange_hash_to(Resource):
    def get(self, hash_to):
        result = query_db("SELECT * FROM cross_block.exchanges WHERE hash_to = %s", (hash_to,))
        return json.dumps(result)

class Exchange_input_from(Resource):
    def get(self, input_from):

        if input_from[0] + input_from[1] == "0x":
            currency = "ETH"
        else:
            currency = "BTC"

        response = Currency_apis.get_transactions_for_address(currency, input_from)
        result = []

        if response:
            for tx in response:
                found_exchanges = query_db("SELECT * FROM cross_block.exchanges WHERE hash_from = %s", (tx["hash"],))
                result.extend(found_exchanges)
            return json.dumps(result)



class Exchange_input_to(Resource):
    def get(self, input_to):

        if input_to[0] + input_to[1] == "0x":
            currency = "ETH"
        else:
            currency = "BTC"

        response = Currency_apis.get_transactions_for_address(currency, input_to)
        result = []

        for tx in response:
            found_exchanges = query_db("SELECT * FROM cross_block.exchanges WHERE hash_to = %s", (tx["hash"],))
            result.extend(found_exchanges)
        return json.dumps(result)


def query_db(query, parameters):
    db = MySQLdb.connect(host="localhost", user="root", passwd="Sebis2017")
    cur = db.cursor()
    cur.execute(query, parameters)
    results = cur.fetchall()

    empList = []
    for emp in results:
        empDict = {
            "id": emp[0],
            "probability": "90%",
            "currency_from": emp[1],
            "currency_to": emp[2],
            "amount_from": str(emp[3]),
            "amount_to": str(emp[4]),
            "fee_from": str(emp[5]),
            "fee_to": str(emp[6]),
            "address_from": emp[8],
            "address_to": emp[9],
            "hash_from": emp[10],
            "hash_to": emp[11],
            "time_block_from": calendar.timegm(emp[13].timetuple()),
            "time_block_to": calendar.timegm(emp[15].timetuple()),
            "block_nr_from": emp[16],
            "block_nr_to": emp[17],
            "dollarvalue_from": emp[18],
            "dollarvalue_to": emp[19]
        }
        empList.append(empDict)

    #print(json.dumps(empList))
    return empList
    #return {'exchanges': [i[0] for i in results]}

api.add_resource(Exchange_address_from, '/exchanges/address_from/<string:address_from>')
api.add_resource(Exchange_address_to, '/exchanges/address_to/<string:address_to>')
api.add_resource(Exchange_hash_from, '/exchanges/hash_from/<string:hash_from>')
api.add_resource(Exchange_hash_to, '/exchanges/hash_to/<string:hash_to>')
api.add_resource(Exchange_input_from, '/exchanges/input_from/<string:input_from>')
api.add_resource(Exchange_input_to, '/exchanges/input_to/<string:input_to>')



if __name__ == '__main__':
    app.run(debug=True)