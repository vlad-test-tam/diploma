import streamlit as st
import json
import os
from streamlit_cookies_manager import EncryptedCookieManager

from src.repositories.user_repository import UserRepository
from src.services.auth_service import AuthService
from src.utils.database import db
from src.utils.ui import UserInterfaceUtils

class AuthPage:
    """
    Builds the UI for the Login/ Sign Up page.
    """

    def __init__(self, auth_token: str, company_name: str, width, height, logout_button_name: str = 'Logout',
                 hide_menu_bool: bool = False, hide_footer_bool: bool = False, logo_path=""):
        """
        Arguments:
        -----------
        1. self
        2. auth_token : The unique authorization token received from - https://www.courier.com/email-api/
        3. company_name : This is the name of the person/ organization which will send the password reset email.
        4. width : Width of the animation on the login page.
        5. height : Height of the animation on the login page.
        6. logout_button_name : The logout button name.
        7. hide_menu_bool : Pass True if the streamlit menu should be hidden.
        8. hide_footer_bool : Pass True if the 'made with streamlit' footer should be hidden.
        9. lottie_url : The lottie animation you would like to use on the login page. Explore animations at - https://lottiefiles.com/featured
        """
        self.auth_token = auth_token
        self.company_name = company_name
        self.width = width
        self.height = height
        self.logout_button_name = logout_button_name
        self.hide_menu_bool = hide_menu_bool
        self.hide_footer_bool = hide_footer_bool
        self.ui_utils = UserInterfaceUtils()
        self.logo_path = logo_path
        self.auth_service = AuthService()

        self.cookies = EncryptedCookieManager(
            prefix="streamlit_login_ui_yummy_cookies",
            password='9d68d6f2-4258-45c9-96eb-2d6bc74ddbb5-d8f49cab-edbb-404a-94d0-b25b1d4a564b')

        if not self.cookies.ready():
            st.stop()

    def get_current_user(self):
        """Получает текущего пользователя из куков"""
        print("3")
        if '__streamlit_login_signup_ui_username__' in st.session_state:
            print("4")
            email = st.session_state['__streamlit_login_signup_ui_username__']
            return self.auth_service.get_user_by_email(email)
        print("5")
        return None

    def render_auth_header(self):
        """Renders header with auth navigation buttons"""
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
            /* Стиль для форм аутентификации */
            .stForm {{
                margin-top: 220px !important;
                border: 2px solid orange !important;
                border-radius: 10px !important;
                padding: 20px !important;
            }}
            /* Дополнительный отступ для заголовков форм */
            .stMarkdown h2 {{
                margin-top: 0 !important;
                color: orange !important;
            }}
        </style>

        <div class="custom-header">
            <img src="data:image/png;base64,{logo_base64}" alt="Logo" />
            <div class="header-buttons">
                <a href="/?auth=login" target="_self" {'class="active"' if st.query_params.get('auth') == 'login' else ''}>Вход</a>
                <a href="/?auth=signup" target="_self" {'class="active"' if st.query_params.get('auth') == 'signup' else ''}>Создать аккаунт</a>
                <a href="/?auth=reset" target="_self" {'class="active"' if st.query_params.get('auth') == 'reset' else ''}>Сменить пароль</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

    def check_auth_json_file_exists(self, auth_filename: str) -> bool:
        """
        Checks if the auth file (where the user info is stored) already exists.
        """
        file_names = []
        for path in os.listdir('./'):
            if os.path.isfile(os.path.join('./', path)):
                file_names.append(path)

        present_files = []
        for file_name in file_names:
            if auth_filename in file_name:
                present_files.append(file_name)

            present_files = sorted(present_files)
            if len(present_files) > 0:
                return True
        return False

    def get_username(self):
        if not st.session_state['LOGOUT_BUTTON_HIT']:
            fetched_cookies = self.cookies
            if '__streamlit_login_signup_ui_username__' in fetched_cookies.keys():
                username = fetched_cookies['__streamlit_login_signup_ui_username__']
                return username

    def login_widget(self) -> None:
        """
        Creates the login widget, checks and sets cookies, authenticates the users.
        """
        if not st.session_state['LOGGED_IN']:
            if not st.session_state['LOGOUT_BUTTON_HIT']:
                fetched_cookies = self.cookies
                if '__streamlit_login_signup_ui_username__' in fetched_cookies.keys():
                    if fetched_cookies[
                        '__streamlit_login_signup_ui_username__'] != '1c9a923f-fb21-4a91-b3f3-5f18e3f01182':
                        st.session_state['LOGGED_IN'] = True

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
                    else:
                        st.session_state['LOGGED_IN'] = True
                        user = self.auth_service.get_user_by_email(email)
                        st.session_state['USER_ID'] = user.id
                        self.cookies['USER_ID'] = str(user.id)
                        self.cookies['__streamlit_login_signup_ui_username__'] = email
                        self.cookies.save()
                        st.rerun()

    def sign_up_widget(self) -> None:
        """
        Creates the sign-up widget and stores the user info in a secure way in the _secret_auth_.json file.
        """
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
                    self.auth_service.register_new_user(email_sign_up, email_sign_up, username_sign_up, password_sign_up)
                    st.success("Регистрация успешна!")

    def reset_password(self) -> None:
        """
        Creates the reset password widget and after user authentication (email and the password shared over that email),
        resets the password and updates the same in the _secret_auth_.json file.
        """
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

    def logout_widget(self) -> None:
        """
        Creates the logout widget in the sidebar only if the user is logged in.
        """
        if st.session_state['LOGGED_IN']:
            logout_click_check = st.button(self.logout_button_name)
            if logout_click_check:
                st.session_state['LOGOUT_BUTTON_HIT'] = True
                st.session_state['LOGGED_IN'] = False
                self.cookies['__streamlit_login_signup_ui_username__'] = '1c9a923f-fb21-4a91-b3f3-5f18e3f01182'
                st.rerun()

    def build_login_ui(self):
        """
        Brings everything together, calls important functions.
        """
        if 'LOGGED_IN' not in st.session_state:
            st.session_state['LOGGED_IN'] = False

        if 'LOGOUT_BUTTON_HIT' not in st.session_state:
            st.session_state['LOGOUT_BUTTON_HIT'] = False

        auth_json_exists_bool = self.check_auth_json_file_exists('_secret_auth_.json')

        if not auth_json_exists_bool:
            with open("_secret_auth_.json", "w") as auth_json:
                json.dump([], auth_json)

        # Render auth navigation header
        self.render_auth_header()

        # Show appropriate widget based on URL param
        auth_action = st.query_params.get('auth', 'login')

        if auth_action == 'login':
            self.login_widget()
        elif auth_action == 'signup':
            self.sign_up_widget()
        elif auth_action == 'reset':
            self.reset_password()

        return st.session_state['LOGGED_IN']
