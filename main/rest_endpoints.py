from flask import Flask, jsonify, request
from flask_restful import Resource, Api
import calendar
import MySQLdb
import Currency_apis
from decimal import Decimal
import datetime

app = Flask(__name__)
api = Api(app)
shapeshift_main_address_ETH = "0x70faa28a6b8d6829a4b1e649d26ec9a2a39ba413"
shapeshift_withdrawal_addresses = ["0xd3273eba07248020bf98a8b560ec1576a612102f",
                                        "0x3b0bc51ab9de1e5b7b6e34e5b960285805c41736",
                                        "0xeed16856d551569d134530ee3967ec79995e2051",
                                        "0x563b377a956c80d77a7c613a9343699ad6123911"]

class Exchange_block_nr_from(Resource):
    def get(self):
        start = request.args.get('start')
        end = request.args.get('end')
        currency = request.args.get('currency')
        result = query_db("SELECT * FROM cross_block.exchanges WHERE currency_from = %s AND block_nr_from BETWEEN %s AND %s", (currency, start, end))
        return jsonify(result)

class Exchange_block_nr_to(Resource):
    def get(self):
        start = request.args.get('start')
        end = request.args.get('end')
        currency = request.args.get('currency')
        result = query_db("SELECT * FROM cross_block.exchanges WHERE currency_to = %s AND block_nr_to BETWEEN %s AND %s", (currency, start, end))
        return jsonify(result)

class Exchange_time_range(Resource):
    def get(self):
        start = request.args.get('start')
        end = request.args.get('end')
        start = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M:%S")
        end = datetime.datetime.strptime(end, "%Y-%m-%dT%H:%M:%S")

        result = query_db("SELECT * FROM cross_block.exchanges WHERE time_block_from BETWEEN %s AND %s", (start, end))
        return jsonify(result)

class Exchange_address_from(Resource):
    def get(self, address_from):
        result = query_db("SELECT * FROM cross_block.exchanges WHERE address_from = %s", (address_from,))
        return jsonify(result)

class Exchange_address_to(Resource):
    def get(self, address_to):
        result = query_db("SELECT * FROM cross_block.exchanges WHERE address_to = %s", (address_to,))
        return jsonify(result)

class Exchange_hash_from(Resource):
    def get(self, hash_from):
        result = query_db("SELECT * FROM cross_block.exchanges WHERE hash_from = %s", (hash_from,))
        return jsonify(result)

class Exchange_hash_to(Resource):
    def get(self, hash_to):
        result = query_db("SELECT * FROM cross_block.exchanges WHERE hash_to = %s", (hash_to,))
        return jsonify(result)

class Exchange_input_from(Resource):
    def get(self, input_from):

        if input_from[0] + input_from[1] == "0x":
            currency = "ETH"
        else:
            currency = "BTC"

        response = Currency_apis.get_transactions_for_address(currency, input_from)
        result = []

        if not response or len(response) > 10:
            error = "Too many transactions for this input address"
            return jsonify({ "error": error })
        else:
            for tx in response:
                found_exchanges = query_db("SELECT * FROM cross_block.exchanges WHERE hash_from = %s", (tx["hash"],))
                result.extend(found_exchanges)

            result = sorted(result, key=lambda item:(abs(Decimal(item["diff_from_expected_outcome"]) - 1)))
            return jsonify(result)

class Exchange_input_to(Resource):
    def get(self, input_to):

        if input_to[0] + input_to[1] == "0x":
            currency = "ETH"
        else:
            currency = "BTC"

        if input_to in shapeshift_withdrawal_addresses:
            error = "This is a Shapeshift sending address. Too many outputs"
            return jsonify({ "error": error })

        response = Currency_apis.get_transactions_for_address(currency, input_to)
        result = []

        if not response or len(response) > 10:
            error = "Too many transactions for this input address"
            return jsonify({ "error": error })
        else:
            for tx in response:
                found_exchanges = query_db("SELECT * FROM cross_block.exchanges WHERE hash_to = %s", (tx["hash"],))
                result.extend(found_exchanges)

            result = sorted(result, key=lambda item:(abs(Decimal(item["diff_from_expected_outcome"]) - 1)))
            return jsonify(result)


def query_db(query, parameters):
    db = MySQLdb.connect(host="localhost", user="root", passwd="Sebis2017")
    cur = db.cursor()
    cur.execute(query, parameters)
    results = cur.fetchall()

    empList = []
    for emp in results:
        empDict = {
            "id": emp[0],
            "currency_from": emp[1],
            "currency_to": emp[2],
            "amount_from": str(emp[3]),
            "amount_to": str(emp[4]),
            "fee_from": str(emp[5]),
            "fee_to": str(emp[6]),
            "fee_exchange": str(emp[7]),
            "address_from": emp[8],
            "address_to": emp[9],
            "hash_from": emp[10],
            "hash_to": emp[11],
            "time_block_from": emp[13],
            "time_block_to": emp[15],
            "timestamp_block_from": calendar.timegm(emp[13].timetuple()),
            "timestamp_block_to": calendar.timegm(emp[15].timetuple()),
            "block_nr_from": emp[16],
            "block_nr_to": emp[17],
            "dollarvalue_from": emp[18],
            "dollarvalue_to": emp[19],
            "diff_from_expected_outcome": str(float(emp[4]) / (float(emp[3]) * (emp[18] / emp[19]) - float(emp[7])))
        }

        empList.append(empDict)

    empList = sorted(empList, key=lambda item:(abs(Decimal(item["diff_from_expected_outcome"]) - 1)))
    return empList
    #return {'exchanges': [i[0] for i in results]}

api.add_resource(Exchange_address_from, '/address_from/<string:address_from>')
api.add_resource(Exchange_address_to, '/address_to/<string:address_to>')
api.add_resource(Exchange_hash_from, '/hash_from/<string:hash_from>')
api.add_resource(Exchange_hash_to, '/hash_to/<string:hash_to>')
api.add_resource(Exchange_input_from, '/input_from/<string:input_from>')
api.add_resource(Exchange_input_to, '/input_to/<string:input_to>')
#http://127.0.0.1:5000/block_nr_from?currency=ETH&start=4724183&end=4724185
api.add_resource(Exchange_block_nr_from, '/block_nr_from')
api.add_resource(Exchange_block_nr_to, '/block_nr_to')
api.add_resource(Exchange_time_range, '/time_range')


if __name__ == '__main__':
    app.run(debug=True)