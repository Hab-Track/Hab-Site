import argparse
import os
import json
from flask_sitemap import Sitemap
from flask import Flask, render_template, send_from_directory, request, jsonify
from utils.plot_functions import create_plot_for_category

app = Flask(__name__)
ext = Sitemap(app=app)

with open("track_stats.json", "r") as f:
    data = json.load(f)

categories = ['badges', 'furnis', 'clothes', 'effects']
cached_plots_active = {category: create_plot_for_category(data, category, True) for category in categories}
cached_plots_all = {category: create_plot_for_category(data, category, False) for category in categories}


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/graphs_data')
def graphs_data():
    show_active_only = request.args.get('show_active_only', 'false') == 'true'
    return jsonify({'plots': cached_plots_active if show_active_only else cached_plots_all})


@app.route('/graphs')
def graphs():
    show_active_only = False
    if 'show_active_only' in request.args and request.args.get('show_active_only') == 'true':
        show_active_only = True

    plots = cached_plots_active if show_active_only else cached_plots_all
    
    indexed_plots = list(enumerate(plots))
    return render_template('graphs.html', indexed_plots=indexed_plots, categories=categories, show_active_only=show_active_only)


@app.route("/raw_stats")
def raw_stats():
    return jsonify(data)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'img'), 'H.ico', mimetype='image/vnd.microsoft.icon')


### Useless shit


@ext.register_generator
def index():
    yield 'home', {}, "", "", 1
    yield 'graphs', {}, "", "daily", 0.8
    yield 'raw_stats', {}, "", "daily", 0.2


@app.route("/robots.txt")
def robots():
    return send_from_directory(app.template_folder, 'robots.txt')


@app.route("/img/<path:path>")
def send_img(path):
    return send_from_directory(os.path.join(app.root_path, 'img'), path)


@app.route("/google06cec27a8c7f7b33.html")
def google():
    return render_template('google06cec27a8c7f7b33.html')


@app.route("/yandex_67dde65cedc0b4cd.html")
def yandex():
    return render_template('yandex_67dde65cedc0b4cd.html')


@app.route("/ed949a7d7fc84afb88038376ff960d21.txt")
def index_now():
    return render_template('ed949a7d7fc84afb88038376ff960d21.txt')


@app.route("/.well-known/<path:path>")
def well_known(path):
    chemin_fichier = os.path.join(app.root_path, '.well-known', path)
    
    with open(chemin_fichier, 'r') as f:
        contenu = f.read()
    return contenu, 200, {'Content-Type': 'text/plain'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run Flask application.')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    args = parser.parse_args()

    app.run(debug=args.debug)