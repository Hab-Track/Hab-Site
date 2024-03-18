from flask import Flask, render_template
import plotly.graph_objs as go
import json

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/graphs')
def graphs():
    plots = []
    categories = ['badges', 'furnis', 'clothes', 'effects']
    
    for category in categories:
        fig = create_plot(category)
        plots.append(fig.to_html(full_html=False, include_plotlyjs=False))
    
    return render_template('graphs.html', plots=plots)

def create_plot(category):
    fig = go.Figure()

    for retro, stats in data["2024-03-18"].items():
        heights = [int(stat.split()[0]) for stat in stats]
        fig.add_trace(go.Scatter(x=list(data.keys()), y=heights, mode='lines+markers', name=retro))

    fig.update_layout(title=f'Counts of {category}',
                      xaxis_title='Date',
                      yaxis_title='Counts')

    return fig

if __name__ == '__main__':
    with open("log/track_stats.json", "r") as f:
        data = json.load(f)

    app.run(debug=True)
