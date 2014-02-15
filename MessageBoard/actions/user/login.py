import hashlib

def invoke(data):
    assert data.http.post != None and "user" in data.http.post and "password" in data.http.post, ("/login", "Please fill in all the fields.")
    assert data.http.post["user"] in data.storage.users, ("/login", "Username/Password combination not found.")
    assert data.storage.users[data.http.post["user"]] == hashlib.sha512(data.http.post["password"]).digest(), ("/login", "Username/Password combination not found.")

    data.session.loggedIn = True
    data.session.user = data.http.post["user"]
    data.storage.online.append(data.http.post["user"])
    return "/board"