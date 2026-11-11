# ===== app/core/exceptions.py =====
# Step 4 · Custom (domain) exceptions  (+ Step 6: ConflictError)
# What: our own error types. Services raise them; main.py turns them into HTTP responses.
# Concepts: services don't know HTTP; exception handlers map errors to status codes.


class NotFoundError(Exception):  # -> 404
    def __init__(self, resource: str, id: int):
        self.resource = resource  # e.g. "Initiative"
        self.id = id


class ConflictError(Exception):  # -> 409, e.g. email already registered
    def __init__(self, message: str):
        self.message = message
