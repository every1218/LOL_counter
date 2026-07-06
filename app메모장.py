import streamlit as st
import streamlit.components.v1 as components
import json
import os
import base64
from dotenv import load_dotenv

# 실행명령어
# poetry run streamlit run app.py

# .env 파일에서 환경 변수 로드
load_dotenv()

# 데이터 로드 함수 (캐싱 사용)
@st.cache_data
def load_champion_data(file_path):
    """JSONL 파일에서 챔피언 데이터를 로드합니다."""
    champion_dict = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                data = json.loads(line)
                # 챔피언 이름을 키로, 데이터를 값으로 저장
                champion_dict[data['champion']] = data
                
                # 'aliases' 배열의 각 별칭도 같은 데이터를 가리키도록 키로 추가
                for alias in data.get('aliases', []):
                    if alias:
                        champion_dict[alias] = data
                    
    except (FileNotFoundError, json.JSONDecodeError) as e:
        st.error(f"오류: '{file_path}' 파일을 읽을 수 없습니다. ({e})")
        return {}
        
    return champion_dict


def find_image_file(champ_name):
    """챔피언 이름에 해당하는 이미지 파일 경로를 찾습니다. 공백이나 약어 등의 예외 처리를 포함합니다."""
    name = champ_name.strip()
    
    # 1. 정확히 일치하는 파일명 확인
    path = os.path.join("champ_img", f"{name}.png")
    if os.path.exists(path):
        return path
        
    # 2. 공백 제거 후 일치하는 파일명 확인
    name_no_space = name.replace(" ", "")
    path = os.path.join("champ_img", f"{name_no_space}.png")
    if os.path.exists(path):
        return path
        
    # 3. 폴더 내 이미지 파일들과 유사도(포함 여부) 비교 매칭
    if os.path.exists("champ_img"):
        for filename in os.listdir("champ_img"):
            if filename.endswith(".png"):
                img_name = filename[:-4]
                img_name_clean = img_name.replace(" ", "")
                if img_name_clean in name_no_space or name_no_space in img_name_clean:
                    return os.path.join("champ_img", filename)
                    
    return None


def get_image_base64_src(image_path):
    """이미지 파일을 Base64로 인코딩하여 HTML src에 쓸 수 있는 문자열로 반환합니다."""
    try:
        with open(image_path, "rb") as f:
            img_data = f.read()
            base64_data = base64.b64encode(img_data).decode('utf-8')
            return f"data:image/png;base64,{base64_data}"
    except Exception:
        return None


def render_hard_counters(counters):
    """하드 카운터 이미지 그리드를 렌더링합니다.
    카드 클릭 시 BroadcastChannel로 이벤트를 전송해 정보패널에 표시합니다."""
    if not isinstance(counters, list) or not counters:
        st.markdown("<p style='color:#a0aec0;'>정보 없음</p>", unsafe_allow_html=True)
        return

    items_html = ""
    for counter in counters:
        name       = counter.get('name', 'N/A')
        reason_raw = counter.get('reason', 'N/A')
        name_safe   = name.replace('"', '&quot;')
        reason_safe = reason_raw.replace('"', '&quot;')
        img_path = find_image_file(name)

        if img_path:
            img_src = get_image_base64_src(img_path)
            if img_src:
                img_el = (f'<img src="{img_src}" class="hc-img" alt="{name_safe}" '
                          f'data-name="{name_safe}" data-reason="{reason_safe}" />')
            else:
                img_el = (f'<div class="hc-fallback" data-name="{name_safe}" '
                          f'data-reason="{reason_safe}">{name}</div>')
        else:
            img_el = (f'<div class="hc-fallback" data-name="{name_safe}" '
                      f'data-reason="{reason_safe}">{name}</div>')

        items_html += f"""
        <div class="hc-card" data-name="{name_safe}" data-reason="{reason_safe}">
            {img_el}
            <div class="hc-label">{name}</div>
        </div>"""

    card_rows = max(1, (len(counters) + 7) // 8)
    height = max(85, card_rows * 75)

    full_html = f"""
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: 'Noto Sans KR', sans-serif; background: transparent; }}
        .hc-grid {{ display: flex; flex-wrap: wrap; gap: 14px; align-items: flex-start; }}
        .hc-card {{ display: flex; flex-direction: column; align-items: center; gap: 5px; cursor: pointer; }}
        .hc-img {{
            width: 56px; height: 56px; border-radius: 9px;
            border: 2px solid rgba(255,74,74,0.4); object-fit: cover;
            box-shadow: 0 3px 10px rgba(0,0,0,0.3);
            transition: transform .2s, border-color .2s, box-shadow .2s;
            pointer-events: none;
        }}
        .hc-card:hover .hc-img, .hc-card.active .hc-img {{
            transform: scale(1.08); border-color: #ff4a4a;
            box-shadow: 0 0 16px rgba(255,74,74,.5);
        }}
        .hc-fallback {{
            width: 56px; height: 56px; border-radius: 9px;
            border: 2px solid rgba(255,74,74,0.4); background: #2a1a1a; color: #ff6b6b;
            display: flex; align-items: center; justify-content: center;
            font-size: 11px; font-weight: 700; text-align: center; pointer-events: none;
        }}
        .hc-card.active .hc-fallback {{ border-color: #ff4a4a; box-shadow: 0 0 16px rgba(255,74,74,.5); }}
        .hc-label {{
            font-size: 11px; font-weight: 600; color: #718096;
            white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
            max-width: 56px; pointer-events: none;
        }}
        .hc-card.active .hc-label {{ color: #ff4a4a; }}

    </style>
    <div class="hc-grid">{items_html}</div>
    <script>
        const bc = new BroadcastChannel('lol_hc_channel');
        const cards = document.querySelectorAll('.hc-card');
        let activeCard = null;
        cards.forEach(function(card) {{
            card.addEventListener('click', function() {{
                const name   = card.getAttribute('data-name');
                const reason = card.getAttribute('data-reason');
                if (activeCard === card) {{
                    card.classList.remove('active');
                    activeCard = null;
                    bc.postMessage({{type: 'clear'}});
                    return;
                }}
                if (activeCard) activeCard.classList.remove('active');
                card.classList.add('active');
                activeCard = card;
                bc.postMessage({{type: 'show', name: name, reason: reason}});
            }});
        }});
    </script>
    """
    components.html(full_html, height=height, scrolling=False)


def render_general_counters(counters):
    """일반 카운터 이미지 그리드를 렌더링합니다."""
    if not isinstance(counters, list) or not counters:
        st.markdown("<p style='color:#a0aec0;'>정보 없음</p>", unsafe_allow_html=True)
        return

    items_html = ""
    for name in counters:
        img_path = find_image_file(name)
        if img_path:
            img_src = get_image_base64_src(img_path)
            if img_src:
                img_el = f'<img src="{img_src}" class="gc-img" alt="{name}" />'
            else:
                img_el = f'<div class="gc-fallback">{name}</div>'
        else:
            img_el = f'<div class="gc-fallback">{name}</div>'

        items_html += f"""
        <div class="gc-item">
            {img_el}
            <div class="gc-name">{name}</div>
            <div class="gc-tooltip">{name}</div>
        </div>"""

    gc_rows = max(1, (len(counters) + 9) // 10)
    height  = max(110, gc_rows * 82 + 20)

    full_html = f"""
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: 'Noto Sans KR', sans-serif; background: transparent; }}
        .gc-grid {{ display: flex; flex-wrap: wrap; gap: 6px; align-items: flex-start; }}
        .gc-item {{
            background: rgba(255,255,255,0.02); border: 1px solid rgba(0,0,0,0.08);
            border-radius: 10px; padding: 6px; width: 60px; text-align: center; transition: all .2s;
            position: relative;
        }}
        .gc-item:hover {{ background: rgba(0,0,0,0.04); transform: translateY(-2px); }}
        .gc-img {{
            width: 46px; height: 46px; border-radius: 50%;
            border: 2px solid #cbd5e0; object-fit: cover; margin: 0 auto; display: block;
        }}
        .gc-fallback {{
            width: 46px; height: 46px; border-radius: 50%; border: 2px solid #cbd5e0;
            background: #edf2f7; color: #4a5568;
            display: flex; align-items: center; justify-content: center;
            font-size: 10px; font-weight: 700; margin: 0 auto;
        }}
        .gc-name {{
            font-size: 11px; font-weight: 600; color: #718096;
            margin-top: 6px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
        }}
        .gc-tooltip {{
            visibility: hidden; opacity: 0;
            position: absolute; bottom: -22px; left: 50%; transform: translateX(-50%);
            background: rgba(20,20,30,0.92); color: #e2e8f0;
            font-size: 10px; font-weight: 600; white-space: nowrap;
            padding: 3px 7px; border-radius: 5px;
            pointer-events: none; z-index: 9999;
            transition: opacity .18s ease;
            border: 1px solid rgba(255,255,255,0.15);
        }}
        .gc-item:hover .gc-tooltip {{ visibility: visible; opacity: 1; }}
    </style>
    <div class="gc-grid">{items_html}</div>
    """
    components.html(full_html, height=height, scrolling=False)


def render_hard_counter_info(champ_name: str = ""):
    """하드카운터 클릭 시 BroadcastChannel을 통해 정보를 수신해 표시하는 패널입니다.
    champ_name이 바뀌면 iframe이 재생성되어 패널이 자동으로 초기화됩니다."""
    full_html = (
        f"<!-- champ: {champ_name} -->\n"
        """
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Noto Sans KR', sans-serif; background: transparent; }
        .hint { color: #a0aec0; font-size: 13px; padding: 10px 0; }
        .info-panel {
            display: none; padding: 16px 20px;
            background: rgba(255,74,74,0.05);
            border: 1px solid rgba(255,74,74,0.25);
            border-radius: 14px; animation: fadeSlide .2s ease;
            word-break: keep-all; word-wrap: break-word;
        }
        .info-panel.visible { display: block; }
        @keyframes fadeSlide {
            from { opacity:0; transform:translateY(-6px); }
            to   { opacity:1; transform:translateY(0); }
        }
        .info-name { font-size: 16px; font-weight: 700; color: #c53030; margin-bottom: 8px; }
        .info-reason { font-size: 13.5px; color: #2d3748; line-height: 1.8; }
    </style>
    <div class="hint" id="hint">💡 위의 하드 카운터를 클릭하면 설명이 표시됩니다.</div>
    <div class="info-panel" id="infoPanel">
        <div class="info-name"   id="infoName"></div>
        <div class="info-reason" id="infoReason"></div>
    </div>
    <script>
        const bc       = new BroadcastChannel('lol_hc_channel');
        const hint     = document.getElementById('hint');
        const panel    = document.getElementById('infoPanel');
        const infoName   = document.getElementById('infoName');
        const infoReason = document.getElementById('infoReason');
        // 새 챔피언 로드 시 이전 상태 초기화
        bc.postMessage({type: 'clear'});
        bc.onmessage = function(e) {
            if (e.data.type === 'show') {
                hint.style.display = 'none';
                infoName.textContent   = e.data.name;
                infoReason.textContent = e.data.reason;
                panel.classList.remove('visible');
                void panel.offsetWidth;
                panel.classList.add('visible');
            } else if (e.data.type === 'clear') {
                panel.classList.remove('visible');
                hint.style.display = 'block';
            }
        };
    </script>
    """
    )
    components.html(full_html, height=500, scrolling=False)

def render_combo_counters(combos):
    """조합 카운터를 이미지 카드 방식으로 렌더링합니다.
    각 카드에 두 챔피언 아이콘을 나란히 표시하고 하단에 이름을 표시합니다."""
    if not isinstance(combos, list) or not combos:
        return

    st.markdown("## 🔗 추천 카운터 조합")

    cards_html = ""
    for combo in combos:
        parts = [p.strip() for p in combo.split("&")]
        if len(parts) != 2:
            continue
        left_name, right_name = parts[0], parts[1]

        def champ_img_el(name):
            img_path = find_image_file(name)
            if img_path:
                img_src = get_image_base64_src(img_path)
                if img_src:
                    return f'<img src="{img_src}" class="cc-img" alt="{name}" />'
            return f'<div class="cc-fallback">{name[:2]}</div>'

        left_el  = champ_img_el(left_name)
        right_el = champ_img_el(right_name)

        cards_html += f"""
        <div class="cc-card">
            <div class="cc-imgs">
                {left_el}
                <div class="cc-plus">+</div>
                {right_el}
            </div>
            <div class="cc-label">{left_name} &amp; {right_name}</div>
        </div>"""

    rows = max(1, (len(combos) + 4) // 5)
    height = max(110, rows * 110 + 10)

    full_html = f"""
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: 'Noto Sans KR', sans-serif; background: transparent; }}
        .cc-grid {{
            display: flex; flex-wrap: wrap; gap: 6px; align-items: flex-start;
        }}
        .cc-card {{
            background: rgba(255,255,255,0.02);
            border: 1px solid rgba(0,0,0,0.08);
            border-radius: 10px;
            padding: 8px 8px 6px;
            text-align: center;
            width: 130px;
            transition: all .2s;
            cursor: default;
        }}
        .cc-card:hover {{
            background: rgba(0,0,0,0.04);
            transform: translateY(-2px);
        }}
        .cc-imgs {{
            display: flex; align-items: center; justify-content: center; gap: 3px;
        }}
        .cc-img {{
            width: 46px; height: 46px; border-radius: 50%;
            border: 2px solid #cbd5e0; object-fit: cover;
        }}
        .cc-fallback {{
            width: 46px; height: 46px; border-radius: 50%;
            border: 2px solid #cbd5e0;
            background: #edf2f7; color: #4a5568;
            display: flex; align-items: center; justify-content: center;
            font-size: 10px; font-weight: 700;
        }}
        .cc-plus {{
            font-size: 12px; font-weight: 600;
            color: #a0aec0;
            padding: 0 1px;
        }}
        .cc-label {{
            margin-top: 6px;
            font-size: 11px; font-weight: 600;
            color: #718096;
            white-space: nowrap;
            overflow: hidden; text-overflow: ellipsis;
        }}
    </style>
    <div class="cc-grid">
        {cards_html}
    </div>
    """
    components.html(full_html, height=height, scrolling=False)





def inject_custom_css():
    """앱에 프리미엄 테마 및 스타일을 적용하기 위한 CSS를 주입합니다."""
    custom_css = """
    <style>
    /* 브라우저 다크모드 강제 비활성화 */
    :root {
        color-scheme: light only;
    }
    html {
        color-scheme: light only;
        forced-color-adjust: none;
    }
    /* Streamlit 내부 컨테이너도 라이트 모드 강제 */
    .stApp, .stApp > *, [data-testid="stAppViewContainer"],
    [data-testid="stHeader"], [data-testid="stSidebar"],
    [data-testid="stMain"], [data-testid="stBottom"] {
        color-scheme: light only !important;
    }

    /* 폰트 및 기본 디자인 설정 */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Noto+Sans+KR:wght@300;400;700&display=swap');
    
    
    html, body, [class*="css"], .stMarkdown {
        font-family: 'Outfit', 'Noto Sans KR', sans-serif;
    }
    
    /* 제목 스타일 커스텀 */
    .app-header {
        text-align: center;
        padding: 2.5rem 0;
        margin-bottom: 2rem;
        background: linear-gradient(135deg, #181824 0%, #0a0a0f 100%);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    
    .app-title {
        font-family: 'Outfit', 'Noto Sans KR', sans-serif;
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #ff7b00, #ff007b, #9d00ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .app-subtitle {
        font-family: 'Outfit', 'Noto Sans KR', sans-serif;
        font-size: 1rem;
        color: #8888a0;
    }
    
    
    /* 하드 카운터 그리드 및 스타일 */
    .hard-counter-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 20px;
        margin-top: 15px;
    }
    
    .hard-counter-wrapper {
        background: rgba(255, 74, 74, 0.03);
        border: 1px solid rgba(255, 74, 74, 0.15);
        border-radius: 16px;
        padding: 10px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        display: inline-block;
    }
    
    .hard-counter-wrapper:hover {
        background: rgba(255, 74, 74, 0.06);
        border-color: rgba(255, 74, 74, 0.35);
        box-shadow: 0 6px 20px rgba(255, 74, 74, 0.15);
        transform: translateY(-2px);
    }
    
    .hard-counter-details {
        width: 100%;
    }
    
    .hard-counter-summary {
        list-style: none;
        outline: none;
        cursor: pointer;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    
    .hard-counter-summary::-webkit-details-marker {
        display: none;
    }
    
    .hard-counter-img {
        width: 90px;
        height: 90px;
        border-radius: 12px;
        border: 2px solid #ff4a4a;
        object-fit: cover;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        transition: transform 0.2s ease;
    }
    
    .hard-counter-img:hover {
        transform: scale(1.05);
    }
    
    .hard-counter-fallback {
        width: 90px;
        height: 90px;
        border-radius: 12px;
        border: 2px solid #ff4a4a;
        background: #2a1a1a;
        color: #ff6b6b;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 14px;
        font-weight: 700;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        transition: transform 0.2s ease;
    }
    
    .hard-counter-fallback:hover {
        transform: scale(1.05);
    }
    
    .hard-counter-content {
        margin-top: 12px;
        padding-top: 12px;
        border-top: 1px dashed rgba(255, 74, 74, 0.25);
        max-width: 320px;
        color: #e2e8f0;
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 13.5px;
        line-height: 1.6;
    }
    
    .hard-counter-name {
        font-size: 15px;
        font-weight: 700;
        color: #ff6b6b;
        margin-bottom: 6px;
    }
    
    .hard-counter-reason {
        color: #cbd5e0;
        text-align: justify;
    }
    
    /* 일반 카운터 그리드 및 스타일 */
    .general-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 16px;
        margin-top: 15px;
    }
    
    .general-item {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 10px;
        width: 84px;
        text-align: center;
        transition: all 0.2s ease;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }
    
    .general-item:hover {
        background: rgba(255, 255, 255, 0.06);
        border-color: rgba(255, 255, 255, 0.2);
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(0,0,0,0.3);
    }
    
    .general-img {
        width: 64px;
        height: 64px;
        border-radius: 50%;
        border: 2px solid #4a5568;
        object-fit: cover;
        margin: 0 auto;
        display: block;
        box-shadow: 0 3px 8px rgba(0,0,0,0.3);
    }
    
    .general-fallback {
        width: 64px;
        height: 64px;
        border-radius: 50%;
        border: 2px solid #4a5568;
        background: #2d3748;
        color: #e2e8f0;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 12px;
        font-weight: 700;
        text-align: center;
        margin: 0 auto;
        box-shadow: 0 3px 8px rgba(0,0,0,0.3);
    }
    
    .general-name {
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 12px;
        font-weight: 600;
        color: #a0aec0;
        margin-top: 8px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    /* 타이틀(표시용 h3) 크게, 섹션헤더(표시용 h2) 작게 */
    h2 {
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        margin-bottom: 0.3rem !important;
    }
    h3 {
        font-size: 1.45rem !important;
        font-weight: 700 !important;
        margin-bottom: 0.5rem !important;
        text-align: center !important;
    }

    /* 입력 폼: 테두리 제거 (컨테이너가 패널 역할) */
    div[data-testid="stForm"] {
        border: none !important;
        padding: 0 !important;
        box-shadow: none !important;
        background: transparent !important;
    }
    div[data-testid="stForm"] .stTextInput input {
        font-size: 14px !important;
        padding: 6px 10px !important;
    }
    div[data-testid="stForm"] .stTextInput label {
        font-size: 13px !important;
    }
    div[data-testid="stForm"] .stFormSubmitButton button {
        font-size: 13px !important;
        padding: 4px 16px !important;
    }
    /* 헤더 hover 앵커 링크 아이콘 완전 숨김 */
    h1 a, h2 a, h3 a, h4 a, h5 a, h6 a,
    .stMarkdown h1 a, .stMarkdown h2 a, .stMarkdown h3 a {
        display: none !important;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


def main():
    """Streamlit 웹 앱의 메인 함수입니다. <- 렉걸려서 폐기""" 
    st.set_page_config(
        page_title="롤 카운터 조회",
        # page_icon="champ_img/카운터조회.png",
    #     layout="centered",
    )
    inject_custom_css()

    # 모바일 접속 시 안내 메시지 (CSS 미디어 쿼리로 모바일에서만 표시)
    st.markdown(
        """
        <style>
        .mobile-warning {
            display: none;
        }
        @media (max-width: 768px) {
            .mobile-warning {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                border: 1px solid rgba(200, 155, 60, 0.5);
                border-radius: 12px;
                padding: 20px;
                margin: 10px 0 20px 0;
                color: #c89b3c;
                font-size: 16px;
                font-weight: 600;
                text-align: center;
                box-shadow: 0 4px 20px rgba(200, 155, 60, 0.15);
            }
            .mobile-warning .icon {
                font-size: 24px;
                flex-shrink: 0;
            }
        }
        </style>
        <div class="mobile-warning">
            <span class="icon">🖥️</span>
            <span>모바일은 데스크톱 모드를 사용해주세요</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 데이터 로드 (딕셔너리 형태로)
    champion_data_store = load_champion_data('champ.jsonl')

    if not champion_data_store:
        st.warning("챔피언 데이터가 없습니다. 'champ.jsonl' 파일을 확인해주세요.")
        return

    # 세션 상태로 현재 챔피언 이미지 경로 관리
    if 'champ_img_src' not in st.session_state:
        default_img_path = os.path.join('champ_img', '초기이미지창.png')
        st.session_state.champ_img_src = get_image_base64_src(default_img_path)

    # 이미지 + 검색폼을 하나의 패널(border=True 컨테이너) 안에 배치
    with st.container(border=True):
        img_col, form_col = st.columns([1, 3])

        with img_col:
            if st.session_state.champ_img_src:
                st.markdown(
                    f"<img src='{st.session_state.champ_img_src}' "
                    f"style='width:110px;height:110px;object-fit:cover;"
                    f"border-radius:14px;border:2px solid rgba(255,255,255,0.15);"
                    f"box-shadow:0 4px 16px rgba(0,0,0,0.4);display:block;margin:auto;' />",
                    unsafe_allow_html=True
                )

        with form_col:
            with st.form("search_form"):
                champion_name_query = st.text_input("카운터 정보를 알고 싶은 챔피언 이름을 입력하세요:", "")
                submitted = st.form_submit_button("조회하기")

    if submitted:
        if champion_name_query:
            
            # 딕셔너리에서 데이터 조회
            found_data = champion_data_store.get(champion_name_query)

            if not found_data:
                st.error(f"'{champion_name_query}'에 대한 데이터를 찾을 수 없습니다. 챔피언 이름(별칭 포함)을 다시 확인해주세요.")
            else:
                # 챔피언 이미지 업데이트 후 세션에 결과 저장 → 리런으로 이미지 즉시 반영
                champ_real_name = found_data.get('champion', champion_name_query)
                img_path = find_image_file(champ_real_name)
                if img_path:
                    st.session_state.champ_img_src = get_image_base64_src(img_path)
                else:
                    default_img_path = os.path.join('champ_img', '초기이미지창.png')
                    st.session_state.champ_img_src = get_image_base64_src(default_img_path)

                st.session_state.found_data = found_data
                st.rerun()

        else:
            st.warning("챔피언 이름을 입력해주세요.")

    # 세션에 저장된 조회 결과가 있으면 카운터 섹션 렌더링
    if st.session_state.get('found_data'):
        found_data = st.session_state.found_data
        combo_counters = found_data.get('combo_counters', [])

        # 하드 카운터
        st.markdown("## 💀 하드 카운터")
        render_hard_counters(found_data.get('hard_counters'))

        st.markdown("---")

        # 일반 카운터
        st.markdown("## 🔥 일반 카운터")
        render_general_counters(found_data.get('general_counters'))

        # 추천 카운터 (있을 때만 표시, 일반카운터 아래)
        if combo_counters:
            st.markdown("---")
            render_combo_counters(combo_counters)

        st.markdown("---")

        # 하드카운터 설명 패널 (챔피언 이름 전달 → 새 조회 시 iframe 재생성 + 자동 초기화)
        render_hard_counter_info(champ_name=found_data.get('champion', ''))

if __name__ == "__main__":
    main()
