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

존야의 모래시계 : 올라프의 실질적인 하드 카운터 아이템. 궁극기와 W의 버프에 크게 의존하는 올라프는 상대가 경직으로 딜 타이밍을 흘려버릴 경우 급격하게 힘이 빠진다. 1대1이든 한타 도중이든 킬각 잡기가 극도로 까다로워지니 진입 전에 상대의 존야 유무를 미리 체크해두는 게 좋다.



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