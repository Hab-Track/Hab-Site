import os
import json
import argparse
import plotly.graph_objs as go
from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

with open("track_stats.json", "r") as f:
    data = json.load(f)
    

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/graphs')
def graphs():
    plots = []
    categories = ['badges', 'furnis', 'clothes', 'effects']
    dates = list(data.keys())
    
    for date in dates:
        plots.append(create_plots_for_date(date, categories))
    
    return render_template('graphs.html', plots=plots)

def create_plots_for_date(date, categories):
    date_data = data.get(date, {})
    figs = []

    for category in categories:
        fig = create_plot(date_data, category)
        figs.append(fig.to_html(full_html=False, include_plotlyjs=False))
    
    return figs

def create_plot(date_data, category):
    fig = go.Figure()

    for retro, stats in date_data.items():
        heights = [int(stat.split()[0]) for stat in stats if category in stat]
        fig.add_trace(go.Scatter(x=list(date_data.keys()), y=heights, mode='lines+markers', name=retro))

    fig.update_layout(title=f'Counts of {category}', xaxis_title='Date', yaxis_title='Counts')

    return fig


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'img'), 'H.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run Flask application.')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    args = parser.parse_args()
    
    if args.debug:
        app.run(debug=True)
    else:
        app.run(host='0.0.0.0', port=80)

    if args.debug:
        app.run(debug=True)
    else:
        app.run(host='0.0.0.0', port=80)
