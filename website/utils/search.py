import time
import os
from flask import jsonify
from supabase import create_client, Client
from dotenv import load_dotenv


DB_PATH = "retro_data.db"
ALLOWED_ASSET_TYPES = ['badges', 'furnis', 'clothes', 'effects']
ALLOWED_SEARCH_TYPES = ['name', 'title', 'description']

load_dotenv()
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)


def get_retros():
    retros = set()
    table = "retro_urls"
    
    response = supabase.table(table).select("retro").execute()
    for row in response.data:
        retros.add(row['retro'])
    
    return list(retros)


def get_retro_urls(selected_categories, selected_retros):
    supabase_query = supabase.table("retro_urls").select("retro, type, url").in_("retro", selected_retros).in_("type", selected_categories).execute()
    return {(row['retro'], row['type']): row['url'] for row in supabase_query.data}


def fetch_data(category, search_in, selected_retros, search_query):
    res = []
    for retro in selected_retros:
        for search_type in search_in:
            try:
                if category in ["badges", "furnis"]:
                    query = supabase.table(category)\
                        .select("retro, name, title, description")\
                        .eq("retro", retro)\
                        .fts(search_type, search_query)\
                        .execute()
                else:
                    query = supabase.table(category)\
                        .select("retro, name")\
                        .eq("retro", retro)\
                        .fts(search_type, search_query)\
                        .execute()
                res.append(query.data)
            except Exception as e:
                print(f"Timeout for {retro=}, {search_type=} — {e}")
                continue

    return res

def search_database(selected_categories, selected_retros, search_query, search_in=None):
    if not any(search_in in ALLOWED_SEARCH_TYPES for search_in in search_in):
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


def process_search_query(search_query, selected_categories, selected_retros, search_in):
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