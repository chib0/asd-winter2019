// assumes global 'cortex' object



function _makeUserOption(name) {
    let out = {};
    out.info = {name: name};
    out.callback = ()=>window.location = urlWithHashArgs(`user/${name}`, hashArgs());
    return out;
}

function  _makeUserOptions() {
    out = {};
    for (i of cortex.USER_OPTIONS) {
        out[i] = _makeUserOption(i)
    }
    return out
}
USER_OPTIONS = _makeUserOptions()

function enhanceCardInfoFor(card, user) {
    cortex.getUser(user.id, (data) => {
        console.log(data);
        cardSetUserInfo(card, data, true)
    })
}

function urlWithHashArgs(url, args) {
    let out = url.toString() + "#";
    let formattedArgList =Object.keys(args).map((key) => {
        let out = `${key}`;
        if (args[key] === null && args[key]===undefined) return '';
        out += `=${args[key]}`;
        return out;
    }).filter((key)=>key);
    return out + formattedArgList.join("&");
}

function hashArgs() {
    let out = {};
    let h = window.location.hash;
    let args = h.substr(1).split("&");
    for (let arg of args) {
        let parts = arg.split('=');
        out[parts[0]] = parts.length > 1 ? parts[1] : null;
    }
    return out;
}


function loadUser(self) {
    window.location=urlWithHashArgs('/user', {id: self.user_id})
}


function loadSnapshot(snap) {
    window.location=urlWithHashArgs('/user/snapshot', {id: snap.userid, snap:snap.userinfo.timestamp})
}


function setup_user_cards() {
    cortex.getUsers((users) => {
        for (user of users) {
            console.log(user);
            // let card = makeUserCard(user, null, null, loadUser);
            let card = new UserCard(user);
            let element = card.getElement({'click': loadUser});
            cortex.getUser(user.id, (moreinfo) => card.updateElementWith(moreinfo, element));
            document.getElementById("user_cards_div").appendChild(element);
        }
    })
}


function setup_user_option_cards() {
    let user_id = parseInt(hashArgs().id);
    Object.keys(USER_OPTIONS).forEach(
        (option_name) => {
            let card = new UserOptionsCard(USER_OPTIONS[option_name].info);
            let element = card.getElement({'click' : USER_OPTIONS[option_name].callback});
            document.getElementById("user_options_div").appendChild(element);
        });
}


function setup_snapshot_cards() {
    let user_id = parseInt(hashArgs().id);
    cortex.getSnapshots(user_id, (snapshots) => {
        for (snap of snapshots) {
            let card = new SnapshotCard(user_id, snap);
             let element = card.getElement({'click': loadSnapshot});
             document.getElementById("user_snapshots_div").appendChild(element);

        }

    })
}

