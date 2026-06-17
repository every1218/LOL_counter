import re

with open('lolcounter.py', encoding='utf-8') as f:
    content = f.read()

new_func = r'''def render_hard_counters(counters):
    """하드 카운터 목록을 이미지 그리드 + 하단 정보 패널 형식 HTML로 렌더링합니다."""
    if not isinstance(counters, list) or not counters:
        st.markdown("<p style='color:#a0aec0;'>정보 없음</p>", unsafe_allow_html=True)
        return

    items_html = ""
    for counter in counters:
        name = counter.get('name', 'N/A')
        # JS 속성값 안전 처리
        reason_safe = counter.get('reason', 'N/A').replace("\\", "\\\\").replace('"', "&quot;")
        name_safe   = name.replace("\\", "\\\\").replace('"', "&quot;")
        img_path = find_image_file(name)

        if img_path:
            img_src = get_image_base64_src(img_path)
            if img_src:
                image_element = (
                    f'<img src="{img_src}" class="hard-counter-img" alt="{name_safe}" '
                    f'data-name="{name_safe}" data-reason="{reason_safe}" />'
                )
            else:
                image_element = (
                    f'<div class="hard-counter-fallback" '
                    f'data-name="{name_safe}" data-reason="{reason_safe}">{name}</div>'
                )
        else:
            image_element = (
                f'<div class="hard-counter-fallback" '
                f'data-name="{name_safe}" data-reason="{reason_safe}">{name}</div>'
            )

        items_html += f'''
        <div class="hc-card" data-name="{name_safe}" data-reason="{reason_safe}">
            {image_element}
            <div class="hc-label">{name}</div>
        </div>
        '''

    card_rows = (len(counters) + 5) // 6
    base_height = max(160, card_rows * 140 + 40)

    full_html = f\'\'\'
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ overflow: hidden; background: transparent; font-family: "Noto Sans KR", sans-serif; }}

        .hard-counter-grid {{
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
            margin-top: 10px;
            align-items: flex-start;
        }}

        .hc-card {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 6px;
            cursor: pointer;
        }}

        .hard-counter-img {{
            width: 90px;
            height: 90px;
            border-radius: 12px;
            border: 2px solid rgba(255, 74, 74, 0.4);
            object-fit: cover;
            box-shadow: 0 4px 12px rgba(0,0,0,0.35);
            transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
            display: block;
            pointer-events: none;
        }}
        .hc-card:hover .hard-counter-img,
        .hc-card.active .hard-counter-img {{
            transform: scale(1.07);
            border-color: #ff4a4a;
            box-shadow: 0 0 18px rgba(255, 74, 74, 0.55);
        }}

        .hard-counter-fallback {{
            width: 90px;
            height: 90px;
            border-radius: 12px;
            border: 2px solid rgba(255, 74, 74, 0.4);
            background: #2a1a1a;
            color: #ff6b6b;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 13px;
            font-weight: 700;
            text-align: center;
            box-shadow: 0 4px 12px rgba(0,0,0,0.35);
            transition: border-color 0.2s ease, box-shadow 0.2s ease;
            pointer-events: none;
        }}
        .hc-card.active .hard-counter-fallback {{
            border-color: #ff4a4a;
            box-shadow: 0 0 18px rgba(255, 74, 74, 0.55);
        }}

        .hc-label {{
            font-size: 12px;
            font-weight: 600;
            color: #a0aec0;
            white-space: nowrap;
            pointer-events: none;
        }}
        .hc-card.active .hc-label {{ color: #ff6b6b; }}

        /* 하단 정보 패널 */
        .info-panel {{
            display: none;
            margin-top: 18px;
            padding: 16px 20px;
            background: rgba(255, 74, 74, 0.05);
            border: 1px solid rgba(255, 74, 74, 0.25);
            border-radius: 14px;
            animation: fadeSlide 0.2s ease;
        }}
        .info-panel.visible {{ display: block; }}

        @keyframes fadeSlide {{
            from {{ opacity: 0; transform: translateY(-6px); }}
            to   {{ opacity: 1; transform: translateY(0); }}
        }}

        .info-name {{
            font-size: 16px;
            font-weight: 700;
            color: #ff6b6b;
            margin-bottom: 8px;
        }}
        .info-reason {{
            font-size: 13.5px;
            color: #cbd5e0;
            line-height: 1.7;
        }}
    </style>

    <div class="hard-counter-grid">
        {items_html}
    </div>

    <div class="info-panel" id="infoPanel">
        <div class="info-name"   id="infoName"></div>
        <div class="info-reason" id="infoReason"></div>
    </div>

    <script>
        const cards    = document.querySelectorAll('.hc-card');
        const panel    = document.getElementById('infoPanel');
        const infoName   = document.getElementById('infoName');
        const infoReason = document.getElementById('infoReason');
        let activeCard = null;

        function pushHeight() {{
            setTimeout(function() {{
                const h = document.documentElement.scrollHeight;
                window.parent.postMessage({{type: 'streamlit:setFrameHeight', height: h + 10}}, '*');
            }}, 60);
        }}

        cards.forEach(function(card) {{
            card.addEventListener('click', function() {{
                const name   = card.getAttribute('data-name');
                const reason = card.getAttribute('data-reason');

                if (activeCard === card) {{
                    card.classList.remove('active');
                    panel.classList.remove('visible');
                    activeCard = null;
                    pushHeight();
                    return;
                }}

                if (activeCard) activeCard.classList.remove('active');
                card.classList.add('active');
                activeCard = card;

                infoName.textContent   = name;
                infoReason.textContent = reason;

                panel.classList.remove('visible');
                void panel.offsetWidth;
                panel.classList.add('visible');
                pushHeight();
            }});
        }});

        window.addEventListener('load', pushHeight);
    </script>
    \'\'\'
    components.html(full_html, height=base_height, scrolling=False)

'''

# render_hard_counters 함수 전체를 교체
pattern = r'def render_hard_counters\(counters\):.*?(?=\ndef render_general_counters)'
result = re.sub(pattern, new_func, content, flags=re.DOTALL)

if result == content:
    print("ERROR: 패턴 매칭 실패!")
else:
    with open('lolcounter.py', 'w', encoding='utf-8') as f:
        f.write(result)
    print("OK: render_hard_counters 교체 완료")
