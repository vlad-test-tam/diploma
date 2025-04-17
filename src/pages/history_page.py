import io

import streamlit as st
import base64
from pathlib import Path

from src.pages.auth_page import AuthPage
from src.services.account_service import AccountService
from src.services.history_service import HistoryService
from src.services.main_service import MainService
from src.utils.ui import UserInterfaceUtils
from streamlit_image_comparison import image_comparison
from PIL import Image
from urllib.parse import parse_qs, urlparse


class HistoryPage:
    def __init__(self, auth: AuthPage, logo_path="", arrow_left_path="", arrow_right_path=""):
        self.logo_path = logo_path
        self.arrow_left_path = arrow_left_path
        self.arrow_right_path = arrow_right_path
        self.ui_utils = UserInterfaceUtils()
        self.liked_states = {}
        self.history_service = HistoryService()
        self.auth = auth

    def get_query_params(self):
        """Получаем параметры из URL (например, ?view_image=1)"""
        return st.query_params.get("view_image", None)

    def set_query_params(self, params):
        """Устанавливаем параметры URL (например, ?view_image=1)"""
        st.query_params.update(**params)  # Обновляем параметры

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
                margin-top: 220px; /* Увеличен отступ для хедера */
            }}
            .image-view-content {{
                margin-top: 120px;
                display: flex;
                flex-direction: column;
                align-items: center;
            }}
            .image-view-buttons {{
                display: flex;
                gap: 16px;
                margin-top: 20px;
                margin-bottom: 20px;
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

    def render_image_view(self, item):
        st.markdown('<div class="image-view-content">', unsafe_allow_html=True)

        # Сравнение изображений
        image_comparison(
            img1=item.defected_path,
            img2=item.fixed_path,
            label1="До",
            label2="После",
            width=700
        )

        # Стили для кнопок
        st.markdown("""
            <style>
                .stButton > button {
                    background-color: #1e2228;
                    color: white !important;
                    border: 2px solid orange;
                }
                
                div[data-testid="stDownloadButton"] > button {
                background-color: orange;
                color: white;
                border: 2px solid orange;
            }
            
            div[data-testid="stDownloadButton"] > button:hover {
                background-color: #fff5e6 !important;
            }
            </style>
            
            
            """, unsafe_allow_html=True)

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
                type="primary"  # Оранжевая кнопка с белым текстом
            )
            if st.session_state.get(f"back_{item.id}"):
                st.query_params.clear()
                st.query_params["page"] = "history"
                st.rerun()

        with col2:
            # Кнопка скачивания с выбором формата
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
                        file_ext = "jpg"
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
            type="secondary"  # Темно-серая кнопка с белым текстом
        )
        if st.session_state.get(f"delete_{item.id}"):
            self.history_service.delete_image_by_id(item.id)
            st.query_params.clear()
            st.query_params["page"] = "history"
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    def render_content(self, history_items):
        st.markdown('<div class="main-content">', unsafe_allow_html=True)

        # Понравившиеся фото
        liked_items = [item for item in history_items if item.is_liked]
        if liked_items:
            st.markdown("<h2 style='text-align: center;'>Понравившиеся</h2>", unsafe_allow_html=True)
            self.display_liked_items(liked_items)

        # Разделитель и текст "Все фото"
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center;'>Все фото</h2>", unsafe_allow_html=True)

        # Все фото (включая понравившиеся)
        self.display_items(history_items)

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
                        # Изображение
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

                        # Дата
                        st.markdown(
                            f"<div style='margin-top: 10px; font-size: 20px; font-weight: bold; text-align: center;'>{item.fix_datetime}</div>",
                            unsafe_allow_html=True)

                        # Кнопки "Посмотреть" и "Лайк"
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            if st.button("Посмотреть", key=f"view_{item_id}_liked", type="primary",
                                         use_container_width=True):
                                self.set_query_params({"view_image": str(item_id)})  # Устанавливаем параметр URL
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
                        # Изображение
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

                        # Дата
                        st.markdown(
                            f"<div style='margin-top: 10px; font-size: 20px; font-weight: bold; text-align: center;'>{item.fix_datetime}</div>",
                            unsafe_allow_html=True)

                        # Кнопки "Посмотреть" и "Лайк"
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            if st.button("Посмотреть", key=f"view_{item_id}", type="primary", use_container_width=True):
                                self.set_query_params({"view_image": str(item_id)})  # Устанавливаем параметр URL
                                st.rerun()

                        with col2:
                            heart = "❤️" if self.liked_states[item_id] else "🤍"
                            if st.button(heart, key=f"like_{item_id}", use_container_width=True):
                                self.history_service.toggle_like_status(item.id)
                                st.rerun()

    def run(self):
        example_image_path = "D:/Projects/Python/diploma_project/saved_images/front/example_1.png"


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
            self.auth.auth_service.get_user_by_id(user_id)

        history_data = self.history_service.image_repo.get_user_images(user_id)

        self.render_header()

        # Получаем ID изображения из URL (если есть)
        image_id = self.get_query_params()

        if image_id:
            # Находим изображение по ID
            selected_item = next((item for item in history_data if str(item.id) == image_id), None)
            if selected_item:
                self.render_image_view(selected_item)
            else:
                st.error("Изображение не найдено!")
                self.set_query_params({"view_image": None})  # Очищаем параметр
                st.rerun()
        else:
            self.render_content(history_data)