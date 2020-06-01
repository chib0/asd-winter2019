
function Cortex(base) {
    this.base = new URL(base);

    this.getFrom = ( url_parts, callback) => {
        url = new URL(base);
        url.pathname = url_parts.join('/');
        $.get(url.toString()).done((data) => callback(JSON.parse(data)));
    };

    this.getUsers= (callback) => {
        this.getFrom(['users'], callback);
    };

    this.getUser = (num, callback) => {
        this.getFrom(['users', num], callback);
    };

    this.getSnapshots = (userid, callback) => {
        this.getSnapshot(userid,'', callback)
    };

    this.getSnapshot = (userid , snapid, callback) => {
        this.getFrom(['users', userid, 'snapshots', snapid], callback);
    };

    this.getSnapshotPart = (userid, snapid, part, callback) => {
        this.getFrom(['users', userid, 'snapshots', snapid, part], (result) => {
                return callback(result)
        });
    };

    this.getSnapshotWithHandlers = (userid, snapid, handlers)  => {
        this.getSnapshot(userid, snapid, (data) => {
                for (let field of data) {
                    if (handlers[field]) {
                        console.log(`getting ${field}`);
                        this.getSnapshotPart(userid, snapid, field, (result) => handlers[field](userid, snapid, result))
                    }
                }
            }
        )
    };


    this.getUserLocations = (userid, callback) =>
        this.getFrom(["users", userid, 'locations'], callback);
    this.getUserFeelings = (userid, callback) =>
        this.getFrom(["users", userid, 'feelings'], callback);
    this.USER_OPTIONS = {{user_option_list}}
}

cortex = new Cortex("{{API_URL}}");