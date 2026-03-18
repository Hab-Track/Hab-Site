import plotly.graph_objs as go

def string_to_color(s):
    hash_val = 0
    for char in s:
        hash_val = ord(char) + ((hash_val << 5) - hash_val)
    
    hue = abs(hash_val % 360)
    saturation = 65 + (abs(hash_val) % 20)
    lightness = 55 + (abs(hash_val >> 8) % 15)
    
    return f'hsl({hue}, {saturation}%, {lightness}%)'

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

    sorted_retros = sorted(retros_data.keys())

    for retro in sorted_retros:
        rd = retros_data[retro]
        if show_active_only and last_date not in rd['dates']:
            continue

        color = string_to_color(retro)
        
        fig.add_trace(go.Scatter(
            x=rd['dates'],
            y=rd['values'],
            mode='lines+markers',
            name=retro,
            marker=dict(size=8, color=color),
            line=dict(shape="hv", width=2, color=color),
            connectgaps=True,
            hovertemplate='<b>%{fullData.name}</b><br>Date: %{x}<br>Count: %{y}<extra></extra>'
        ))

    fig.update_layout(
        title=f'{category.capitalize()}',
        xaxis_title='Date',
        yaxis_title='Count',
        font=dict(color='white'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        hoverlabel=dict(
            bgcolor='#2c2c2c',
            font_size=16,
            font_family='Segoe UI',
            font_color='white'
        )
    )
    
    return fig.to_json()