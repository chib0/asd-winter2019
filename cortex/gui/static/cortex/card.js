

function elementWithClass(element, classNames='') {
    // expecting classnames to be either a string or a list, if not a string list(or iterable) assumed
    out = document.createElement(element);
    if (typeof classNames == 'string') {
        out.className = classNames
    }
    else {
        for (let name of classNames) {
            out.classList.add(name);
        }
    }
    return out ;
}


cardClassForTag = {
    'p': 'card-text',
    'h5': 'card-title',
    'img': 'card-img'
};
function setCardChildren(card, children, clear_previous=false, append=true) {
    // set append to be false when entering child nodes, since they are already added to the tree by inheritance,
    // and we just need to set their classes

    if (!children.length) return;

    if (card.card_body && clear_previous) {
        while(card.card_body.lastElementChild) card.card_body.removeChild(card.card_body.lastElementChild);
    }
    if (children) {
        for (i of children) {
            if (!i) {
                continue;
            }
            c = cardClassForTag[i.tagName];
            if (append) {
                card.card_body.appendChild(i);
            }
            if (c) {
                i.classList.add(c);
            }
            if (i.hasChildNodes()) {
                setCardChildren(i, i.children, clear_previous, false)
            }
        }
    }
}


function getFormattedDate(date) {
    let year = date.getFullYear();
    let month = (1 + date.getMonth()).toString().padStart(2, '0');
    let day = date.getDate().toString().padStart(2, '0');

    return month + '/' + day + '/' + year;
}

function Card() {
    this.children=null;

    this.getElement = (evtListeners = null) => {
        this._parse();
        let card = elementWithClass('div', 'card');
        card.style += " width: 18rem;";
        card.card_body = elementWithClass('div', 'card-body');
        this._makeElement(card);
        card.appendChild(card.card_body);
        if (!evtListeners) return card;
        Object.keys(evtListeners).forEach( (key) => {
            card.addEventListener(key, () => evtListeners[key](this));
        });

        return card;
    };
    this._makeElement = (element) => {
        let image = this.getImage();
        if (image) {
            element.appendChild(image);
            image.classList.append("card-img-top")
        }
        setCardChildren(element, this.children, true);

        return element;
    };
    this.getImage= () => null;
    this.updateElementWith= (userinfo, element=null) => {
        this.userinfo = userinfo;
        this._parse();
        if (!element || element.card_body === undefined) return;
        this._makeElement(element)
    };
    this.makeTitle = () => {
        let t = document.createElement("h5");
        t.innerText = this._titleText();
        return t;
    }

}

function UserCard(userinfo) {
    this._titleText = () => {
        return `${this.user_id}. ${this.name}`
    };

    this._extractChildren = () => {
        let out = [];

        // make the title
        out.push(this.makeTitle());

        if (this.birthday) {
            let t = document.createElement("p");
            t.innerText = getFormattedDate(this.birthday);
            out.push(t)
        }
        return out;
    };

    this._parse = function () {
        this.name = this.userinfo.username ? this.userinfo.username : this.userinfo.info.username;
        this.user_id = this.userinfo.id;
        this.birthday = this.userinfo.birthday ? new Date(1000 * this.userinfo.birthday) : null;
        this.children = this._extractChildren();
    };

    Card.call(this);
    this.userinfo = userinfo;
}

UserCard.prototype.parent = Card.prototype;

function SnapshotCard(user_id, snapshot_info) {
    this._parse = () => {
        this.date = this.userinfo.timestamp ? new Date(this.userinfo.timestamp) : null;
        this._id = this.userinfo.id ? this.userinfo.id : null;
        this.children = this._extractChildren();
    };

    // this._enhanceWith = (crtx, element) => {
    //     crtx.getSnapshot(this.userid, this.userinfo.timestamp, (fields) => {
    //         if (!fields) return;
    //         for (field of fields) {
    //
    //         }
    //         }
    //     )
    // };
    this._extractChildren = () => {
        return [this.makeTitle()]
    };
    this._titleText = () => `Snapshot: ${getFormattedDate(this.date)}`;

    Card.call(this);
    this.userid = user_id;
    this.userinfo = snapshot_info;
    this.userinfo.user_id = user_id; // just in case

}

SnapshotCard.prototype.parent = Card.prototype;


function UserOptionsCard(userinfo) {
    this._parse = () => {this.name = userinfo.name; this.children=this._extractChildren()};
    this._titleText = () => this.name;
    this._extractChildren = () =>[this.makeTitle()];

    Card.call(this);
}
UserOptionsCard.prototype.parent = Card.prototype;