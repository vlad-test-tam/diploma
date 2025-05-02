from src.pages.html_jnjection_handlers.base_handler import BaseInjectionHandler


class AccountInjectionHandler(BaseInjectionHandler):
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
                    margin-top: 130px;
                }}
                .plan-box {{
                    background-color: #f3f3f3;
                    border: 2px solid orange;
                    border-radius: 12px;
                    padding: 20px;
                    text-align: center;
                    color: orange;
                    font-weight: 500;
                }}
                .orange-button {{
                    background-color: #1e2228;
                    color: orange;
                    border: 2px solid orange;
                    padding: 10px;
                    border-radius: 8px;
                    width: 100%;
                    font-size: 16px;
                    cursor: pointer;
                    margin-top: 10px;
                }}
                .orange-button:hover {{
                    background-color: #2e3238;
                }}
                .personal-block-title {{
                    font-size: 22px;
                    margin-top: 60px;
                    margin-bottom: 20px;
                    font-weight: bold;
                    text-align: center;
                }}
                .input-button {{
                    background-color: orange;
                    color: white;
                    border: none;
                    padding: 10px;
                    border-radius: 8px;
                    width: 100%;
                    font-size: 16px;
                    cursor: pointer;
                    margin-top: 10px;
                }}
                .input-button:hover {{
                    background-color: #e67300;
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

    def plan_box_styles_injection(self, st):
        st.markdown("""
            <style>
            .plan-box {
                background-color: #f3f3f3;
                border: 2px solid orange;
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                color: orange;
                font-weight: 500;
            }

            .stButton > button {
                background-color: #3a3e45 !important;
                color: white !important;
                border: 2px solid orange !important;
                border-radius: 8px;
                width: 100%;
                padding: 10px;
                font-weight: bold;
                cursor: pointer;
            }

            .stButton > button:hover {
                background-color: #2e2e2e !important;
            }
            </style>
        """, unsafe_allow_html=True)

    def plan_box_injection(self, st, duration_str, price_str):
        st.markdown(f"""
            <div class="plan-box">
                <div style="font-size: 34px; font-weight: bold;">{duration_str}</div>
                <div style="font-size: 30px;"><strong>{price_str}</strong></div>
            </div>
        """, unsafe_allow_html=True)
