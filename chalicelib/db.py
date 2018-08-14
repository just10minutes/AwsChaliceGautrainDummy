from uuid import uuid4

from boto3.dynamodb.conditions import Key


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

class DynamoDBCards(CardsDB):
    def __init__(self, table_resource):
        self._table = table_resource

    def list_all_items(self):
        response = self._table.scan()
        return response['Items']

    def list_items(self, card_id):
        response = self._table.query(
            KeyConditionExpression=Key('card_id').eq(card_id)
        )
        return response['Items']

    def add_item(self, card_id, expiry_date='2022-12-31', balance=0):
        self._table.put_item(
            Item={
                'card_id' : card_id,
                'expiry_date': expiry_date,
                'balance': balance,
            }
        )
        return card_id

    def get_item(self, card_id):
        response = self._table.get_item(
            Key={
                'card_id': card_id,
                },
        )
        return response['Item']

    def delete_item(self, card_id):
        self._table.delete_item(
            Key={
                'card_id': card_id,
            }
        )

    def update_item(self, card_id, balance=0):
        # We could also use update_item() with an UpdateExpression.
        item = self.get_item(card_id)
        if balance is not None:
            item['balance'] = item['balance'] + balance
        self._table.put_item(Item=item)
