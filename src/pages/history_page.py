import io

import streamlit as st
import base64
from pathlib import Path

from src.pages.auth_page import AuthPage
from src.pages.base_page import BasePage
from src.pages.html_jnjection_handlers.history_handler import HistoryInjectionHandler
from src.services.history_service import HistoryService
from src.utils.ui import UserInterfaceUtils
from src.utils.logger import logger
from streamlit_image_comparison import image_comparison
from PIL import Image


class HistoryPage(BasePage):
    def __init__(self, auth: AuthPage, paths: dict):
        self.logo_path = paths["logo_path"]
        self.arrow_left_path = paths["arrow_left_path"]
        self.arrow_right_path = paths["arrow_right_path"]

        self.history_data = []
        self.liked_states = {}
        self.auth = auth

        self.ui_utils = UserInterfaceUtils()
        self.history_service = HistoryService()
        self.injection_handler = HistoryInjectionHandler()

    def get_query_params(self):
        return st.query_params.get("view_image", None)

    def set_query_params(self, params):
        st.query_params.update(**params)

    def build_header(self):
        logo_base64 = self.ui_utils.get_image_base64(self.logo_path)
        self.injection_handler.header_injection(st, logo_base64)

    def render_image_view(self, item):
        st.markdown('<div class="image-view-content">', unsafe_allow_html=True)

        image_comparison(
            img1=item.defected_path,
            img2=item.fixed_path,
            label1="До",
            label2="После",
            width=700
        )

        self.injection_handler.button_styles_injection(st)

        col1, col2 = st.columns([1, 1])

        with col1:
            heart = "❤️" if self.liked_states.get(item.id, False) else "🤍"
            if st.button(heart, key=f"like_view_{item.id}", use_container_width=True):
                self.history_service.toggle_like_status(item.id)
                st.rerun()

            st.button(
                "← Вернуться",
                key=f"back_{item.id}",
                use_container_width=True,
                type="primary"
            )
            if st.session_state.get(f"back_{item.id}"):
                st.query_params.clear()
                st.query_params["page"] = "history"
                st.rerun()

        with col2:
            fixed_img_path = Path(item.fixed_path)
            if fixed_img_path.exists():
                with Image.open(fixed_img_path) as img:
                    img_bytes = io.BytesIO()

                    img_format = st.selectbox(
                        "Формат",
                        ["PNG", "JPG (JPEG)"],
                        key=f"format_select_{item.id}",
                        label_visibility="collapsed"
                    )

                    if img_format == "JPG (JPEG)":
                        if img.mode == 'RGBA':
                            img = img.convert('RGB')
                        img.save(img_bytes, format='JPEG', quality=95)
                        file_ext = "jpeg"
                        mime_type = "image/jpeg"
                    else:
                        img.save(img_bytes, format='PNG')
                        file_ext = "png"
                        mime_type = "image/png"

                    img_bytes = img_bytes.getvalue()

                st.download_button(
                    label="⬇️ Скачать",
                    data=img_bytes,
                    file_name=f"fixed_{item.id}.{file_ext}",
                    mime=mime_type,
                    key=f"download_{item.id}",
                    use_container_width=True
                )
            else:
                st.warning("Файл не найден")

        st.button(
            "🗑️ Удалить",
            key=f"delete_{item.id}",
            use_container_width=True,
            type="secondary"
        )
        if st.session_state.get(f"delete_{item.id}"):
            self.history_service.delete_image_by_id(item.id)
            st.query_params.clear()
            st.query_params["page"] = "history"
            logger.info(f"Image (id={item.id}) has been deleted")
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    def build_content(self):
        st.markdown('<div class="main-content">', unsafe_allow_html=True)

        liked_items = [item for item in self.history_data if item.is_liked]
        if liked_items:
            st.markdown("<h2 style='text-align: center;'>Понравившиеся</h2>", unsafe_allow_html=True)
            self.display_liked_items(liked_items)

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center;'>Все фото</h2>", unsafe_allow_html=True)

        self.display_items(self.history_data)

        st.markdown('</div>', unsafe_allow_html=True)

    def display_liked_items(self, items):
        for i in range(0, len(items), 3):
            row = st.columns(3)
            for j in range(3):
                if i + j < len(items):
                    item = items[i + j]
                    item_id = item.id
                    if item_id not in self.liked_states:
                        self.liked_states[item_id] = item.is_liked

                    with row[j]:
                        img_path = Path(item.fixed_path)
                        if img_path.exists():
                            with open(img_path, "rb") as img_file:
                                encoded = base64.b64encode(img_file.read()).decode()
                            st.markdown(
                                f"<img src='data:image/png;base64,{encoded}' width='100%' style='border-radius: 8px;'/>",
                                unsafe_allow_html=True
                            )
                        else:
                            st.warning("Изображение не найдено.")

                        st.markdown(
                            f"<div style='margin-top: 10px; font-size: 20px; font-weight: bold; text-align: center;'>{item.fix_datetime}</div>",
                            unsafe_allow_html=True)

                        col1, col2 = st.columns([3, 1])
                        with col1:
                            if st.button("Посмотреть", key=f"view_{item_id}_liked", type="primary",
                                         use_container_width=True):
                                self.set_query_params({"view_image": str(item_id)})
                                st.rerun()

                        with col2:
                            heart = "❤️" if self.liked_states[item_id] else "🤍"
                            if st.button(heart, key=f"like_{item_id}_liked", use_container_width=True):
                                self.history_service.toggle_like_status(item.id)
                                st.rerun()

    def display_items(self, items):
        for i in range(0, len(items), 3):
            row = st.columns(3)
            for j in range(3):
                if i + j < len(items):
                    item = items[i + j]
                    item_id = item.id
                    if item_id not in self.liked_states:
                        self.liked_states[item_id] = item.is_liked

                    with row[j]:
                        img_path = Path(item.fixed_path)
                        if img_path.exists():
                            with open(img_path, "rb") as img_file:
                                encoded = base64.b64encode(img_file.read()).decode()
                            st.markdown(
                                f"<img src='data:image/png;base64,{encoded}' width='100%' style='border-radius: 8px;'/>",
                                unsafe_allow_html=True
                            )
                        else:
                            st.warning("Изображение не найдено.")

                        st.markdown(
                            f"<div style='margin-top: 10px; font-size: 20px; font-weight: bold; text-align: center;'>{item.fix_datetime}</div>",
                            unsafe_allow_html=True)

                        col1, col2 = st.columns([3, 1])
                        with col1:
                            if st.button("Посмотреть", key=f"view_{item_id}", type="primary", use_container_width=True):
                                self.set_query_params({"view_image": str(item_id)})
                                st.rerun()

                        with col2:
                            heart = "❤️" if self.liked_states[item_id] else "🤍"
                            if st.button(heart, key=f"like_{item_id}", use_container_width=True):
                                self.history_service.toggle_like_status(item.id)
                                logger.info(f"Image (id={item.id}) like status has been changed")
                                st.rerun()

    def run(self):
        ui_utils = UserInterfaceUtils()
        user = ui_utils.get_current_user(st, self.auth)

        self.history_data = self.history_service.image_repo.get_user_images(user.id)
        self.build_header()
        image_id = self.get_query_params()

        if image_id:
            selected_item = next((item for item in self.history_data if str(item.id) == image_id), None)
            if selected_item:
                self.render_image_view(selected_item)
            else:
                st.error("Изображение не найдено!")
                self.set_query_params({"view_image": None})
                st.rerun()
        else:
            self.build_content()
