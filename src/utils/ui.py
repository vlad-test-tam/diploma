import base64


class UserInterfaceUtils:
    def get_image_base64(self, image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()

    def init_paths(self):
        return {
            "temp_folder": r"saved_images\buff",
            "upload_folder": r"saved_images\storage",
            "logo_path": r"saved_images\front\logo-flawless.png",
            "arrow_left_path": r"saved_images\front\right_to_left.png",
            "arrow_right_path": r"saved_images\front\left_to_right.png",
            "example1_path": r"saved_images\front\ex_1.png",
            "example2_path": r"saved_images\front\ex_2.png",
            "example3_path": r"saved_images\front\ex_3.png"
        }

    def get_current_user(self, st, auth):
        if 'USER_ID' not in st.session_state:
            if 'USER_ID' in auth.cookies:
                st.session_state['USER_ID'] = int(auth.cookies['USER_ID'])
        if 'USER_ID' not in st.session_state or not st.session_state['USER_ID']:
            st.warning("Пожалуйста, войдите в систему")
            return
        user_id = st.session_state['USER_ID']
        if not user_id:
            st.warning("Пожалуйста, войдите в систему")
            return
        else:
            user = auth.auth_service.get_user_by_id(user_id)
            return user


