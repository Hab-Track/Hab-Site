import sqlite3
import time
from flask import jsonify


DB_PATH = "retro_data.db"
ALLOWED_ASSET_TYPES = ['badges', 'furnis', 'clothes', 'effects']


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_retros():
    with get_db_connection() as conn:
        retros = conn.execute('SELECT DISTINCT retro FROM badges UNION SELECT DISTINCT retro FROM furnis UNION SELECT DISTINCT retro FROM clothes UNION SELECT DISTINCT retro FROM effects').fetchall()
    
    return [retro[0] for retro in retros]


def get_retro_urls(conn, selected_categories, selected_retros):
    url_query = "SELECT retro, type, url FROM retro_urls WHERE retro IN ({}) AND type IN ({})".format(
        ','.join('?' * len(selected_retros)),
        ','.join('?' * len(selected_categories))
    )
    url_params = selected_retros + selected_categories
    return {(row['retro'], row['type']): row['url'] 
            for row in conn.execute(url_query, url_params).fetchall()}


def search_database(selected_categories, selected_retros, search_query):
    with get_db_connection() as conn:
        urls = get_retro_urls(conn, selected_categories, selected_retros)
        search_results = {}
        
        for category in selected_categories:
            if category not in ALLOWED_ASSET_TYPES:
                raise ValueError("Invalid asset type provided.")
            
            query = f"""
                SELECT retro, name 
                FROM {category} 
                WHERE retro IN ({','.join('?' * len(selected_retros))})
                AND name LIKE ?
            """
            params = selected_retros + [f'%{search_query}%']
            rows = conn.execute(query, params).fetchall()
            
            for row in rows:
                retro = row['retro']
                name = row['name']
                base_url = urls.get((retro, category))
                
                if base_url:
                    extension = ".gif" if category == "badges" else ".nitro"
                    search_results.setdefault(retro, {})
                    category_name = {
                        'badges': 'Badges',
                        'furnis': 'Furniture',
                        'clothes': 'Clothes',
                        'effects': 'Effects'
                    }[category]
                    
                    search_results[retro].setdefault(category_name, {})
                    index = len(search_results[retro][category_name])
                    search_results[retro][category_name][str(index)] = (name, f"{base_url}{name}{extension}")
    
    return search_results


def process_search_query(search_query, selected_categories, selected_retros):
    if not search_query:
        return jsonify({'warning': 'No search query provided.'})
    
    start_time = time.time()
    
    try:
        search_results = search_database(selected_categories, selected_retros, search_query)
    except ValueError as e:
        return jsonify({'error': str(e)})
        
    execution_time = round(time.time() - start_time, 2)
    
    if not search_results:
        return jsonify({
            'results': {},
            'execution_time': execution_time,
            'message': 'No results found for your search.'
        })
    
    return jsonify({
        'results': search_results,
        'execution_time': execution_time
    })