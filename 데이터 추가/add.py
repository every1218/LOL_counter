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

존야의 모래시계 : 마스터 이와 비에고의 하드카운터 아이템. 두 챔피언은 각각 '처치 시 스킬 쿨타임 감소 및 궁극기 연장'과 '처치 관여 시 적 지배 및 체력 회복, 궁극기 초기화'라는 강력한 패시브 메커니즘을 가지고 있어 첫 킬이 한타의 성패를 가를 정도로 굉장히 중요한데, 존야의 모래시계는 그 첫 단추를 완벽하게 잠가버려 탱킹과 기동력 능력을 크게 봉쇄시켜버린다. 물론 단순하게 상대가 존야를 간다고 해서 무조건 진다 할 정도는 아니지만, 한타 교전에서 가장 중요한 첫 킬 변수가 강제로 2.5초간 차단된다는 점, 그리고 포커싱해야 할 핵심 딜러가 이 아이템을 두르고 있다면 얘기가 달라진다는 점들에서 꽤나 골치 아프다. 특히 딸피인 대상에게 진입하는 타이밍에 존야를 켜버리면 마스터 이는 일파 스트라이크(Q)의 딜이 씹히고 궁극기 유효 시간만 낭비하게 되며, 비에고 역시 궁극기(R) 진입이 무위로 돌아가며 덩그러니 노출되는 뼈아픈 상황이 연출된다.


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