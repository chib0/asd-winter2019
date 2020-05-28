"""
the db argument is given by the database wrapping the handler.
the data is the result of the parsing. it's probably a dict.
"""

def save_feelings(db, data):
    db.update_snapshot(data['user'], data['timestamp'], data['result'])
