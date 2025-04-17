from datetime import datetime

import streamlit as st

from src.models.user import User
from src.pages.auth_page import AuthPage
from src.services.account_service import AccountService
from src.utils.ui import UserInterfaceUtils


class AccountPage:
    def __init__(self, auth: AuthPage, logo_path="", arrow_left_path="", arrow_right_path=""):
        self.logo_path = logo_path
        self.arrow_left_path = arrow_left_path
        self.arrow_right_path = arrow_right_path
        self.ui_utils = UserInterfaceUtils()
        self.auth = auth
        self.account_service = AccountService()

    def render_header(self):
        logo_base64 = self.ui_utils.get_image_base64(self.logo_path)
        st.markdown(f"""
        <style>
            .custom-header {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 200px;
                background-color: #1e2228;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding-top: 10px;
                z-index: 1000;
                box-shadow: 0 2px 6px rgba(0,0,0,0.2);
            }}
            .custom-header img {{
                height: 110px;
                margin-bottom: 10px;
            }}
            .header-buttons {{
                display: flex;
                gap: 16px;
            }}
            .header-buttons a {{
                padding: 6px 16px;
                border-radius: 8px;
                background-color: transparent;
                color: orange;
                border: 2px solid orange;
                font-weight: 500;
                text-decoration: none;
                text-align: center;
            }}
            .header-buttons a:hover {{
                background-color: #3a3e45;
            }}
            .main-content {{
                margin-top: 130px;
            }}
            .plan-box {{
                background-color: #f3f3f3;
                border: 2px solid orange;
                border-radius: 12px;
                padding: 20px;
                text-align: center;
                color: orange;
                font-weight: 500;
            }}
            .orange-button {{
                background-color: #1e2228;
                color: orange;
                border: 2px solid orange;
                padding: 10px;
                border-radius: 8px;
                width: 100%;
                font-size: 16px;
                cursor: pointer;
                margin-top: 10px;
            }}
            .orange-button:hover {{
                background-color: #2e3238;
            }}
            .personal-block-title {{
                font-size: 22px;
                margin-top: 60px;
                margin-bottom: 20px;
                font-weight: bold;
                text-align: center;
            }}
            .input-button {{
                background-color: orange;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 8px;
                width: 100%;
                font-size: 16px;
                cursor: pointer;
                margin-top: 10px;
            }}
            .input-button:hover {{
                background-color: #e67300;
            }}
        </style>

        <div class="custom-header">
            <img src="data:image/png;base64,{logo_base64}" alt="Logo" />
            <div class="header-buttons">
                <a href="/" target="_self">Главная</a>
                <a href="/?page=history" target="_self">История</a>
                <a href="/?page=account" target="_self">Аккаунт</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

    def render_content(self, user_info: User):
        st.markdown('<div class="main-content">', unsafe_allow_html=True)

        st.markdown(f"<h2 style='text-align: center;'>Добро пожаловать, {user_info.username}!</h2>",
                    unsafe_allow_html=True)

        free_uses = user_info.free_attempts_count
        is_subscription_active, remain_time = self.account_service.calculate_subscription_time_left(user_info)

        if is_subscription_active:
            if remain_time["days"] > 0:
                st.markdown(
                    f"""
                                <div class='usage-box' style='
                                    text-align: center;
                                    background-color: #f3f3f3;
                                    padding: 10px;
                                    border-radius: 8px;
                                    margin-bottom: 30px;
                                    width: 270px;
                                    margin-left: auto;
                                    margin-right: auto;
                                    color: orange;
                                    border: 2px solid orange;
                                    font-weight: 500;
                                '>
                                    <span>Дней до истечения подписки: {remain_time["days"]}</span>
                                </div>
                                """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""
                        <div class='usage-box' style='
                            text-align: center;
                            background-color: #f3f3f3;
                            padding: 10px;
                            border-radius: 8px;
                            margin-bottom: 30px;
                            width: 270px;
                            margin-left: auto;
                            margin-right: auto;
                            color: orange;
                            border: 2px solid orange;
                            font-weight: 500;
                        '>
                            <span>Часов до истечения подписки: {remain_time["hours"]}</span>
                        </div>
                        """,
                    unsafe_allow_html=True
                )
        elif free_uses > 0:
            st.markdown(
                f"""
                <div class='usage-box' style='
                    text-align: center;
                    background-color: #f3f3f3;
                    padding: 10px;
                    border-radius: 8px;
                    margin-bottom: 30px;
                    width: 220px;
                    margin-left: auto;
                    margin-right: auto;
                    color: orange;
                    border: 2px solid orange;
                    font-weight: 500;
                '>
                    <span>Бесплатных применений: {free_uses}</span>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("<h3 style='text-align: center;'>Доступные планы</h3>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)

        st.markdown("""
                <style>
            .plan-box {
                background-color: #f3f3f3;
                border: 2px solid orange;
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                color: orange;
                font-weight: 500;
            }
        
            .stButton > button {
                background-color: #3a3e45 !important;
                color: white !important;
                border: 2px solid orange !important;
                border-radius: 8px;
                width: 100%;
                padding: 10px;
                font-weight: bold;
                cursor: pointer;
            }
        
            .stButton > button:hover {
                background-color: #2e2e2e !important;
            }
            </style>
        """, unsafe_allow_html=True)

        with col1:
            with st.container():
                st.markdown("""
                    <div class="plan-box">
                        <div style="font-size: 34px; font-weight: bold;">1 месяц</div>
                        <div style="font-size: 30px;"><strong>Цена: 299₽</strong></div>
                    </div>
                """, unsafe_allow_html=True)
                if st.button("Купить", key="buy_1"):
                    st.session_state['subscription_message'] = ("success", "Подписка успешно продлена на 1 месяц!")
                    st.session_state['subscription_duration'] = 1
                    self.account_service.update_subscription(user_info.id, 1)
                    st.rerun()
                if 'subscription_message' in st.session_state and st.session_state['subscription_duration'] == 1:
                    msg_type, message = st.session_state['subscription_message']
                    if msg_type == "success":
                        st.success(message)
                    del st.session_state['subscription_message']
                    del st.session_state['subscription_duration']

        with col2:
            with st.container():
                st.markdown("""
                    <div class="plan-box">
                        <div style="font-size: 34px; font-weight: bold;">3 месяца</div>
                        <div style="font-size: 30px;"><strong>Цена: 749₽</strong></div>
                    </div>
                """, unsafe_allow_html=True)
                if st.button("Купить", key="buy_3"):
                    st.session_state['subscription_message'] = ("success", "Подписка успешно продлена на 3 месяца!")
                    st.session_state['subscription_duration'] = 3
                    self.account_service.update_subscription(user_info.id, 3)
                    st.rerun()
                if 'subscription_message' in st.session_state and st.session_state['subscription_duration'] == 3:
                    msg_type, message = st.session_state['subscription_message']
                    if msg_type == "success":
                        st.success(message)
                    del st.session_state['subscription_message']
                    del st.session_state['subscription_duration']

        with col3:
            with st.container():
                st.markdown("""
                    <div class="plan-box">
                        <div style="font-size: 34px; font-weight: bold;">12 месяцев</div>
                        <div style="font-size: 30px;"><strong>Цена: 2390₽</strong></div>
                    </div>
                """, unsafe_allow_html=True)
                if st.button("Купить", key="buy_12"):
                    st.session_state['subscription_message'] = ("success", "Подписка успешно продлена на 12 месяцев!")
                    st.session_state['subscription_duration'] = 12
                    self.account_service.update_subscription(user_info.id, 12)
                    st.rerun()
                if 'subscription_message' in st.session_state and st.session_state['subscription_duration'] == 12:
                    msg_type, message = st.session_state['subscription_message']
                    if msg_type == "success":
                        st.success(message)
                    del st.session_state['subscription_message']
                    del st.session_state['subscription_duration']

        st.markdown("---")
        st.markdown('<div class="personal-block-title">Изменить персональные данные</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("Новое имя")
            if st.button("Сменить имя", key="change_name"):
                if self.auth.auth_service.non_empty_str_check(new_name):
                    st.session_state['name_change_message'] = ("success", f"Имя успешно изменено на {new_name}!")
                    self.auth.auth_service.change_name(user_info.id, new_name)
                    st.rerun()
            if 'name_change_message' in st.session_state:
                msg_type, message = st.session_state['name_change_message']
                if msg_type == "success":
                    st.success(message)
                del st.session_state['name_change_message']

        with col2:
            new_password = st.text_input("Новый пароль", type="password")
            if st.button("Сменить пароль", key="change_password"):
                st.session_state['password_change_message'] = ("success", f"Пароль успешно изменен!")
                self.auth.auth_service.change_password(user_info.email, new_password)
                st.rerun()
            if 'password_change_message' in st.session_state:
                msg_type, message = st.session_state['password_change_message']
                if msg_type == "success":
                    st.success(message)
                del st.session_state['password_change_message']

        st.markdown("---")
        self.auth.logout_widget()

        st.markdown('</div>', unsafe_allow_html=True)

    def run(self):
        # user_info = self.get_user_info()
        if 'USER_ID' not in st.session_state:
            if 'USER_ID' in self.auth.cookies:
                st.session_state['USER_ID'] = int(self.auth.cookies['USER_ID'])
        if 'USER_ID' not in st.session_state or not st.session_state['USER_ID']:
            st.warning("Пожалуйста, войдите в систему")
            return
        user_id = st.session_state['USER_ID']
        if not user_id:
            st.warning("Пожалуйста, войдите в систему")
            return
        else:
            user = self.auth.auth_service.get_user_by_id(user_id)

        self.render_header()
        self.render_content(user)
