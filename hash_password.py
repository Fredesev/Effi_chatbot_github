import bcrypt

# Den nye adgangskode vi vil hashe
plain_password = "test123"

# Hash adgangskoden
hashed = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt())

# Vis hash
print("Ny hash for adgangskoden:")
print(hashed.decode())


