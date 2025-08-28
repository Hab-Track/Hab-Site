import os
import json
import markdown
from flask_sitemap import Sitemap
from flask import Flask, render_template, send_from_directory, request, jsonify, redirect

from .utils.plot_functions import create_plot_for_category
from .utils.search import process_search_query, get_retros


app = Flask(__name__)
ext = Sitemap(app=app)

app.config['CACHE_TYPE'] = 'simple'
app.config['CACHE_DEFAULT_TIMEOUT'] = 3600

discord_server = "https://discord.gg/7SvKF6wpss"

with open("track_stats.json", "r") as f:
    data = json.load(f)

categories = ['badges', 'furnis', 'clothes', 'effects']
cached_plots_active = {category: create_plot_for_category(data, category, True) for category in categories}
cached_plots_all = {category: create_plot_for_category(data, category, False) for category in categories}


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/discord')
def discord():
    return redirect(discord_server)


@app.route('/graphs_data')
def graphs_data():
    show_active_only = request.args.get('show_active_only', 'false') == 'true'
    plots = cached_plots_active if show_active_only else cached_plots_all

    return jsonify({'categories': list(plots.keys()), 'plots': list(plots.values())})


@app.route('/graphs')
def graphs():
    return render_template('graphs.html', categories=categories)


@app.route('/search', methods=['GET'])
def search():
    return render_template('search.html', retros=get_retros())


@app.route('/search', methods=['POST'])
def search_post():
    search_query = request.form.get('search', '')
    selected_categories = request.form.getlist('categories')
    selected_retros = request.form.getlist('retros')
    search_in = request.form.getlist('search_in')
    
    return process_search_query(
        search_query,
        selected_categories,
        selected_retros,
        search_in
    )


@app.route('/about')
def about():
    with open("website/content/about.md", 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    html_content = markdown.markdown(md_content)
    
    return render_template('markdown_page.html', content=html_content, url='/about', description='About the Hab Track project')


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'img'), 'H.ico', mimetype='image/vnd.microsoft.icon')


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


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error="Page not found"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error="Internal server error"), 500