import re
import json
import sys

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

신속의 장화: 아트록스의 진짜 하드 카운터는 피오라나 이렐리아가 아닌 사실상 신속의 장화라고 봐도 과언이 아니다. 이동속도가 다른 신발들보다 빨라서 다르킨의 검을 피하기 쉽고, 거기에 둔화 저항이 있어서 지옥사슬을 맞춰도 끌릴 확률을 떨어트려서 사슬을 통한 콤보를 넣어야 하는 아트록스 입장에선 상당히 골치 아프다. 이 아이템을 티모나 럼블같은 이속증가 스킬을 가진 챔피언이 간다면 딜교 성립을 시키기 힘들어지고 아트록스는 그냥 허공에 칼만 휘두르게 된다.




    """
    # ⭐️⭐️⭐️⭐️⭐️
    
    print("--- 텍스트 파싱 시작 ---")
    
    # 2. 파싱 실행
    parsed_data = parse_champion_descriptions(RAW_TEXT_INPUT)

    print("--- 파싱 완료 (줄바꿈 없이 한 줄로 출력) ---")
    
# 3. ⭐️ 수정된 출력 로직 (마지막 콤마 제거)
    output_lines = []
    for i, item in enumerate(parsed_data):
        json_line = json.dumps(item, ensure_ascii=False)
        output_lines.append(json_line + ", ")

    full_output = "".join(output_lines)

    # 터미널 출력 (줄바꿈으로 인한 한글 깨짐 발생 가능)
    print(full_output)

    # [OK] 파일 출력 (복사할 때는 이 파일을 사용하세요)
    output_path = "output.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_output + "\n")
    print(f"\n[OK] 결과가 '{output_path}' 파일에 저장되었습니다. 복사는 파일에서 하세요!")


if __name__ == '__main__':
    main()