def student_screen():

    style_background_dashboard()
    style_base_layout()

    if "student_data" in st.session_state:
        student_dashboard()
        return

    # ---------------------------------
    # HEADER
    # ---------------------------------
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')

    with c1:
        header_dashboard()

    with c2:
        if st.button(
            "Go back to Home",
            type='secondary',
            key='student_home_btn',
            shortcut="control+backspace"
        ):
            st.session_state['login_type'] = None
            st.session_state.pop('student_registration', None)
            st.session_state.pop('registration_photo', None)
            st.rerun()

    # ---------------------------------
    # REGISTRATION STATE
    # ---------------------------------
    if "student_registration" not in st.session_state:
        st.session_state.student_registration = False

    # ---------------------------------
    # REGISTRATION FORM
    # ---------------------------------
    if st.session_state.student_registration:

        st.header(
            'Register New Student',
            text_alignment='center'
        )

        st.info(
            "Your face was detected but was not recognized. "
            "Create a new profile below."
        )

        with st.container(border=True):

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
                    "'I am present, my name is Akash.'",
                    key="registration_voice"
                )
            except Exception as e:
                st.error(f"Audio recording failed: {e}")

            col1, col2 = st.columns(2)

            with col1:
                create_account = st.button(
                    "Create Account",
                    type="primary",
                    width="stretch",
                    icon=":material/person_add:"
                )

            with col2:
                cancel_registration = st.button(
                    "Cancel",
                    type="secondary",
                    width="stretch"
                )

            # ---------------------------------
            # CANCEL
            # ---------------------------------
            if cancel_registration:
                st.session_state.student_registration = False
                st.session_state.pop("registration_photo", None)
                st.session_state.pop("new_student_name", None)
                st.rerun()

            # ---------------------------------
            # CREATE ACCOUNT
            # ---------------------------------
            if create_account:

                if not new_name.strip():
                    st.warning("Please enter your name.")

                elif "registration_photo" not in st.session_state:
                    st.error(
                        "Registration photo is missing. "
                        "Please capture your face again."
                    )

                else:

                    with st.spinner("Creating your profile..."):

                        try:

                            # Retrieve saved registration image
                            img = np.array(
                                Image.open(
                                    st.session_state.registration_photo
                                ).convert("RGB")
                            )

                            # Extract face embedding
                            encodings = get_face_embeddings(img)

                            if not encodings:
                                st.error(
                                    "Couldn't capture your facial features. "
                                    "Please try again with better lighting."
                                )

                            else:

                                face_emb = encodings[0].tolist()

                                # ---------------------------------
                                # VOICE EMBEDDING
                                # ---------------------------------
                                voice_emb = None

                                if audio_data:
                                    try:
                                        voice_emb = get_voice_embedding(
                                            audio_data.read()
                                        )
                                    except Exception as e:
                                        st.warning(
                                            f"Voice enrollment failed: {e}"
                                        )

                                # ---------------------------------
                                # CREATE STUDENT
                                # ---------------------------------
                                response_data = create_student(
                                    new_name.strip(),
                                    face_embedding=face_emb,
                                    voice_embedding=voice_emb
                                )

                                if response_data:

                                    # Retrain face classifier
                                    train_classifier()

                                    # Login student
                                    student = response_data[0]

                                    st.session_state.is_logged_in = True
                                    st.session_state.user_role = "student"
                                    st.session_state.student_data = student

                                    # Clear registration state
                                    st.session_state.student_registration = False
                                    st.session_state.pop(
                                        "registration_photo",
                                        None
                                    )

                                    st.toast(
                                        f"Profile Created! "
                                        f"Hi {new_name}!",
                                        icon="🎉"
                                    )

                                    time.sleep(1)
                                    st.rerun()

                                else:
                                    st.error(
                                        "Student profile could not be created. "
                                        "Please check your database connection."
                                    )

                        except Exception as e:

                            st.error(
                                f"Registration failed: {str(e)}"
                            )

        footer_dashboard()
        return

    # ---------------------------------
    # FACE LOGIN
    # ---------------------------------
    st.header(
        'Login using FaceID',
        text_alignment='center'
    )

    st.space()
    st.space()

    photo_source = st.camera_input(
        "Position your face in the center",
        key="student_face_camera"
    )

    if photo_source:

        img = np.array(
            Image.open(photo_source).convert("RGB")
        )

        with st.spinner("AI is scanning..."):

            try:

                detected, all_ids, num_faces = predict_attendance(img)

                # ---------------------------------
                # NO FACE
                # ---------------------------------
                if num_faces == 0:

                    st.warning(
                        "Face not found. Please position your face "
                        "inside the camera."
                    )

                # ---------------------------------
                # MULTIPLE FACES
                # ---------------------------------
                elif num_faces > 1:

                    st.warning(
                        "Multiple faces found. "
                        "Please make sure only one person is visible."
                    )

                # ---------------------------------
                # ONE FACE
                # ---------------------------------
                else:

                    if detected:

                        student_id = list(
                            detected.keys()
                        )[0]

                        all_students = get_all_students()

                        student = next(
                            (
                                s for s in all_students
                                if int(s['student_id']) == int(student_id)
                            ),
                            None
                        )

                        if student:

                            st.session_state.is_logged_in = True
                            st.session_state.user_role = "student"
                            st.session_state.student_data = student

                            st.toast(
                                f"Welcome back {student['name']}!",
                                icon="👋"
                            )

                            time.sleep(1)
                            st.rerun()

                        else:

                            st.error(
                                "Student record not found. "
                                "Please contact your teacher."
                            )

                    else:

                        # ---------------------------------
                        # NEW STUDENT
                        # ---------------------------------

                        # Save image so it survives reruns
                        st.session_state.registration_photo = photo_source

                        # Activate registration mode
                        st.session_state.student_registration = True

                        st.rerun()

            except Exception as e:

                st.error(
                    f"Face recognition failed: {str(e)}"
                )

    footer_dashboard()
