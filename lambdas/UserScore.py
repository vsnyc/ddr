import decimal
import json
import logging
import operator
import os

import boto3

s3bucket = os.environ['s3bucket']
collectionId = os.environ['collectionId']
s3prefix = os.environ['s3prefix']
# s3region = 'us-west-2'
jediTable = os.environ['jediTable']
#leaderboardTable = os.environ['leaderboardTable']

dynamodb = boto3.resource('dynamodb')

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def scoreTotal(nickname):
  table = dynamodb.Table(jediTable)
  response = table.get_item(
    Key={
      'nick_name': nickname
    }
  )
  scores = response['Item']['scores'].values()
  avg = float(sum(scores))/len(scores)
  return avg


# Lambda function handler method
def lambda_handler(event, context):
  # 'queryStringParameters': {'l': 'shukla', 'f': 'vinod', 'n': 'vsnyc'}
  logger.info('got event {}'.format(event))
  params = event['queryStringParameters']

  try:
    scoreResponse = scoreTotal(nickname=params['n'])
    logger.debug('User {} score is {}'.format(params['n'], scoreResponse))
    status = {'statusCode': 200, 'score': scoreResponse}
  except Exception as e:
    status = {'statusCode': 400, 'reason': -1}

  response = {
    "statusCode": status['statusCode'],
    "headers": {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "POST"
    },
    "body": json.dumps(status, indent=4, cls=DecimalEncoder)
  }

  return response


class DecimalEncoder(json.JSONEncoder):
  # Helper class to convert a DynamoDB item to JSON.
  def default(self, o):
    if isinstance(o, decimal.Decimal):
      if o % 1 > 0:
        return float(o)
      else:
        return int(o)
    return super(DecimalEncoder, self).default(o)
