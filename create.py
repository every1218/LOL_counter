import json
import os
import re
#from dotenv import load_dotenv

# .env 파일 로드 (LLM 요약을 위해 필요할 수 있음)
#load_dotenv()

TARGET_FILE = "champ.jsonl" # 우리가 최종 저장할 파일
HARD_KEYWORDS = ["하드 카운터", "하드카운터", "극상성", "닷지", "최악의 상대", "매우 불리하다", "극카운터", "극 카운터", "최악의 카운터", "필벤"]

# --- 1. 파일 관리 함수 ---
def load_and_prepare_data(file_path):
    """기존 JSONL 데이터를 리스트로 로드합니다."""
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return []
    
    data_list = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data_list.append(json.loads(line))
            except json.JSONDecodeError:
                print(f"경고: '{file_path}' 파일의 일부 라인이 깨져있습니다. 해당 라인을 건너뜕니다.")
    return data_list

def save_data(file_path, data_list):
    """
    데이터 리스트를 JSONL 형식으로 저장합니다.
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        for i, champ_data in enumerate(data_list):
            f.write(json.dumps(champ_data, ensure_ascii=False) + '\n')

# --- 2. 핵심 파싱 로직 ---
def parse_manual_data(champion_name, raw_aliases_text, raw_counters_text, raw_footnotes_text):
    """
    사용자가 붙여넣기 한 텍스트를 파싱하여 JSON 객체로 만듭니다.
    """
    
    # 0단계: 별칭 파싱
    aliases = [alias.strip() for alias in raw_aliases_text.split(',') if alias.strip()]
    print(f"-> 별칭 파싱 완료: {aliases}")

    # 1단계: 각주 맵 생성
    footnote_map = {}
    footnote_parts = raw_footnotes_text.split('[')
    for part in footnote_parts[1:]:
        match = re.match(r'(\d+)\]\s*([\s\S]*)', part)
        if match:
            number = match.group(1)
            text = match.group(2).strip()
            text = text.split('[')[0].strip()
            footnote_map[number] = text

    print(f"-> 각주 맵 생성 완료 (총 {len(footnote_map)}개)")

    # 2단계: 카운터 텍스트 파싱
    hard_counters = []
    general_counters = []
    
    # ⭐️ 수정된 부분: 쉼표(,), 공백( ), 글머리 기호(•, ■, -), 줄바꿈(\n)을 모두 분리 기준으로 사용
    # 이렇게 하면 쉼표로 연결된 긴 리스트도 정확하게 분리됨.
    counter_items = re.split(r'\s*,\s*|\s*(?:•|■|-|\n)\s*', raw_counters_text)
    
    for item in counter_items:
        if not item:
            continue
        
        # 챔피언 이름과 각주 번호 분리 (예: "이렐리아[30]")
        match = re.match(r'([^\[]+)(?:\[(\d+)\])?', item.strip())
        
        if match:
            name = match.group(1).strip()
            number = match.group(2)
            
            # 이름이 빈 문자열인 경우 건너뜀
            if not name:
                continue
            
            if number and number in footnote_map:
                # 각주 번호가 있고, 맵에도 존재
                description = footnote_map[number]
                
                # 키워드 검사
                if any(keyword in description for keyword in HARD_KEYWORDS):
                    # ⭐️ 하드 카운터
                    # reason = summarize_reason_llm(description, name) # LLM 요약 (현재 더미)
                    reason = description # ⭐️ 그냥 원본 텍스트를 넣고 싶으면 이걸로
                    hard_counters.append({"name": name, "reason": reason})
                else:
                    # ⭐️ 일반 카운터 (각주O, 키워드X)
                    general_counters.append(name)
            else:
                # ⭐️ 일반 카운터 (각주X)
                general_counters.append(name)

    print(f"-> 파싱 완료: 하드카운터({len(hard_counters)}), 일반({len(general_counters)})")

    # 3단계: 최종 JSON 객체 반환
    return {
        "champion": champion_name,
        "aliases": aliases,
        "hard_counters": hard_counters,
        "general_counters": general_counters
    }

# --- 3. 메인 실행 함수 ---
def main():
    
    # ⭐️⭐️⭐️⭐️⭐️
    # 1. 여기에 챔피언 이름 입력
    CHAMPION_NAME = "로크"
    
    # 2. 여기에 챔피언 별칭 입력 (쉼표로 구분)
    RAW_ALIASES_TEXT = ""

    # 3. 여기에 '상대하기 힘든 챔피언' 섹션 텍스트 복사
    RAW_COUNTERS_TEXT = """ 
이렐리아[1], 야스오[2], 레넥톤, 크산테, 자헨

    """
    
    # 4. 여기에 '각주' 섹션 텍스트 복사
    RAW_FOOTNOTES_TEXT = """


[1] 패시브가 활성화 된 이렐리아의 맞딜은 두말할것 없이 이렐리아가 압도적이며 Q스킬의 칼날쇄도로 로크의 Q스킬이랑 궁극기 따위는 그냥 가뿐히 피해버린다. 이렐리아는 순간 폭딜 능력이 없어 W스킬의 효율이 떨어지는데다 로크의 폭딜은 그냥 저항의 춤(W) 한번만 딱 누르고 있으면 되며 한타도 로크에게 절대로 밀리지가 않는다. 어지간해선 밴하거나 만약 밴을 잊어먹으면 닷지를 하자.
[2] 이렐리아 못지않은 하드카운터로 이쪽도 한타랑 지속싸움이 뛰어난데다 질풍검의 뛰어난 기동력 덕분에 라인전에서 의식용 대못(Q)은 가뿐하게 피할수가 있으며 로크의 Q스킬이랑 궁극기는 투사체 판정이므로 야스오의 바람 장막에 완벽하게 막혀버린다. 그나마 야스오는 체력 아이템을 가는 일이 드물기 때문에 이렐리아랑은 달리 야스오는 폭딜에 취약하다는 단점이 있다.

"""
    # ⭐️⭐️⭐️⭐️⭐️
    
    print(f"--- 수동 파서 시작: {CHAMPION_NAME} ---")
    
    # 5. 파싱 실행
    new_champion_data = parse_manual_data(CHAMPION_NAME, RAW_ALIASES_TEXT, RAW_COUNTERS_TEXT, RAW_FOOTNOTES_TEXT)

    # 6. 기존 데이터 로드
    all_data_list = load_and_prepare_data(TARGET_FILE)

    # 7. 데이터 업데이트 또는 추가
    updated = False
    for i, data in enumerate(all_data_list):
        if data.get('champion') == new_champion_data['champion']:
            all_data_list[i] = new_champion_data # 기존 데이터 덮어쓰기
            updated = True 
            print(f"'{new_champion_data['champion']}'의 데이터를 업데이트했습니다.")
            break
            
    if not updated:
        all_data_list.append(new_champion_data) # 새 데이터 추가
        print(f"'{new_champion_data['champion']}'의 데이터를 새로 추가했습니다.")

    # 8. 파일 저장
    save_data(TARGET_FILE, all_data_list)
    print(f"성공: 데이터가 '{TARGET_FILE}' 파일에 저장되었습니다.")
if __name__ == '__main__':
    main()