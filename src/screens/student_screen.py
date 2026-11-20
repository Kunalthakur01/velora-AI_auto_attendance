import streamlit as st

from src.ui.base_layout import style_background_dashboard, style_base_layout

from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from PIL import Image
import numpy as np

from src.pipelines.face_pipeline import (
    predict_attendance,
    get_face_embeddings,
    train_classifier
)

from src.pipelines.voice_pipeline import get_voice_embedding

from src.database.db import (
    get_all_students,
    create_student,
    get_student_subjects,
    get_student_attendance,
    unenroll_student_to_subject
)

import time

from src.components.dialog_enroll import enroll_dialog
from src.components.subject_card import subject_card


# =========================================================
# STUDENT DASHBOARD
# =========================================================

def student_dashboard():

    student = st.session_state.get("student_data")

    if not student:
        return

    style_background_dashboard()
    style_base_layout()

    # -----------------------------------------------------
    # Header
    # -----------------------------------------------------

    c1, c2 = st.columns(
        2,
        vertical_alignment='center',
        gap='xxlarge'
    )

    with c1:
        header_dashboard()

    with c2:
        if st.button(
            "Logout",
            type='secondary',
            key='student_logout'
        ):
            st.session_state.pop('student_data', None)
            st.session_state.pop('is_logged_in', None)
            st.session_state.pop('user_role', None)
            st.rerun()

    st.header(
        f"Welcome, {student['name']} 👋",
        text_alignment='center'
    )

    # -----------------------------------------------------
    # Student Attendance
    # -----------------------------------------------------

    st.subheader("My Attendance")

    attendance = get_student_attendance(
        student['student_id']
    )

    if attendance:
        st.write(attendance)
    else:
        st.info("No attendance records found.")

    # -----------------------------------------------------
    # My Subjects
    # -----------------------------------------------------

    st.subheader("My Subjects")

    subjects = get_student_subjects(
        student['student_id']
    )

    if subjects:

        for subject in subjects:

            sid = subject.get('subject_id')

            with st.container(border=True):

                subject_card(subject)

                if st.button(
                    "Unenroll from this course",
                    key=f"unenroll_{sid}",
                    type='secondary'
                ):

                    unenroll_student_to_subject(
                        student['student_id'],
                        sid
                    )

                    st.success(
                        "Successfully unenrolled from the course."
                    )

                    time.sleep(1)
                    st.rerun()

    else:

        st.info(
            "You are not enrolled in any subject yet."
        )

    # -----------------------------------------------------
    # Enroll in Subject
    # -----------------------------------------------------

    st.subheader("Enroll in a Subject")

    if st.button(
        "Enroll in Subject",
        type='primary',
        key='student_enroll'
    ):
        enroll_dialog()

    footer_dashboard()


# =========================================================
# STUDENT LOGIN + REGISTRATION
# =========================================================

def student_screen():

    style_background_dashboard()
    style_base_layout()

    # Already logged in
    if "student_data" in st.session_state:
        student_dashboard()
        return

    c1, c2 = st.columns(
        2,
        vertical_alignment='center',
        gap='xxlarge'
    )

    with c1:
        header_dashboard()

    with c2:
        if st.button(
            "Go back to Home",
            type='secondary',
            key='loginbackbtn',
            shortcut="control+backspace"
        ):
            st.session_state['login_type'] = None
            st.rerun()

    st.header(
        'Login using FaceID',
        text_alignment='center'
    )

    st.space()
    st.space()

    show_registration = False

    photo_source = st.camera_input(
        "Position your face in the center"
    )

    if photo_source:

        img = np.array(
            Image.open(photo_source)
        )

        with st.spinner('AI is scanning..'):

            detected, all_ids, num_faces = predict_attendance(img)

            # -------------------------------------------------
            # No face
            # -------------------------------------------------

            if num_faces == 0:

                st.warning(
                    'Face not found! Please position your face correctly.'
                )

            # -------------------------------------------------
            # Multiple faces
            # -------------------------------------------------

            elif num_faces > 1:

                st.warning(
                    'Multiple faces found. '
                    'Please show only one face.'
                )

            # -------------------------------------------------
            # Exactly one face
            # -------------------------------------------------

            else:

                # ---------------------------------------------
                # Face recognized
                # ---------------------------------------------

                if detected:

                    student_id = list(
                        detected.keys()
                    )[0]

                    all_students = get_all_students()

                    student = next(
                        (
                            s for s in all_students
                            if s['student_id'] == student_id
                        ),
                        None
                    )

                    # Student exists → Login
                    if student:

                        st.session_state.is_logged_in = True
                        st.session_state.user_role = 'student'
                        st.session_state.student_data = student

                        st.toast(
                            f'Welcome Back {student["name"]}'
                        )

                        time.sleep(1)
                        st.rerun()

                    # Model recognized ID but DB doesn't contain it
                    else:

                        st.info(
                            'Student not registered. '
                            'Please create a new profile.'
                        )

                        show_registration = True

                # ---------------------------------------------
                # Face not recognized
                # ---------------------------------------------

                else:

                    st.info(
                        'Face not recognized! '
                        'Please create a new student profile.'
                    )

                    show_registration = True

    # =========================================================
    # NEW STUDENT REGISTRATION
    # =========================================================

    if show_registration:

        with st.container(border=True):

            st.header(
                'Register New Profile'
            )

            new_name = st.text_input(
                "Enter your name",
                placeholder='E.g. Hamza Rizvi'
            )

            st.subheader(
                'Optional: Voice Enrollment'
            )

            st.info(
                "Enroll your voice for voice-only attendance."
            )

            audio_data = None

            try:

                audio_data = st.audio_input(
                    'Record a short phrase like '
                    '"I am present" or '
                    '"My name is Akash."'
                )

            except Exception:

                st.error(
                    'Audio data failed!'
                )

            if st.button(
                'Create Account',
                type='primary',
                key='create_student_account'
            ):

                if new_name:

                    with st.spinner(
                        'Creating profile..'
                    ):

                        # Use same captured image
                        img = np.array(
                            Image.open(photo_source)
                        )

                        encodings = get_face_embeddings(
                            img
                        )

                        if encodings:

                            face_emb = encodings[0].tolist()

                            voice_emb = None

                            if audio_data:

                                voice_emb = get_voice_embedding(
                                    audio_data.read()
                                )

                            response_data = create_student(
                                new_name,
                                face_embedding=face_emb,
                                voice_embedding=voice_emb
                            )

                            if response_data:

                                train_classifier()

                                st.session_state.is_logged_in = True
                                st.session_state.user_role = 'student'
                                st.session_state.student_data = response_data[0]

                                st.toast(
                                    f'Profile Created! '
                                    f'Hi {new_name}!'
                                )

                                time.sleep(1)
                                st.rerun()

                        else:

                            st.error(
                                "Couldn't capture your facial "
                                "features for registration."
                            )

                else:

                    st.warning(
                        'Please enter your name!'
                    )

    footer_dashboard()
