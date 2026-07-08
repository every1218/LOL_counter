import re
import json
import sys
import os

# Windows 터미널 UTF-8 출력 설정
sys.stdout.reconfigure(encoding='utf-8')

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

아칼리 : 출시 초부터 로크의 카운터로 떠오른 미드 챔피언. 기동력이 좋은 챔피언이며, 모든 스킬이 로크의 카운터급이다. Q로 로크에게 cs를 먹으려 할 때마다 견제를 해대고, 로크가 Q를 아무리 잘 맞히고 들어가도 아칼리가 W로 장막 펼치고 딜교 자체를 피해 버리면 로크는 할 수 있는 것이 없다. W 쿨타임까지 계산해서 잘 들어가도 E로 또 도망갈 수 있으니 로크 입장에선 미칠 노릇. 물론 아칼리가 장막으로 은신해도 로크의 E 순간이동으로 표식을 터뜨릴 수 있고 어쩌다가 표식 각을 허용해 준다면 Q로 견제한 것이 다 원상복구되므로 아칼리 입장에서도 대놓고 나댈 수는 없....으나 적당히 템이 나오고 서로 6레벨이 된다면 아칼리가 점점 더 로크를 압도하기 시작한다. E와 궁극기의 4단 돌진으로 선딜이 긴 로크의 궁은 손쉽게 피해버리고, 로크의 장점 중 하나인 '이론상 최강의 콤보 딜량'도 Q와 패시브를 서너번씩 돌리며 브루저도 암살하는 아칼리의 딜량 앞에서는 한 수 접어야 하기에 스킬을 다 맞히더라도 승리를 장담할 수 없다. 이 엄청난 딜량 때문에 로크의 W 회복 따위로는 아칼리의 암살 콤보를 받아내기 힘든 것도 한몫한다.


    """
    # ⭐️⭐️⭐️⭐️⭐️
    
    print("--- 텍스트 파싱 시작 ---")
    
    # 2. 파싱 실행
    parsed_data = parse_champion_descriptions(RAW_TEXT_INPUT)

    print("--- 파싱 완료 ---")

# 3. ⭐️ pretty-print JSON 블록 출력 로직
    output_lines = []
    for item in parsed_data:
        # 들여쓰기 2칸으로 JSON 직렬화 후, 각 줄 앞에 6칸 공백 추가
        json_block = json.dumps(item, ensure_ascii=False, indent=2)
        indented = "\n".join("      " + line for line in json_block.splitlines())
        output_lines.append(indented + ",")

    full_output = "\n".join(output_lines)

    # 터미널 출력
    print(full_output)

    # [OK] 파일 출력 (복사할 때는 이 파일을 사용하세요)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, "output.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_output + "\n")
    print(f"\n[OK] 결과가 '{output_path}' 파일에 저장되었습니다. 복사는 파일에서 하세요!")


if __name__ == '__main__':
    main()