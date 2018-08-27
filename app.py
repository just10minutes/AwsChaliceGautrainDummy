from chalice import Chalice
from chalicelib import db
import os
import boto3
import json

app = Chalice(app_name='hackathon2018')
app.debug = True
_GCDTBL = None #Gautrain Table
_SBADTBL = None #Sb Account Details
_SBTTBL = None #Sb transaction table
_SBGCMTBL = None #Sb Gautrain Card Meta  stores cards meta like email mobile alert etc
_GSGLTBL = None  #Gautrain Stations Geo Location

#Function for cards table
def get_gautrain_cards_details():
    global _GCDTBL
    if _GCDTBL is None:
        _GCDTBL = db.DynamoGautrainCardDetails(
            boto3.resource('dynamodb').Table(
                os.environ['GAUTRAIN_CARDS'])
        )
    return _GCDTBL

#Function for SB data (metadata of cards) table
def get_sb_account_details():
    global _SBADTBL
    if _SBADTBL is None:
        _SBADTBL = db.DynamoSBAccountDetails(
            boto3.resource('dynamodb').Table(
                os.environ['SB_ACCOUNT_DETAILS'])
        )
    return _SBADTBL

#Function for Transaction table
def get_sb_transactions():
    global _SBTTBL
    if _SBTTBL is None:
        _SBTTBL = db.DynamoSBTransactions(
            boto3.resource('dynamodb').Table(
                os.environ['SB_TRANSACTIONS'])
        )
    return _SBTTBL

#Function for sb gautrain card meta
def get_sb_gautrain_cards_meta():
    global _SBGCMTBL
    if _SBGCMTBL is None:
        _SBGCMTBL = db.DynamoSBGautrainCardsMeta(
            boto3.resource('dynamodb').Table(
                os.environ['SB_GAUTRAIN_CARDS_META'])
        )
    return _SBGCMTBL

def get_sb_gautrain_stations_data():
    global _GSGLTBL
    if _GSGLTBL is None:
        _GSGLTBL = db.DynamoGautrainStationDetails(
            boto3.resource('dynamodb').Table(
                os.environ['GAUTRAIN_STATIONS'])
        )
    return _GSGLTBL



@app.route('/', methods=['GET'])
def index():
    return 'Welcome to Hackathon 2018'



#gc stands for Gautrain cards end point
@app.route('/gcd', methods=['GET'],cors=True)
def get_cards():
    return get_gautrain_cards_details().list_all_items()


@app.route('/gcd', methods=['POST'],cors=True)
def add_new_card():
    body = app.current_request.json_body
    return get_gautrain_cards_details().add_item(
        cardId=body['cardId'],
        expiryDate=body['expiryDate'],
        balance=body['balance'],
    )


@app.route('/gcd/{cardId}', methods=['GET'],cors=True)
def get_card(cardId):
    return get_gautrain_cards_details().get_item(cardId)


@app.route('/gcd/{cardId}', methods=['DELETE'],cors=True)
def delete_card(cardId):
    return get_gautrain_cards_details().delete_item(cardId)


@app.route('/gcd/{cardId}', methods=['PUT'],cors=True)
def update_card(cardId):
    body = app.current_request.json_body
    get_gautrain_cards_details().update_item(
        cardId=cardId,
        expiryDate=body.get('expiryDate'),
        balance=body.get('balance')
        )



#sbad stand for Standarda Bank Account details
@app.route('/sbad', methods=['GET'],cors=True)
def list_account_details():
    return get_sb_account_details().list_all_items()

@app.route('/sbad', methods=['POST'],cors=True)
def add_new_account_details():
    body = app.current_request.json_body
    return get_sb_account_details().add_item(
        accountNumber = body['accountNumber'],
        latestBalance = body['latestBalance'],
        currentBalance = body['currentBalance'],
        beneficiaryCount = body['beneficiaryCount'],
        accountKey= body['accountKey'],
        accountType= body['accountType']
    )


@app.route('/sbad/{accountNumber}', methods=['GET'],cors=True)
def get_account_details(accountNumber):
    return get_sb_account_details().get_item(accountNumber)


@app.route('/sbad/{accountNumber}', methods=['DELETE'],cors=True)
def delete_account_details(accountNumber):
    return get_sb_account_details().delete_item(accountNumber)


@app.route('/sbad/{accountNumber}', methods=['PUT'],cors=True)
def update_account_details(accountNumber):
    body = app.current_request.json_body
    get_sb_account_details().update_item(
        accountNumber = accountNumber,
        latestBalance = body['latestBalance'],
        currentBalance = body['currentBalance'],
        beneficiaryCount = body['beneficiaryCount'],
        accountKey= body['accountKey'],
        accountType= body['accountType']
        )



#sbt stands for SB transactions
@app.route('/sbt', methods=['GET'],cors=True)
def get_sb_trans_list():
    return get_sb_transactions().list_all_items()

@app.route('/sbt/{accountNumber}', methods=['GET'],cors=True)
def get_sb_trans_detail(accountNumber):
    return get_sb_transactions().list_items(accountNumber)


@app.route('/sbt', methods=['POST'],cors=True)
def add_sb_trans_new():
    body = app.current_request.json_body
    return get_sb_transactions().add_item(
        topupItemId = body['topupItemId'],
        accountNumber = body['accountNumber'],
        topupType = body['topupType'],
        topupAmount = body['topupAmount'],
        reference = body['reference'],
        lbAlert = body['lbAlert'],
        geoAlert = body['geoAlert'],
        lbLimit = body['lbLimit'],
        email = body['email'],
        mobile = body['mobile']
    )

@app.route('/sbt/delete/{uid}', methods=['DELETE'],cors=True)
def delete_sb_trans_detail(uid):
    return get_sb_transactions().delete_item(uid)



#sbgcm stands for standard bank gautrain card meta
@app.route('/sbgcm/{accountNumber}', methods=['GET'],cors=True)
def get_sb_gc_meta_list(accountNumber):
    return get_sb_gautrain_cards_meta().list_items(accountNumber)


@app.route('/sbgcm', methods=['POST'],cors=True)
def add_sb_gc_meta_new():
    body = app.current_request.json_body
    return get_sb_gautrain_cards_meta().add_item(
        cardId = body['cardId'],
        accountNumber = body['accountNumber'],
        reference = body['reference'],
        lbAlert = body['lbAlert'],
        geoAlert = body['geoAlert'],
        lbLimit = body['lbLimit'],
        email = body['email'],
        mobile = body['mobile']
    )


@app.route('/sbgcm/{accountNumber}/{cardId}', methods=['GET'],cors=True)
def sb_gc_meta_acc_card(accountNumber,cardId):
    return get_sb_gautrain_cards_meta().get_item(accountNumber,cardId)


@app.route('/sbgcm/delete/{accountNumber}/{cardId}', methods=['DELETE'],cors=True)
def delete_sb_gc_meta_acc_card(accountNumber,cardId):
    return get_sb_gautrain_cards_meta().delete_item(accountNumber,cardId)


@app.route('/sbgcm/{accountNumber}/{cardId}', methods=['PUT'],cors=True)
def update_sb_gc_meta_acc_card(accountNumber,cardId):
    body = app.current_request.json_body
    get_sb_gautrain_cards_meta().update_item(
        accountNumber=accountNumber,
        cardId=cardId,
        reference = body['reference'],
        lbAlert = body['lbAlert'],
        geoAlert = body['geoAlert'],
        lbLimit = body['lbLimit'],
        email = body['email'],
        mobile = body['mobile']
        )

@app.route('/sbgcm', methods=['GET'],cors=True)
def get_sb_gautrain_cards_meta_list():
    return get_sb_gautrain_cards_meta().list_all_items()

geoLocations = json.dumps([
        {"sandton":{ "latitude":"10.0","longitude":"20.0"} },
         {"rosebank":{"latitude":"11.0","longitude":"22.0"} }
        ])

@app.route('/gsgl', methods=['GET'],cors=True)
def get_gs_geoLocation():
    #return geoLocations
    data = get_sb_gautrain_stations_data().list_all_items()[0]
    return (data['stations'])

@app.route('/gsgl/list', methods=['GET'],cors=True)
def get_gs_geoLocation():
    #return geoLocations
    data = get_sb_gautrain_stations_data().list_all_items()
    return (data)

@app.route('/gsgl', methods=['POST'],cors=True)
def add_gs_geoLocation():
    body = app.current_request.json_body
    return get_sb_gautrain_stations_data().add_item(
    stations = body
    #stations = geoLocations

    )

@app.route('/gsgl', methods=['DELETE'],cors=True)
def delete_gs_geoLocation():
    return get_sb_gautrain_stations_data().delete_item()

@app.route('/gsgl/update', methods=['PUT'],cors=True)
def update_gs_geoLocation():
    body = app.current_request.json_body
    return get_sb_gautrain_stations_data().update_item(
            stations = body)


@app.route('/test-ddb')
def test_ddb():
    resource = boto3.resource('dynamodb')
    gautrainCards = resource.Table(os.environ['GAUTRAIN_CARDS'])
    sbAcntDtls = resource.Table(os.environ['SB_ACCOUNT_DETAILS'])
    sbTransactions = resource.Table(os.environ['SB_TRANSACTIONS'])
    sbGCMeta = resource.Table(os.environ['SB_GAUTRAIN_CARDS_META'])
    gautrainStations = resource.Table(os.environ['GAUTRAIN_STATIONS'])
    return (gautrainCards.name, sbAcntDtls.name, sbTransactions.name,sbGCMeta.name,gautrainStations.name )





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
