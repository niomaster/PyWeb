import datetime

def invoke(data):
    assert data.session.has("loggedIn") and data.session.loggedIn, ("/login", "Please log in first.")
    assert data.http.post != None and "recipient" in data.http.post and "text" in data.http.post, ("/board", "Please fill in all the fields.")
    assert data.http.post["recipient"] in data.storage.users, ("/board", "User does not exist.")

    data.storage.messages.append({ "sender": data.session.user, 
        "recipient": data.http.post["recipient"], 
        "text": data.http.post["text"], 
        "new": { data.session.user: True, data.http.post["recipient"]: True }, 
        "sent": datetime.datetime.now(), 
        "formattedSent": datetime.datetime.now().strftime("%H:%M:%S %d/%m/%Y") })

    return "/board"