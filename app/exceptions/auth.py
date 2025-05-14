class UserNotFound(Exception):
    def __init__(self):
        self.status_code = 404
        self.msg = "user not found"
        super().__init__()

    def __str__(self):
        return self.msg

class InvalidCredentials(Exception):
    def __init__(self):
        self.status_code = 401
        self.msg = "invalid credentials"
        super().__init__()

    def __str__(self):
        return self.msg
