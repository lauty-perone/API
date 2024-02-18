def user_schema(user) -> dict:
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "email": user["email"],
        "password": user["password"],
        "disabled": user["disabled"]}

def users_schema(users) -> list:
    return [user_schema(user) for user in users]


