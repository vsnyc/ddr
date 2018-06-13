import sys
import boto3

def createCollection(collectionId):
  client=boto3.client('rekognition', region_name='us-west-2')
  print('Creating collection:' + collectionId)
  response=client.create_collection(CollectionId=collectionId)
  collectionArn = response['CollectionArn']
  print('Collection ARN: ' + collectionArn)
  return collectionArn

def indexFaces(bucket, collectionId, prefix, fileName):
  # s3://ddr-code/jedi-masters/profiles/vsnyc_profile.jpg
  client=boto3.client('rekognition', region_name='us-west-2')
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

def listFaces(bucket, collectionId):
  maxResults=20
  tokens=True

  client=boto3.client('rekognition', region_name='us-west-2')
  response=client.list_faces(CollectionId=collectionId,
                             MaxResults=maxResults)

  print('Faces in collection ' + collectionId)

  while tokens:

    faces=response['Faces']

    for face in faces:
      print (face)
    if 'NextToken' in response:
      nextToken=response['NextToken']
      response=client.list_faces(CollectionId=collectionId,
                                 NextToken=nextToken,MaxResults=maxResults)
    else:
      tokens=False


def searchFaces(bucket, collectionId, s3Prefix, s3FileName):
  threshold = 70
  maxFaces=2
  client=boto3.client('rekognition', region_name = 'us-west-2')

  response=client.search_faces_by_image(CollectionId=collectionId,
                                        Image={'S3Object':{'Bucket':bucket,'Name':s3Prefix + s3FileName}},
                                        FaceMatchThreshold=threshold,
                                        MaxFaces=maxFaces)

  faceMatches=response['FaceMatches']
  print ('Matching faces')
  for match in faceMatches:
    print ('FaceId:' + match['Face']['FaceId'])
    print ('Similarity: ' + "{:.2f}".format(match['Similarity']) + "%")
    print ()


def main(argv):
  # collectionArn = createCollection('jedi-masters')

  # Should not index the same face multiple times
  # faceIds = indexFaces('ddr-code', 'jedi-masters', 'jedi-masters/profiles/', 'vsnyc_profile.jpg')
  # faceIds0 = indexFaces('ddr-code', 'jedi-masters', 'jedi-masters/profiles/', 'vsnyc_profile0.jpg')
  # faceIds1 = indexFaces('ddr-code', 'jedi-masters', 'jedi-masters/profiles/', 'vsnyc_profile1.jpg')
  listFaces('ddr-code', 'jedi-masters')
  # This can be used to identify faceId for pose images
  searchFaces('ddr-code', 'jedi-masters', 'jedi-masters/profiles/', 'vsnyc_pose1.jpg')


if __name__ == '__main__':
  main(sys.argv[1:])