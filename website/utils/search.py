import time
import os
from flask import jsonify
from supabase import create_client, Client


DB_PATH = "retro_data.db"
ALLOWED_ASSET_TYPES = ['badges', 'furnis', 'clothes', 'effects']
ALLOWED_SEARCH_TYPES = ['name', 'title', 'description']

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


def search_database(selected_categories, selected_retros, search_query, search_in=None):
    if not any(search_in in ALLOWED_SEARCH_TYPES for search_in in search_in):
        raise ValueError("Invalid search type provided.")
    
    urls = get_retro_urls(selected_categories, selected_retros)
    search_results = {}
    
    for category in selected_categories:
        res_query = []
        if category not in ALLOWED_ASSET_TYPES:
            raise ValueError("Invalid asset type provided.")
        
        if 'name' in search_in:
            query = query = supabase.table(category).select("retro, name").in_("retro", selected_retros).like("name", search_query).execute()
            res_query.append(query.data)
        if category in ['badges', 'furnis']:
            if 'title' in search_in:
                query = query = supabase.table(category).select("retro, name, title, description").in_("retro", selected_retros).like("title", search_query).execute()
                res_query.append(query.data)
            if 'description' in search_in:
                query = query = supabase.table(category).select("retro, name, title, description").in_("retro", selected_retros).like("description", search_query).execute()
                res_query.append(query.data)
        
        for rows in res_query:
            for row in rows:
                retro = row['retro']
                name = row['name']
                title = row.get('title', '')
                description = row.get('description', '')
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
                    search_results[retro][category_name][str(index)] = (name, f"{base_url}{name}{extension}", title, description)
    
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