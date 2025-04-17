import streamlit as st

from src.pages.history_page import HistoryPage

st.set_page_config(page_title="Flawless App", layout="centered")

from src.pages.auth_page import AuthPage
from src.pages.main_page import MainPage
from src.pages.account_page import AccountPage

if __name__ == "__main__":
    # Авторизация
    auth = AuthPage(
        auth_token="your_auth_token",
        company_name="FlawlessAI",
        width=400,
        height=300,
        logout_button_name='Выйти из аккаунта',
        hide_menu_bool=True,
        hide_footer_bool=True,
        logo_path=r"D:\Projects\Python\diploma_project\saved_images\front\logo-flawless.png"
    )

    logged_in = auth.build_login_ui()

    # Если авторизован — обрабатываем роутинг
    if logged_in:
        # Используем st.query_params вместо устаревшего st._get_query_params()
        query_params = st.query_params
        print(query_params)

        # Извлекаем параметр 'page' и делаем его списком (для совместимости с логикой)
        page = query_params.get("page", "main")

        if page == "main":
            app = MainPage(
                auth=auth,
                upload_folder=r"D:\Projects\Python\diploma_project\saved_images\storage",
                logo_path=r"D:\Projects\Python\diploma_project\saved_images\front\logo-flawless.png",
                example_img_path=r"D:\Projects\Python\diploma_project\saved_images\front\example_1.png",
                arrow_left_path=r"D:\Projects\Python\diploma_project\saved_images\front\right_to_left.png",
                arrow_right_path=r"D:\Projects\Python\diploma_project\saved_images\front\left_to_right.png"
            )
            app.run()

        elif page == "account":
            app = AccountPage(
                logo_path=r"D:\Projects\Python\diploma_project\saved_images\front\logo-flawless.png",
                auth=auth
            )
            app.run()

        elif page == "history":
            app = HistoryPage(
                logo_path=r"D:\Projects\Python\diploma_project\saved_images\front\logo-flawless.png",
                auth=auth
            )
            app.run()

        else:
            st.error("Страница не найдена.")
