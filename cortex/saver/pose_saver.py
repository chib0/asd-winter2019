"""
the db argument is given by the database wrapping the handler.
the data is the result of the parsing. it's probably a dict.
"""

def save_pose(db, data):
    print(f'saving: {data}')
    db.update_snapshot(data['user'], data['timestamp'], data['result'])

