from werkzeug.exceptions import HTTPException


class InvalidRequestError(HTTPException):
    """Bad reqeust error"""

    code = 400


class ItemNotFoundError(HTTPException):
    """Not found error"""

    code = 404


class UnexpectedError(HTTPException):
    """Exception for any other error from server"""

    code = 500
    description = "Unexpected error occurred"
