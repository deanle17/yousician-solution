# Yousician assignment solution

This is the solution to interview assignment for Backend Developer position at Yousician. The solution is written in **Python 3.8** using **Flask** framework, **Poetry** as dependency manager and **Pytest** for testing purpose.

## Getting started

The application requires Python 3.7 as minimum version, and Poetry. If you don't have Poetry yet, please follow [this instruction](https://python-poetry.org/docs/#installation) to install it. After Poetry is installed, follow these step below to get the app started:

1. Activate env: `poetry shell`
2. Install project's dependencies: `poetry install`
3. Activate premade script: `source launch.sh`

From here, to start the app:

```bash
run_app
```

To run all tests:

```bash
run_test
```

To clean up files like **pycache**, etc.:

```bash
clean_up
```

**Note:** In case you encounter `command not found: poetry`, you need to have **Poetry** bin's directory in your `PATH`. Probably, you can try:

```bash
export PATH=$HOME/.poetry/bin:$PATH
```

## API

**GET /songs**
Get all songs with pagination

**GET /songs/avg/difficulty**: Get average difficulty of songs at certain level
Query example: `/songs/avg/difficulty?level=9`

**GET /songs/search**: Search songs by artist or title
Query example: `/songs/search?q=yousicians`

**POST /songs/rating**: Rate a song by id
Body example: `{"_id": "abcxyz1234567", rating: 5}`

**GET /songs/avg/rating/<song_id>**: Get rating data of a song by id

You can use tool like [Postman](https://www.postman.com/downloads/) to test the API

## Further improvement

-   Assuming the application is getting bigger, project structure can be organized in functional-wise, for example:

```
project/
  __init__.py
  models/
    __init__.py
    base.py
    songs.py
    artists.py
    ...
  routes/
    __init__.py
    songs.py
    artists.py
    ...
  templates/
  services/
  util/
```

-   At that point, when the project is large and functions start calling each other, it's neccessary to have unit tests. For now, to keep it simple, I only implement integration tests.

--

##### This is the end of my solution. I hope you like it.
