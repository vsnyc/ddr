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
leaderboardTable = os.environ['leaderboardTable']

dynamodb = boto3.resource('dynamodb')

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def fetchLeaderboard(count = 10):
  table = dynamodb.Table(leaderboardTable)
  response = table.get_item(
    Key={
      'all_scores': 'dummy'
    }
  )
  logger.debug("leaderboard response")
  print(json.dumps(response, indent=4, cls=DecimalEncoder))
  scores = response['Item']['scores']
  sorted_x = sorted(scores.items(), key=operator.itemgetter(1), reverse=True)
  print(json.dumps(scores, indent=4, cls=DecimalEncoder))
  return sorted_x[:count]


# Lambda function handler method
def lambda_handler(event, context):
  logger.info('got event {}'.format(event))

  leaderBoard = fetchLeaderboard()

  logger.debug('score is {}'.format(leaderBoard))

  status = leaderBoard

  response = {
    "statusCode": 200,
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
