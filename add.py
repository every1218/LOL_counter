import re
import json
import sys

def parse_champion_descriptions(raw_text):
    """
    "이름 : 설명" 형식의 여러 문단 텍스트를
    [{"name": "...", "reason": "..."}, ...] JSON 리스트로 변환합니다.
    """
    
    # 1. 텍스트의 앞뒤 공백/줄바꿈 제거
    text_to_split = raw_text.strip()
    
    # 2. re.findall을 사용하여 (이름)과 (설명)을 직접 캡처
    #    - (이름 패턴) : (설명 패턴)
    #    - 설명은 다음 이름 패턴이 나오거나, 문자열 끝(\Z)이 나오기 전까지 모두 캡처 (re.DOTALL)
    pattern = re.compile(
        # ⭐️ 이름 패턴에 &와 콤마(,) 문자 추가 ⭐️
        r'([가-힣A-Za-z\s()（）&,]+?)\s*:\s*(.*?)(?=\n[가-힣A-Za-z\s()（）&,]+?\s*:|\Z)', 
        re.DOTALL
    )
    
    matches = pattern.findall(text_to_split)
    
    champion_list = []
    
    # 3. 캡처된 (이름, 설명) 튜플을 순회
    for name_raw, reason_raw in matches:
        
        # 4. 이름과 설명에서 공백 제거
        name = name_raw.strip()
        reason = reason_raw.strip()
        
        if not name or not reason: # 둘 중 하나라도 비어있으면 건너뛰기
            continue
            
        # 5. 설명(reason)에서 각주 번호([47] 등) 제거
        reason = re.sub(r'\[\d+\]', '', reason).strip()
        
        # 6. 리스트에 딕셔너리 형태로 추가
        champion_list.append({"name": name, "reason": reason})
            
    return champion_list

# --- 4. 메인 실행 함수 ---
def main():
    
    # ⭐️⭐️⭐️⭐️⭐️
    # 1. 여기에 위키에서 복사한 "기타" 섹션 등의 텍스트를 붙여넣기
    RAW_TEXT_INPUT = """

르블랑 : 미드 블라디미르 밴 대상 1순위. 상대가 후픽으로 르블랑이 나온다면 닷지하는 게 좋다. 르블랑은 아칼리와 마찬가지로 치고 빠지는 식으로 딜교를 하기 때문에 블라디와 쉽게 맞딜을 해주지도 않는다. 맞딜을 한다 하더라도 블라디와 르블랑의 기동력 차이가 심한 탓에 블라디가 딜교에서 손해를 보며 무엇보다 르블랑의 사슬에 걸리면 웅덩이를 써도 속박에 걸리기 때문에 블라디가 CS만 받아먹는 것말고는 할 수 있는 게 아예 없다. 블라디는 16렙까지 성장해야만 한타에서 변수를 만들 수가 있는데 16렙 되기 전도 문제인데 기동력이 뛰어난 아칼리나 르블랑같은 하나 때문에 탑과 바텀이 계속해서 사려야하는 상황이 발생할뿐더러 아칼리나 르블랑의 움직임 하나 때문에 팀원들이 고통받는 상황이 나오는 게 가장 큰 문제이며 애초에 라인전도 이기기가 쉽지 않은데 르블랑 팀이 시간을 끄는 게 아닌 이상 게임을 지는 상황도 자주 나온다.

    """
    # ⭐️⭐️⭐️⭐️⭐️
    
    print("--- 텍스트 파싱 시작 ---")
    
    # 2. 파싱 실행
    parsed_data = parse_champion_descriptions(RAW_TEXT_INPUT)

    print("--- 파싱 완료 (줄바꿈 없이 한 줄로 출력) ---")
    
# 3. ⭐️ 수정된 출력 로직 (마지막 콤마 제거)
    for i, item in enumerate(parsed_data):
        json_line = json.dumps(item, ensure_ascii=False)
        print(json_line, end="") # 객체만 출력

        print(", ", end="")
            
    # 마지막에만 줄바꿈을 한 번 실행 (터미널 프롬프트가 붙는 것 방지)
    print()


if __name__ == '__main__':
    main()