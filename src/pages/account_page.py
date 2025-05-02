import streamlit as st

from src.models.user import User
from src.pages.auth_page import AuthPage
from src.pages.base_page import BasePage

from src.pages.html_jnjection_handlers.account_handler import AccountInjectionHandler
from src.services.account_service import AccountService
from src.utils.logger import logger
from src.utils.ui import UserInterfaceUtils


class AccountPage(BasePage):
    def __init__(self, auth: AuthPage, paths: dict):
        self.auth = auth
        self.logo_path = paths["logo_path"]
        self.ui_utils = UserInterfaceUtils()
        self.account_service = AccountService()
        self.injection_handler = AccountInjectionHandler()

    def build_header(self):
        logo_base64 = self.ui_utils.get_image_base64(self.logo_path)
        self.injection_handler.header_injection(st, logo_base64)


    def build_content(self, user_info: User):
        st.markdown('<div class="main-content">', unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align: center;'>Добро пожаловать, {user_info.username}!</h2>", unsafe_allow_html=True)

        free_uses = user_info.free_attempts_count
        is_subscription_active, remain_time = self.account_service.calculate_subscription_time_left(user_info)

        if is_subscription_active:
            if remain_time["days"] > 0:
                self.injection_handler.remain_subscription_injection(st, "Дней до истечения подписки", remain_time["days"], 270)
            else:
                self.injection_handler.remain_subscription_injection(st, "Часов до истечения подписки", remain_time["hours"], 270)
        elif free_uses > 0:
            self.injection_handler.remain_subscription_injection(st, "Бесплатных применений", free_uses, 220)

        st.markdown("<h3 style='text-align: center;'>Доступные планы</h3>", unsafe_allow_html=True)

        self.injection_handler.plan_box_styles_injection(st)
        col1, col2, col3 = st.columns(3)

        with col1:
            with st.container():
                self.injection_handler.plan_box_injection(st, "1 месяц", "Цена: 299 BYN")
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
                self.injection_handler.plan_box_injection(st, "3 месяца", "Цена: 749 BYN")
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
                self.injection_handler.plan_box_injection(st, "12 месяцев", "Цена: 2399 BYN")
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
                    logger.info(f"User (id={user_info.id}) changed name to {new_name}")
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
                logger.info(f"User (id={user_info.id}) changed password successfully")
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
        ui_utils = UserInterfaceUtils()
        user = ui_utils.get_current_user(st, self.auth)

        self.build_header()
        self.build_content(user)
