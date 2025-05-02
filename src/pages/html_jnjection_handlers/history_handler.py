from src.pages.html_jnjection_handlers.base_handler import BaseInjectionHandler


class HistoryInjectionHandler(BaseInjectionHandler):
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
                <img src="data:image/png;base64,{logo}" alt="Logo" />
                <div class="header-buttons">
                    <a href="/" target="_self">Главная</a>
                    <a href="/?page=history" target="_self">История</a>
                    <a href="/?page=account" target="_self">Аккаунт</a>
                </div>
            </div>
            """, unsafe_allow_html=True)

    def button_styles_injection(self, st):
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
