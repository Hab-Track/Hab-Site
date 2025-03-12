import sqlite3
import time
from flask import jsonify
from concurrent.futures import ThreadPoolExecutor, as_completed

DB_PATH = "retro_data.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_retros():
    conn = get_db_connection()
    retros = conn.execute('SELECT DISTINCT retro FROM badges UNION SELECT DISTINCT retro FROM furnis UNION SELECT DISTINCT retro FROM clothes UNION SELECT DISTINCT retro FROM effects').fetchall()
    conn.close()
    return [retro[0] for retro in retros]

def get_asset_url(conn, retro, asset_type):
    query = "SELECT url FROM retro_urls WHERE retro = ? AND type = ?"
    row = conn.execute(query, (retro, asset_type)).fetchone()
    return row['url'] if row else None

def search_assets(retro, asset_type, search_query):
    conn = get_db_connection()

    ALLOWED_ASSET_TYPES = ['badges', 'furnis', 'clothes', 'effects']
    if asset_type not in ALLOWED_ASSET_TYPES:
        raise ValueError("Invalid asset type provided.")

    query = f"SELECT name FROM {asset_type} WHERE retro = ? AND name LIKE ?"
    rows = conn.execute(query, (retro, f'%{search_query}%')).fetchall()
    
    if rows:
        base_url = get_asset_url(conn, retro, asset_type)
        if base_url:
            extension = ".gif" if asset_type == "badges" else ".nitro"
            result = [(row[0], f"{base_url}{row[0]}{extension}") for row in rows]
        else:
            result = [(row[0], None) for row in rows]
    else:
        result = None
    
    conn.close()
    return retro, asset_type, result

def process_search_query(search_query, selected_categories, selected_retros):
    if not search_query:
        return jsonify({'warning': 'No search query provided.'})
    
    start_time = time.time()
    search_results = {}
    try:
        for retro in selected_retros:
            for category in selected_categories:
                retro, asset_type, result = search_assets(retro, category, search_query)
                
                if result:
                    found_results = True
                    search_results.setdefault(retro, {})
                    
                    category_names = {
                        'badges': 'Badges',
                        'furnis': 'Furniture',
                        'clothes': 'Clothes',
                        'effects': 'Effects'
                    }
                    search_results[retro][category_names[asset_type]] = {
                        str(i): item for i, item in enumerate(result)
                    }

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
    except ValueError as e:
        return jsonify({'error': str(e)})