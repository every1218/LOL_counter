"""
lolcounter.py 에서 render_counters 함수를
render_hard_counters / render_general_counters / render_hard_counter_info
세 함수로 교체하고, main() 호출도 수정합니다.
"""

NEW_FUNCTIONS = '''
def render_hard_counters(counters):
    """하드 카운터 이미지 그리드를 렌더링합니다.
    카드 클릭 시 BroadcastChannel로 이벤트를 전송해 정보패널에 표시합니다."""
    if not isinstance(counters, list) or not counters:
        st.markdown("<p style=\'color:#a0aec0;\'>정보 없음</p>", unsafe_allow_html=True)
        return

    items_html = ""
    for counter in counters:
        name       = counter.get('name', 'N/A')
        reason_raw = counter.get('reason', 'N/A')
        name_safe   = name.replace(\'"\', '&quot;')
        reason_safe = reason_raw.replace(\'"\', '&quot;')
        img_path = find_image_file(name)

        if img_path:
            img_src = get_image_base64_src(img_path)
            if img_src:
                img_el = (f\'<img src="{img_src}" class="hc-img" alt="{name_safe}" \'
                          f\'data-name="{name_safe}" data-reason="{reason_safe}" />\')
            else:
                img_el = (f\'<div class="hc-fallback" data-name="{name_safe}" \'
                          f\'data-reason="{reason_safe}">{name}</div>\')
        else:
            img_el = (f\'<div class="hc-fallback" data-name="{name_safe}" \'
                      f\'data-reason="{reason_safe}">{name}</div>\')

        items_html += f"""
        <div class="hc-card" data-name="{name_safe}" data-reason="{reason_safe}">
            {img_el}
            <div class="hc-label">{name}</div>
        </div>"""

    card_rows = max(1, (len(counters) + 5) // 6)
    height = max(110, card_rows * 100 + 20)

    full_html = f"""
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: 'Noto Sans KR', sans-serif; background: transparent; }}
        .hc-grid {{ display: flex; flex-wrap: wrap; gap: 14px; align-items: flex-start; }}
        .hc-card {{ display: flex; flex-direction: column; align-items: center; gap: 5px; cursor: pointer; }}
        .hc-img {{
            width: 68px; height: 68px; border-radius: 10px;
            border: 2px solid rgba(255,74,74,0.4); object-fit: cover;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            transition: transform .2s, border-color .2s, box-shadow .2s;
            pointer-events: none;
        }}
        .hc-card:hover .hc-img, .hc-card.active .hc-img {{
            transform: scale(1.08); border-color: #ff4a4a;
            box-shadow: 0 0 16px rgba(255,74,74,.5);
        }}
        .hc-fallback {{
            width: 68px; height: 68px; border-radius: 10px;
            border: 2px solid rgba(255,74,74,0.4); background: #2a1a1a; color: #ff6b6b;
            display: flex; align-items: center; justify-content: center;
            font-size: 12px; font-weight: 700; text-align: center; pointer-events: none;
        }}
        .hc-card.active .hc-fallback {{ border-color: #ff4a4a; box-shadow: 0 0 16px rgba(255,74,74,.5); }}
        .hc-label {{ font-size: 11px; font-weight: 600; color: #718096; white-space: nowrap; pointer-events: none; }}
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
        st.markdown("<p style=\'color:#a0aec0;\'>정보 없음</p>", unsafe_allow_html=True)
        return

    items_html = ""
    for name in counters:
        img_path = find_image_file(name)
        if img_path:
            img_src = get_image_base64_src(img_path)
            if img_src:
                img_el = f\'<img src="{img_src}" class="gc-img" alt="{name}" />\'
            else:
                img_el = f\'<div class="gc-fallback">{name}</div>\'
        else:
            img_el = f\'<div class="gc-fallback">{name}</div>\'

        items_html += f"""
        <div class="gc-item">
            {img_el}
            <div class="gc-name">{name}</div>
        </div>"""

    gc_rows = max(1, (len(counters) + 7) // 8)
    height  = max(130, gc_rows * 100 + 80)

    full_html = f"""
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: 'Noto Sans KR', sans-serif; background: transparent; }}
        .gc-grid {{ display: flex; flex-wrap: wrap; gap: 6px; align-items: flex-start; }}
        .gc-item {{
            background: rgba(255,255,255,0.02); border: 1px solid rgba(0,0,0,0.08);
            border-radius: 10px; padding: 6px; width: 60px; text-align: center; transition: all .2s;
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
    </style>
    <div class="gc-grid">{items_html}</div>
    """
    components.html(full_html, height=height, scrolling=False)


def render_hard_counter_info():
    """하드카운터 클릭 시 BroadcastChannel을 통해 정보를 수신해 표시하는 패널입니다.
    일반카운터 아래에 항상 렌더링되며, 선택된 카운터가 없으면 안내 문구를 보여줍니다."""
    full_html = """
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Noto Sans KR', sans-serif; background: transparent; }
        .hint { color: #a0aec0; font-size: 13px; padding: 10px 0; }
        .info-panel {
            display: none; padding: 16px 20px;
            background: rgba(255,74,74,0.05);
            border: 1px solid rgba(255,74,74,0.25);
            border-radius: 14px; animation: fadeSlide .2s ease;
        }
        .info-panel.visible { display: block; }
        @keyframes fadeSlide {
            from { opacity:0; transform:translateY(-6px); }
            to   { opacity:1; transform:translateY(0); }
        }
        .info-name { font-size: 16px; font-weight: 700; color: #c53030; margin-bottom: 8px; }
        .info-reason { font-size: 13.5px; color: #2d3748; line-height: 1.7; }
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
    components.html(full_html, height=220, scrolling=False)
'''

# main() 에서 render_counters 호출을 세 함수 호출로 교체
OLD_MAIN_BLOCK = """                # 하드카운터 + 일반카운터 통합 렌더링 (정보패널은 일반카운터 아래)
                render_counters(
                    found_data.get('hard_counters'),
                    found_data.get('general_counters')
                )"""

NEW_MAIN_BLOCK = """                # 하드 카운터
                st.markdown("### 💀 하드 카운터")
                render_hard_counters(found_data.get('hard_counters'))

                st.markdown("---")

                # 일반 카운터
                st.markdown("### 🔥 일반 카운터")
                render_general_counters(found_data.get('general_counters'))

                # 하드카운터 설명 패널 (일반카운터 아래)
                render_hard_counter_info()"""

OLD_MAIN_BLOCK2 = """                # 하드 카운터
                st.markdown("### 💀 하드 카운터")
                render_hard_counters(found_data.get('hard_counters'))

                st.markdown("---")

                # 일반 카운터
                st.markdown("### 🔥 일반 카운터")
                render_general_counters(found_data.get('general_counters'))"""

with open('lolcounter.py', encoding='utf-8') as f:
    content = f.read()

# 1) render_counters 함수 전체를 세 함수로 교체
OLD_FN_START = 'def render_counters(hard_counters, general_counters):'
OLD_FN_END_MARKER = '\ndef render_combo_counters('

start = content.find(OLD_FN_START)
end   = content.find(OLD_FN_END_MARKER, start)

if start == -1:
    print("ERROR: render_counters not found")
elif end == -1:
    print("ERROR: end marker not found")
else:
    content = content[:start] + NEW_FUNCTIONS.lstrip('\n') + content[end:]
    print(f"Replaced render_counters ({end-start} chars → {len(NEW_FUNCTIONS)} chars)")

# 2) main() 의 호출부 교체
for old, new in [(OLD_MAIN_BLOCK, NEW_MAIN_BLOCK), (OLD_MAIN_BLOCK2, NEW_MAIN_BLOCK)]:
    if old in content:
        content = content.replace(old, new, 1)
        print("Fixed main() render calls")
        break
else:
    print("WARNING: main() block not found - check manually")

with open('lolcounter.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Done. Lines:", content.count('\n'))
