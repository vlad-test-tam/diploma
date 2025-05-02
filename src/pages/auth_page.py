import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager

from src.pages.base_page import BasePage
from src.pages.html_jnjection_handlers.auth_handler import AuthInjectionHandler
from src.services.auth_service import AuthService
from src.settings.cookies_settings import CookiesSettings
from src.utils.logger import logger
from src.utils.ui import UserInterfaceUtils


class AuthPage(BasePage):
    def __init__(self, logo_path):
        self.ui_utils = UserInterfaceUtils()
        self.auth_action = ""
        self.logo_path = logo_path
        self.auth_service = AuthService()
        self.injection_handler = AuthInjectionHandler()
        self.cookies_settings = CookiesSettings()
        self.cookies = EncryptedCookieManager(
            prefix=self.cookies_settings.cookies_prefix,
            password=self.cookies_settings.cookies_password.get_secret_value(),
        )
        if not self.cookies.ready():
            st.stop()

    def build_header(self):
        logo_base64 = self.ui_utils.get_image_base64(self.logo_path)
        self.injection_handler.header_injection(st, logo_base64)

    def login_widget(self) -> None:
        if not st.session_state['LOGGED_IN']:
            if not st.session_state['LOGOUT_BUTTON_HIT']:
                fetched_cookies = self.cookies
                if '__streamlit_login_signup_ui_username__' in fetched_cookies.keys():
                    if fetched_cookies['__streamlit_login_signup_ui_username__'] != self.cookies_settings.cookies_username:
                        st.session_state['LOGGED_IN'] = True
                        logger.debug(f"Authentication passed using cookies")

        if not st.session_state['LOGGED_IN']:
            st.session_state['LOGOUT_BUTTON_HIT'] = False

            with st.form("Login Form"):
                st.markdown("## Вход в аккаунт")
                email = st.text_input("Адрес электронной почты")
                password = st.text_input("Пароль", type='password')
                st.markdown("###")
                login_submit_button = st.form_submit_button(label='Войти')

                if login_submit_button:
                    authenticate_user_check = self.auth_service.check_usr_pass(email, password)

                    if not authenticate_user_check:
                        st.error("Неверный адрес почты или пароль")
                        logger.debug(f"Authentication failed")
                    else:
                        st.session_state['LOGGED_IN'] = True
                        user = self.auth_service.get_user_by_email(email)
                        st.session_state['USER_ID'] = user.id
                        self.cookies['USER_ID'] = str(user.id)
                        self.cookies['__streamlit_login_signup_ui_username__'] = email
                        self.cookies.save()
                        logger.debug(f"User (id={user.id}) successfully passed authentication")
                        st.rerun()

    def sign_up_widget(self) -> None:
        with st.form("Sign Up Form"):
            st.markdown("## Создать аккаунт")

            email_sign_up = st.text_input("Адрес электронной почты *", placeholder='')
            valid_email_check = self.auth_service.check_valid_email(email_sign_up)
            unique_email_check = self.auth_service.check_unique_email(email_sign_up)

            username_sign_up = st.text_input("Имя *")
            password_sign_up = st.text_input("Пароль *", type='password')
            check_password_sign_up = st.text_input("Повторите пароль *", type='password')
            password_check = self.auth_service.check_password(password_sign_up, check_password_sign_up)
            username_check = self.auth_service.non_empty_str_check(username_sign_up)

            st.markdown("###")
            sign_up_submit_button = st.form_submit_button(label='Создать')

            if sign_up_submit_button:
                if not password_check:
                    st.error("Пароли не совпадают")
                elif not valid_email_check:
                    st.error("Введите действительный адрес почты")
                elif not unique_email_check:
                    st.error("Адрес почты уже используется")
                elif not username_check:
                    st.error("Введите имя")
                if password_check and valid_email_check and unique_email_check:
                    self.auth_service.register_new_user(email_sign_up, username_sign_up, password_sign_up)
                    st.success("Регистрация успешна!")
                    logger.info(f"Registration passed")
                else:
                    logger.debug(f"Registration failed")

    def reset_password_widget(self) -> None:
        with st.form("Reset Password Form"):
            st.markdown("## Сменить пароль")
            email_reset_passwd = st.text_input("Адрес электронной почты *")
            email_exists_check, username_reset_passwd = self.auth_service.check_email_exists(email_reset_passwd)

            current_passwd = st.text_input("Текущий пароль")
            current_passwd_check = self.auth_service.check_current_password(email_reset_passwd, current_passwd)
            new_passwd = st.text_input("Новый пароль", type='password')
            new_passwd_1 = st.text_input("Повторите новый пароль", type='password')
            st.markdown("###")
            reset_passwd_submit_button = st.form_submit_button(label='Сменить пароль')

            if reset_passwd_submit_button:
                if not email_exists_check:
                    st.error("Неверный адрес электронной почты")
                elif not current_passwd_check:
                    st.error("Неверный текущий пароль")
                elif new_passwd != new_passwd_1:
                    st.error("Пароли не совпадают")
                else:
                    self.auth_service.change_password(email_reset_passwd, new_passwd)
                    st.success("Пароль изменен!")
                    logger.info(f"Password changed successfully")

    def logout_widget(self) -> None:
        if st.session_state['LOGGED_IN']:
            logout_click_check = st.button("Выйти из аккаунта")
            if logout_click_check:
                st.session_state['LOGOUT_BUTTON_HIT'] = True
                st.session_state['LOGGED_IN'] = False
                self.cookies['__streamlit_login_signup_ui_username__'] = self.cookies_settings.cookies_username
                st.rerun()
                logger.debug(f"Logged out successfully")

    def run(self):
        if 'LOGGED_IN' not in st.session_state:
            st.session_state['LOGGED_IN'] = False
        if 'LOGOUT_BUTTON_HIT' not in st.session_state:
            st.session_state['LOGOUT_BUTTON_HIT'] = False
        self.build_header()
        self.auth_action = st.query_params.get('auth', 'login')
        self.build_content()
        return st.session_state['LOGGED_IN']

    def build_content(self):
        if self.auth_action == 'login':
            self.login_widget()
        elif self.auth_action == 'signup':
            self.sign_up_widget()
        elif self.auth_action == 'reset':
            self.reset_password_widget()
