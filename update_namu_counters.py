import sys
import re
import json
import urllib.parse
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

TARGET_URL = "https://namu.wiki/w/갱플랭크"
#python update_namu_counters.py "https://namu.wiki/w/그라가스"

def clean_namu_url(raw_url):
    """
    URL에서 주소 영역만 추출하고, 한글 챔피언명을 안전하게 퍼센트 인코딩 처리합니다.
    """
    clean = raw_url.split('#')[0].strip()
    unquoted = urllib.parse.unquote(clean)
    
    if "namu.wiki/w/" in unquoted:
        champ_name_part = unquoted.split("namu.wiki/w/")[-1]
        encoded_champ = urllib.parse.quote(champ_name_part)
        return f"https://namu.wiki/w/{encoded_champ}"
    
    return clean


def extract_counter_reasons_from_namu(url):
    """
    나무위키 URL을 받아 '상대하기 힘든 챔피언' 항목의 각주 이유를 추출합니다.
    반환값: tuple (target_champ_name, { champ_name: reason_text })
    """
    clean_url = clean_namu_url(url)
    
    print(f"[*] 나무위키 접속 시도: {clean_url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(clean_url, wait_until="networkidle", timeout=15000)
        except Exception:
            page.goto(clean_url, wait_until="domcontentloaded")
            
        page.wait_for_timeout(3500) # DOM 렌더링 완료 대기
        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")

    # 챔피언 이름 (문서 제목) 가져오기 및 정규화
    title_tag = soup.find("title")
    page_title = title_tag.get_text().split("-")[0].strip() if title_tag else ""

    if not page_title:
        h1 = soup.find("h1")
        page_title = h1.get_text().strip() if h1 else ""

    clean_champ_title = re.sub(r"\s*\(리그\s*오브\s*레전드\)", "", page_title).strip()
    clean_champ_title = re.sub(r"\s*\(.*?\)", "", clean_champ_title).strip()

    print(f"[*] 나무위키 문서 챔피언: [{clean_champ_title}] (원본 문서 제목: {page_title})")

    # 1. 모든 각주 (footnote) 수집 (fn_id -> text)
    footnote_map = {}
    for fn_anchor in soup.find_all("span", id=re.compile(r"^fn-\d+$")):
        fn_id = fn_anchor.get("id").replace("fn-", "")
        parent_container = fn_anchor.parent
        if parent_container:
            full_text = parent_container.get_text(" ", strip=True)
            clean_text = re.sub(r"^\[\d+\]\s*", "", full_text)
            clean_text = re.sub(r"^\d+\.\s*", "", clean_text)
            clean_text = re.sub(r"\s+", " ", clean_text).strip()
            footnote_map[fn_id] = clean_text

    print(f"[*] 총 각주 {len(footnote_map)}개 인덱싱 완료")

    # 2. '상대하기 힘든 챔피언' 섹션 탐색 및 컨테이너 선정
    parsed_counters = {}
    target_node = soup.find(string=re.compile(r"상대하기\s*(힘든|어려운|껄끄러운|나쁜)"))
    
    if not target_node:
        print("[!] '상대하기 힘든/어려운 챔피언' 섹션을 찾지 못했습니다.")
        return clean_champ_title, parsed_counters

    # 조상을 거슬러 올라가며 각주 링크(a[href^="#fn-"])가 포함된 유효 컨테이너 탐색
    curr = target_node.parent
    outer_container = None
    for _ in range(10):
        if not curr:
            break
        fn_links = curr.find_all("a", href=re.compile(r"^#fn-\d+$"))
        if len(fn_links) > 0:
            outer_container = curr
            break
        curr = curr.parent

    if not outer_container:
        outer_container = soup # fallback

    links = outer_container.find_all("a")
    for i, a in enumerate(links):
        # '상대하기 쉬운' 섹션이 시작되면 탐색 종료
        text_around = a.parent.get_text() if a.parent else ""
        if "상대하기 쉬운" in text_around or "상대하기 무난" in text_around:
            if "상대하기 쉬운" in a.get_text() or (a.parent and "상대하기 쉬운" in a.parent.get_text()):
                break

        href = a.get("href", "")
        if href.startswith("#fn-") or href.startswith("#rfn-"):
            fn_num = href.replace("#fn-", "").replace("#rfn-", "")
            
            # 각주 직전 챔피언 링크 탐색
            prev_champ = None
            for k in range(i - 1, -1, -1):
                prev_a = links[k]
                prev_href = prev_a.get("href", "")
                prev_text = prev_a.get_text(strip=True)
                if prev_href.startswith("/w/") and not prev_href.startswith("#") and prev_text and not prev_text.startswith("["):
                    prev_champ = prev_text
                    break
            
            if prev_champ and fn_num in footnote_map:
                parsed_counters[prev_champ] = footnote_map[fn_num]
                print(f"  - 추출 성공: [{prev_champ}] (각주 {fn_num}) -> {footnote_map[fn_num][:50]}...")

    return clean_champ_title, parsed_counters


def update_champ_json(champ_title, parsed_counters, json_path="champ.json"):
    """
    추출한 카운터 이유를 champ.json 파일에 업데이트합니다.
    - 하드 카운터(hard_counters): 추출된 이유가 있으면 최신 내용으로 덮어쓰기
    - 일반 카운터(general_counters): 
      * 추출된 이유가 있으면 최신 내용으로 덮어쓰기
      * 각주가 없거나 이유가 없더라도 무조건 {"name": "...", "reason": ""} 객체 형태로 생성/통일
    """
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    champ_entry = None
    for entry in data:
        if entry.get("champion") == champ_title:
            champ_entry = entry
            break

    if not champ_entry:
        print(f"[!] champ.json에서 [{champ_title}] 챔피언을 찾을 수 없습니다.")
        return False

    print(f"\n[*] [{champ_title}] champ.json 데이터 업데이트 시작...")
    
    # 1. 하드 카운터 (hard_counters) 업데이트
    hard_counters = champ_entry.get("hard_counters", [])
    hard_updated_count = 0
    for item in hard_counters:
        if isinstance(item, dict):
            champ_name = item.get("name", "")
            base_name = re.sub(r"\s*\(.*?\)", "", champ_name).strip()
            if base_name in parsed_counters:
                new_reason = parsed_counters[base_name]
                item["reason"] = new_reason
                hard_updated_count += 1
                print(f"  [하드 카운터 최신화] {champ_name}: 나무위키 각주 내용으로 덮어쓰기 완료!")

    # 2. 일반 카운터 (general_counters) 업데이트
    general_counters = champ_entry.get("general_counters", [])
    gen_updated_count = 0

    new_general_counters = []
    
    for item in general_counters:
        if isinstance(item, dict):
            champ_name = item.get("name", "")
            existing_reason = item.get("reason", "").strip()
        else:
            champ_name = str(item)
            existing_reason = ""

        base_name = re.sub(r"\s*\(.*?\)", "", champ_name).strip()

        # 나무위키 각주에서 새로 추출된 reason이 있는 경우 -> 덮어쓰기 (최신화)
        if base_name in parsed_counters:
            new_reason = parsed_counters[base_name]
            updated_item = {
                "name": champ_name,
                "reason": new_reason
            }
            new_general_counters.append(updated_item)
            gen_updated_count += 1
            print(f"  [일반 카운터 최신화] {champ_name}: 나무위키 각주 내용으로 덮어쓰기 완료!")
        else:
            # 추출된 각주 이유가 없는 항목도 무조건 { "name": ..., "reason": ... } 객체 형태로 통일
            updated_item = {
                "name": champ_name,
                "reason": existing_reason # 기존 이유가 있으면 유지, 없으면 빈 문자열("")
            }
            new_general_counters.append(updated_item)

    champ_entry["hard_counters"] = hard_counters
    champ_entry["general_counters"] = new_general_counters

    # 변경사항 저장
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

    try:
        from clean import clean_champ_json
        clean_champ_json(json_path)
    except Exception as e:
        print(f"[!] 포맷팅 중 경고: {e}")

    print(f"\n[★] [{champ_title}] 업데이트 완료!")
    print(f"    - 하드 카운터 최신화: {hard_updated_count}개")
    print(f"    - 일반 카운터 최신화: {gen_updated_count}개")
    print(f"    - general_counters 전체 객체 형태 통일 완료")
    return True


if __name__ == "__main__":
    input_url = sys.argv[1] if (len(sys.argv) > 1 and "namu.wiki" in sys.argv[1]) else TARGET_URL
    champ_title, parsed_counters = extract_counter_reasons_from_namu(input_url)
    if champ_title:
        update_champ_json(champ_title, parsed_counters, "champ.json")
    else:
        print("[!] 챔피언 정보를 찾을 수 없습니다.")
