from uuid import uuid4
from datetime import datetime
from boto3.dynamodb.conditions import Key
import boto3
import os, time, json

#Create empty object for all methods
class TableFunctions(object):
    def list_items(self):
        pass

    def add_item(self):
        pass

    def get_item(self):
        pass

    def delete_item(self):
        pass

    def update_item(self):
        pass

#This is for the expected Gautrain card details data balance and expiryDate
class DynamoGautrainCardDetails(TableFunctions):
    def __init__(self, table_resource):
        self._table = table_resource

    #List all items not specific to any account or card
    def list_all_items(self):
        response = self._table.scan()
        return response['Items']

    #List only specific card details -- This is not getting used as of now
    def list_items(self, cardId):
        response = self._table.query(
            KeyConditionExpression=Key('cardId').eq(cardId)
        )
        return response['Items']

    #Add new entry on the table
    def add_item(self, cardId, expiryDate='2022-12-31', balance=0):
        self._table.put_item(
            Item={
                'cardId' : cardId,
                'expiryDate': expiryDate,
                'balance': int(balance),
            }
        )
        return cardId

    #Get specific card detail
    def get_item(self, cardId):
        response = self._table.get_item(
            Key={
                'cardId': cardId,
                },
        )
        return response['Item']

    #Delete specific data
    def delete_item(self, cardId):
        self._table.delete_item(
            Key={
                'cardId': cardId,
            },
        )

    #update the balance of the card
    def update_balance(self, cardId, balance=0):
        # We could also use update_item() with an UpdateExpression.
        item = self.get_item(cardId)
        if balance is not None:
            item['balance'] = item['balance'] + int(balance)
        self._table.put_item(Item=item)

    #update the entire card of the card
    def update_item(self, cardId, expiryDate, balance=0):
        # We could also use update_item() with an UpdateExpression.
        item = self.get_item(cardId)
        if balance is not None:
            item['balance'] =  int(balance)
        if expiryDate is not None:
            item['expiryDate'] =  expiryDate
        self._table.put_item(Item=item)


class DynamoSBAccountDetails(TableFunctions):
    def __init__(self, table_resource):
        self._table = table_resource

    #List all items not specific to any account or card
    def list_all_items(self):
        response = self._table.scan()
        return response['Items']

    #List only specific card details -- This is not getting used as of now
    def list_items(self, accountNumber):
        response = self._table.query(
            KeyConditionExpression=Key('accountNumber').eq(accountNumber)
        )
        return response['Items']

    #Add new entry on the table
    def add_item(self, accountNumber, accountKey, accountType, latestBalance=0, currentBalance=0, beneficiaryCount=0):
        self._table.put_item(
            Item={
                'accountNumber' : accountNumber,
                'latestBalance': int(latestBalance),
                'currentBalance': int(currentBalance),
                'beneficiaryCount' : int(beneficiaryCount),
                'accountKey': accountKey,
                'accountType': accountType,
            }
        )
        return accountNumber

    #Get specific card detail
    def get_item(self, accountNumber):
        response = self._table.get_item(
            Key={
                'accountNumber': accountNumber,
                },
        )
        return response['Item']

    #Delete specific data
    def delete_item(self, accountNumber):
        self._table.delete_item(
            Key={
                'accountNumber': accountNumber,
            },
        )

    #update the balance of the card
    def update_item(self, accountNumber, latestBalance, currentBalance, beneficiaryCount, accountKey, accountType):
        # We could also use update_item() with an UpdateExpression.
        item = self.get_item(accountNumber)
        if latestBalance is not None:
            item['latestBalance'] = int(latestBalance)
        if currentBalance is not None:
            item['currentBalance'] =  int(currentBalance)
        if beneficiaryCount is not None:
            item['beneficiaryCount'] =  int(beneficiaryCount)
        if accountKey is not None:
            item['accountKey'] =  accountKey
        if accountType is not None:
            item['accountType'] =  accountType
        self._table.put_item(Item=item)

    def deduct_balance(self, accountNumber, amount):
        item = self.get_item(accountNumber)
        item['latestBalance'] = int(item['latestBalance']) - int(amount)
        item['currentBalance'] = int(item['currentBalance']) - int(amount)
        self._table.put_item(Item=item)


class DynamoSBTransactions(TableFunctions):
    def __init__(self, table_resource):
        self._table = table_resource

    def list_all_items(self):
        response = self._table.scan()
        return response['Items']

    def list_items(self, accountNumber):
        response = self._table.query(
            KeyConditionExpression=Key('accountNumber').eq(accountNumber)
        )
        return response['Items']

    def add_item(self, accountNumber, topupItemId, topupType ,topupAmount, reference='', lbAlert='N', geoAlert='N', lbLimit=50, email='', mobile=''   ):
        time_now_utc=str(datetime.utcnow())
        cardId = topupItemId
        balance = int(topupAmount)
        amount = balance
        uid = str(uuid4())
        self._table.put_item(
            Item={
                'uid' : uid,
                'topupItemId' : topupItemId,
                'accountNumber' : accountNumber,
                'topupType' : topupType,
                'topupAmount': int(topupAmount),
                'topup_time' : time_now_utc
            }
        )
        #run few more updates
        #cardId = topupItemId
        if topupType.lower() == 'gautrain':
            print ('Updating Meta data')
            DynamoSBGautrainCardsMeta(boto3.resource('dynamodb').Table(
                os.environ['SB_GAUTRAIN_CARDS_META'])).add_item(cardId, accountNumber, reference,  lbAlert, geoAlert, lbLimit, email, mobile)
            print ('balance deduction in progress')
            DynamoSBAccountDetails(boto3.resource('dynamodb').Table(
                os.environ['SB_ACCOUNT_DETAILS'])).deduct_balance(accountNumber, amount)
            print ('Recharge in progress')
            DynamoGautrainCardDetails(boto3.resource('dynamodb').Table(
                os.environ['GAUTRAIN_CARDS'])).update_balance(cardId, balance)

        return str(accountNumber) + str(topupItemId)

    def get_item(self, uid):
        response = self._table.get_item(
            Key={
                'uid': uid
                },
        )
        return response['Item']

    def delete_item(self, uid):
        self._table.delete_item(
            Key={
                'uid': uid
            },
        )

    def update_item(self, uid, topupItemId, topupAmount, topupType, accountNumber):
        # We could also use update_item() with an UpdateExpression.
        time_now_utc=str(datetime.utcnow())
        item = self.get_item(uid)
        if topupItemId is not None:
            item['topupItemId'] = topupItemId
        if topupAmount is not None:
            item['topupAmount'] = int(topupAmount)
        if time_now_utc is not None:
            item['topup_time'] = time_now_utc
        if topupType is not None:
            item['topupType'] = topupType
        if accountNumber is not None:
            item['accountNumber'] = accountNumber
        self._table.put_item(Item=item)


class DynamoSBGautrainCardsMeta(TableFunctions):
    def __init__(self, table_resource):
        self._table = table_resource

    def list_all_items(self):
        response = self._table.scan()
        return response['Items']

    def list_items(self, accountNumber):
        response = self._table.query(
            KeyConditionExpression=Key('accountNumber').eq(accountNumber)
        )
        return response['Items']

    def add_item(self, cardId, accountNumber, reference='',  lbAlert='N', geoAlert='N', lbLimit=50, email='', mobile='' ):
        time_now_utc=str(datetime.utcnow())
        self._table.put_item(
            Item={
                'cardId' : cardId,
                'accountNumber' : accountNumber,
                'reference' : reference,
                'lbAlert': lbAlert,
                'geoAlert': geoAlert,
                'lbLimit':int(lbLimit),
                'email':email,
                'mobile': mobile,
                'addedOn' : time_now_utc,
                'lastUpdated' : time_now_utc
            }
        )
        return cardId

    def get_item(self, accountNumber, cardId ):
        response = self._table.get_item(
            Key={
                'accountNumber' :accountNumber,
                'cardId': cardId

                },
        )
        return response['Item']

    def delete_item(self, accountNumber, cardId ):
        self._table.delete_item(
            Key={
                'accountNumber' :accountNumber,
                'cardId': cardId,

            },
        )

    def update_item(self, cardId, accountNumber, reference='',  lbAlert='N', geoAlert='N', lbLimit=50, email='', mobile=''):
        # We could also use update_item() with an UpdateExpression.
        time_now_utc=str(datetime.utcnow())
        item = self.get_item(cardId, accountNumber)
        isChanged = 0
        if reference != item['reference']:
            isChanged += 1
            item['reference'] = reference
        if email != item['email']:
            isChanged += 1
            item['email'] = email
        if mobile != item['mobile']:
            isChanged += 1
            item['mobile'] = mobile
        if lbLimit != item['lbLimit']:
            isChanged += 1
            item['lbLimit'] = int(lbLimit)
        if lbAlert != item['lbAlert']:
            isChanged += 1
            item['lbAlert'] = lbAlert
        if geoAlert != item['geoAlert']:
            isChanged += 1
            item['geoAlert'] = geoAlert
        item['addedOn'] = addedOn
        item['lastUpdated'] = time_now_utc
        if isChanged > 0:
            self._table.put_item(Item=item)

class DynamoGautrainStationDetails(TableFunctions):
    def __init__(self, table_resource):
        self._table = table_resource

    def list_all_items(self):
        response = self._table.scan()
        output = response['Items']
        return output

    def add_item(self, stations):
        time_now_utc=str(datetime.utcnow())
        self._table.put_item(
            Item={
                'id' : '1',
                'stations' : json.dumps(stations),
            }
        )
        return stations

    def get_item(self, stations):
        response = self._table.get_item(
            Key={
                'stations': stations,
                },
        )
        return response['Item']

    def delete_item(self):
        self._table.delete_item(
            Key={
                'id': '1',
            },
        )

    def update_item(self, stations):
        # We could also use update_item() with an UpdateExpression.
        self._table.put_item(
            Item={
                'id': '1',
                'stations' : json.dumps(stations)
            }
        )
        return stations
