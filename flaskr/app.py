from flask import Flask, jsonify, request
import re
from flask_pymongo import PyMongo
from pymongo import ReturnDocument
from http import HTTPStatus
from bson.objectid import ObjectId

app = Flask(__name__)
app.config[
    "MONGO_URI"
] = "mongodb+srv://admin:admin@cluster0.pan4f.gcp.mongodb.net/yousician?ssl_cert_reqs=CERT_NONE"
mongo = PyMongo(app)


@app.route("/songs", methods=["GET"])
def get_songs():
    songs = mongo.db.songs.find()
    ret = []
    for song in songs:
        song["_id"] = str(song["_id"])
        ret.append(song)
    return jsonify(ret)


@app.route("/songs/avg/difficulty", methods=["GET"])
def get_average_songs_difficulty():
    level = request.args.get("level")
    condition = {"level": int(level)} if level is not None else {}
    songs = mongo.db.songs.find(condition)
    difficulties = list(map(lambda song: song["difficulty"], list(songs)))
    avg_difficulty = sum(difficulties) / len(difficulties)
    return {"average_difficulty": avg_difficulty}


@app.route("/songs/search", methods=["GET"])
def search_song():
    query = request.args.get("q")
    query = query if query is not None else ""
    condition = {
        "$or": [
            {"artist": re.compile(query, re.IGNORECASE)},
            {"title": re.compile(query, re.IGNORECASE)},
        ]
    }
    songs = mongo.db.songs.find(condition)
    ret = []
    for song in songs:
        song["_id"] = str(song["_id"])
        ret.append(song)
    return jsonify(ret)


@app.route("/songs/rating", methods=["POST"])
def rate_song():
    payload = dict(request.json)
    print(payload)
    song = mongo.db.songs.find_one_and_update(
        {"_id": ObjectId(payload["_id"])},
        {"$push": {"rates": payload["rating"]}},
        return_document=ReturnDocument.AFTER,
    )
    song["_id"] = str(song["_id"])
    return song


@app.route("/songs/avg/rating/<song_id>", methods=["GET"])
def get_song_avg_rating(song_id):
    song = mongo.db.songs.find_one({"_id": ObjectId(song_id)})

    ret = {
        "lowest": min(song["rates"]),
        "highest": max(song["rates"]),
        "average": sum(song["rates"]) / len(song["rates"]),
    }

    return ret
