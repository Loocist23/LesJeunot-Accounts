from hashlib import md5
import argon2


CUSTOM_ARGON_PROFILE = argon2.Parameters(
    time_cost=1,
    memory_cost=2097152, # 2 GiB
    parallelism=8,
    salt_len=64,
    hash_len=1024,
    # Do not modify parameters below
    type=argon2.Type.ID,
    version=19,
)


class Hasher:
    def __init__(self, params: argon2.Parameters = CUSTOM_ARGON_PROFILE) -> None:
        """Create an Argon2 Haser using te specified parameters (or default ones).

        :param argon2.Parameters params: The Argon2 parameters to load, defaults to CUSTOM_ARGON_PROFILE 
        """
        self.params = params
        self.argon = argon2.PasswordHasher.from_parameters(self.params)
    
    def hash(self, password: str) -> str:
        """Hashes a password.

        :param str password: Password to hash
        :return str: Hashed password
        """
        return self.argon.hash(password)
    
    def verify(self, hash: str, password: str) -> bool:
        """Verify if the hash and password corresponds.

        :param str hash: The hash to check against
        :param str password: The password to check
        :return bool: True if they correspond, else False
        """
        try: isValid = self.argon.verify(hash, password)
        except: isValid = False
        return isValid
    
    def rehash(self, hash: str, password: str) -> str:
        """Automatically rehashes a password if needed.

        :param str hash: The original hash
        :param str password: The password
        :return str: The new hash if it needed to be rehashed, else the one provided.
        """
        needsRehash = self.argon.check_needs_rehash(hash)
        if needsRehash: return self.hash(password)
        else: return hash
    
    def verify_and_rehash(self, hash: str, password: str) -> tuple[bool, str]:
        """Automatically verifies and rehashes the password (if valid).

        :param str hash: The hash to check against / rehash
        :param str password: The password
        :return tuple[bool, str]: If the password and hash corresponds,
        the tuple is True and has the new hash (or old one if it didn't need to be rehashed).
        If the password and hash does not correspond, the tuple will be False,
        and it will not return any hash.
        """
        isValid = self.verify(hash, password)
        if isValid: return (True, self.rehash(hash, password))
        else: return (False, '')
    
    def md5(self, string: str) -> str: return md5(string.encode()).hexdigest()
