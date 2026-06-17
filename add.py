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

아무무 : 말파이트 이상의 최악의 하드카운터. 짜증내기(E)의 물리 피해 감소 효과로 궁사의 집중(Q)를 카운터 칠 수도 있어서 애쉬의 공격 쯤이야 간지러운 수준으로 받아내고, 무엇보다 생존기가 부실한 애쉬에게는 아무무의 CC기는 항상 위험하며, 주변에 팀원들이 있거나, 점멸이 없는 이상 거의 죽는다고 보면 된다. 게다가 아무무는 가끔식 서포터로도 나오는데, 이때는 아무무가 진짜 바보가 아닌 이상 이길 수가 없다. 또한 아무무의 궁극기는 즉발이어서 한타 때나 교전 도중에 아무무의 궁극기에 맞게 되면 순식간에 죽게 된다. 말파이트보다도 답이 없는 최악의 상대.
야스오 : 최악의 하드 카운터. 원거리 딜러의 천적인 만큼 애쉬도 예외가 아니다. 바람 장막(W)으로 애쉬의 모든 공격 수단을 아예 증발시켜 애쉬가 아예 뭔가 하질 못하게 만들어 버릴 수 있다. 그뿐만 아니라 기동성도 좋기에 뚜벅이인 애쉬에게 쉽게 접근할 수 있고 야스오나 적팀의 에어본에 맞아서 최후의 숨결(R)을 맞는다면 십중팔구 그자리에서 죽는다. 하지만 미니언이 없는 곳에서는 뚜벅이라 장막이 이미 빠졌거나 장막이 유지되는 시간 동안 애쉬를 잡아내지 못하면 역으로 허우적대며 애쉬의 카이팅에 아무것도 못 한다. 미니언이 많은 곳에서의 대면은 최대한 피하자.

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