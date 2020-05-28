

def save_color_image(db, data):
    db.update_snapshot(data['user'], data['timestamp'], data['result'])


def save_depth_image(db, data):
    db.update_snapshot(data['user'], data['timestamp'], data['result'])