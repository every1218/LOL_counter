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

일라오이 : 몇년만에 LCK에서 일라오이가 나왔을 정도로(26.04.26 DK vs DNS) 라인전의 최악 하드 카운터. 레넥톤 입장에서는 초반에 솔킬을 여러 번 따두고 갱도 불러서 아예 불구로 만들어 버리는 게 아닌 이상 혼자 이기는 건 거의 불가능하다. 돌진하면서 머리를 들이미는 레넥톤 특성상 일라오이의 영혼의 시험(E)각을 매우 쉽게 내주고 또 근접으로 싸우는 챔이라서 영혼에 끌렸을 때 손해도 더욱 크다. 그래도 초반 라인전은 레넥의 힘이 강하고 일라오이는 꽤 약해서 리드도 어느 정도는 가능하다. 근데 가장 큰 문제는 라인전 중반부터는 이런 식으로도 이길각이 아예 사라진다는 것, 레넥의 장기인 궁 체급도 일라오이의 궁 앞에는 한없이 초라해지고, 시간이 지날수록 일라오이의 E쿨이 줄어들고 맞혔을 때의 리턴도 더 커지는데 레넥톤의 폭딜은 일라오이가 방템 몇 개 적당히 둘러주면 잘 박히지도 않는다. 들어가도 손해를 보고 안 들어가도 계속 촉수를 맞고 영혼 끌려다가 두들겨 맞는 딜레마가 계속된다는 것. 시간이 지날수록 라인전에서 버틸 방법은 타워 허깅하면서 일라가 E를 던질 때마다 E로 피하는 거 빼고는 없어진다. 갱을 부르자니 일라오이는 궁이 있으면 오히려 다인전을 좋아하는 챔프라 역으로 잡아먹힐 가능성이 큰 것도 문제. 후반 한타 영향력은 일라오이가 촉수 사전 작업을 하지 않았다면 크게 밀리지는 않지만, 몸을 들이대서 싸우는 레넥톤의 특성상 일라오이의 E 셔틀이 되어 다인궁 재료가 되면서 그대로 한타가 폭망할 수 있기에 매우 거슬린다. 물론 후반 사이드는 상대도 안 되지만 한타는 레넥톤 입장에서도 할만 하기에 최대한 오브젝트 주변 촉수를 지워 일라오이가 힘을 못 쓰게 만들어주자.


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