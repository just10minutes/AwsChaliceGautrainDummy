from chalice import Chalice
from chalicelib import db
import os
import boto3

app = Chalice(app_name='gautrain')
app.debug = True
_DB = None


def get_app_db():
    global _DB
    if _DB is None:
        _DB = db.DynamoDBCards(
            boto3.resource('dynamodb').Table(
                os.environ['CARDS_TABLE_NAME'])
        )
    return _DB


@app.route('/', methods=['GET'])
def get_cards():
    return get_app_db().list_all_items()


@app.route('/', methods=['POST'])
def add_new_card():
    body = app.current_request.json_body
    return get_app_db().add_item(
        card_id=body['card_id'],
        expiry_date=body['expiry_date'],
        balance=body['balance'],
    )


@app.route('/{card_id}', methods=['GET'])
def get_card(card_id):
    return get_app_db().get_item(card_id)


@app.route('/{card_id}', methods=['DELETE'])
def delete_card(card_id):
    return get_app_db().delete_item(card_id)


@app.route('/{card_id}', methods=['PUT'])
def update_card(card_id):
    body = app.current_request.json_body
    get_app_db().update_item(
        card_id=card_id,
        balance=body.get('balance')
        )

@app.route('/test-ddb')
def test_ddb():
    resource = boto3.resource('dynamodb')
    table = resource.Table(os.environ['CARDS_TABLE_NAME'])
    return table.name
