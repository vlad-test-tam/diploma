import streamlit as st
from src.utils.ui import UserInterfaceUtils

st.set_page_config(page_title="Flawless App", layout="centered")

from src.pages.auth_page import AuthPage
from src.pages.main_page import MainPage
from src.pages.account_page import AccountPage
from src.pages.history_page import HistoryPage

if __name__ == "__main__":
    ui_utils = UserInterfaceUtils()
    paths = ui_utils.init_paths()

    auth = AuthPage(logo_path=paths["logo_path"])
    logged_in = auth.run()

    if logged_in:
        query_params = st.query_params
        page = query_params.get("page", "main")
        if page == "main":
            main_page = MainPage(auth=auth, paths=paths)
            main_page.run()
        elif page == "account":
            account_page = AccountPage(auth=auth, paths=paths)
            account_page.run()
        elif page == "history":
            history_page = HistoryPage(auth=auth, paths=paths)
            history_page.run()
        else:
            st.error("Страница не найдена.")
