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

리신: 대표적인 카운터. 저레벨 싸움에서 리신을 절대 이길 수가 없으며, 궁으로 한숨을 돌리려고 해도 리 신도 발차기로 킨드레드를 안식처 바깥으로 날려버릴 수 있다. 만약 싸울 경우 음파를 피하면 훨씬 할만해지며, 2-3렙 싸움에선 킨드레드가 일방적으로 패니 초반에 적극적인 카정으로 성장 차이를 벌려 놓아야 한다.
뽀삐: 킨드레드 최악의 카운터로 유명한 캐릭 중 하나. 가뜩이나 뽀삐는 E스킬을 통해 킨드레드를 궁극기 밖으로 끄집어 낼 수 있는 캐릭인데 킨드레드의 주력기인 Q가 이동기 판정을 가지고 있다 보니 뽀삐의 W에 막혀버린다. 거기다 정글 뽀삐의 경우 정글 교전력도 매우 강해서 카정에도 지장이 생긴다. 후반 성장 기대치는 킨드가 월등하고 뽀삐 본인도 교전 사거리가 짧고 한타때 상당히 수동적이라 킨드가 스택을 많이 모아서 사거리가 길어지면 개활지에서 뽀삐의 교전 사거리 밖에서 신나게 평타와 Q를 쓸 수는 있지만, 그래도 매우 까다로운 상대.

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