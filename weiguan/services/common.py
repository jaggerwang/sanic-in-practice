class ServiceException(Exception):
    def __init__(self, message, code=None):
        super().__init__(message)

        self.message = message
        self.code = code
