from enum import Enum

DATABASE_IP = "localhost"
DATABASE_PORT = 27017
DATABASE_NAME = "AIS"

class Database(Enum):
    USERS = "users"
    Coords="coordinates"