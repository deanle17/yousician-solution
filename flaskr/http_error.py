from werkzeug.exceptions import HTTPException
from http import HTTPStatus


class InvalidRequestError(HTTPException):
    """Bad reqeust error"""

    code = HTTPStatus.BAD_REQUEST


class ItemNotFoundError(HTTPException):
    """Not found error"""

    code = HTTPStatus.NOT_FOUND


class UnexpectedError(HTTPException):
    """Exception for any other error from server"""

    code = HTTPStatus.INTERNAL_SERVER_ERROR
    description = "Unexpected error occurred"
