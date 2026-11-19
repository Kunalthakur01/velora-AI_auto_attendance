import streamlit as st

from src.ui.base_layout import style_background_dashboard, style_base_layout

from src.components.header import header_dashboard
from src.components.footer import footer_dashboard

from PIL import Image
import numpy as np
import time

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

from src.components.dialog_enroll import enroll_dialog
from src.components.subject_card import subject_card


# ============================================================
# STUDENT DASHBOARD
# ============================================================

def student_dashboard():

    student_data = st.session_state.student_data
    student_id = student_data["student_id"]

    c1, c2 = st.columns(
        2,
        vertical_alignment="center",
        gap="xxlarge"
    )

    with c1:
        header_dashboard()

    with c2:
        st.subheader(f'Welcome, {student_data["name"]}')

        if st.button(
            "Logout",
            type="secondary",
            key="student_logout_btn",
            shortcut="control+backspace"
        ):
            st.session_state["is_logged_in"] = False
            st.session_state.pop("user_role", None)
            st.session_state.pop("student_data", None)

            # Clear registration state too
            st.session_state.pop("student_registration", None)
            st.session_state.pop("registration_photo", None)

            st.rerun()

    st.space()

    c1, c2 = st.columns(2)

    with c1:
        st.header("Your Enrolled Subjects")

    with c2:
        if st.button(
            "Enroll in Subject",
            type="primary",
            width="stretch",
            key="enroll_subject_btn"
        ):
            enroll_dialog()

    st.divider()

    # --------------------------------------------------------
    # LOAD SUBJECTS + ATTENDANCE
    # --------------------------------------------------------

    with st.spinner("Loading your enrolled subjects.."):

        subjects = get_student_subjects(student_id)
        logs = get_student_attendance(student_id)

    # --------------------------------------------------------
    # ATTENDANCE STATISTICS
    # --------------------------------------------------------

    stats_map = {}

    for log in logs:

        sid = log["subject_id"]

        if sid not in stats_map:
            stats_map[sid] = {
                "total": 0,
                "attended": 0
            }

        stats_map[sid]["total"] += 1

        if log.get("is_present"):
            stats_map[sid]["attended"] += 1

    # --------------------------------------------------------
    # SUBJECT CARDS
    # --------------------------------------------------------

    cols = st.columns(2)

    for i, sub_node in enumerate(subjects):

        sub = sub_node["subjects"]

        sid = sub["subject_id"]

        stats = stats_map.get(
            sid,
            {
                "total": 0,
                "attended": 0
            }
        )

        def unenroll_button(
            sid=sid,
            subject_name=sub["name"]
        ):

            if st.button(
                "Unenroll from this course",
                key=f"unenroll_{sid}",
                type="tertiary",
                width="stretch",
                icon=":material/delete_forever:"
            ):

                unenroll_student_to_subject(
                    student_id,
                    sid
                )

                st.toast(
                    f"Unenrolled from {subject_name} successfully!"
                )

                st.rerun()

        with cols[i % 2]:

            subject_card(
                name=sub["name"],
                code=sub["subject_code"],
                section=sub["section"],
                stats=[
                    (
                        "📅",
                        "Total",
                        stats["total"]
                    ),
                    (
                        "✅",
                        "Attended",
                        stats["attended"]
                    )
                ],
                footer_callback=unenroll_button
            )

    footer_dashboard()


# ============================================================
# STUDENT LOGIN / REGISTRATION
# ============================================================

def student_screen():

    # --------------------------------------------------------
    # PAGE STYLING
    # --------------------------------------------------------

    style_background_dashboard()
    style_base_layout()

    # --------------------------------------------------------
    # INITIALIZE SESSION STATE
    # --------------------------------------------------------

    if "student_registration" not in st.session_state:
        st.session_state.student_registration = False

    if "registration_photo" not in st.session_state:
        st.session_state.registration_photo = None

    # --------------------------------------------------------
    # IF ALREADY LOGGED IN
    # --------------------------------------------------------

    if "student_data" in st.session_state:

        student_dashboard()

        return

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    c1, c2 = st.columns(
        2,
        vertical_alignment="center",
        gap="xxlarge"
    )

    with c1:
        header_dashboard()

    with c2:

        if st.button(
            "Go back to Home",
            type="secondary",
            key="student_home_btn",
            shortcut="control+backspace"
        ):

            st.session_state["login_type"] = None

            st.session_state.student_registration = False
            st.session_state.registration_photo = None

            st.rerun()

    # ========================================================
    # REGISTRATION MODE
    # ========================================================

    if st.session_state.student_registration:

        st.header(
            "Register New Student",
            text_alignment="center"
        )

        st.space()

        # ----------------------------------------------------
        # GET SAVED PHOTO
        # ----------------------------------------------------

        photo_source = st.session_state.registration_photo

        if photo_source is None:

            st.error(
                "Registration photo is missing. "
                "Please capture your face again."
            )

            if st.button(
                "Back to Face Login",
                key="back_to_face_login_btn"
            ):

                st.session_state.student_registration = False

                st.rerun()

            footer_dashboard()

            return

        # ----------------------------------------------------
        # REGISTRATION FORM
        # ----------------------------------------------------

        with st.container(border=True):

            st.subheader("Create your profile")

            st.image(
                photo_source,
                caption="Captured face",
                width=250
            )

            new_name = st.text_input(
                "Enter your name",
                placeholder="E.g. Hamza Rizvi",
                key="new_student_name"
            )

            st.subheader("Optional: Voice Enrollment")

            st.info(
                "Enroll your voice for voice-only attendance."
            )

            audio_data = None

            try:

                audio_data = st.audio_input(
                    "Record a short phrase like "
                    "'I am present' or 'My name is Akash'.",
                    key="registration_voice"
                )

            except Exception as e:

                st.warning(
                    f"Voice enrollment is unavailable: {e}"
                )

            # ------------------------------------------------
            # CREATE ACCOUNT
            # ------------------------------------------------

            if st.button(
                "Create Account",
                type="primary",
                width="stretch",
                key="create_student_btn"
            ):

                if not new_name.strip():

                    st.warning(
                        "Please enter your name!"
                    )

                else:

                    with st.spinner(
                        "Creating your profile..."
                    ):

                        try:

                            # --------------------------------
                            # CONVERT IMAGE
                            # --------------------------------

                            img = np.array(
                                Image.open(photo_source)
                            )

                            # --------------------------------
                            # GET FACE EMBEDDING
                            # --------------------------------

                            encodings = get_face_embeddings(img)

                            if not encodings:

                                st.error(
                                    "Couldn't capture your "
                                    "facial features. "
                                    "Please try again with "
                                    "better lighting."
                                )

                            else:

                                # ----------------------------
                                # FACE EMBEDDING
                                # ----------------------------

                                face_emb = encodings[0].tolist()

                                # ----------------------------
                                # VOICE EMBEDDING
                                # ----------------------------

                                voice_emb = None

                                if audio_data is not None:

                                    try:

                                        voice_bytes = (
                                            audio_data.read()
                                        )

                                        if voice_bytes:

                                            voice_emb = (
                                                get_voice_embedding(
                                                    voice_bytes
                                                )
                                            )

                                    except Exception as voice_error:

                                        st.warning(
                                            "Voice enrollment "
                                            "failed, but you can "
                                            "continue with face "
                                            "registration."
                                        )

                                        st.caption(
                                            str(voice_error)
                                        )

                                # ----------------------------
                                # CREATE STUDENT
                                # ----------------------------

                                response_data = create_student(
                                    new_name.strip(),
                                    face_embedding=face_emb,
                                    voice_embedding=voice_emb
                                )

                                # ----------------------------
                                # CHECK DATABASE RESPONSE
                                # ----------------------------

                                if response_data:

                                    # ------------------------
                                    # RETRAIN CLASSIFIER
                                    # ------------------------

                                    try:

                                        train_classifier()

                                    except Exception as train_error:

                                        st.warning(
                                            "Student was created, "
                                            "but the face classifier "
                                            "could not be retrained."
                                        )

                                        st.caption(
                                            str(train_error)
                                        )

                                    # ------------------------
                                    # LOGIN NEW STUDENT
                                    # ------------------------

                                    st.session_state.is_logged_in = True

                                    st.session_state.user_role = (
                                        "student"
                                    )

                                    st.session_state.student_data = (
                                        response_data[0]
                                    )

                                    # ------------------------
                                    # CLEAR REGISTRATION STATE
                                    # ------------------------

                                    st.session_state.student_registration = (
                                        False
                                    )

                                    st.session_state.registration_photo = (
                                        None
                                    )

                                    st.session_state.pop(
                                        "new_student_name",
                                        None
                                    )

                                    st.toast(
                                        f"Profile Created! "
                                        f"Hi {new_name.strip()}! 🎉"
                                    )

                                    time.sleep(1)

                                    st.rerun()

                                else:

                                    st.error(
                                        "Student account could not "
                                        "be created. Please check "
                                        "your database connection "
                                        "and try again."
                                    )

                        except Exception as e:

                            st.error(
                                "Registration failed."
                            )

                            st.exception(e)

        # ----------------------------------------------------
        # BACK BUTTON
        # ----------------------------------------------------

        st.space()

        if st.button(
            "← Back to Face Login",
            key="registration_back_btn"
        ):

            st.session_state.student_registration = False
            st.session_state.registration_photo = None

            st.rerun()

        footer_dashboard()

        return

    # ========================================================
    # NORMAL FACE LOGIN MODE
    # ========================================================

    st.header(
        "Login using FaceID",
        text_alignment="center"
    )

    st.space()
    st.space()

    # --------------------------------------------------------
    # CAMERA
    # --------------------------------------------------------

    photo_source = st.camera_input(
        "Position your face in the center",
        key="student_face_camera"
    )

    # --------------------------------------------------------
    # PROCESS FACE
    # --------------------------------------------------------

    if photo_source:

        img = np.array(
            Image.open(photo_source)
        )

        with st.spinner("AI is scanning.."):

            try:

                detected, all_ids, num_faces = (
                    predict_attendance(img)
                )

            except Exception as e:

                st.error(
                    "Face recognition failed."
                )

                st.exception(e)

                footer_dashboard()

                return

        # ====================================================
        # NO FACE
        # ====================================================

        if num_faces == 0:

            st.warning(
                "Face not found! "
                "Please position your face properly."
            )

        # ====================================================
        # MULTIPLE FACES
        # ====================================================

        elif num_faces > 1:

            st.warning(
                "Multiple faces found. "
                "Please keep only one person in the frame."
            )

        # ====================================================
        # ONE FACE
        # ====================================================

        else:

            # ------------------------------------------------
            # CHECK WHETHER FACE WAS RECOGNIZED
            # ------------------------------------------------

            if detected:

                student_id = list(detected.keys())[0]

                # --------------------------------------------
                # GET CURRENT STUDENTS FROM DATABASE
                # --------------------------------------------

                all_students = get_all_students()

                # --------------------------------------------
                # FIND MATCHING STUDENT
                # --------------------------------------------

                student = next(
                    (
                        s
                        for s in all_students
                        if str(s.get("student_id"))
                        == str(student_id)
                    ),
                    None
                )

                # ============================================
                # EXISTING STUDENT
                # ============================================

                if student:

                    st.session_state.is_logged_in = True

                    st.session_state.user_role = "student"

                    st.session_state.student_data = student

                    st.toast(
                        f"Welcome back {student['name']}! 👋"
                    )

                    time.sleep(1)

                    st.rerun()

                # ============================================
                # CLASSIFIER FOUND AN OLD / INVALID ID
                # ============================================

                else:

                    st.warning(
                        "This face is not linked to an "
                        "active student profile."
                    )

                    st.info(
                        "You can register as a new student below."
                    )

                    # Save photo so it survives rerun
                    st.session_state.registration_photo = (
                        photo_source
                    )

                    st.session_state.student_registration = (
                        True
                    )

                    if st.button(
                        "Register as New Student",
                        type="primary",
                        key="register_invalid_id_btn"
                    ):

                        st.rerun()

            # =================================================
            # FACE NOT RECOGNIZED
            # =================================================

            else:

                st.info(
                    "Face not recognized. "
                    "You can register as a new student."
                )

                # Save photo
                st.session_state.registration_photo = (
                    photo_source
                )

                # Directly enter registration mode
                st.session_state.student_registration = (
                    True
                )

                st.rerun()

    footer_dashboard()
