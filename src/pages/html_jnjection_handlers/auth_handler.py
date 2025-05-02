from src.pages.html_jnjection_handlers.base_handler import BaseInjectionHandler


class AuthInjectionHandler(BaseInjectionHandler):
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
                <img src="data:image/png;base64,{logo}" alt="Logo" />
                <div class="header-buttons">
                    <a href="/?auth=login" target="_self" {'class="active"' if st.query_params.get('auth') == 'login' else ''}>Вход</a>
                    <a href="/?auth=signup" target="_self" {'class="active"' if st.query_params.get('auth') == 'signup' else ''}>Создать аккаунт</a>
                    <a href="/?auth=reset" target="_self" {'class="active"' if st.query_params.get('auth') == 'reset' else ''}>Сменить пароль</a>
                </div>
            </div>
            """, unsafe_allow_html=True)
