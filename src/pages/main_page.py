import os

from PIL import Image
import streamlit as st
from streamlit_image_comparison import image_comparison

from src.models.user import User
from src.pages.auth_page import AuthPage
from src.pages.base_page import BasePage
from src.pages.html_jnjection_handlers.main_handler import MainInjectionHandler
from src.services.account_service import AccountService
from src.services.main_service import MainService
from src.utils.logger import logger
from src.utils.ui import UserInterfaceUtils


class MainPage(BasePage):
    def __init__(self, auth: AuthPage, paths: dict):
        self.temp_folder = paths["temp_folder"]
        self.upload_folder = paths["upload_folder"]
        self.logo_path = paths["logo_path"]
        self.example1_img_path = paths["example1_path"]
        self.example2_img_path = paths["example2_path"]
        self.example3_img_path = paths["example3_path"]
        self.arrow_left_path = paths["arrow_left_path"]
        self.arrow_right_path = paths["arrow_right_path"]

        self.ui_utils = UserInterfaceUtils()
        self.main_service = MainService()
        self.account_service = AccountService()
        self.injection_handler = MainInjectionHandler()

        self.auth = auth
        os.makedirs(self.upload_folder, exist_ok=True)

    def setup_session_state(self):
        for key, default in {
            "state": "initial",
        }.items():
            if key not in st.session_state:
                st.session_state[key] = default

    def build_header(self):
        logo_base64 = self.ui_utils.get_image_base64(self.logo_path)
        self.injection_handler.header_injection(st, logo_base64)

    def reset_app(self):
        self.main_service.delete_temp_image(self.temp_folder, st.session_state["filename"])
        st.session_state.state = "initial"
        st.session_state.uploaded_image = None
        st.session_state.original_image = None
        st.session_state.result_image = None

    def process_image(self):
        st.session_state.state = "processing"
        # st.rerun()

    def build_content(self, user_info: User):
        self.injection_handler.styles_injection(st)
        free_uses = user_info.free_attempts_count
        is_subscription_active, remain_time = self.account_service.calculate_subscription_time_left(user_info)
        st.markdown('<div class="main-content">', unsafe_allow_html=True)

        self.injection_handler.greeting_injection(st)

        if free_uses > 0 and st.session_state.state != "processed":
            self.injection_handler.remain_subscription_injection(st, "Бесплатных применений", free_uses, 220)

        if st.session_state.state == "initial":
            st.markdown("<h2 style='text-align: center;'>Перетащите или выберите изображение</h2>", unsafe_allow_html=True)
            uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"])
            if uploaded_file:
                st.session_state.uploaded_image = uploaded_file
                st.session_state.state = "uploaded"
                st.rerun()

        elif st.session_state.state == "uploaded":
            st.image(st.session_state.uploaded_image, use_container_width=True)
            col1, col2 = st.columns(2)
            with col1:
                st.checkbox("Отображать этапы обработки", key="show_steps")
            with col2:
                st.button("Начать обработку", on_click=self.process_image)

        elif st.session_state.state == "processing":
            if free_uses > 0 or is_subscription_active:
                if free_uses > 0:
                    self.main_service.decrease_attempts_count(user_info.id)

                st.markdown(
                    """
                    <div style='padding: 15px; background-color: #ff6600; color: white; border-radius: 8px; font-size: 18px; text-align: center;'>🚀 Обработка изображения...</div>
                    """,
                    unsafe_allow_html=True
                )

                filename = self.main_service.generate_unique_filename(st.session_state.uploaded_image.name)
                st.session_state["filename"] = filename
                self.main_service.handle_processing(st, self.temp_folder, filename)
                if not st.session_state["show_steps"]:
                    st.session_state.state = "processed"
                else:
                    st.session_state.state = "processed_with_steps"
                logger.debug(f"User (id={user_info.id}) successfully processed image")
                st.rerun()
            else:
                st.error("У вас закончились бесплатные попытки, купите подписку")
                logger.debug(f"User (id={user_info.id}) tried to process without permissions")

        elif st.session_state.state == "processed" or st.session_state.state == "processed_with_steps":
            st.markdown("<h3 style='text-align:center;'>Результат обработки:</h3>", unsafe_allow_html=True)
            if st.session_state.state == "processed_with_steps":
                st.markdown("<h4 style='text-align:center;'>Маска изображения:</h4>", unsafe_allow_html=True)
                image_comparison(
                    img1=Image.open(st.session_state.original_image),
                    img2=st.session_state.masked_image,
                    label1="До", label2="После"
                )
                st.markdown("<h4 style='text-align:center;'>Удаление найденных дефектов:</h4>", unsafe_allow_html=True)
                image_comparison(
                    img1=st.session_state.masked_image,
                    img2=st.session_state.result_image,
                    label1="До", label2="После"
                )

            image_comparison(
                img1=Image.open(st.session_state.original_image),
                img2=st.session_state.result_image,
                label1="До", label2="После"
            )
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Сохранить результат"):
                    self.main_service.add_image(user_info.id, False, self.temp_folder, self.upload_folder, st.session_state["filename"])
                    logger.info(f"User (id={user_info.id}) save image successfully")
                    st.success("Изображение сохранено")
            with col2:
                if st.button("⭐ Добавить в понравившиеся"):
                    self.main_service.add_image(user_info.id, True, self.temp_folder, self.upload_folder, st.session_state["filename"])
                    logger.info(f"User (id={user_info.id}) save image as 'liked' successfully")
                    st.success("Изображение сохранено")

            st.button("🔙 Вернуться", on_click=self.reset_app)

        st.markdown('</div>', unsafe_allow_html=True)

        self.build_description_and_faq()

    def build_description_and_faq(self):
        example1 = self.ui_utils.get_image_base64(self.example1_img_path)
        example2 = self.ui_utils.get_image_base64(self.example2_img_path)
        example3 = self.ui_utils.get_image_base64(self.example3_img_path)
        left = self.ui_utils.get_image_base64(self.arrow_left_path)
        right = self.ui_utils.get_image_base64(self.arrow_right_path)

        st.markdown("<div style='display: flex; flex-direction: column; align-items: center;  margin-top: 150px;'>", unsafe_allow_html=True)
        self.injection_handler.odd_card_injection(st, example1, "Это первое описание — здесь можно рассказать, что делает система или показать пример исправления.")
        self.injection_handler.arrow_injection(st, left)
        self.injection_handler.even_card_injection(st, example2, "Второй пример: можно продемонстрировать шаг обработки или результат сравнения до/после.")
        self.injection_handler.arrow_injection(st, right)
        self.injection_handler.odd_card_injection(st, example3, "Третий блок может содержать отзывы, подсказки или любые важные моменты работы с системой.")
        st.markdown("</div>", unsafe_allow_html=True)

        self.injection_handler.faq_injection(st)
        st.markdown('</div>', unsafe_allow_html=True)

    def run(self):
        self.setup_session_state()
        ui_utils = UserInterfaceUtils()
        user = ui_utils.get_current_user(st, self.auth)
        self.build_header()
        self.build_content(user)
