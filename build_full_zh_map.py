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
    zh_champs = json.loads(urllib.request.urlopen(f'https://ddragon.leagueoflegends.com/cdn/{latest_ver}/data/zh_CN/champion.json').read())['data']
    champ_map = {ko_champs[k]['name']: zh_champs[k]['name'] for k in ko_champs if k in zh_champs}
    print(f"Champions mapped: {len(champ_map)}")

    # 2. Items
    ko_items = json.loads(urllib.request.urlopen(f'https://ddragon.leagueoflegends.com/cdn/{latest_ver}/data/ko_KR/item.json').read())['data']
    zh_items = json.loads(urllib.request.urlopen(f'https://ddragon.leagueoflegends.com/cdn/{latest_ver}/data/zh_CN/item.json').read())['data']
    item_map = {ko_items[k]['name']: zh_items[k]['name'] for k in ko_items if k in zh_items}
    print(f"Items mapped: {len(item_map)}")

    # 3. Runes
    ko_runes = json.loads(urllib.request.urlopen(f'https://ddragon.leagueoflegends.com/cdn/{latest_ver}/data/ko_KR/runesReforged.json').read())
    zh_runes = json.loads(urllib.request.urlopen(f'https://ddragon.leagueoflegends.com/cdn/{latest_ver}/data/zh_CN/runesReforged.json').read())
    rune_map = {}

    def extract_runes(r_ko_list, r_zh_list):
        for r_ko, r_zh in zip(r_ko_list, r_zh_list):
            rune_map[r_ko['name']] = r_zh['name']
            if 'slots' in r_ko and 'slots' in r_zh:
                for s_ko, s_zh in zip(r_ko['slots'], r_zh['slots']):
                    extract_runes(s_ko['runes'], s_zh['runes'])

    extract_runes(ko_runes, zh_runes)
    print(f"Runes mapped: {len(rune_map)}")

    # 4. Summoner Spells
    ko_sum = json.loads(urllib.request.urlopen(f'https://ddragon.leagueoflegends.com/cdn/{latest_ver}/data/ko_KR/summoner.json').read())['data']
    zh_sum = json.loads(urllib.request.urlopen(f'https://ddragon.leagueoflegends.com/cdn/{latest_ver}/data/zh_CN/summoner.json').read())['data']
    sum_map = {ko_sum[k]['name']: zh_sum[k]['name'] for k in ko_sum if k in zh_sum}
    print(f"Summoners mapped: {len(sum_map)}")

    full_map = {}
    full_map.update(champ_map)
    full_map.update(item_map)
    full_map.update(rune_map)
    full_map.update(sum_map)

    custom_mappings = {
        "강철의 솔라리 팬던트": "钢铁烈阳之匣",
        "치유 감소 아이템": "重伤装备",
        "하드탱커": "重型坦克",
        "유틸형 원거리 서포터": "远程软辅",
        "애니보다 팔이 긴 챔피언": "攻击距离大于安妮的英雄"
    }
    full_map.update(custom_mappings)

    # Add space-less variations
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
    print(f"Missing in Data Dragon zh_CN: {missing}")

    # Generate champ_zh_map.js
    line_map = {
        '탑': '上单',
        '정글': '打野',
        '미드': '中单',
        '원딜': 'ADC',
        '바텀': 'ADC',
        '서폿': '辅助',
        '서포터': '辅助',
        '전체': '全部'
    }

    content = f"// Riot Data Dragon {latest_ver} Official Chinese Mappings (zh_CN)\n"
    content += "var CHAMP_ZH_MAP = " + json.dumps(full_map, ensure_ascii=False, indent=2) + ";\n\n"
    content += "var LINE_ZH_MAP = " + json.dumps(line_map, ensure_ascii=False, indent=2) + ";\n\n"
    content += "var ZH_TO_KO_MAP = {};\n"
    content += "for (var koName in CHAMP_ZH_MAP) {\n"
    content += "    ZH_TO_KO_MAP[CHAMP_ZH_MAP[koName].toLowerCase()] = koName;\n"
    content += "}\n"

    with open('champ_zh_map.js', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated champ_zh_map.js successfully!")

if __name__ == '__main__':
    main()
