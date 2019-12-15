import os
import pathlib
import string
import sys
import website

# general note: I'm writing this pretty late, way after the submissions deadline.
# I would ahve created a class to hold all the handler methods and would have implemented it using the cli class.
# I have had a doubt that decorating a method would work the same way as decorating a global function, so I didn't,
# and I chose to use a global DataDir together with a global ThoughtSite 'website' instasnce instead.

ThoughtSite = website.Website()
DataDir = None

INDEX_TEMPLATE = string.Template("""
<html>
    <head>
        <title>Brain Computer Interface</title>
    </head>
    <body>
        <ul>
            ${USERS}
        </ul>
    </body>
</html>
""")
USER_LIST_ITEM_TEMPLATE = string.Template("""<li><a href="/users/${USER}">user ${USER}</a></li>""")

USER_TEMPLATE = string.Template("""
<html>
    <head>
        <title>Brain Computer Interface: User ${USER}</title>
    </head>
    <body>
        <table>
        ${THOUGHTS}
        </table>
    </body>
</html>
""")

THOUGHT_TEMPLATE = string.Template("""
            <tr>
                <td>${TIMESTAMP}</td>
                <td>${CONTENT}</td>
            </tr>
""")


def _get_user_list_items():
    return [USER_LIST_ITEM_TEMPLATE.substitute({"USER": user.stem})
            for user in DataDir.iterdir()]


@ThoughtSite.route("/")
def _handle_index():
    users = _get_user_list_items()
    page = INDEX_TEMPLATE.substitute({'USERS': "\n".join(users)})
    return 200, page

def _timestamp_from_stem(stem):
    """
    file name is 'y-M-d_h-m-s'.
    converts it to 'y-M-d h:n:s'
    :param stem:
    :return:
    """
    date, time = stem.split("_")
    time = time.replace("-", ":")
    return " ".join([date, time])

def _get_user_thought_table(user_dir):
    total_thoughts = ''
    for timestamp_file in user_dir.iterdir():
        timestamp = _timestamp_from_stem(timestamp_file.stem)
        with open(timestamp_file, "r") as thoughts_file:
            total_thoughts += "\n".join((THOUGHT_TEMPLATE.substitute({
                            "TIMESTAMP":timestamp,
                            "CONTENT": line}) for line in thoughts_file.readlines()))
    return total_thoughts

@ThoughtSite.route("/users/([1-9]+)")
def _handle_user(user):
    print(f"handling user {user}")
    user_dir = DataDir / user
    if not user_dir.exists():
        return _handle_page_not_found()
    page = USER_TEMPLATE.substitute({"USER": user, "THOUGHTS": _get_user_thought_table(user_dir)})

    return 200, page


def _handle_page_not_found():
    return 404, ""

def run_webserver(addr, data):
    if not os.path.exists(data):
        os.makedirs(data)
    global DataDir
    DataDir = pathlib.Path(data)

    ThoughtSite.run(addr)


def main(argv):
    run_webserver(_make_address(argv[1]), argv[2])


def _make_address(address):
    ip, port = address.split(":")
    return ip, int(port)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"USAGE\n{sys.argv[0]} ADDRESS:PORT data_dir")
        exit(-1)
    exit(main(sys.argv))