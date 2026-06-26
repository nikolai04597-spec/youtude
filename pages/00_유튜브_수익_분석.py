import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import pandas as pd
from matplotlib import font_manager

# ==========================
# 페이지 설정
# ==========================
st.set_page_config(
    page_title="유튜브 수익 분석기",
    layout="wide"
)

# ==========================
# 한글 폰트 설정
# ==========================
font_path = "NanumGothic.ttf"

font_manager.fontManager.addfont(font_path)

font_name = fm.FontProperties(
    fname=font_path
).get_name()

plt.rc('font', family=font_name)
plt.rcParams['axes.unicode_minus'] = False

# ==========================
# 제목
# ==========================
st.title("💰 유튜브 예상 수익 분석기")

st.markdown("""
유튜브 조회수를 기반으로 예상 광고 수익을 계산합니다.

※ 실제 수익은 국가, 시청자 특성, 광고 유형 등에 따라 달라질 수 있습니다.
""")

