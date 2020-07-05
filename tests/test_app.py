"""Integration test suite for app.py"""
import json, os

os.environ["MONGO_USER"] = "admin"
os.environ["MONGO_PASSWORD"] = "admin"
os.environ["DB_NAME"] = "test"

from flaskr.app import app, mongo
from http import HTTPStatus
from flask_pymongo import PyMongo
import pytest


@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown():
    """
    Setup and teardown for each test
    """
    with open("songs.json") as json_file:
        data = json.load(json_file)

    mongo.db["songs"].insert_many(data)

    yield

    mongo.db["songs"].delete_many({})


def test_get_songs_success():
    """
    GET /songs

    Should retrieve the song correctly
    """
    client = app.test_client()
    url = "/songs"

    response = client.get(url)

    responsed_data = json.loads(response.data)
    assert response.status_code == HTTPStatus.OK
    assert len(responsed_data["songs"]) == 10
    assert responsed_data["songs"][0]["title"] == "Lycanthropic Metamorphosis"

    """With pagination"""
    url = "/songs?from={}".format(responsed_data["last_id"])

    response = client.get(url)

    responsed_data = json.loads(response.data)
    assert response.status_code == HTTPStatus.OK
    assert len(responsed_data["songs"]) == 1
    assert responsed_data["songs"][0]["title"] == "Babysitting"


def test_get_average_songs_difficulty_success():
    """
    GET /songs/avg/diffulty

    Should retrieve the song average difficulty correctly with level
    """
    client = app.test_client()
    url = "/songs/avg/difficulty"

    response = client.get(url)

    responsed_data = json.loads(response.data)
    assert response.status_code == HTTPStatus.OK
    assert responsed_data["avg_difficulty"] == 10.32

    """With query string"""
    url = "/songs/avg/difficulty?level=9"

    response = client.get(url)

    responsed_data = json.loads(response.data)
    assert response.status_code == HTTPStatus.OK
    assert responsed_data["avg_difficulty"] == 9.69


def test_get_average_songs_difficulty_fail():
    """
    GET /songs/avg/diffulty

    Should return NOT FOUND if there is no songs with requested level
    """
    client = app.test_client()
    url = "/songs/avg/difficulty?level=100"

    response = client.get(url)

    responsed_data = json.loads(response.data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert responsed_data["message"] == "No songs found with level 100"


def test_song_search_success():
    """
    GET /songs/search

    Should return songs that have artist or title matches search string
    """
    client = app.test_client()
    url = "/songs/search?q=finger"

    response = client.get(url)

    responsed_data = json.loads(response.data)
    assert response.status_code == HTTPStatus.OK
    assert len(responsed_data) == 2
    assert responsed_data[0]["artist"] == "Mr Fastfinger"
    assert responsed_data[0]["title"] == "Awaki-Waki"
    assert responsed_data[1]["artist"] == "The Yousicians"
    assert responsed_data[1]["title"] == "Greasy Fingers - boss level"

    """Return empty list if search string have no matches"""
    url = "/songs/search?q=woohoo"

    response = client.get(url)

    responsed_data = json.loads(response.data)
    assert response.status_code == HTTPStatus.OK
    assert len(responsed_data) == 0


def test_rate_song_success():
    """
    POST /songs/rating

    Should add rating to the song and return the updated data
    """
    client = app.test_client()
    response = client.get("/songs")
    responsed_data = json.loads(response.data)
    song_id = json.loads(response.data)["songs"][0]["_id"]

    url = "/songs/rating"

    response = client.post(
        url, data=json.dumps({"_id": song_id, "rating": 5}), headers={"Content-Type": "application/json"}
    )
    response = client.post(
        url, data=json.dumps({"_id": song_id, "rating": 3}), headers={"Content-Type": "application/json"}
    )

    responsed_data = json.loads(response.data)
    assert response.status_code == HTTPStatus.OK
    assert responsed_data["_id"] == song_id
    assert responsed_data["rates"] == [5, 3]


def test_rate_song_fail():
    """
    POST /songs/rating

    Should return BAD REQUEST if payload is invalid
    """
    client = app.test_client()
    response = client.get("/songs")
    responsed_data = json.loads(response.data)
    song_id = json.loads(response.data)["songs"][0]["_id"]

    url = "/songs/rating"

    response = client.post(
        url, data=json.dumps({"_id": song_id, "haha": 5}), headers={"Content-Type": "application/json"}
    )

    responsed_data = json.loads(response.data)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert responsed_data["message"] == {
        "rating": ["Missing data for required field."],
        "haha": ["Unknown field."],
    }

    """
    Should return BAD REQUEST if rating is not in range 1 to 5
    """
    response = client.post(
        url, data=json.dumps({"_id": song_id, "rating": 7}), headers={"Content-Type": "application/json"}
    )

    responsed_data = json.loads(response.data)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert responsed_data["message"] == {"rating": ["Rating must be in between 1 and 5"]}


def test_get_song_avg_rating():
    """
    GET /songs/avg/rating/<song_id>

    Return the rating data of a song include: lowest, highest, average and count
    """
    client = app.test_client()
    response = client.get("/songs")
    responsed_data = json.loads(response.data)
    song_id1 = json.loads(response.data)["songs"][0]["_id"]
    song_id2 = json.loads(response.data)["songs"][1]["_id"]
    response = client.post(
        "/songs/rating",
        data=json.dumps({"_id": song_id1, "rating": 5}),
        headers={"Content-Type": "application/json"},
    )
    response = client.post(
        "/songs/rating",
        data=json.dumps({"_id": song_id1, "rating": 3}),
        headers={"Content-Type": "application/json"},
    )

    url = "/songs/avg/rating/{}".format(song_id1)

    response = client.get(url)

    responsed_data = json.loads(response.data)
    assert response.status_code == HTTPStatus.OK
    assert responsed_data == {"lowest": 3, "highest": 5, "average": 4, "count": 2}

    """
    Return -1 for each fields when the song doesn't have any rating
    """
    url = "/songs/avg/rating/{}".format(song_id2)

    response = client.get(url)

    responsed_data = json.loads(response.data)
    assert response.status_code == HTTPStatus.OK
    assert responsed_data == {"lowest": -1, "highest": -1, "average": -1, "count": 0}
