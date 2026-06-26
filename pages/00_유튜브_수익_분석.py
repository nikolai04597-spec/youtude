import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import pandas as pd
from matplotlib import font_manager

# 한글 폰트 등록
font_path = "./NanumGothic.ttf"

font_manager.fontManager.addfont(font_path)
font_name = fm.FontProperties(fname=font_path).get_name()

plt.rc('font', family=font_name)
plt.rcParams['axes.unicode_minus'] = False

# 확인용 (한 번만 실행해 보세요)
st.write("현재 적용된 폰트:", font_name)

※ 실제 수익은 국가, 시청자 특성, 광고 유형 등에 따라 달라질 수 있습니다.
""")

# --------------------------
# 입력
# --------------------------

col1, col2 = st.columns(2)

with col1:
    views = st.number_input(
        "총 조회수",
        min_value=0,
        value=100000,
        step=1000
    )

with col2:
    upload_count = st.number_input(
        "월 업로드 개수",
        min_value=1,
        value=4
    )

st.subheader("광고 단가 설정")

cpm = st.slider(
    "CPM (1000회 조회당 광고비, USD)",
    min_value=0.5,
    max_value=20.0,
    value=3.0,
    step=0.5
)

revenue_share = st.slider(
    "크리에이터 수익 배분율 (%)",
    min_value=30,
    max_value=70,
    value=55
)

# --------------------------
# 수익 계산
# --------------------------

creator_cpm = cpm * (revenue_share / 100)

estimated_revenue = (views / 1000) * creator_cpm

low_estimate = estimated_revenue * 0.7
high_estimate = estimated_revenue * 1.3

monthly_income = estimated_revenue * upload_count
yearly_income = monthly_income * 12

# --------------------------
# 결과
# --------------------------

st.subheader("📊 예상 수익")

col1, col2, col3 = st.columns(3)

col1.metric(
    "예상 최소 수익",
    f"${low_estimate:,.2f}"
)

col2.metric(
    "예상 평균 수익",
    f"${estimated_revenue:,.2f}"
)

col3.metric(
    "예상 최대 수익",
    f"${high_estimate:,.2f}"
)

st.subheader("📈 월간 / 연간 수익")

col1, col2 = st.columns(2)

col1.metric(
    "예상 월 수익",
    f"${monthly_income:,.2f}"
)

col2.metric(
    "예상 연 수익",
    f"${yearly_income:,.2f}"
)

# --------------------------
# 차트
# --------------------------

st.subheader("수익 비교 차트")

income_df = pd.DataFrame({
    "구분": ["최소", "평균", "최대"],
    "수익(USD)": [
        low_estimate,
        estimated_revenue,
        high_estimate
    ]
})

fig, ax = plt.subplots(figsize=(8, 4))

ax.bar(
    income_df["구분"],
    income_df["수익(USD)"]
)

# 제목
ax.set_title(
    "예상 광고 수익",
    fontname=font_name
)

# y축 이름
ax.set_ylabel(
    "USD",
    fontname=font_name
)

# x축 눈금(최소/평균/최대)
for label in ax.get_xticklabels():
    label.set_fontname(font_name)

# y축 눈금
for label in ax.get_yticklabels():
    label.set_fontname(font_name)

st.pyplot(fig)
