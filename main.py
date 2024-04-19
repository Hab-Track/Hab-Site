import argparse
import os
import json
from flask_sitemap import Sitemap
from flask import Flask, render_template, send_from_directory
from utils.plot_functions import create_plot_for_category

app = Flask(__name__)
ext = Sitemap(app=app)

with open("track_stats.json", "r") as f:
    data = json.load(f)


@ext.register_generator
def index():
    yield 'home', {}, "", "", 1
    yield 'graphs', {}, "", "daily", 0.8
    yield 'raw_stats', {}, "", "daily", 0.2


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/graphs')
def graphs():
    plots = []
    categories = ['badges', 'furnis', 'clothes', 'effects']
    
    for category in categories:
        plots.append(create_plot_for_category(data, category))
    
    plots_html = ''.join(plots)
    return render_template('graphs.html', plots=plots)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'img'), 'H.ico', mimetype='image/vnd.microsoft.icon')


@app.route("/raw_stats")
def raw_stats():
    return data


@app.route("/google06cec27a8c7f7b33.html")
def google():
    return render_template('google06cec27a8c7f7b33.html')


@app.route("/yandex_67dde65cedc0b4cd.html")
def yandex():
    return render_template('yandex_67dde65cedc0b4cd.html')


@app.route("/robots.txt")
def robots():
    return send_from_directory(app.template_folder, 'robots.txt')


@app.route("/.well-known/<path:path>")
def well_known(path):
    chemin_fichier = os.path.join(app.root_path, '.well-known', path)
    
    with open(chemin_fichier, 'r') as f:
        contenu = f.read()
    return contenu, 200, {'Content-Type': 'text/plain'}


@app.route("/img/<path:path>")
def send_img(path):
    return send_from_directory(os.path.join(app.root_path, 'img'), path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run Flask application.')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    args = parser.parse_args()
    
    if args.debug:
        app.run(debug=True)
    else:
        app.run(host='0.0.0.0', port=80)
