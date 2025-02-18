import plotly.graph_objs as go

def create_plot_for_category(data, category, show_active_only):
    fig = go.Figure()
    retros_data = {}
    last_date = max(data.keys())

    for date, date_data in data.items():
        date_data = data[date]
        for retro, stats in date_data.items():
            if retro not in retros_data:
                retros_data[retro] = {'dates': [], 'values': []}
            
            value = next((int(s.split()[0]) for s in stats if s.endswith(f" {category}")), None)
            retros_data[retro]['dates'].append(date)
            retros_data[retro]['values'].append(value)

    for retro in retros_data.keys():
        rd = retros_data[retro]
        if show_active_only and last_date not in rd['dates']:
            continue

        fig.add_trace(go.Scatter(
            x=rd['dates'],
            y=rd['values'],
            mode='lines+markers',
            name=retro,
            marker=dict(size=8),
            line=dict(width=2)
        ))

    fig.update_layout(
        title=f'{category.capitalize()}',
        xaxis_title='Date',
        yaxis_title='Count',
        font=dict(color='white'),
        plot_bgcolor='rgba(50,50,50,50)',
        paper_bgcolor='rgba(50,50,50,50)',
    )
    
    return fig.to_html(full_html=False, include_plotlyjs=False)