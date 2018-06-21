import sys
import boto3
import json
import test.rekognition_faceid
import ddr_server.ddb_util
import decimal
import operator

s3bucket = 'ddr-code'
collectionId = 'jedi-masters'
s3prefix = 'jedi-masters/profiles/'
s3region = 'us-west-2'
dynamodb = boto3.resource('dynamodb', region_name=s3region)
jediTable = 'jedi-api-1-JediMastersTable-B5N4X9Q7ZK0K'
leaderboardTable = 'jedi-api-1-JediLeaderboardTable-1S38W5DL2YTQ3'

def registerUser(nickname, firstName, lastName, hasDP = True):
  regData = {'nick_name': nickname, 'first_name': firstName, 'last_name': lastName, 'scores': {}}
  if hasDP:
    faceId = test.rekognition_faceid.indexFaces(s3bucket, collectionId, s3prefix, nickname + "_profile.jpg")
    regData['faceId'] = faceId[0]

  table = dynamodb.Table(jediTable)
  response = table.put_item(
    Item=regData
  )

  print(json.dumps(response, indent=4, cls=ddr_server.ddb_util.DecimalEncoder))

def saveScore(nickname, poseNum, score):
  table = dynamodb.Table(jediTable)
  response = table.update_item(
      Key={
        'nick_name': nickname
      },
      UpdateExpression="set scores.pose" + str(poseNum) + " = :s",
      ExpressionAttributeValues={
        ':s': decimal.Decimal(score)
      },
      ReturnValues="UPDATED_NEW"
    )
  print(json.dumps(response, indent=4, cls=ddr_server.ddb_util.DecimalEncoder))

def updateLeaderboard(nickname):
  table = dynamodb.Table(leaderboardTable)
  try:
    response = table.update_item(
      Key={
        'all_scores': 'dummy'
      },
      UpdateExpression="set scores." + nickname + " = :s",
      ExpressionAttributeValues={
        ':s': decimal.Decimal(scoreTotal(nickname))
      },
      ReturnValues="UPDATED_NEW"
    )
  except:
    scoresData = {
      'all_scores': 'dummy',
      'scores': {
        nickname: decimal.Decimal(scoreTotal(nickname))
      }
    }
    response = table.put_item(
      Item=scoresData
    )
  print(json.dumps(response, indent=4, cls=ddr_server.ddb_util.DecimalEncoder))


def fetchScore(nickname, poseNum):
  table = dynamodb.Table(jediTable)
  response = table.get_item(
    Key={
      'nick_name': nickname
    }
  )
  return response['Item']['scores']['pose' + str(poseNum)]

def fetchLeaderboard(count = 10):
  table = dynamodb.Table(leaderboardTable)
  response = table.get_item(
    Key={
      'all_scores': 'dummy'
    }
  )

  scores = response['Item']['scores']
  sorted_x = sorted(scores.items(), key=operator.itemgetter(1), reverse=True)
  print(sorted_x[:count])
  print(json.dumps(scores, indent=4, cls=ddr_server.ddb_util.DecimalEncoder))

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

def main(argv):
  # Registration done via API
  # e.g. https://m6ijjr30j9.execute-api.us-west-2.amazonaws.com/prod/register?n=vsnyc&f=Vinod&l=Shukla
  # registerUser('vsnyc', 'Vinod', 'Shukla', hasDP=False)

  saveScore('abc_def', 1, '100.0')
  saveScore('abc_def', 2, '90.0')
  updateLeaderboard('abc_def')

  saveScore('vsnyc', 1, '80.0')
  saveScore('vsnyc', 2, '80.0')
  updateLeaderboard('vsnyc')

  # #saveScore('vsnyc', 'Total', 80.0)
  # score1 = fetchScore('vsnyc', 1)
  # scoreT = scoreTotal('vsnyc2')
  # print(score1)
  # print(scoreT)
  # #updateLeaderboard('vsnyc')

  # fetchLeaderboard()


if __name__ == '__main__':
  main(sys.argv[1:])