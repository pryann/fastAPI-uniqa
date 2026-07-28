class NotFoundError(Exception):
    def __init__(self, message="Resource not found"):
        self.message = message
        super().__init__(self.message)


class AlreadyExistsError(Exception):
    def __init__(self, message="Resource already exists"):
        self.message = message
        super().__init__(self.message)


class AuthenticationError(Exception):
    def __init__(self, message="Authentication failed"):
        self.message = message
        super().__init__(self.message)


class AuthorizationError(Exception):
    def __init__(self, message="You do not have permission to access this resource"):
        self.message = message
        super().__init__(self.message)
