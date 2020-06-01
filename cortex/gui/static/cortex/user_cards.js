
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

function _userCardTitle(userinfo) {
    let title = elementWithClass('h5', '');
    let name = userinfo.username ? userinfo.username : userinfo.info.username;
    title.innerText = userinfo.id.toString() + ". " + name;
    return title;
}
function _userCardDate(userinfo) {
    let bday =undefined;
    if (userinfo.birthday) {
        console.log("got date");
        bday = userinfo.birthday
    } else if (userinfo.info && userinfo.info.birthday) {
        bday = userinfo.info.birthday
    }
    if (bday === undefined) {
        return null
    }
    let date = elementWithClass('p');
    date.innerText = getFormattedDate(new Date(1000 * bday))
    return date
}


function cardSetUserInfo(card, user_info, clear_previous=false) {
    let date = _userCardDate(user_info);
    let title = _userCardTitle(user_info);
    setCardChildren(card, [title, date], clear_previous)
}

function makeUserCard(userinfo, image=null, children=null, onclick=null) {
    let c = makeCard(null, image, children, null, onclick);
    cardSetUserInfo(c, userinfo);
    c.userinfo=userinfo;
    return c
}

function makeCard(title=null, image=null, children=null, onload=null, onclick=null) {
    let card = elementWithClass('div', 'card');
    card.style = "width: 18rem;"
    let card_body = elementWithClass('div', 'card-body');
    if (image) {
        card.appendChild(image);
        image.classList.append("card-img-top")
    }
    children = children != null ? children : [];
    if (title) {
        let _title = elementWithClass('h5', '');
        _title.innerText = title.toString();
        children.push(_title)
    }
    card.card_body = card_body;
    setCardChildren(card, children);
    card.addEventListener("load", onload);
    card.addEventListener("click", ()=>onclick(card));
    card.appendChild(card_body);
    return card;
}