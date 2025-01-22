import streamlit as st

# BMI 계산 함수
def calculate_bmi(weight, height):
    bmi = weight / (height ** 2)
    return bmi

# BMI 해석 함수 (성별 고려)
def bmi_interpretation(bmi, gender):
    if gender == "여성":
        if bmi < 18.5:
            return "저체중입니다."
        elif 18.5 <= bmi < 24.9:
            return "정상 체중입니다."
        elif 25 <= bmi < 29.9:
            return "과체중입니다."
        else:
            return "비만입니다."
    else:  # 남성의 경우
        if bmi < 18.5:
            return "저체중입니다."
        elif 18.5 <= bmi < 24.9:
            return "정상 체중입니다."
        elif 25 <= bmi < 29.9:
            return "과체중입니다."
        else:
            return "비만입니다."

# 스트림릿 앱
def main():
    st.sidebar.title("비건 식단 관리 프로그램")
    
    # 사이드바 버튼
    if st.sidebar.button("📈 신체 분석"):
        st.session_state["section"] = "신체 분석"
    if st.sidebar.button("🏢 영양소 분석"):
        st.session_state["section"] = "영양소 분석"
    if st.sidebar.button("🤖 식단 조언"):
        st.session_state["section"] = "식단 조언"
    if st.sidebar.button("📅 월별 식단"):
        st.session_state["section"] = "월별 식단"
    if st.sidebar.button("🔍 메뉴 추천"):
        st.session_state["section"] = "메뉴 추천"

    # 섹션에 따른 기능 실행
    if "section" in st.session_state:
        if st.session_state["section"] == "신체 분석":
            st.title("신체 분석")
            gender = st.radio("성별을 선택하세요", ("여성", "남성"))
            height = st.number_input("키 (m 단위)", min_value=0.0, max_value=3.0, value=1.7)
            weight = st.number_input("몸무게 (kg 단위)", min_value=0.0, max_value=200.0, value=70.0)
            
            if st.button("BMI 계산"):
                bmi = calculate_bmi(weight, height)
                st.write(f"당신의 BMI는 {bmi:.2f}입니다.")
                
                interpretation = bmi_interpretation(bmi, gender)
                st.write(interpretation)

        elif st.session_state["section"] == "영양소 분석":
            st.title("영양소 분석")
            protein = st.number_input("일일 단백질 섭취량 (g)", min_value=0, value=40)
            iron = st.number_input("일일 철분 섭취량 (mg)", min_value=0, value=15)
            calcium = st.number_input("일일 칼슘 섭취량 (mg)", min_value=0, value=800)
            
            if st.button("영양소 분석하기"):
                analysis = nutrition_analysis(protein, iron, calcium)
                for nutrient, (intake, target) in analysis.items():
                    st.write(f"{nutrient} 섭취량: {intake}g (목표: {target}g)")

                    if intake < target:
                        st.warning(f"{nutrient} 섭취가 부족합니다!")
                    else:
                        st.success(f"{nutrient} 섭취가 충분합니다!")

        elif st.session_state["section"] == "식단 조언":
            st.title("식단 조언")
            goal = st.selectbox("건강 목표를 선택하세요", ["체중 감량", "근육 증가", "균형 잡힌 식사"])
            
            if st.button("식단 조언 받기"):
                advice = meal_advice(goal)
                st.write(advice)

        elif st.session_state["section"] == "월별 식단":
            st.title("월별 식단")
            month = st.selectbox("월을 선택하세요", list(calendar.month_name[1:]))
            year = st.number_input("년을 입력하세요", min_value=2020, max_value=2100, value=datetime.now().year)
            
            st.write(monthly_plan(month, year))

        elif st.session_state["section"] == "메뉴 추천":
            st.title("메뉴 추천")
            preference = st.selectbox("선호하는 메뉴 유형을 선택하세요", ["고단백", "저칼로리", "다양한 메뉴"])
            
            if st.button("메뉴 추천 받기"):
                recommendations = menu_recommendation(preference)
                st.write("추천 메뉴:")
                for menu in recommendations:
                    st.write(f"- {menu}")

if __name__ == "__main__":
    main()
