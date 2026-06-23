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

나서스 : 밴 대상 1순위. 피오라 픽의 이유를 없애버리는 상성이다. 말파이트와 비슷한 상성인데 대인전은 더욱 불리하다. 초반부터 이속과 공속을 각각 47%, 35%씩 5초 동안 깎아먹는 쇠약은 피오라의 찌르기를 빨리걷기로 만들어 버리며 피오라의 모든 공격 수단인 평타와 Q를 악화시킨다. W는 즉발 타겟팅이라 응수로 씹는 건 운빨에 불과하고, 후반이 아닌 이상 체급차가 심해 한번 씹는다고 쿨타임 동안 압도적 우위를 점할 수 있는 것도 아니다. 피오라는 라인푸쉬와 유지력이 딸리기에 초반에 영혼의 불길(E) 장판으로 라인을 포탑에 박아넣고 스택을 쌓아가는 전술도 상당한 부담이다. 게다가 나서스의 스택이 쌓이고 11렙 이후가 되는 중반 시점부터는 체급 차이가 굉장히 심해지며, 무한 성장 메커니즘으로 인해 극후반에도 승부를 운에 맡길 수밖에 없다. 결국 사이드에서든 한타에서든 모두 밀리는 답이 없는 상대.






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