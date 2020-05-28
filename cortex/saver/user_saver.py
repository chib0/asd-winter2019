
def save_user_info(db, data):
    db.maybe_create_user(data['id'], data)
