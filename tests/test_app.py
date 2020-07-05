"""Integration test suite for app.py"""
import json, os
from flaskr.app import app, mongo
from http import HTTPStatus
from flask_pymongo import PyMongo
import pytest

client = app.test_client()


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

    def without_pagination():
        url = "/songs"
        response = client.get(url)

        responsed_data = json.loads(response.data)
        assert response.status_code == HTTPStatus.OK
        assert len(responsed_data["songs"]) == 10
        assert responsed_data["songs"][0]["title"] == "Lycanthropic Metamorphosis"

        return responsed_data["last_id"]

    last_id = without_pagination()

    def with_pagination():
        url = "/songs?from={}".format(last_id)

        response = client.get(url)

        responsed_data = json.loads(response.data)
        assert response.status_code == HTTPStatus.OK
        assert len(responsed_data["songs"]) == 1
        assert responsed_data["songs"][0]["title"] == "Babysitting"

    with_pagination()


def test_get_average_songs_difficulty_success():
    """
    GET /songs/avg/diffulty

    Should retrieve the song average difficulty correctly
    """

    def without_level():
        url = "/songs/avg/difficulty"

        response = client.get(url)

        responsed_data = json.loads(response.data)
        assert response.status_code == HTTPStatus.OK
        assert responsed_data["avg_difficulty"] == 10.32

    def with_level():
        url = "/songs/avg/difficulty?level=9"

        response = client.get(url)

        responsed_data = json.loads(response.data)
        assert response.status_code == HTTPStatus.OK
        assert responsed_data["avg_difficulty"] == 9.69

    without_level()
    with_level()


def test_get_average_songs_difficulty_fail():
    """
    GET /songs/avg/diffulty

    Should return NOT FOUND if there is no songs with requested level
    """
    url = "/songs/avg/difficulty?level=9999"

    response = client.get(url)

    responsed_data = json.loads(response.data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert responsed_data["message"] == "No songs found with level 9999"


def test_song_search_success():
    """
    GET /songs/search

    Should return songs that have artist or title matches search string
    """

    def has_2_matches():
        url = "/songs/search?q=finger"

        response = client.get(url)

        responsed_data = json.loads(response.data)
        assert response.status_code == HTTPStatus.OK
        assert len(responsed_data) == 2
        assert responsed_data[0]["artist"] == "Mr Fastfinger"
        assert responsed_data[0]["title"] == "Awaki-Waki"
        assert responsed_data[1]["artist"] == "The Yousicians"
        assert responsed_data[1]["title"] == "Greasy Fingers - boss level"

    def has_0_matches():
        url = "/songs/search?q=woohoo"

        response = client.get(url)

        responsed_data = json.loads(response.data)
        assert response.status_code == HTTPStatus.OK
        assert len(responsed_data) == 0

    has_2_matches()
    has_0_matches()


def test_rate_song_success():
    """
    POST /songs/rating

    Should add rating to the song and return the updated data
    """
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

    Should return BAD REQUEST if request payload is doesn't match schema
    """
    response = client.get("/songs")
    responsed_data = json.loads(response.data)
    song_id = json.loads(response.data)["songs"][0]["_id"]

    url = "/songs/rating"

    def invalid_payload():

        response = client.post(
            url, data=json.dumps({"_id": song_id, "haha": 5}), headers={"Content-Type": "application/json"}
        )

        responsed_data = json.loads(response.data)
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert responsed_data["message"] == {
            "rating": ["Missing data for required field."],
            "haha": ["Unknown field."],
        }

    def invalid_objectid():
        response = client.post(
            url, data=json.dumps({"_id": "123456", "rating": 5}), headers={"Content-Type": "application/json"}
        )

        responsed_data = json.loads(response.data)
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert responsed_data["message"] == {"_id": ["123456 is not valid ObjectId"]}

    def rating_is_out_of_range():
        response = client.post(
            url, data=json.dumps({"_id": song_id, "rating": 7}), headers={"Content-Type": "application/json"}
        )

        responsed_data = json.loads(response.data)
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert responsed_data["message"] == {"rating": ["Rating must be in between 1 and 5"]}

    invalid_payload()
    invalid_objectid()
    rating_is_out_of_range()


def test_get_song_avg_rating():
    """
    GET /songs/avg/rating/<song_id>

    Return the rating data of a song include: lowest, highest, average and count
    """
    response = client.get("/songs")
    responsed_data = json.loads(response.data)
    song_id1 = json.loads(response.data)["songs"][0]["_id"]
    song_id2 = json.loads(response.data)["songs"][1]["_id"]

    def has_some_rates():
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

    def has_0_rates():
        url = "/songs/avg/rating/{}".format(song_id2)

        response = client.get(url)

        responsed_data = json.loads(response.data)
        assert response.status_code == HTTPStatus.OK
        assert responsed_data == {"lowest": -1, "highest": -1, "average": -1, "count": 0}

    has_some_rates()
    has_0_rates()
