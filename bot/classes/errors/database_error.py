class DatabaseError(Exception):
    pass


class DatabaseUnsupportedDriverError(DatabaseError):
    pass
