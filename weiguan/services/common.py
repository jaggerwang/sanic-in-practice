class UsecaseException(Exception):
    def __init__(self, message):
        super().__init__(message)

        self.message = message


class UnauthenticatedException(UsecaseException):
    def __init__(self, message):
        super().__init__(message)


class UnauthorizedException(UsecaseException):
    def __init__(self, message):
        super().__init__(message)


class NotFoundException(UsecaseException):
    def __init__(self, message):
        super().__init__(message)
