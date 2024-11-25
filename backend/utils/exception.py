class UvicornException(Exception):
    def __init__(self, status_code: int, message: str, error: str) -> None:
        self.status_code = status_code
        self.message = message
        self.error = error
