import os
import streamlit as st
import pandas as pd

import economy_news
import corpinfo
import interview_supporter
import chatbot
import calendar_app
from cp_search import CompanySearch, show_company_search_section  # cp_search.py에서 CompanySearch 클래스와 show_company_search_section 함수를 가져옴


# 사이드바 네비게이션
def show_sidebar_navigation():  
    """사이드바 네비게이션"""
    st.sidebar.title("📊 메뉴")
    # 섹션 이동 버튼
    if st.sidebar.button("📈 경제 현황"):
        st.session_state["section"] = "경제 현황"
    if st.sidebar.button("🏢 금융 공기업 정보"):
        st.session_state["section"] = "기업 동향"
    if st.sidebar.button("💬 면접 예상 질문"):
        st.session_state["section"] = "면접 질문"
    if st.sidebar.button("🤖 챗봇"):
        st.session_state["section"] = "챗봇"
    if st.sidebar.button("📅 채용 달력"):
        st.session_state["section"] = "채용 달력"
    if st.sidebar.button("🔍 기업 검색"):
        st.session_state["section"] = "기업 검색"

# 메인 실행 함수
def main():
    # Streamlit 앱
    st.set_page_config(page_title="경제금융기업 AI 활용 취업 지원 서비스", layout="wide")
    st.title("📊 경제금융기업 AI 활용 취업 지원 서비스")
    
    # 사이드바 네비게이션
    show_sidebar_navigation()

    # 현재 활성화된 섹션에 따라 해당 함수 호출
    if st.session_state.get("section", "경제 현황") == "경제 현황":
        economy_news.show()
    elif st.session_state["section"] == "기업 동향":
        corpinfo.show()
    elif st.session_state["section"] == "면접 질문":
        interview_supporter.show()
    elif st.session_state["section"] == "챗봇":
        chatbot.show()
    elif st.session_state["section"] == "채용 달력":
        calendar_app.show()
    elif st.session_state["section"] == "기업 검색":
        show_company_search_section()  # 이제 이 함수가 정의되어 있으므로 오류가 발생하지 않음

# 앱 실행
if __name__ == "__main__":
    main()
