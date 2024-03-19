import plotly.graph_objs as go

def create_plot_for_category(data, category):
    fig = go.Figure()
    retros_data = {}
    
    for date, date_data in data.items():
        for retro, stats in date_data.items():
            if retro not in retros_data:
                retros_data[retro] = {'dates': [], 'heights': []}
            heights = []
            for stat in stats:
                heights.append(int(stat.split()[0]))
            retros_data[retro]['dates'].append(date)
            retros_data[retro]['heights'].append(heights[0] if heights else None)
    
    for retro, retro_data in retros_data.items():
        fig.add_trace(go.Scatter(x=retro_data['dates'], y=retro_data['heights'], mode='lines+markers', name=retro, marker=dict(size=10)))
    
    fig.update_layout(
        title=f'{category.capitalize()}', 
        xaxis_title='Date', 
        yaxis_title='Total',
        plot_bgcolor='rgba(50,50,50,50)',
        paper_bgcolor='rgba(50,50,50,50)',
        font=dict(color='white')
    )
    
    return fig.to_html(full_html=False, include_plotlyjs=False)
