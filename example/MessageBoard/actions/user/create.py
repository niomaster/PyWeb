import hashlib

def invoke(data):
    assert data.http.post != None and "user" in data.http.post and "password" in data.http.post,  ("/create", "Please fill in all the fields")
    assert len(data.http.post["user"]) >= 2 and len(data.http.post["password"]) >= 6,  ("/create", "Please enter a username of at least 2 characters and a password of at least 6 characters")
    assert not data.http.post["user"] in data.storage.users,  ("/create", "This user already exists. Please pick another username.")

    data.storage.users[data.http.post["user"]] = hashlib.sha512(data.http.post["password"]).digest()
    return "/login"