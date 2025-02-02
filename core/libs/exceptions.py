class FyleError(Exception):
    status_code = 400

    def __init__(self, status_code, message):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code

    def to_dict(self):
        res = dict()
        res['message'] = self.message
        return res

class ResourceNotFoundException(Exception):
    """Exception raised when a requested resource is not found"""
    pass

class InvalidRequestException(FyleError):
    """Exception raised when the request is invalid"""
    def __init__(self, message="Invalid request"):
        super().__init__(status_code=400, message=message)
