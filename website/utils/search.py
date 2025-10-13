import time
from flask import jsonify
from utils.db import conn


ALLOWED_ASSET_TYPES = ['badges', 'furnis', 'clothes', 'effects']
ALLOWED_SEARCH_TYPES = ['name', 'title', 'description']


def get_retros():
    with conn.cursor() as cur:
        cur.execute("SELECT DISTINCT retro FROM retro_urls;")
        return [r["retro"] for r in cur.fetchall()]


def get_retro_urls(selected_categories, selected_retros):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT retro, type, url
            FROM retro_urls
            WHERE retro = ANY(%s) AND type = ANY(%s)
        """, (selected_retros, selected_categories))
        return {(r["retro"], r["type"]): r["url"] for r in cur.fetchall()}


def fetch_data(category, search_in, selected_retros, search_query):
    res = []
    with conn.cursor() as cur:
        for retro in selected_retros:
            for search_type in search_in:
                if category not in ALLOWED_ASSET_TYPES:
                    continue
                try:
                    if category in ["badges", "furnis"]:
                        cur.execute(f"""
                            SELECT retro, name, title, description
                            FROM {category}
                            WHERE retro = %s
                            AND {search_type} ILIKE %s
                        """, (retro, f"%{search_query}%"))
                    else:
                        cur.execute(f"""
                            SELECT retro, name
                            FROM {category}
                            WHERE retro = %s
                            AND {search_type} ILIKE %s
                        """, (retro, f"%{search_query}%"))
                    res.append(cur.fetchall())
                except Exception as e:
                    print(f"Error for {retro=}, {search_type=}: {e}")
    return res


def search_database(selected_categories, selected_retros, search_query, search_in=None):
    if not any(s in ALLOWED_SEARCH_TYPES for s in search_in):
        raise ValueError("Invalid search type provided.")
    
    urls = get_retro_urls(selected_categories, selected_retros)
    search_results = {}
    
    for category in selected_categories:
        if category not in ALLOWED_ASSET_TYPES:
            raise ValueError("Invalid asset type provided.")
        
        res_query = fetch_data(category, search_in, selected_retros, search_query)
        processed_items = {}
        
        for rows in res_query:
            for row in rows:
                retro = row['retro']
                name = row['name']
                item_key = (retro, name)
                
                if item_key in processed_items:
                    if category in ['badges', 'furnis']:
                        if row.get('title'):
                            processed_items[item_key]['title'] = row['title']
                        if row.get('description'):
                            processed_items[item_key]['description'] = row['description']
                else:
                    processed_items[item_key] = {
                        'title': row.get('title', '') if category in ['badges', 'furnis'] else '',
                        'description': row.get('description', '') if category in ['badges', 'furnis'] else '',
                        'retro': retro,
                        'name': name
                    }
        
        for (retro, name), data in processed_items.items():
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
                search_results[retro][category_name][str(index)] = (
                    name, 
                    f"{base_url}{name}{extension}", 
                    data['title'], 
                    data['description']
                )
    
    return search_results


def process_search_query(search_query, selected_categories, selected_retros, search_in) -> jsonify:
    if not search_query:
        return jsonify({'warning': 'No search query provided.'})
    
    if not search_in:
        return jsonify({'warning': 'Please select at least one search field.'})
        
    start_time = time.time()
    
    try:
        search_results = search_database(selected_categories, selected_retros, search_query, search_in)
    except ValueError as e:
        return jsonify({'error': str(e)})
    except Exception as e:
        print(search_query, selected_categories, selected_retros, search_in)
        print(e)
        return jsonify({"error": "An unknown error occurs, please try again later"})
        
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