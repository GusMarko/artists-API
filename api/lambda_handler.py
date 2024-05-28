import json
import requests
import os
import boto3
import io
import csv
from scripts.spotify import *
import uuid
import urllib.parse

# pravi se sesija sa s3
s3 = boto3.client("s3")


def lambda_handler(event, context):
    s3 = boto3.client("s3")
    s3_res = boto3.resource("s3")
    # iz metadata od eventa vadimo bucket i fajl koji nam treba
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = urllib.parse.unquote_plus(
        event["Records"][0]["s3"]["object"]["key"], encoding="utf-8"
    )

    response = s3.get_object(Bucket=bucket, Key=key)

    # ovde dekodujemo csv fajl sa potrebnim funkcijama
    data = response["Body"].read().decode("utf-8")
    reader = csv.reader(io.StringIO(data))
    songs_list = []
    for row in reader:
        for item in row:
            songs_list.append(item)

    artists_list = []

    for song in songs_list:
        artists_list.append(get_artist(song))

    ### upisivanje artista iz liste u drugi s3 bucket
    destinations3 = boto3.resource("s3")
    destination_bucket = os.getenv("OUTPUT_BUCKET_NAME")
    body = "\n".join(artists_list)
    id_num = str(uuid.uuid4().hex)
    object = s3_res.Object(
        os.getenv("OUTPUT_BUCKET_NAME"), f"project1/artists-{id_num}.txt"
    )
    object.put(Body=body)
