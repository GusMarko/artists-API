from requests import post, get
import os
import json
import base64


# test funckija
def main():

    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    token = get_token(client_id, client_secret)
    track_data = search_for_track(token, "highest in the room")

    artist = track_data["tracks"]["items"][0]["album"]["artists"][0]["name"]
    print(artist)


# potreban nam je spotify access token da bismo obavljali api pozive,
# koji dobijamo tako sto saljemo  user kredencijale (id , secret)
# kroz encode base64- da bismo dobili token
def get_token(client_id, client_secret):
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    # ovo su potrebni info koje prosledjujemo pri trazenju tokena
    # authorization , content type, grant type
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token


# fukncija koja namesta automatski header za buduce pozive
# nije obavezna
def get_auth_header(token):
    return {"Authorization": "Bearer " + token}


# funkcija koja ce traziti pesmu
# url koji saljemo, headers koje prosledjujemo (token)
# query je sta trazimo + mogucnost filtriranja search-a
def search_for_track(token, track_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={track_name}&type=track&limit=1"

    # url i query se spajaju da bi zahtev bio potpun
    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)
    return json_result


def get_artist(song_name):

    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    token = get_token(client_id, client_secret)
    track_data = search_for_track(token, song_name)

    artist = track_data["tracks"]["items"][0]["album"]["artists"][0]["name"]
    return artist


if __name__ == "__main__":
    main()
