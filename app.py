import streamlit as st

st.set_page_config(page_title="LOL Counter")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
    .center-wrap {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 60vh;
        gap: 16px;
    }
    .main-text {
        font-size: 26px;
        font-weight: 700;
        color: #2d3748;
        text-align: center;
    }
    .link-text {
        font-size: 20px;
        font-weight: 700;
        color: #ff7b00;
        text-decoration: underline;
    }
    .link-text:hover {
        color: #cc6200;
    }
    </style>
    <div class="center-wrap">
        <div class="main-text">주소가 변경되었습니다</div>
        <a class="link-text" href="https://vschamp.lol" target="_blank">vschamp.lol</a>
    </div>
    """,
    unsafe_allow_html=True,
)