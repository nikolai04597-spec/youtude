import re
import os
from collections import Counter

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import streamlit as st

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from wordcloud import WordCloud

# ==================================================
# Streamlit 설정
# ==================================================
st.set_page_config(
    page_title="YouTube 댓글 분석기",
    layout="wide"
)

# ==================================================
# 한글 폰트 설정
# ==================================================
font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pages', 'NanumGothic.ttf')
system_font = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'

if not os.path.exists(font_path):
    font_path = system_font

font_prop = fm.FontProperties(fname=font_path)
plt.rcParams["font.family"] = font_prop.get_name()
plt.rcParams["axes.unicode_minus"] = False

# ==================================================
# YouTube API Key
# ==================================================
try:
    YOUTUBE_API_KEY = st.secrets["YOUTUBE_API_KEY"]
except:
    YOUTUBE_API_KEY = "본인의_API_KEY"

# ==================================================
# 제목
# ==================================================
st.title("📺 YouTube 댓글 분석 웹앱")

st.markdown("""
유튜브 영상 댓글을 수집하여 사용자 반응을 분석합니다.
""")

# ==================================================
# 입력 영역
# ==================================================
video_url = st.text_input(
    "유튜브 영상 링크를 입력하세요"
)

comment_count = st.slider(
    "수집할 댓글 수",
    min_value=10,
    max_value=5000,
    value=100,
    step=10
)

# ==================================================
# 영상 ID 추출
# ==================================================
def extract_video_id(url):

    patterns = [
        r"v=([a-zA-Z0-9_-]+)",
        r"youtu\.be/([a-zA-Z0-9_-]+)"
    ]

    for pattern in patterns:
        match = re.search(pattern, url)

        if match:
            return match.group(1)

    return None

# ==================================================
# 댓글 수집
# ==================================================
def get_comments(video_id, max_comments):

    youtube = build(
        "youtube",
        "v3",
        developerKey=YOUTUBE_API_KEY
    )

    comments = []

    try:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100,
            textFormat="plainText"
        )

        while request and len(comments) < max_comments:

            response = request.execute()

            for item in response["items"]:

                snippet = item["snippet"]["topLevelComment"]["snippet"]

                comments.append({
                    "작성자": snippet["authorDisplayName"],
                    "댓글": snippet["textDisplay"],
                    "좋아요": snippet["likeCount"],
                    "작성시간": snippet["publishedAt"]
                })

                if len(comments) >= max_comments:
                    break

            request = youtube.commentThreads().list_next(
                request,
                response
            )

    except HttpError as e:
        st.error(f"YouTube API 오류 발생\n\n{e}")
        return pd.DataFrame()

    return pd.DataFrame(comments)

# ==================================================
# 워드클라우드
# ==================================================
def create_wordcloud(text):

    words = re.findall(r"[가-힣]{2,}", text)

    stopwords = {
        "진짜", "정말", "너무", "영상",
        "댓글", "오늘", "그냥", "이거",
        "제가", "저는", "합니다"
    }

    words = [
        word for word in words
        if word not in stopwords
    ]

    counter = Counter(words)

    wc = WordCloud(
        font_path=font_path,
        width=1000,
        height=500,
        background_color="white",
        colormap="viridis"
    ).generate(" ".join(words))

    return wc, counter

# ==================================================
# 분석 시작
# ==================================================
if st.button("댓글 분석 시작"):

    if not video_url:
        st.warning("유튜브 링크를 입력해주세요.")
        st.stop()

    video_id = extract_video_id(video_url)

    if not video_id:
        st.error("올바른 유튜브 링크가 아닙니다.")
        st.stop()

    with st.spinner("댓글 수집 중..."):

        df = get_comments(
            video_id,
            comment_count
        )

    if df.empty:
        st.stop()

    st.success(f"{len(df)}개의 댓글 수집 완료!")

    # ==================================================
    # 전처리
    # ==================================================
    df["작성시간"] = pd.to_datetime(df["작성시간"])
    df["시간"] = df["작성시간"].dt.hour

    # ==================================================
    # 댓글 데이터
    # ==================================================
    st.subheader("📄 수집된 댓글")

    st.dataframe(
        df.head(20),
        use_container_width=True
    )

    # ==================================================
    # 시간대별 댓글 추이
    # ==================================================
    st.subheader("⏰ 시간대별 댓글 추이")

    hourly = (
        df.groupby("시간")
        .size()
        .reset_index(name="댓글수")
    )

    fig1, ax1 = plt.subplots(figsize=(10, 4))

    ax1.plot(
        hourly["시간"],
        hourly["댓글수"],
        marker="o"
    )

    ax1.set_title("시간대별 댓글 수", fontproperties=font_prop)
    ax1.set_xlabel("시간", fontproperties=font_prop)
    ax1.set_ylabel("댓글 수", fontproperties=font_prop)

    st.pyplot(fig1)

    # ==================================================
    # 좋아요 분석
    # ==================================================
    st.subheader("👍 댓글 좋아요 분석")

    fig2, ax2 = plt.subplots(figsize=(10, 4))

    ax2.hist(df["좋아요"], bins=30)

    ax2.set_title("댓글 좋아요 분포", fontproperties=font_prop)
    ax2.set_xlabel("좋아요 수", fontproperties=font_prop)
    ax2.set_ylabel("댓글 개수", fontproperties=font_prop)

    st.pyplot(fig2)

    # ==================================================
    # 워드클라우드
    # ==================================================
    st.subheader("☁️ 워드클라우드")

    all_text = " ".join(df["댓글"].astype(str))

    wc, counter = create_wordcloud(all_text)

    fig3, ax3 = plt.subplots(figsize=(14, 7))

    ax3.imshow(wc, interpolation="bilinear")
    ax3.axis("off")

    st.pyplot(fig3)

    # ==================================================
    # 단어 빈도 TOP20
    # ==================================================
    st.subheader("📊 자주 등장하는 단어 TOP20")

    top20 = pd.DataFrame(
        counter.most_common(20),
        columns=["단어", "빈도"]
    )

    fig4, ax4 = plt.subplots(figsize=(10, 6))

    ax4.barh(top20["단어"], top20["빈도"])
    ax4.invert_yaxis()
    ax4.set_title("단어 빈도 TOP20", fontproperties=font_prop)
    ax4.set_xlabel("빈도수", fontproperties=font_prop)

    for label in ax4.get_yticklabels():
        label.set_fontproperties(font_prop)

    for label in ax4.get_xticklabels():
        label.set_fontproperties(font_prop)

    st.pyplot(fig4)

    st.dataframe(top20, use_container_width=True)

    # ==================================================
    # 통계
    # ==================================================
    st.subheader("📈 댓글 통계")

    col1, col2, col3 = st.columns(3)

    col1.metric("총 댓글 수", len(df))
    col2.metric("평균 좋아요", round(df["좋아요"].mean(), 2))
    col3.metric("최대 좋아요", int(df["좋아요"].max()))

    # ==================================================
    # CSV 다운로드
    # ==================================================
    csv = df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "📥 댓글 CSV 다운로드",
        csv,
        "youtube_comments.csv",
        "text/csv"
    )
