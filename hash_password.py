import bcrypt

plain_password = "test123"

hashed = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt())

print("Ny hash for adgangskoden:")
print(hashed.decode())


