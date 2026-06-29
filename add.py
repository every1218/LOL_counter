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

바루스 : 극카운터 2. 메타를 크게 타는 챔피언이기에 자주 등장하진 않지만, 일단 탑 바루스가 유행을 탔다 하면 쉔 입장에서는 절대로 이길 수 없는 카운터픽이 된다. 탑 바루스는 주로 AP/AS 빌드를 타는데, 만약 상대가 AP 빌드를 들고 오면 쉔은 하루 종일 얻어맞다가 6렙을 찍은 바루스의 궁-WQ 연계에 그냥 죽어야 한다. AS 빌드면 그나마 결계로 평타를 몇 대 막을 수는 있지만, 바루스가 결계가 끝나기를 기다렸다가 스택을 터트리기만 하면 바루스는 흠집 정도만 나 있는데 쉔은 체력이 너덜너덜해지는 불합리한 교환이 나온다. 그나마 초반에 갱을 불러서 딸 수는 있지만, 그동안 상대가 아래를 터트리면 아군 의존도가 극심한 쉔 입장에서는 당연히 기분이 나쁜 데다가 어차피 중후반 단계로 가면 무조건 1대 1을 진다. 이 타이밍의 바루스는 탱템을 섞는 경우가 많기에 아군을 끌고 와도 바루스를 터트리지 못하면 교환 구도가 나오거나 최악의 경우 둘 다 죽어야 한다. 바텀 포킹(사실상 바루스가 가장 많이 서게 되고, 가장 많이 보이는 포지션이다) 바루스라고 해서 나을 것도 없는 것이, 바루스의 Q는 최대 사거리가 1625이기에 쉔 혼자서는 절대로 Q만 쏴대는 바루스를 물 수가 없다. 기본 능력치도 하위권이라 다른 탱커들에 비해 더 살살 녹는 건 덤이다.




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