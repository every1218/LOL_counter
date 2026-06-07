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
    CHAMPION_NAME = "킨드"
    
    # 2. 여기에 챔피언 별칭 입력 (쉼표로 구분)
    RAW_ALIASES_TEXT = ""

    # 3. 여기에 '상대하기 힘든 챔피언' 섹션 텍스트 복사
    RAW_COUNTERS_TEXT = """ 
그라가스[28],리 신[31], 신 짜오[32], 카밀, 잭스[33], 니달리, 샤코, 판테온[34], 엘리스[35], 마스터 이[36]

    """
    
    # 4. 여기에 '각주' 섹션 텍스트 복사
    RAW_FOOTNOTES_TEXT = """


리딜을 할 수 있기 때문에 막은 듯하다.
[22] 이러한 특성 때문에 시간이 많이 흐른 뒤인 2023년에 온 맵을 싸돌아다니며 싸움을 벌이는 서폿 트위치가 일시적으로 유행한 바 있다.
[23] 4스택 기준 575에, 보통 중반에는 7스택인 600 전후로 늘어나고 게임이 길어진다면 625까지도 늘어난다. 650 정도면 보통 게임이 압도적으로 기울어진 상태. 원거리 딜러의 평균 사거리가 보통 550이며, 압도적인 사거리를 아이덴티티로 삼는 케이틀린의 사거리가 650이고, 다른 원딜과 유의미한 차이를 보여주는 바루스가 575라는 것을 생각하면 4스택만으로도 상급의 수치다.
[24] 아무리 망해도 4스택을 못 찍는 것은 어렵다. 꼭 킬을 하지 않아도 어시를 먹거나 정글몹을 잡아서 스택을 찍을 수 있기 때문.
[25] 일반적으로 몸이 약한 킨드레드가 먼저 체력이 빠지더라도, 상대와의 지속딜 및 사거리 싸움에서 킨드레드가 우위를 점하면서 상대의 체력을 일방적으로 깎아내릴 수 있다.
[26] 쿨타임이 길고 특유의 각이 나올 때 점사해야 하는 블라디미르, 케넨 등의 한타형 챔피언들이 킨드레드가 있는 진영 쪽으로 선진입하는 것은 자살 행위 수준으로 위험하다.
[27] 다만 날아가는 늑대는 추가 피해를 가진 평타 판정이라 이미 늑대가 발사되면 상대가 공격을 막을 만한 생존기를 쓰지 못하면 부쉬로 들어가건 벽을 넘어가건 적중 확정이다.
[28] 최악의 카운터 중 하나. 배치기 연계에서 나오는 특유의 폭딜은 3렙 이후 킨드레드를 터트리기에 충분하며, 궁극기를 적절하게 깔아도 맞궁 한 번이면 킨드레드의 팀원들을 모조리 쫓아내고 양의 안식처를 강제점거할 수 있다. 갱킹 능력도 출중하기에 라인 개입을 통해 성장을 벌리는 것도 쉽지가 않다. 다만 아군이 탑/미드 그라가스를 픽했다면 ad-ap 딜 밸런스가 적절하게 맞을 뿐만 아니라 반반 이상이 보장되는 라인전을 통해 표식 확보를 도와주거나 뛰어난 갱킹 능력을 통해 킨드의 성장을 도울 수도 있고, 무엇보다 양의 안식처 내에서 난전이 펼쳐진다면 술통 폭발로 역으로 상대방을 몰아낼 수 있기에 아군으로 나왔을 때는 궁합이 잘 맞는다.
[29] 특히 리워크로 벽꿍이 생겼기 때문에 벽을 끼고 넘어다니면서 심리전을 펼쳐야 하는 킨드레드 입장에서는 함부로 접근하기가 불편해졌다.
[30] 물론 이 점 때문에 만약 알리가 아군일땐 최고의 파트너가 된다. 킨드가 궁을 쓰면 알리가 핵심딜러를 밖으로 밀어낸 틈을 타 킨드의 뛰어난 기동력으로 추격해서 딜러를 찢을 수 있기 때문이다.
[31] 대표적인 카운터. 저레벨 싸움에서 리신을 절대 이길 수가 없으며, 궁으로 한숨을 돌리려고 해도 리 신도 발차기로 킨드레드를 안식처 바깥으로 날려버릴 수 있다. 만약 싸울 경우 음파를 피하면 훨씬 할만해지며, 2-3렙 싸움에선 킨드레드가 일방적으로 패니 초반에 적극적인 카정으로 성장 차이를 벌려 놓아야 한다.
[32] 리 신보다 더 강력한 저레벨 강자다. 일단 E스킬로 물리는 순간 도주하는 것은 상당히 힘들며, 맞딜 성립도 안 된다. 갱킹 능력으로만 따지자면 신 짜오 쪽이 더 좋기 때문에 골치아픈 존재.
[33] 모든 평딜러들의 까다로운 난적으로 6렙 이후 맞딜도 강하거니와 킨드레드의 핵심 딜링 수단인 평타와 강점인 궁극기 사용 후 역관광도 반격 하나로 무력화 해버린다. 잭스도 킨드레드처럼 성장형 챔피언이지만 저레벨에도 맞다이 하나만큼은 강해서 초반 유충/전령 교전에서 킨드레드가 불리하다. 도주 능력이 늑대의 영역 안이 한계인 킨드레드랑 다르게 잭스의 추격 능력은 상당하기 때문에 뿌리치기 힘든 것도 문제. 잭스 또한 후반으로 갈수록 강해지는 왕귀챔이라 후반을 본다 해도 상대하기 힘들다. 시간이 끌리면 잭스는 탱킹력의 상승, 피흡, 짧아진 반격의 쿨타임과 존야, 수호 천사 같은 어그로 핑퐁 수단을 갖추고 한타에서 반격을 2회 이상 돌릴 수 있게 되는데 이렇게 되면 킨드레드의 궁극기가 잭스를 마킹하는 데 유의미하게 활용될 것이라 장담하기 어렵고 오히려 반격 쿨타임을 재거나 딜러를 노릴 시간을 버는 데 이용당할 위험이 커지게 된다.
[34] 꽤나 골치 아프다. 초반 교전력이 막강한 편이고 킨드레드의 누킹을 방어할 수 있으며, 스택이 제대로 쌓이지 않은 초중반에는 판테온의 방호의 도약 사거리보다 킨드레드의 사거리가 더 짧기 때문에 근접 vs 원거리인데도 판테온이 선공권을 쥐고 있으며 방어 아이템은커녕 딜링형 아이템만 채용하는 킨드레드에게는 판테온의 스킬 하나 하나가 치명적으로 아프다. 궁극기로 판테온의 누킹을 방지할 수 있긴 하지만 방어력 관통 아이템을 올리는 암살자 트리의 판테온이 가진 순간 딜량은 킨드레드의 허약한 방어 능력치로는 딜이 가늠이 안 돼서 궁 미아도 자주 발생하며, 궁극기를 켰다고 해도 판테온은 킨드레드의 궁극기가 끝나기 직전 방패 돌격으로 체력을 보존할 수 있기에 궁이 끝나도 아군의 도움이 없다면 위험한 쪽은 킨드레드다. 판테온이 갖은 패치와 조정으로 정글에서도 자주 등장하기 시작한 이후부터는 최대한 판테온을 피하며 스택과 레벨링을 하고, 중후반 밸류로 승부를 봐야 그나마 유리해진다. 스택을 통한 사거리가 늘어나기 시작할 때부터는 판테온도 쉽사리 접근하기 어려워지니 성장에 힘을 쏟아야 한다.
[35] 고치만 맞힐 수 있다면 저레벨 싸움에서도 매우 강하고 굳이 킨드레드와 싸워주지 않더라도 갱킹에 대해서도 원거리 하드 CC기도 있고 다이브도 능한 엘리스가 훨씬 우위다. 단 엘리스는 고치의 의존도가 높으므로 고치를 피하는 순간 싸울 만해진다.
[36] 성장형 정글러긴 하지만 초반 맞딜은 육식급으로 강력하기에 카정에 성공하기 쉽지 않다. 킨드레드의 E스킬을 명상으로 상쇄할 수도 있다. 게다가 추격 능력도 상급이라 CC기가 부실한 킨드레드로는 한번 물리면 살아나오기 힘들다. 6레벨 이후 마스터 이가 궁극기를 사용한다면 둔화 저항 때문에 하드 CC가 없는 킨드는 개활지에서 마주치면 도주할 방법이 없다. 무엇보다 후반 성장성도 킨드레드를 상회하기 때문에 까다로운 상대. 게다가 궁극기는 팀원의 체력을 골고루 양념해서 마스터 이가 날뛸 환경을 만드는 역적 스킬이 될 수도 있다.
[37] 이쪽은 그랩하고 은신을 모두 보유하고 있다. 그랩으로 궁극기를 무력화하거나 은신으로 카이팅을 무용지물로 만들 수 있기 때문에 그렇게 만만한 상대는 절대 아니다.
[38] 다만 이쪽은 스타일 연계만 쌓을 수 있으면 궁극기를 다시 쓸 수 있기 때문에 절대 쉬운 상대는 아니다.
[39] 다만, 아무무의 궁은 강력하므로 되도록이면 먼저 궁을 쓰도록 유인하는 게 좋다.
[40] 뚜벅이 마법사에 제대로 된 생존기가 없고, 궁극기도 양의 안식처로 쉽게 막을 수 있다. 손쉬운 먹잇감.
[41] 궁극기를 양의 안식처로 쉽게 카운터칠 수 있다.
[42] 전체 승률 52%, 골드는 약 52%, 플레티넘은 약 50.6%, 다이아는 53%에 가깝다. 다만 마스터는 판수가 부족해 20%로 나오고, 챌린저는 아예 없다.
[43] 늑대의 광기의 기본 지속 효과로 킨드레드가 이동하거나 공격을 하면 마치 기민한 발놀림 룬처럼 충전이 되어 100 스택을 쌓게 되면 다음 양의 기본 공격으로 발동하여 킨드레드가 체력을 회복하게 된다.


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