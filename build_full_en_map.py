import urllib.request
import json
import re

def main():
    ver_url = 'https://ddragon.leagueoflegends.com/api/versions.json'
    versions = json.loads(urllib.request.urlopen(ver_url).read())
    latest_ver = versions[0]
    print(f"Latest Data Dragon version: {latest_ver}")

    # 1. Champions
    ko_champs = json.loads(urllib.request.urlopen(f'https://ddragon.leagueoflegends.com/cdn/{latest_ver}/data/ko_KR/champion.json').read())['data']
    en_champs = json.loads(urllib.request.urlopen(f'https://ddragon.leagueoflegends.com/cdn/{latest_ver}/data/en_US/champion.json').read())['data']
    champ_map = {ko_champs[k]['name']: en_champs[k]['name'] for k in ko_champs if k in en_champs}
    print(f"Champions mapped: {len(champ_map)}")

    # 2. Items
    ko_items = json.loads(urllib.request.urlopen(f'https://ddragon.leagueoflegends.com/cdn/{latest_ver}/data/ko_KR/item.json').read())['data']
    en_items = json.loads(urllib.request.urlopen(f'https://ddragon.leagueoflegends.com/cdn/{latest_ver}/data/en_US/item.json').read())['data']
    item_map = {ko_items[k]['name']: en_items[k]['name'] for k in ko_items if k in en_items}
    print(f"Items mapped: {len(item_map)}")

    # 3. Runes
    ko_runes = json.loads(urllib.request.urlopen(f'https://ddragon.leagueoflegends.com/cdn/{latest_ver}/data/ko_KR/runesReforged.json').read())
    en_runes = json.loads(urllib.request.urlopen(f'https://ddragon.leagueoflegends.com/cdn/{latest_ver}/data/en_US/runesReforged.json').read())
    rune_map = {}

    def extract_runes(r_ko_list, r_en_list):
        for r_ko, r_en in zip(r_ko_list, r_en_list):
            rune_map[r_ko['name']] = r_en['name']
            if 'slots' in r_ko and 'slots' in r_en:
                for s_ko, s_en in zip(r_ko['slots'], r_en['slots']):
                    extract_runes(s_ko['runes'], s_en['runes'])

    extract_runes(ko_runes, en_runes)
    print(f"Runes mapped: {len(rune_map)}")

    # 4. Summoner Spells
    ko_sum = json.loads(urllib.request.urlopen(f'https://ddragon.leagueoflegends.com/cdn/{latest_ver}/data/ko_KR/summoner.json').read())['data']
    en_sum = json.loads(urllib.request.urlopen(f'https://ddragon.leagueoflegends.com/cdn/{latest_ver}/data/en_US/summoner.json').read())['data']
    sum_map = {ko_sum[k]['name']: en_sum[k]['name'] for k in ko_sum if k in en_sum}
    print(f"Summoners mapped: {len(sum_map)}")

    full_map = {}
    full_map.update(champ_map)
    full_map.update(item_map)
    full_map.update(rune_map)
    full_map.update(sum_map)

    custom_mappings = {
        "강철의 솔라리 팬던트": "Locket of the Iron Solari",
        "치유 감소 아이템": "Grievous Wounds Items",
        "하드탱커": "Hard Tank",
        "유틸형 원거리 서포터": "Ranged Enchanter Support",
        "애니보다 팔이 긴 챔피언": "Champions with longer range than Annie",
    }
    full_map.update(custom_mappings)

    # Add space-less variations (e.g. "판금장화" -> "Plated Steelcaps")
    variations = {}
    for k, v in list(full_map.items()):
        no_space = k.replace(' ', '')
        if no_space != k and no_space not in full_map:
            variations[no_space] = v
    full_map.update(variations)

    # Check against champ.json entries
    champ_data = json.load(open('champ.json', encoding='utf-8'))
    all_counter_names = set()
    for c in champ_data:
        for hc in c.get('hard_counters', []):
            raw = hc['name'] if isinstance(hc, dict) else hc
            clean = re.sub(r'\s*\(.*?\)\s*$', '', raw).strip()
            all_counter_names.add(clean)
        for gc in c.get('general_counters', []):
            raw = gc['name'] if isinstance(gc, dict) else gc
            clean = re.sub(r'\s*\(.*?\)\s*$', '', raw).strip()
            all_counter_names.add(clean)

    missing = [n for n in all_counter_names if n not in full_map]
    print(f"Total counter items/runes/champs in champ.json: {len(all_counter_names)}")
    print(f"Total mapped entries: {len(full_map)}")
    print(f"Missing in Data Dragon: {missing}")

    # Generate champ_en_map.js
    line_map = {
        '탑': 'Top',
        '정글': 'Jungle',
        '미드': 'Mid',
        '원딜': 'ADC',
        '바텀': 'ADC',
        '서폿': 'Support',
        '서포터': 'Support',
        '전체': 'All'
    }

    content = f"// Riot Data Dragon {latest_ver} Official Mappings (Champions, Items, Runes, Spells)\n"
    content += "var CHAMP_EN_MAP = " + json.dumps(full_map, ensure_ascii=False, indent=2) + ";\n\n"
    content += "var LINE_EN_MAP = " + json.dumps(line_map, ensure_ascii=False, indent=2) + ";\n\n"
    content += "var EN_TO_KO_MAP = {};\n"
    content += "for (var koName in CHAMP_EN_MAP) {\n"
    content += "    EN_TO_KO_MAP[CHAMP_EN_MAP[koName].toLowerCase()] = koName;\n"
    content += "}\n"

    with open('champ_en_map.js', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated champ_en_map.js successfully!")

if __name__ == '__main__':
    main()
