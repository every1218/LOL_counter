import streamlit as st
import json
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
# (참고: Streamlit Community Cloud에 배포할 땐 .env 대신 Secrets를 써야 함)
load_dotenv()

# 데이터 로드 함수 (캐싱 사용)
@st.cache_data
def load_champion_data(file_path):
    """JSONL 파일에서 챔피언 데이터를 로드합니다."""
    # ⭐️ 딕셔너리로 로드/인덱싱하는 게 훨씬 빠름!
    champion_dict = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                data = json.loads(line)
                # 챔피언 이름을 키로, 데이터를 값으로 저장
                champion_dict[data['champion']] = data
                
                # ⭐️ 'aliases' 배열의 각 별칭도 같은 데이터를 가리키도록 키로 추가
                for alias in data.get('aliases', []):
                    if alias:
                        champion_dict[alias] = data
                    
    except (FileNotFoundError, json.JSONDecodeError) as e:
        st.error(f"오류: '{file_path}' 파일을 읽을 수 없습니다. ({e})")
        return {} # 리스트 대신 빈 딕셔너리 반환
        
    return champion_dict


def format_hard_counters(counters):
    """하드 카운터 목록의 형식을 지정합니다."""
    # counters가 리스트가 아니거나 비어있으면 빈 문자열 반환
    if not isinstance(counters, list) or not counters:
        return "정보 없음"
    return "\n".join([f"  - **{counter.get('name', 'N/A')}**: {counter.get('reason', 'N/A')}" for counter in counters])

def format_general_counters(counters):
    """일반 카운터 목록의 형식을 지정합니다."""
    if not isinstance(counters, list) or not counters:
        return "정보 없음"
    return ", ".join(counters)

def render_combo_counters(combos):
    """조합 카운터를 시각적으로 렌더링합니다. (& 기준으로 원딜/서포터 구분)"""
    if not isinstance(combos, list) or not combos:
        return

    st.markdown("### 🔗 조합 카운터")
    for combo in combos:
        parts = combo.split("&")
        if len(parts) == 2:
            left = parts[0].strip()   # & 앞: 원딜
            right = parts[1].strip()  # & 뒤: 서포터
            st.markdown(
                f"<span style='color:#7ecfff'>🗡️ **{left}**</span>"
                f"<span style='color:#888'> + </span>"
                f"<span style='color:#c9a0ff'>🛡️ **{right}**</span>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(f"- {combo}")

def main():
    """Streamlit 웹 앱의 메인 함수입니다."""
    st.title("👑 LOL 챔피언 카운터 조회 👑") # AI 챗봇이 아니므로 제목 변경

    # 데이터 로드 (딕셔너리 형태로)
    champion_data_store = load_champion_data('champ.jsonl')

    if not champion_data_store:
        st.warning("챔피언 데이터가 없습니다. 'champ.jsonl' 파일을 확인해주세요.")
        return

    # 사용자 입력 (엔터키 또는 버튼 클릭 모두 동작)
    with st.form("search_form"):
        champion_name_query = st.text_input("카운터 정보를 알고 싶은 챔피언 이름을 입력하세요:", "")
        submitted = st.form_submit_button("조회하기")

    if submitted:
        if champion_name_query:
            
            # ⭐️ 딕셔너리에서 데이터 조회 (반복문 대신 .get() 사용)
            found_data = champion_data_store.get(champion_name_query)

            if not found_data:
                st.error(f"'{champion_name_query}'에 대한 데이터를 찾을 수 없습니다. 챔피언 이름(별칭 포함)을 다시 확인해주세요.")
                return

            # ⭐️ LLM 스피너 문구 변경
            with st.spinner('챔피언 카운터 정보를 조회 중입니다...'):
                
                # 1. 데이터 포맷팅
                hard_counters_str = format_hard_counters(found_data.get('hard_counters'))
                general_counters_str = format_general_counters(found_data.get('general_counters'))
                combo_counters = found_data.get('combo_counters', [])

                # 2. 결과 출력
                st.markdown("---")
                st.subheader(f"📜 {found_data['champion']} 카운터 조회 결과")

                # 조합 카운터 (있을 때만 표시)
                if combo_counters:
                    render_combo_counters(combo_counters)
                    st.markdown("---")

                # 하드 카운터
                st.markdown("### 💀 하드 카운터")
                st.markdown(hard_counters_str)

                st.markdown("---")

                # 일반 카운터
                st.markdown("### 🔥 일반 카운터")
                st.markdown(general_counters_str)
                
        else:
            st.warning("챔피언 이름을 입력해주세요.")

if __name__ == "__main__":
    main()