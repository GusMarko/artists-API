import json
import requests
import os
import boto3
import io
import csv
import scripts.spotify
import uuid

# pravi se sesija sa s3
s3 = boto3.client("s3")


def lambda_handler(event, context):
    # iz metadata od eventa vadimo bucket i fajl koji nam treba
    bucket = event["Records"][0]["bucket"]["name"]
    key = event["Records"][0]["s3"]["object"]["key"]

    response = s3.get_object(Bucket=bucket, Key=key)

    # ovde dekodujemo csv fajl sa potrebnim funkcijama
    data = response["Body"].read().decode("utf-8")
    reader = csv.reader(io.StringIO(data))
    songs_list = []
    for row in reader:
        for item in row:
            songs_list.append(item)

    artist_list = []

    for song in songs_list:
        artists_list.append(get_artist(song))

    ### upisivanje artista iz liste u dynamo db
    dynamodb = boto3.client("dynamodb")
    table = dynamodb.Table(os.getenv(ARTISTS_TABLE))
    id_num = uuid.uuid4()

    for artist in artist_list:
        table.put_item(Item={"DataId": id_num, "ArtistName": artist})
        id_num = uuid.uuid4()
