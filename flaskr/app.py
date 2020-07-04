from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException
from werkzeug import Response as ErrResponse
from flask_pymongo import PyMongo
from pymongo import ReturnDocument
from http import HTTPStatus
from bson.objectid import ObjectId
from .http_error import UnexpectedError, ItemNotFoundError
import re
import json

app = Flask(__name__)
mongo = PyMongo(
    app, "mongodb+srv://admin:admin@cluster0.pan4f.gcp.mongodb.net/yousician?ssl_cert_reqs=CERT_NONE"
)

ITEMS_PER_PAGE = 10
SONG_COLLECTION = "songs"


@app.errorhandler(HTTPException)
def handle_exception(e: HTTPException) -> ErrResponse:
    response = e.get_response()
    response.data = json.dumps({"statusCode": e.code, "message": e.description})
    response.content_type = "application/json"
    return response


@app.route("/songs", methods=["GET"])
def get_songs():
    try:
        last_id = request.args.get("from")

        if last_id is None:
            songs = mongo.db[SONG_COLLECTION].find().limit(ITEMS_PER_PAGE)
        else:
            songs = mongo.db[SONG_COLLECTION].find({"_id": {"$gt": ObjectId(last_id)}}).limit(ITEMS_PER_PAGE)

        ret = {"songs": []}
        for song in songs:
            song["_id"] = str(song["_id"])
            ret["songs"].append(song)

        ret["last_id"] = ret["songs"][-1]["_id"] if len(ret["songs"]) > 0 else ""
        return ret
    except Exception as e:
        print(e)
        raise UnexpectedError()


@app.route("/songs/avg/difficulty", methods=["GET"])
def get_average_songs_difficulty():
    level = request.args.get("level")
    condition = {"level": int(level)} if level is not None else {}

    songs = list(mongo.db[SONG_COLLECTION].find(condition))

    if len(songs) == 0:
        raise ItemNotFoundError("No song found with level {}".format(level))

    difficulties = list(map(lambda song: song["difficulty"], list(songs)))
    avg_difficulty = sum(difficulties) / len(difficulties)
    return {"avg_difficulty": avg_difficulty}


@app.route("/songs/search", methods=["GET"])
def search_song():
    query = request.args.get("q")
    query = query if query is not None else ""
    condition = {
        "$or": [{"artist": re.compile(query, re.IGNORECASE)}, {"title": re.compile(query, re.IGNORECASE)}]
    }

    songs = mongo.db[SONG_COLLECTION].find(condition)

    ret = []
    for song in songs:
        song["_id"] = str(song["_id"])
        ret.append(song)
    return jsonify(ret)


@app.route("/songs/rating", methods=["POST"])
def rate_song():
    payload = dict(request.json)
    song = mongo.db[SONG_COLLECTION].find_one_and_update(
        {"_id": ObjectId(payload["_id"])},
        {"$push": {"rates": payload["rating"]}},
        projection={"rates": True, "_id": True},
        return_document=ReturnDocument.AFTER,
    )

    if song is None:
        raise ItemNotFoundError("Song not found with _id {}".format(payload["_id"]))

    song["_id"] = str(song["_id"])
    return song


@app.route("/songs/avg/rating/<song_id>", methods=["GET"])
def get_song_avg_rating(song_id):
    song = mongo.db[SONG_COLLECTION].find_one({"_id": ObjectId(song_id)})

    if song is None:
        raise ItemNotFoundError("Song not found with _id {}".format(song_id))

    ret = {
        "lowest": min(song["rates"]),
        "highest": max(song["rates"]),
        "average": sum(song["rates"]) / len(song["rates"]),
    }
    return ret
