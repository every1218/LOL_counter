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

독사의 송곳니 : 모데카이저 최악의 하드카운터 아이템. 불멸의 보호막을 큰 폭으로 깎아서 탱킹 능력을 크게 봉쇄시켜버린다. 물론 단순하게 ad 챔피언이 독사를 간다고 해서 그 독사를 간 챔피언이 모데카이저를 무조건 이긴다 할 정도는 아니지만 교전에서 탱킹 변수가 하나는 사라진다는 점, 그리고 맞싸움에서 최강자격 챔프들이 가게 된다면 얘기가 달라진다는 점들에서 꽤나 골치 아프다. 그나마 효과와는 별개로 하위 아이템 가성비는 쓰레기급이라서 아이템이 나오기 이전까지는 괜찮아도 아이템이 나온 이후에는 상당히 골치아프다. 특히나 불멸(W)의 보호막 탱킹 의존도가 매우 높은 모데이기에 그 어떤 챔프보다도 독사의 송곳니 체감이 매우 크게 다가오는 것이 뼈아프다. 물론 독사의 송곳니는 ad암살자/일부 브루저가 사야만 효율이 있는 아이템이기에 구매층이 한정된 방관템이긴 하지만 그 일부 AD 암살자/브루저 중에서도 저런 방관템을 부담없이 구매 가능한 챔피언들이 있는 만큼 모데를 저격하기 위해[121] 독사의 송곳니를 구매하면 모데카이저로 그들을 상대할 때 큰 손해를 입게 되는 경우가 많다.


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