
import jwt
import datetime
import hashlib

from cryptography.hazmat.primitives import serialization

class Authenticate:
    private_key = open('./keys/key', 'r').read()
    private_key = serialization.load_ssh_private_key(private_key.encode(), password=b'')
    public_key = open('./keys/key.pub', 'r').read()
    public_key = serialization.load_ssh_public_key(public_key.encode())

    @classmethod
    def encode_auth_token(cls, user_id, minutes):
        try:
            payload = {
                'exp': (datetime.datetime.now() + datetime.timedelta(days=0, minutes=minutes)).timestamp(),
                'iat': datetime.datetime.now().timestamp(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                key = cls.private_key,
                algorithm='RS256'
            )
        except Exception as e:
            print(f"[ERROR: {datetime.datetime.now().strftime('%d/%m/%Y-%H:%M:%S')}] {e}")

    @classmethod
    def decode_auth_token(cls, auth_token):
        try:
            payload = jwt.decode(
                auth_token,
                key = cls.public_key,
                algorithms='RS256')
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False
        
    @classmethod
    def hash_password(cls, password):
        # Convert the password string to bytes
        password_bytes = password.encode('utf-8')
        
        # Create a new SHA-256 hash object
        sha256_hash = hashlib.sha256()
        
        # Update the hash object with the password bytes
        sha256_hash.update(password_bytes)
        
        # Get the hexadecimal representation of the hashed password
        hashed_password = sha256_hash.hexdigest()
        
        return hashed_password
