from uuid import uuid4
from datetime import datetime
from boto3.dynamodb.conditions import Key

#This account will be used as default
DEFAULT_ACCOUNT = '2018090506'

#Create empty object for all methods
class CardsDB(object):
    def list_items(self):
        pass

    def add_item(self, description, metadata=None):
        pass

    def get_item(self, uid):
        pass

    def delete_item(self, uid):
        pass

    def update_item(self, uid, description=None, state=None,
                    metadata=None):
        pass

#This is for the expected Gautrain card details data balance and expiry_date
class DynamoDBCards(CardsDB):
    def __init__(self, table_resource):
        self._table = table_resource

    #List all items not specific to any account or card
    def list_all_items(self):
        response = self._table.scan()
        return response['Items']

    #List only specific card details -- This is not getting used as of now
    def list_items(self, card_id):
        response = self._table.query(
            KeyConditionExpression=Key('card_id').eq(card_id)
        )
        return response['Items']

    #Add new entry on the table
    def add_item(self, card_id, expiry_date='2022-12-31', balance=0):
        self._table.put_item(
            Item={
                'card_id' : card_id,
                'expiry_date': expiry_date,
                'balance': balance,
            }
        )
        return card_id

    #Get specific card detail
    def get_item(self, card_id):
        response = self._table.get_item(
            Key={
                'card_id': card_id,
                },
        )
        return response['Item']

    #Delete specific data
    def delete_item(self, card_id):
        self._table.delete_item(
            Key={
                'card_id': card_id,
            },
        )

    #update the balance of the card
    def update_balance(self, card_id, balance=0):
        # We could also use update_item() with an UpdateExpression.
        item = self.get_item(card_id)
        if balance is not None:
            item['balance'] = item['balance'] + balance
        self._table.put_item(Item=item)



class DynamoDBSb(CardsDB):
    def __init__(self, table_resource):
        self._table = table_resource

    def list_all_items(self):
        response = self._table.scan()
        return response['Items']

    def list_items(self, account_num=DEFAULT_ACCOUNT):
        response = self._table.query(
            KeyConditionExpression=Key('account_num').eq(account_num)
        )
        return response['Items']

    def add_item(self, card_id, reference='', email='', mobile='',lb_limit=50, lb_alert='N',geo_alert='N',alert_to='', account_num=DEFAULT_ACCOUNT,):
        time_now_utc=str(datetime.utcnow())
        self._table.put_item(
            Item={
                'card_id' : card_id,
                'account_num' : account_num,
                'reference' : reference,
                'email': email,
                'mobile': mobile,
                'lb_limit':lb_limit,
                'lb_alert':lb_alert,
                'geo_alert': geo_alert,
                'alert_to': alert_to,
                'added_on' : time_now_utc,
                'last_updated' : time_now_utc
            }
        )
        return card_id

    def get_item(self, card_id, account_num=DEFAULT_ACCOUNT):
        response = self._table.get_item(
            Key={
                'card_id': card_id,
                'account_num' :account_num,
                },
        )
        return response['Item']

    def delete_item(self, card_id, account_num=DEFAULT_ACCOUNT):
        self._table.delete_item(
            Key={
                'card_id': card_id,
                'account_num' :account_num,
            },
        )

    def update_item(self, card_id, reference, email, mobile, lb_limit, lb_alert, geo_alert,alert_to, added_on, account_num=DEFAULT_ACCOUNT):
        # We could also use update_item() with an UpdateExpression.
        time_now_utc=str(datetime.utcnow())
        item = self.get_item(card_id, account_num)
        if reference is not None:
            item['reference'] = reference
        if email is not None:
            item['email'] = email
        if mobile is not None:
            item['mobile'] = mobile
        if lb_limit is not None:
            item['lb_limit'] = lb_limit
        if lb_alert is not None:
            item['lb_alert'] = lb_alert
        if geo_alert is not None:
            item['geo_alert'] = geo_alert
        if alert_to is not None:
            item['alert_to'] = alert_to
        if added_on is not None:
            item['added_on'] = added_on
        if time_now_utc is not None:
            item['last_updated'] = time_now_utc
        self._table.put_item(Item=item)


class DynamoDBSbTrans(CardsDB):
    def __init__(self, table_resource):
        self._table = table_resource

    def list_all_items(self):
        response = self._table.scan()
        return response['Items']

    def list_items(self, account_num=DEFAULT_ACCOUNT):
        response = self._table.query(
            KeyConditionExpression=Key('account_num').eq(account_num)
        )
        return response['Items']

    def add_item(self, card_id, topup, account_num=DEFAULT_ACCOUNT):
        time_now_utc=str(datetime.utcnow())
        uid = str(uuid4())
        self._table.put_item(
            Item={
                'uid' : uid,
                'card_id' : card_id,
                'account_num' : account_num,
                'topup': topup,
                'topup_time' : time_now_utc
            }
        )
        return uid

    def get_item(self, uid, account_num=DEFAULT_ACCOUNT):
        response = self._table.get_item(
            Key={
                'uid': uid,
                'account_num' :account_num,
                },
        )
        return response['Item']

    def delete_item(self, uid, account_num=DEFAULT_ACCOUNT):
        self._table.delete_item(
            Key={
                'uid': uid,
                'account_num' :account_num,
            },
        )

    def update_item(self, uid, card_id, topup, account_num=DEFAULT_ACCOUNT):
        # We could also use update_item() with an UpdateExpression.
        time_now_utc=str(datetime.utcnow())
        item = self.get_item(uid, account_num)
        if card_id is not None:
            item['card_id'] = card_id
        if topup is not None:
            item['topup'] = topup
        if time_now_utc is not None:
            item['topup_time'] = time_now_utc
        self._table.put_item(Item=item)
