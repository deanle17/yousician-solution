  #!/bin/bash
export FLASK_ENV=development
export FLASK_APP=flaskr/app.py

run_app () {
    DB_NAME=yousician flask run
}

run_test () {
    DB_NAME=test pytest -vvv
}

clean_up() {
    find . -type f -name "*.py[co]" -delete
    find . -type d -name "__pycache__" -delete
}