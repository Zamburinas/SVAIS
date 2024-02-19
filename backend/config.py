from enum import Enum

DATABASE_IP = "127.0.0.1"
DATABASE_PORT = 27017
DATABASE_NAME = "AIS"

class Database(Enum):
    USERS = "users"