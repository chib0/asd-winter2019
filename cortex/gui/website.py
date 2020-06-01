from pathlib import Path

import urlpath
from flask import Flask, render_template, request


def get_server(api_host, api_port, server_name="server_gui", static_dir=None):
    static_dir = static_dir or Path(__file__).parent / 'static'
    template_dir = Path(static_dir).parent / 'templates'
    app = Flask(server_name, static_folder=str(static_dir), template_folder=str(template_dir))
    api_url = urlpath.URL().with_scheme("http").with_hostinfo(api_host, api_port)

    root_cards_view = dict(SETUP_CARDS_FUNCTION="setup_user_cards()",
                           CARDS_DIV_NAME='user_cards_div',
                           BRAND_LOGO_CLASS="")

    user_cards_view = dict(SETUP_CARDS_FUNCTION="setup_user_option_cards()",
                           CARDS_DIV_NAME='user_options_div',
                           BRAND_LOGO_CLASS="fa fa-angle-left")

    snapshot_card_view=dict(SETUP_CARDS_FUNCTION="setup_snapshot_cards()",
                           CARDS_DIV_NAME='user_snapshots_div',
                           BRAND_LOGO_CLASS="fa fa-angle-left")

    user_location_view = dict(BRAND_LOGO_CLASS="fa fa-angle-left", CHART_NAME='3dgraph')
    user_feelings_view = dict(BRAND_LOGO_CLASS="fa fa-angle-left", CHART_NAME='linegraph')
    user_snapshot_view = dict()

    # these are the options a user gets when they go into a user menu
    # TODO: aggregate automatically
    user_option_list = ['locations', 'feelings', 'snapshots']


    @app.route('/js/cortex.js')
    def setup_cortex():
        return render_template('cortex.js', API_URL=str(api_url),
                               user_option_list=user_option_list)

    @app.route("/")
    def index():
        return render_template('cards_view.html', **root_cards_view)

    @app.route("/user")
    def user():
        return render_template('cards_view.html', **user_cards_view)


    @app.route("/user/snapshots")
    def user_snapshots():
        return render_template('cards_view.html', **snapshot_card_view)

    @app.route("/user/locations")
    def user_locations():
        return render_template('location_view.html', **user_location_view)


    @app.route("/user/feelings")
    def user_feelings():
        return render_template('feelings_view.html',  **user_feelings_view)

    @app.route("/user/snapshot")
    def user_snapshot():
        return render_template('snapshot_view.html', **user_snapshot_view)


    @app.after_request
    def set_caching(r):
        r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        r.headers["Pragma"] = "no-cache"
        r.headers["Expires"] = "0"
        r.headers['Cache-Control'] = 'public, max-age=0'
        return r

    return app


def run_server(host, port, api_host, api_port):
    server = get_server(api_host, api_port)
    server.run(host=host, port=port)
