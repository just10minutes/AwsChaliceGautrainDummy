from chalice import Chalice
from chalicelib import db
import os
import boto3

app = Chalice(app_name='gautrain')
app.debug = True
_DB = None
_SB = None #Sb table stores cards meta like email mobile alert etc
_SBT = None #Sb transaction table_exists

#Function for cards table
def get_app_db():
    global _DB
    if _DB is None:
        _DB = db.DynamoDBCards(
            boto3.resource('dynamodb').Table(
                os.environ['CARDS_TABLE_NAME'])
        )
    return _DB

#Function for SB data (metadata of cards) table
def get_sb_db():
    global _SB
    if _SB is None:
        _SB = db.DynamoDBSb(
            boto3.resource('dynamodb').Table(
                os.environ['SB_TABLE_NAME'])
        )
    return _SB

#Function for Transaction table
def get_sbt_db():
    global _SBT
    if _SBT is None:
        _SBT = db.DynamoDBSbTrans(
            boto3.resource('dynamodb').Table(
                os.environ['SB_TRANS_TABLE_NAME'])
        )
    return _SBT

@app.route('/', methods=['GET'])
def index():
    return 'Welcome to Hackathon 2018'



#gc stands for Gautrain cards end point
@app.route('/gc', methods=['GET'])
def get_cards():
    return get_app_db().list_all_items()


@app.route('/gc', methods=['POST'])
def add_new_card():
    body = app.current_request.json_body
    return get_app_db().add_item(
        card_id=body['card_id'],
        expiry_date=body['expiry_date'],
        balance=body['balance'],
    )


@app.route('/gc/{card_id}', methods=['GET'])
def get_card(card_id):
    return get_app_db().get_item(card_id)


@app.route('/gc/{card_id}', methods=['DELETE'])
def delete_card(card_id):
    return get_app_db().delete_item(card_id)


@app.route('/gc/{card_id}', methods=['PUT'])
def update_card(card_id):
    body = app.current_request.json_body
    get_app_db().update_balance(
        card_id=card_id,
        balance=body.get('balance')
        )

#sb stands for standard bank details which is saved from bank side
@app.route('/sb', methods=['GET'])
def get_sb_cards():
    return get_sb_db().list_items()


@app.route('/sb', methods=['POST'])
def add_sb_new_card():
    body = app.current_request.json_body
    return get_sb_db().add_item(
        card_id=body['card_id'],
        email=body['email'],
        mobile=body['mobile'],
        lb_limit=body['lb_limit'],
        lb_alert=body['lb_alert'],
        geo_alert=body['geo_alert'],
        alert_to=body['alert_to'],
    )


@app.route('/sb/{card_id}', methods=['GET'])
def get_sb_card(card_id):
    return get_sb_db().get_item(card_id)


@app.route('/sb/{card_id}', methods=['DELETE'])
def delete_sb_card(card_id):
    return get_sb_db().delete_item(card_id)


@app.route('/sb/{card_id}', methods=['PUT'])
def update_sb_card(card_id):
    body = app.current_request.json_body
    get_sb_db().update_item(
        card_id=card_id,
        reference=body.get('reference'),
        email=body.get('email'),
        mobile=body.get('mobile'),
        lb_limit=body.get('lb_limit'),
        lb_alert=body.get('lb_alert'),
        geo_alert=body.get('geo_alert'),
        alert_to=body.get('alert_to'),
        added_on=body.get('added_on')
        )

@app.route('/sb/list', methods=['GET'])
def get_sb_cards_list():
    return get_sb_db().list_all_items()



#sbt stands for SB transactions
@app.route('/sbt', methods=['GET'])
def get_sbt_trans():
    return get_sbt_db().list_items()


@app.route('/sbt', methods=['POST'])
def add_sbt_new_card():
    body = app.current_request.json_body
    return get_sbt_db().add_item(
        card_id=body['card_id'],
        topup=body['topup'],
    )

@app.route('/sbt/list', methods=['GET'])
def get_sbt_trans_list():
    return get_sbt_db().list_all_items()


@app.route('/test-ddb')
def test_ddb():
    resource = boto3.resource('dynamodb')
    cards = resource.Table(os.environ['CARDS_TABLE_NAME'])
    sb = resource.Table(os.environ['SB_TABLE_NAME'])
    sbt = resource.Table(os.environ['SB_TRANS_TABLE_NAME'])
    return (cards.name, sb.name, sbt.name)




'''
Get and post request URL samples
Gautrain exposed data
    List all available cards
        https://3knn851s69.execute-api.us-east-2.amazonaws.com/api/
    Get a Specific card data:
        https://3knn851s69.execute-api.us-east-2.amazonaws.com/api/123456789012345
    Post new card data:
        echo {"card_id" : "123456789012315" , "expiry_date" : "2019-12-31" , "balance" : 10} | http POST https://3knn851s69.execute-api.us-east-2.amazonaws.com/api/
    Update Balance:
        echo { "balance" : 20} | http PUT https://3knn851s69.execute-api.us-east-2.amazonaws.com/api/123456789012345
    Delete Card
        http DELETE https://3knn851s69.execute-api.us-east-2.amazonaws.com/api/123456789012345


Standard Bank - Card Metadata for Adding and notification
    List cards linked to specific account - account_num is used as default account number 2018090506
        https://3knn851s69.execute-api.us-east-2.amazonaws.com/api/sb
    Get a Specific card data:
        https://3knn851s69.execute-api.us-east-2.amazonaws.com/api/sb/123456789012345
    Post new card data:
        echo {"card_id" : "123456789012315" , "email" : "rajesh.hemmadi@standardbank.co.za" , "mobile" : "0838993991", "lb_limit" : 100 , "lb_alert":"Yes" , "geo_alert" : "Yes", "alert_to" : "email" }
        | http POST https://3knn851s69.execute-api.us-east-2.amazonaws.com/api/sb
    Update Card Details:
        echo { "email" : "rajesh.hemmadi@standardbank.co.za" , "mobile" : "0838993991", "lb_limit" : 100 , "lb_alert":"Yes" , "geo_alert" : "Yes", "alert_to" : "email" }
        | http POST https://3knn851s69.execute-api.us-east-2.amazonaws.com/api/sb/123456789012315
    Delete Card
        http DELETE https://3knn851s69.execute-api.us-east-2.amazonaws.com/api/sb/123456789012345
    List all SB card list not specific to any account
        https://3knn851s69.execute-api.us-east-2.amazonaws.com/api/sb/list


standardbank card transaction details
    List transaction related to specific account
        https://3knn851s69.execute-api.us-east-2.amazonaws.com/api/sbt
    Add new transaction
        echo {"card_id" : "123456789012315" , "topup": 50} | http POST https://3knn851s69.execute-api.us-east-2.amazonaws.com/api/sbt

    List all transaction # not related to any specific account
        https://3knn851s69.execute-api.us-east-2.amazonaws.com/api/sbt



Create table command
    python createtable.py --table-type sb_trans #anyone from the list[cards,sb,sb_trans]
Get table name  #Change the table name in test_ddb
    http localhost:8000/test-ddb
Delete table
    aws dynamodb delete-table --table-name sb-4fecc4cf-16a2-4437-bc3a-bdc0a7bd1b87

'''
