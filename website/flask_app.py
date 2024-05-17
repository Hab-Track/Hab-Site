import os
import json

from flask_sitemap import Sitemap
from flask import Flask, render_template, send_from_directory, redirect

from .utils.plot_functions import create_plot_for_category


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
    categories = ['badges', 'furnis', 'clothes', 'effects']
    plots = [create_plot_for_category(data, category) for category in categories]
    
    return render_template('graphs.html', plots=plots)


# Img stuff

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'img'), 'H.ico', mimetype='image/vnd.microsoft.icon')


@app.route("/img/<path:path>")
def send_img(path):
    return send_from_directory(os.path.join(app.root_path, 'img'), path)


# Verif shit

@app.route("/robots.txt")
def robots():
    return send_from_directory(os.path.join(app.template_folder, 'miscellaneous'),  'robots.txt')


@app.route("/google06cec27a8c7f7b33.html")
def google():
    print('tedst')
    return send_from_directory(os.path.join(app.root_path, 'miscellaneous'), 'google06cec27a8c7f7b33.html')


@app.route("/ed949a7d7fc84afb88038376ff960d21.txt")
def index_now():
    return render_template(os.path.join('miscellaneous', 'ed949a7d7fc84afb88038376ff960d21.txt'))


@app.route("/.well-known/<path:path>")
def well_known(path):
    chemin_fichier = os.path.join(app.root_path, 'miscellaneous', '.well-known', path)
    
    with open(chemin_fichier, 'r') as f:
        contenu = f.read()
    
    return contenu, 200, {'Content-Type': 'text/plain'}