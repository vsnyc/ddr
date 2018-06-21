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

def indexFaces(bucket, collectionId, prefix, fileName):
  # s3://ddr-code/jedi-masters/profiles/vsnyc_profile.jpg
  client=boto3.client('rekognition')
  response=client.index_faces(CollectionId=collectionId,
                              Image={'S3Object':{'Bucket':bucket,'Name': prefix + fileName}},
                              ExternalImageId=fileName,
                              DetectionAttributes=['ALL'])

  print ('Faces in ' + fileName)
  faceIds = []
  for faceRecord in response['FaceRecords']:
    faceId = faceRecord['Face']['FaceId']
    print (faceId)
    faceIds.append(faceId)
  return faceIds

def userExists(nickname):
  table = dynamodb.Table(jediTable)
  getItemResult = table.get_item(
      Key={
      'nick_name': nickname
      }
    )
  return 'Item' in getItemResult

def registerUser(nickname, firstName, lastName, hasDP = True):
  regData = {'nick_name': nickname, 'first_name': firstName, 'last_name': lastName, 'scores': {}}
  if hasDP:
    faceId = indexFaces(s3bucket, collectionId, s3prefix, nickname + "_profile.jpg")
    regData['faceId'] = faceId[0]

  table = dynamodb.Table(jediTable)
  response = table.put_item(
    Item=regData
  )
  return response



# Lambda function handler method
def lambda_handler(event, context):
  # 'queryStringParameters': {'l': 'shukla', 'f': 'vinod', 'n': 'vsnyc'}
  logger.info('got event {}'.format(event))
  params = event['queryStringParameters']
  isDuplicate = userExists(nickname=params['n'])

  if not isDuplicate:
    try:
      registerResponse = registerUser(params['n'], params['f'], params['l'] )
      logger.debug('Registration response is {}'.format(registerResponse))
      status = {'statusCode': 200, 'reason': 'Registration successful'}
    except Exception as e:
      status = {'statusCode': 400, 'reason': str(e)}
  else:
    status = {'statusCode': 400, 'reason': 'Duplicate nickname'}

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
