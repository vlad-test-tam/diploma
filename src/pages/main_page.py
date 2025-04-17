import os
import uuid
from datetime import datetime

from PIL import Image
import streamlit as st
from streamlit_image_comparison import image_comparison

from src.models.user import User
from src.pages.auth_page import AuthPage
from src.services.account_service import AccountService
from src.services.main_service import MainService
from src.utils.ui import UserInterfaceUtils


class MainPage:
    def __init__(self, auth: AuthPage, upload_folder=r"D:\Projects\Python\diploma_project\saved_images\storage", logo_path="", example_img_path="", arrow_left_path="", arrow_right_path=""):
        self.upload_folder = upload_folder
        self.logo_path = logo_path
        self.example_img_path = example_img_path
        self.arrow_left_path = arrow_left_path
        self.arrow_right_path = arrow_right_path
        self.ui_utils = UserInterfaceUtils()
        self.main_service = MainService()
        self.account_service = AccountService()
        self.auth = auth
        os.makedirs(self.upload_folder, exist_ok=True)

    def setup_session_state(self):
        for key, default in {
            "state": "initial",
        }.items():
            if key not in st.session_state:
                st.session_state[key] = default

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
                display: inline-block;
                text-align: center;
            }}

            .header-buttons a:hover {{
                background-color: #3a3e45;
            }}

            .main-content {{
                margin-top: 130px;
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

    def inject_styles(self):
        st.markdown("""
        <style>
        .stButton > button {
            background-color: #ff6600;
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            border: 2px solid #ff6600;
            font-size: 16px;
            cursor: pointer;
            transition: background-color 0.3s ease;
            width: 100%;
        }

        .stButton > button:hover {
            background-color: #e67300;
        }

        .usage-box {
            padding: 6px 16px;
            border-radius: 8px;
            background-color: transparent;
            color: orange;
            border: 2px solid orange;
            font-weight: 500;
            display: flex;
            align-items: center;
            height: 38px;
        }

        .stCheckbox > div > div > div {
            font-size: 16px;
            color: #333333;
            justify-content: center;
            align-items: center;
        }

        .stCheckbox input[type="checkbox"]:checked {
            background-color: #ff6600;
        }
        </style>
        """, unsafe_allow_html=True)

    def reset_app(self):
        st.session_state.state = "initial"
        st.session_state.uploaded_image = None
        st.session_state.original_image = None
        st.session_state.result_image = None

    def process_image(self):
        st.session_state.state = "processing"
        st.rerun()

    def handle_processing(self, filename, show_steps):
        processed_image, masked_image = self.main_service.image_processing(st.session_state.uploaded_image, self.upload_folder, filename)
        st.session_state.original_image = st.session_state.uploaded_image
        st.session_state.masked_image = masked_image
        st.session_state.result_image = processed_image

        defected_image = Image.open(st.session_state.original_image)
        defected_image.save(self.upload_folder + "/defected/" + filename)
        st.session_state.result_image.save(self.upload_folder + "/fixed/" + filename)

        if not show_steps:
            st.session_state.state = "processed"
        else:
            st.session_state.state = "processed_with_steps"
        st.rerun()

    def render_ui(self, user_info: User):
        self.inject_styles()
        free_uses = user_info.free_attempts_count
        is_subscription_active, remain_time = self.account_service.calculate_subscription_time_left(user_info)
        st.markdown('<div class="main-content">', unsafe_allow_html=True)

        st.markdown(
            """
            <h1 style='font-size: 65px; color: #222222; text-align: center; margin-bottom: 50px;'>
                ОДИН счастливый пользователь по всему миру!
            </h1>
            <h1 style='font-size: 50px; color: #222222; text-align: center; margin-bottom: 60px;'>
                Исправляйте быстро свои изображения
            </h1>
            """,
            unsafe_allow_html=True
        )
        if free_uses > 0 and st.session_state.state != "processed":
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
                self.main_service.decrease_attempts_count(user_info.id)

                st.markdown(
                    """
                    <div style='padding: 15px; background-color: #ff6600; color: white; border-radius: 8px; font-size: 18px; text-align: center;'>
                        🚀 Обработка изображения...
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                filename = self.generate_unique_filename(st.session_state.uploaded_image.name)
                st.session_state["filename"] = filename
                self.handle_processing(filename, st.session_state["show_steps"])
            else:
                st.error("У вас закончились бесплатные попытки, купите подписку")

        elif st.session_state.state == "processed" or st.session_state.state == "processed_with_steps":
            defected_file_path = os.path.join(self.upload_folder, "defected", st.session_state["filename"])
            print("upload_folder", self.upload_folder)
            fixed_file_path = os.path.join(self.upload_folder, "fixed", st.session_state["filename"])
            masked_file_path = os.path.join(self.upload_folder, "masked", st.session_state["filename"])
            segmented_file_path = os.path.join(self.upload_folder, "segmented", st.session_state["filename"])

            st.markdown("<h3 style='text-align:center;'>Результат обработки:</h3>", unsafe_allow_html=True)
            image_comparison(
                img1=Image.open(st.session_state.original_image),
                img2=st.session_state.result_image,
                label1="До", label2="После"
            )
            if st.session_state.state == "processed_with_steps":
                st.markdown("<h4 style='text-align:center;'>Маска изображения:</h4>", unsafe_allow_html=True)
                st.image(st.session_state.masked_image, use_container_width=True)
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Сохранить результат"):
                    self.main_service.add_image(user_info.id, False, defected_file_path, fixed_file_path, masked_file_path, segmented_file_path)
                    st.success("Изображение сохранено")
            with col2:
                if st.button("⭐ Добавить в понравившиеся"):
                    self.main_service.add_image(user_info.id, True, defected_file_path, fixed_file_path,
                                                masked_file_path, segmented_file_path)
                    st.success("Изображение сохранено")

            st.button("🔙 Вернуться", on_click=self.reset_app)

        st.markdown('</div>', unsafe_allow_html=True)

    def generate_unique_filename(self, original_filename: str) -> str:
        ext = original_filename.split('.')[-1]
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = uuid.uuid4().hex
        return f"{timestamp}_{unique_id}.{ext}"

    def render_description_and_faq(self):
        example = self.ui_utils.get_image_base64(self.example_img_path)
        left = self.ui_utils.get_image_base64(self.arrow_left_path)
        right = self.ui_utils.get_image_base64(self.arrow_right_path)

        to_right_arrow_img_html = f"""
        <div style='margin: 30px 0; display: flex; justify-content: center;'>
            <img src="data:image/png;base64,{right}" style='height: 75px;' />
        </div>
        """

        # Центрированное изображение-стрелка
        to_left_arrow_img_html = f"""
        <div style='margin: 30px 0; display: flex; justify-content: center;'>
            <img src="data:image/png;base64,{left}" style='height: 75px;' />
        </div>
        """

        # Здесь можно вывести карточки и FAQ, аналогично как было в оригинале
        card1 = f"""
            <div style='width: 700px; height: 250px; background-color: #f3f3f3; border-radius: 12px; display: flex; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin-top: 100px;'>
                <div style='flex: 5;'>
                    <img src="data:image/png;base64,{example}" style='height: 100%; width: 100%; object-fit: cover;' />
                </div>
                <div style='flex: 8; padding: 20px; display: flex; align-items: center; justify-content: center;'>
                    <p style='font-size: 18px; color: #222; text-align: center;'>
                        Это первое описание — здесь можно рассказать, что делает система или показать пример исправления.
                    </p>
                </div>
            </div>
            """

        card2 = f"""
            <div style='width: 700px; height: 250px; background-color: #f3f3f3; border-radius: 12px; display: flex; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.1);'>
                <div style='flex: 8; padding: 20px; display: flex; align-items: center; justify-content: center;'>
                    <p style='font-size: 18px; color: #222; text-align: center;'>
                        Второй пример: можно продемонстрировать шаг обработки или результат сравнения до/после.
                    </p>
                </div>
                <div style='flex: 5;'>
                    <img src="data:image/png;base64,{example}" style='height: 100%; width: 100%; object-fit: cover;' />
                </div>
            </div>
            """

        card3 = f"""
            <div style='width: 700px; height: 250px; background-color: #f3f3f3; border-radius: 12px; display: flex; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin-bottom: 60px;'>
                <div style='flex: 5;'>
                    <img src="data:image/png;base64,{example}" style='height: 100%; width: 100%; object-fit: cover;' />
                </div>
                <div style='flex: 8; padding: 20px; display: flex; align-items: center; justify-content: center;'>
                    <p style='font-size: 18px; color: #222; text-align: center;'>
                        Третий блок может содержать отзывы, подсказки или любые важные моменты работы с системой.
                    </p>
                </div>
            </div>
            """

        # Выводим карточки по очереди
        st.markdown("<div style='display: flex; flex-direction: column; align-items: center;'>", unsafe_allow_html=True)
        st.markdown(card1, unsafe_allow_html=True)
        st.markdown(to_left_arrow_img_html, unsafe_allow_html=True)
        st.markdown(card2, unsafe_allow_html=True)
        st.markdown(to_right_arrow_img_html, unsafe_allow_html=True)
        st.markdown(card3, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # ---------- FAQ секция ----------
        st.markdown(
            """
            <h2 style='text-align: center; color: #222222; margin-top: 60px;'>
                Популярные вопросы:
            </h2>
            <div style='max-width: 700px; margin: 30px auto 0 auto;'>
            <details style='background-color: #2e2e2e; padding: 10px; border-radius: 8px; margin-bottom: 10px;'>
                <summary style='cursor: pointer; color: #f5c518; font-size: 18px;'>Какой формат изображений поддерживается?</summary>
                <p style='color: white; padding-left: 15px;'>Вы можете загружать изображения в формате JPG, JPEG и PNG.</p>
            </details>
            <details style='background-color: #2e2e2e; padding: 10px; border-radius: 8px; margin-bottom: 10px;'>
                <summary style='cursor: pointer; color: #f5c518; font-size: 18px;'>Где сохраняются загруженные изображения?</summary>
                <p style='color: white; padding-left: 15px;'>Все изображения сохраняются в папку <code>uploaded_images</code> внутри проекта.</p>
            </details>
            <details style='background-color: #2e2e2e; padding: 10px; border-radius: 8px; margin-bottom: 10px;'>
                <summary style='cursor: pointer; color: #f5c518; font-size: 18px;'>Как изменить изображение после загрузки?</summary>
                <p style='color: white; padding-left: 15px;'>Просто загрузите новое изображение — оно заменит предыдущее.</p>
            </details>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown('</div>', unsafe_allow_html=True)

    def run(self):
        self.setup_session_state()
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
        self.render_ui(user)
        self.render_description_and_faq()
