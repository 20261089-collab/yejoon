import streamlit as st
import pandas as pd
from datetime import datetime, date
import os
import calendar

# 1. 페이지 설정
st.set_page_config(
    page_title="수룡이와 함께하는 맞춤형 다이어트",
    page_icon="🐉",
    layout="centered"
)

# [데이터 영구 저장을 위한 파일 경로 설정]
LOG_FILE = "diet_exercise_log.csv"

# [계산 함수 정의] ---------------------------------------------
def calculate_bmi(weight, height):
    h = height / 100
    return round(weight / (h**2), 1)

def calculate_bmr(weight, height, age, gender):
    if gender == "남자":
        return round(10 * weight + 6.25 * height - 5 * age + 5)
    return round(10 * weight + 6.25 * height - 5 * age - 161)

def calculate_tdee(bmr, activity):
    factors = {
        "거의 안 움직임": 1.2,
        "가벼운 활동": 1.375,
        "보통": 1.55,
        "활발함": 1.725,
        "매우 활발": 1.9
    }
    return round(bmr * factors[activity])
# -----------------------------------------------------------------

# 2. 음식 데이터 정의
foods = {
    "김밥": {"calorie": 450, "type": "한식", "is_healthy": True},
    "참치김밥": {"calorie": 500, "type": "한식", "is_healthy": True},
    "치즈김밥": {"calorie": 530, "type": "한식", "is_healthy": False},
    "샐러드": {"calorie": 250, "type": "가벼운식단", "is_healthy": True},
    "닭가슴살": {"calorie": 165, "type": "단백질", "is_healthy": True},
    "고구마": {"calorie": 130, "type": "가벼운식단", "is_healthy": True},
    "현미밥": {"calorie": 320, "type": "한식", "is_healthy": True},

    "라면": {"calorie": 500, "type": "분식", "is_healthy": False},
    "불닭볶음면": {"calorie": 530, "type": "분식", "is_healthy": False},
    "짜장면": {"calorie": 700, "type": "중식", "is_healthy": False},
    "짬뽕": {"calorie": 650, "type": "중식", "is_healthy": False},
    "햄버거": {"calorie": 550, "type": "패스트푸드", "is_healthy": False},
    "치킨": {"calorie": 700, "type": "패스트푸드", "is_healthy": False},
    "피자": {"calorie": 800, "type": "패스트푸드", "is_healthy": False},
    "떡볶이": {"calorie": 450, "type": "분식", "is_healthy": False},
    "순대": {"calorie": 300, "type": "분식", "is_healthy": False},

    "계란": {"calorie": 80, "type": "단백질", "is_healthy": True},
    "바나나": {"calorie": 90, "type": "간식", "is_healthy": True},
    "사과": {"calorie": 100, "type": "간식", "is_healthy": True},
    "요거트": {"calorie": 120, "type": "간식", "is_healthy": True},
    "연어": {"calorie": 250, "type": "단백질", "is_healthy": True},
    "스테이크": {"calorie": 600, "type": "단백질", "is_healthy": True},
    "파스타": {"calorie": 650, "type": "양식", "is_healthy": False},
    "샌드위치": {"calorie": 400, "type": "간단식", "is_healthy": True},
    "초밥": {"calorie": 500, "type": "일식", "is_healthy": True}
}

# 🔘 [디자인 변경] 로고 크기 및 여백 밸런스 조정
title_col1, title_col2 = st.columns([1.3, 4]) # 로고 칸을 기존보다 더 넓게 확장

with title_col1:
    try:
        # width를 80에서 150으로 키워 큼직하게 노출시킵니다.
        st.image("icon.png", width=150)
    except FileNotFoundError:
        st.error("⚠️ 'icon.png' 파일을 찾을 수 없습니다. 이미지를 코드와 같은 폴더에 넣어주세요.")
    except Exception as e:
        st.error(f"⚠️ 이미지를 불러오는 중 오류가 발생했습니다: {e}")

with title_col2:
    # 대형 로고 높이에 맞추기 위해 상단 패딩용 빈 줄 살짝 삽입
    st.write("")
    st.title("핏메이트")
    st.caption("식단과 운동 기록을 매일 매일 누적하는 똑똑한 다이어트 다이어리")

st.divider()

# 3. 사용자 정보 입력
st.header("👤 사용자 정보 입력")
name = st.text_input("이름", value="수룡이")
gender = st.selectbox("성별", ["여자", "남자"])

col1, col2, col3 = st.columns(3)
with col1:
    age = st.number_input("나이", min_value=1, step=1, value=25)
with col2:
    height = st.number_input("키(cm)", min_value=1.0, value=165.0)
with col3:
    weight = st.number_input("몸무게(kg)", min_value=1.0, value=60.0)

activity = st.selectbox("활동량", ["거의 안 움직임", "가벼운 활동", "보통", "활발함", "매우 활발"])
goal = st.selectbox("목표", ["감량", "유지", "근육증가"])

allergy = st.text_input("알레르기 음식", value="없음")
dislike = st.text_input("싫어하는 음식", value="없음")
food_style = st.selectbox("선호 식단", ["한식", "가벼운식단", "단백질", "간단식", "분식", "중식", "양식", "일식", "간식", "패스트푸드"])

# 🍽️ 오늘 먹은 음식 기록
st.divider()
st.header("🍽️ 오늘 먹은 음식 기록")
selected_foods = st.multiselect("오늘 어떤 음식을 드셨나요?", list(foods.keys()))

# 🔘 분석 확인하기 버튼 생성
st.write("")
analyze_button = st.button("🔍 나의 맞춤형 다이어트 분석 확인하기", use_container_width=True)
st.divider()

# 사용자가 [분석 확인하기] 버튼을 누르기 전 초기 상태 제어
if not analyze_button:
    st.info("💡 위의 정보를 모두 입력 및 식단을 선택하신 후 **[나의 맞춤형 다이어트 분석 확인하기]** 버튼을 누르면 수룡이의 분석 리포트가 시작됩니다!")
else:
    # 건강 지표 계산 (버튼 클릭 시 작동)
    user_bmi = calculate_bmi(weight, height)
    user_bmr = calculate_bmr(weight, height, age, gender)
    user_tdee = calculate_tdee(user_bmr, activity)

    if goal == "감량":
        daily_calorie = user_tdee - 300
    elif goal == "근육증가":
        daily_calorie = user_tdee + 300
    else:
        daily_calorie = user_tdee

    total = 0
    healthy_count = 0
    unhealthy_count = 0

    for food in selected_foods:
        total += foods[food]["calorie"]
        if foods[food]["is_healthy"]: healthy_count += 1
        else: unhealthy_count += 1

    if selected_foods:
        col_h, col_uh = st.columns(2)
        with col_h:
            st.write("🍏 **다이어트에 좋은 식단**")
            for food in selected_foods:
                if foods[food]["is_healthy"]: st.write(f"- {food} ({foods[food]['calorie']} kcal)")
        with col_uh:
            st.write("😈 **다이어트를 방해하는 식단**")
            for food in selected_foods:
                if not foods[food]["is_healthy"]: st.write(f"- {food} ({foods[food]['calorie']} kcal)")

    # 5. 수룡이 게임화면
    st.header("🎮 수룡이의 현재 상태")

    if total == 0:
        suryong_img = "normal_suryong.jpg"
        suryong_msg = f"배가 고파요! 오늘 먹은 음식을 기록해주세요. (현재 BMI: {user_bmi})"
        status_color = "info"
    elif total > daily_calorie + 150:
        suryong_img = "fat_suryong.jpg"
        suryong_msg = f"앗! 권장 칼로리({daily_calorie}kcal)를 많이 초과했어요! 수룡이가 포동포동하게 살이 쪘습니다. 😭"
        status_color = "error"
    elif unhealthy_count > 0 and unhealthy_count >= healthy_count:
        suryong_img = "fat_suryong.jpg"
        suryong_msg = f"식단에 다이어트를 방해하는 음식을 많이 먹었어요! 수룡이 몸이 붓고 살이 찌려고 해요! 👿"
        status_color = "error"
    elif total < daily_calorie - 400:
        suryong_img = "slim_suryong.jpg"
        suryong_msg = "영양이 너무 부족해요! 수룡이가 배가 고파 기운 없이 홀쭉해졌어요.. 🥺"
        status_color = "warning"
    else:
        suryong_img = "normal_suryong.jpg"
        suryong_msg = "완벽해요! 클린하고 건강하게 목표 칼로리 채우기 성공! 수룡이가 따봉을 날립니다! 👍"
        status_color = "success"

    col_char, col_info = st.columns([1, 1])
    with col_char:
        try: st.image(suryong_img, use_container_width=True)
        except: st.error(f"⚠️ 저장소에서 '{suryong_img}' 파일을 찾을 수 없습니다.")

    with col_info:
        if name:
            last_char = name[-1]
            name_with_josa = f"{name}님" if (ord(last_char) - 0xAC00) % 28 > 0 else name
            st.subheader(f"🐲 {name_with_josa}의 수룡이")
        else:
            st.subheader("🐲 사용자님의 수룡이")

        if status_color == "info": st.info(suryong_msg)
        elif status_color == "error": st.error(suryong_msg)
        elif status_color == "warning": st.warning(suryong_msg)
        else: st.success(suryong_msg)

        st.metric("나의 BMI 지수", f"{user_bmi}")
        st.metric("목표 권장 칼로리", f"{daily_calorie} kcal")
        st.metric("현재 섭취량", f"{total} kcal", delta=total - daily_calorie, delta_color="inverse")

    st.divider()

    # 6. 추천 기능 및 다이어트 일지 (탭 구성)
    tab1, tab2, tab3 = st.tabs(["🍱 추천 식단", "🏃 추천 운동 및 설정", "📅 나의 누적 다이어트 일지"])

    with tab1:
        st.write("✨ **수룡이가 엄선한 건강한 다이어트 추천 메뉴**")
        recommended = [f for f in foods if foods[f]["type"] == food_style and foods[f]["is_healthy"] == True and allergy not in f and dislike not in f]
        if not recommended:
            st.warning(f"선택하신 '{food_style}' 카테고리에는 다이어트 전용 추천 식단이 없습니다. 대신 수룡이의 추천 클린 식단을 제공합니다!")
            recommended = ["샐러드", "닭가슴살", "고구마", "계란", "현미밥"]
        for f in recommended:
            st.write(f"- {f}: {foods[f]['calorie']} kcal")

    # 🏃 추천 운동 및 오늘 한 운동 확정 섹션
    with tab2:
        st.write("🏋️ **오늘 나의 상태에 딱 맞는 맞춤형 운동 프로그램**")

        ex_col1, ex_col2, ex_col3 = st.columns(3)
        with ex_col1:
            place_style = st.selectbox("운동 장소 선택 🏢", ["홈트레이닝 (집)", "헬스장 (Gym)"])
        with ex_col2:
            target_part = st.selectbox("운동 부위 설정 🎯", ["전신", "상체 (가슴/팔)", "하체 (엉덩이/허벅지)", "코어 (복부/허리)"])
        with ex_col3:
            condition = st.selectbox("오늘의 컨디션 🌡️", ["컨디션 최고! 🔥", "보통이에요 🙂", "피곤하고 무거워요 😴"])

        bmi_status = "고체중 (관절 보호)" if user_bmi >= 25.0 else ("저체중 (근력 강화)" if user_bmi < 18.5 else "정상 체중")
        st.info(f"📋 **분석 리포트**: {bmi_status} 상태에 맞춤형 [{place_style} - {target_part}] 프로그램을 제안합니다.")

        if condition == "컨디션 최고! 🔥":
            cond_msg = "영상의 동작을 **최대 강도**로 완주하고 아래 추가 미션까지 도전해보세요!"
            gym_set = "4세트"
            home_mission = "💡 맨몸 스쿼트 20회 + 플랭크 1분 추가 진행!"
        elif condition == "보통이에요 🙂":
            cond_msg = "영상의 페이스를 그대로 유지하며 **정석 자세**에 집중하세요."
            gym_set = "3세트"
            home_mission = "💡 영상 가이드를 80% 이상 끈기 있게 따라하기!"
        else:
            cond_msg = "영상의 **속도를 낮추거나, 무리한 동작은 건너뛰고 스트레칭 위주**로 진행하세요."
            gym_set = "2세트 (자극 중심)"
            home_mission = "💡 너무 힘들다면 영상을 앞쪽 10분만 따라 한 뒤 휴식하기!"

        st.warning(f"🌡️ **오늘의 컨디션 케어 멘트**: {cond_msg}")

        # 장소별 가이드 출력
        if place_style == "홈트레이닝 (집)":
            st.success(f"🏠 오늘의 추천 홈트 영상")
            if target_part == "전신":
                st.markdown("- [추천 영상 1](https://youtu.be/gSz5n4sLENI?si=cF8UNYcY7O51vv3P) / [추천 영상 2](https://youtu.be/dZbPtAgofwI?si=fGf1KFgcRwkiR2LU)")
            elif target_part == "상체 (가슴/팔)":
                st.markdown("- [추천 영상 1](https://youtu.be/2swcod5RYvU?si=PiprFfrdaW4POwqI) / [추천 영상 2](https://youtu.be/T-bVqdhqW2U?si=O7RwqaDiVpioeKs7)")
            elif target_part == "하체 (엉덩이/허벅지)":
                st.markdown("- [추천 영상 1](https://youtu.be/dpBYYEhdofI?si=OGiy3ZdSSRCdd__q) / [추천 영상 2](https://youtu.be/NDsjmxTROEo?si=Kx28BPvmyhy8FS4u)")
            elif target_part == "코어 (복부/허리)":
                st.markdown("- [추천 영상 1](https://youtu.be/jpTQdM7okkI?si=Iul-MhU62OggKOCP) / [추천 영상 2](https://youtu.be/iOSYLKBk894?si=B606cM5LgWwS1T5j)")
            with st.expander("ℹ️ 홈트 가이드 설명 보기"):
                st.write(home_mission)
        else:
            st.success(f"💪 오늘의 헬스장 추천 머신 루틴 ({gym_set}씩 수행)")
            if target_part == "상체 (가슴/팔)":
                st.markdown("- [추천 강좌 보기](https://youtu.be/Dw8PbebpF9w?si=5NIbj8CspBo_FwZl)")
            elif target_part == "하체 (엉덩이/허벅지)":
                st.markdown("- [추천 강좌 보기](https://youtu.be/Na0Dhue1oqk?si=4VvIt7heeGHHV4Yd)")
            elif target_part == "코어 (복부/허리)":
                st.markdown("- [추천 숏츠 1](https://youtube.com/shorts/ocMkMZya3ac?si=p89Dw6--vfRyqRNT) / [추천 숏츠 2](https://youtube.com/shorts/bAFDWHA7fG8?si=ez9Av_2x54NiKXtj)")
            elif target_part == "전신":
                st.markdown("- [추천 숏츠 1](https://youtube.com/shorts/ul5GqyTSSIk?si=8NaZLXCPr0ykjo4M) / [추천 숏츠 2](https://youtube.com/shorts/1FZYk9OyxV0?si=ZtGUBllTgPrKHTcM)")

        # 💾 오늘 하루 기록 저장하기 버튼 추가 및 날짜 선택 활성화
        st.subheader("💾 오늘의 다이어트 기록 최종 저장")
        st.caption("식단 입력과 위의 운동 설정을 마친 후 아래 버튼을 누르면 매일 기록이 파일에 누적됩니다.")

        record_date = st.date_input("기록을 저장할 날짜를 선택하세요 📆", value=date.today())

        if st.button("🔥 오늘의 기록 저장하기"):
            new_data = {
                "날짜": record_date.strftime("%Y-%m-%d"),
                "이름": name if name else "사용자",
                "체중(kg)": weight,
                "BMI": user_bmi,
                "목표 칼로리": daily_calorie,
                "오늘 섭취량": total,
                "운동 장소": place_style,
                "운동 부위": target_part,
                "오늘 컨디션": condition
            }

            if os.path.exists(LOG_FILE):
                df = pd.read_csv(LOG_FILE)
            else:
                df = pd.DataFrame(columns=new_data.keys())

            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            df.to_csv(LOG_FILE, index=False, encoding="utf-8-sig")

            st.success(f"🎉 {record_date.strftime('%Y-%m-%d')} 날짜로 기록이 성공적으로 일지에 저장되었습니다! '나의 누적 다이어트 일지' 탭에서 확인하세요.")

    # 📅 저장된 다이어트 일지 조회 및 월별 운동 캘린더 통합 탭
    with tab3:
        st.write("📅 **나의 누적 다이어트 일지**")
        st.caption("그동안 기록했던 데이터들이 파일에 안전하게 보관되어 표출됩니다.")

        if os.path.exists(LOG_FILE):
            df_log = pd.read_csv(LOG_FILE)

            # 1. 원본 데이터 최신순 출력
            st.dataframe(df_log.iloc[::-1], use_container_width=True)

            # 2. 간단한 누적 통계
            st.subheader("📊 나의 다이어트 요약")
            col_stat1, col_stat2 = st.columns(2)
            with col_stat1:
                st.metric("총 기록 일수", f"{len(df_log)} 일")
            with col_stat2:
                avg_cal = int(df_log["오늘 섭취량"].mean()) if len(df_log) > 0 else 0
                st.metric("평균 하루 섭취 칼로리", f"{avg_cal} kcal")

            # 3. 월별 운동 캘린더 결합 구역
            st.divider()
            st.subheader("🗓️ 월별 운동 캘린더")

            if len(df_log) == 0:
                st.info("기록이 아직 없습니다!")
            else:
                df_log["날짜_DT"] = pd.to_datetime(df_log["날짜"], errors="coerce")
                df_log = df_log.dropna(subset=["날짜_DT"])

                if len(df_log) == 0:
                    st.warning("날짜 데이터가 올바르지 않습니다!")
                else:
                    latest_date = df_log["날짜_DT"].max()
                    years = sorted(df_log["날짜_DT"].dt.year.unique())

                    cal_col1, cal_col2 = st.columns(2)
                    with cal_col1:
                        selected_year = st.selectbox(
                            "연도 선택",
                            years,
                            index=years.index(latest_date.year)
                        )
                    with cal_col2:
                        selected_month = st.selectbox(
                            "월 선택",
                            list(range(1, 13)),
                            index=latest_date.month - 1
                        )

                    month_data = df_log[
                        (df_log["날짜_DT"].dt.year == selected_year) &
                        (df_log["날짜_DT"].dt.month == selected_month)
                    ]

                    exercise_days = set(month_data["날짜_DT"].dt.day)

                    cal = calendar.monthcalendar(selected_year, selected_month)
                    st.write(f"📅 **{selected_year}년 {selected_month}월의 기록**")

                    days_kor = ["월", "화", "수", "목", "금", "토", "일"]
                    header = st.columns(7)
                    for i, d in enumerate(days_kor):
                        header[i].markdown(f"**{d}**")

                    for week in cal:
                        cols = st.columns(7)
                        for i, day in enumerate(week):
                            if day == 0:
                                cols[i].write("")
                            else:
                                if day in exercise_days:
                                    cols[i].markdown(f"🟢 **{day}**")
                                else:
                                    cols[i].markdown(f"{day}")

            # 4. 데이터 초기화 버튼 제공
            st.divider()
            if st.checkbox("⚠️ 전체 기록 지우기 (초기화)"):
                if st.button("정말 삭제하시겠습니까?"):
                    try:
                        os.remove(LOG_FILE)
                        st.warning("모든 다이어트 기록이 영구 삭제되었습니다. 페이지를 새로고침 해주세요.")
                    except:
                        st.error("파일 삭제 중 에러가 발생했습니다.")
        else:
            st.info("아직 저장된 다이어트 일지가 없습니다. '추천 운동 및 설정' 탭 하단에서 첫 기록을 저장해보세요!")
