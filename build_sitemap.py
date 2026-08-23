import json
import urllib.parse
from datetime import datetime

with open('champ.json', 'r', encoding='utf-8') as f:
    champs = json.load(f)

with open('champ_en_map.js', 'r', encoding='utf-8') as f:
    js_en = f.read()

with open('champ_zh_map.js', 'r', encoding='utf-8') as f:
    js_zh = f.read()

def extract_map(js_content, var_name):
    start = js_content.find(var_name + ' = {')
    if start == -1:
        return {}
    start += len(var_name + ' = ')
    end = js_content.find('};', start)
    if end == -1:
        return {}
    json_str = js_content[start:end+1]
    return json.loads(json_str)

en_map = extract_map(js_en, 'CHAMP_EN_MAP')
zh_map = extract_map(js_zh, 'CHAMP_ZH_MAP')

today = datetime.now().strftime('%Y-%m-%d')
base_url = 'https://vschamp.lol'

urls = []
urls.append(f'''  <url>
    <loc>{base_url}/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>''')

seen = set()
for c in champs:
    name = c['champion']
    if name in seen:
        continue
    seen.add(name)

    ko_encoded = urllib.parse.quote(name)
    urls.append(f'''  <url>
    <loc>{base_url}/?champ={ko_encoded}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>''')

    en_name = en_map.get(name, name)
    en_encoded = urllib.parse.quote(en_name)
    urls.append(f'''  <url>
    <loc>{base_url}/?lang=en&amp;champ={en_encoded}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>''')

    zh_name = zh_map.get(name, name)
    zh_encoded = urllib.parse.quote(zh_name)
    urls.append(f'''  <url>
    <loc>{base_url}/?lang=zh&amp;champ={zh_encoded}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>''')

xml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
''' + '\n'.join(urls) + '\n</urlset>'

with open('sitemap.xml', 'w', encoding='utf-8') as f:
    f.write(xml_content)

print(f"Generated sitemap.xml with {len(urls)} URLs successfully!")
