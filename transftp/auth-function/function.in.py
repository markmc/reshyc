USERNAME = "@@FTP_USER@@"
PASSWORD = "@@FTP_PASSWORD@@"

def handler(event, context):
    print("Event: ", event)

    for p in ["username", "password"]:
        if p not in event:
            print("{} required".format(p))
            return {}

    username = event["username"]
    password = event["password"]

    if username != USERNAME or password != PASSWORD:
        print("Authentication failed for {}".format(username))
        return {}

    print("Username {} authenticated".format(username))

    response = { "Role": "@@FTP_SERVER_ROLE@@" }

    print("Response: ", response)

    return response
