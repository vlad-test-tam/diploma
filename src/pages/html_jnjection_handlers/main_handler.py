from src.pages.html_jnjection_handlers.base_handler import BaseInjectionHandler


class MainInjectionHandler(BaseInjectionHandler):
    def header_injection(self, st, logo):
        st.markdown(f"""
            <style>
                .custom-header {{
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 260px;
                    background-color: #1e2228;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    padding-top: 60px;
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
                <img src="data:image/png;base64,{logo}" alt="Logo" />
                <div class="header-buttons">
                    <a href="/" target="_self">Главная</a>
                    <a href="/?page=history" target="_self">История</a>
                    <a href="/?page=account" target="_self">Аккаунт</a>
                </div>
            </div>
            """, unsafe_allow_html=True)

    def styles_injection(self, st):
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

    def greeting_injection(self, st):
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

    def remain_subscription_injection(self, st, before_string, datetime_count, width):
        st.markdown(
            f"""
                <div class='usage-box' style='
                    text-align: center;
                    background-color: #f3f3f3;
                    padding: 10px;
                    border-radius: 8px;
                    margin-bottom: 30px;
                    width: {width}px;
                    margin-left: auto;
                    margin-right: auto;
                    color: orange;
                    border: 2px solid orange;
                    font-weight: 500;
                '>
                    <span>{before_string}: {datetime_count}</span>
                </div>
            """,
            unsafe_allow_html=True
        )

    def arrow_injection(self, st, image):
        st.markdown(f"""
        <div style='margin: 30px 0; display: flex; justify-content: center;'>
            <img src="data:image/png;base64,{image}" style='height: 75px;' />
        </div>
        """, unsafe_allow_html=True)

    def odd_card_injection(self, st, image, description):
        st.markdown(f"""
            <div style='width: 700px; height: 250px; background-color: #f3f3f3; border-radius: 12px; display: flex; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.1);'>
                <div style='flex: 5;'>
                    <img src="data:image/png;base64,{image}" style='height: 100%; width: 100%; object-fit: cover;' />
                </div>
                <div style='flex: 8; padding: 20px; display: flex; align-items: center; justify-content: center;'>
                    <p style='font-size: 18px; color: #222; text-align: center;'>
                        {description}
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)

    def even_card_injection(self, st, image, description):
        st.markdown(f"""
            <div style='width: 700px; height: 250px; background-color: #f3f3f3; border-radius: 12px; display: flex; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.1);'>
                <div style='flex: 8; padding: 20px; display: flex; align-items: center; justify-content: center;'>
                    <p style='font-size: 18px; color: #222; text-align: center;'>
                        {description}
                    </p>
                </div>
                <div style='flex: 5;'>
                    <img src="data:image/png;base64,{image}" style='height: 100%; width: 100%; object-fit: cover;' />
                </div>
            </div>
            """, unsafe_allow_html=True)

    def faq_injection(self, st):
        st.markdown(
            """
            <h2 style='text-align: center; color: #222222; margin-top: 150px;'>
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