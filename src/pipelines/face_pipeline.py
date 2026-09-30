import dlib
import numpy as np
import face_recognition_models
from sklearn.svm import SVC
import streamlit as st

from src.database.db import get_all_students


# ============================================================
# LOAD DLIB MODELS
# ============================================================

@st.cache_resource
def load_dlib_models():

    detector = dlib.get_frontal_face_detector()

    sp = dlib.shape_predictor(
        face_recognition_models.pose_predictor_model_location()
    )

    facerec = dlib.face_recognition_model_v1(
        face_recognition_models.face_recognition_model_location()
    )

    return detector, sp, facerec


# ============================================================
# GET FACE EMBEDDINGS FROM IMAGE
# ============================================================

def get_face_embeddings(image_np):

    detector, sp, facerec = load_dlib_models()

    faces = detector(image_np, 1)

    encodings = []

    for face in faces:

        shape = sp(
            image_np,
            face
        )

        face_descriptor = facerec.compute_face_descriptor(
            image_np,
            shape,
            1
        )

        encodings.append(
            np.array(face_descriptor)
        )

    return encodings


# ============================================================
# TRAIN SVM MODEL
# ============================================================

@st.cache_resource
def get_trained_model():

    X = []
    y = []

    student_db = get_all_students()

    if not student_db:
        return None

    for student in student_db:

        embedding = student.get("face_embedding")

        student_id = student.get("id")

        if embedding and student_id is not None:

            X.append(
                np.array(embedding)
            )

            y.append(
                student_id
            )

    if len(X) == 0:
        return None

    clf = SVC(
        kernel="linear",
        probability=True,
        class_weight="balanced"
    )

    try:

        clf.fit(
            X,
            y
        )

    except ValueError:

        return None

    return {
        "clf": clf,
        "X": X,
        "y": y
    }


# ============================================================
# RETRAIN / CLEAR MODEL CACHE
# ============================================================

def train_classifier():

    st.cache_resource.clear()

    model_data = get_trained_model()

    return bool(model_data)


# ============================================================
# PREDICT ATTENDANCE
# ============================================================

import dlib
import numpy as np
import face_recognition_models
from sklearn.svm import SVC
import streamlit as st

from src.database.db import get_all_students


@st.cache_resource
def load_dlib_models():

    detector = dlib.get_frontal_face_detector()

    sp = dlib.shape_predictor(
        face_recognition_models.pose_predictor_model_location()
    )

    facerec = dlib.face_recognition_model_v1(
        face_recognition_models.face_recognition_model_location()
    )

    return detector, sp, facerec


def get_face_embeddings(image_np):

    detector, sp, facerec = load_dlib_models()

    faces = detector(image_np, 1)

    encodings = []

    for face in faces:

        shape = sp(
            image_np,
            face
        )

        face_descriptor = facerec.compute_face_descriptor(
            image_np,
            shape,
            1
        )

        encodings.append(
            np.array(face_descriptor)
        )

    return encodings


@st.cache_resource
def get_trained_model():

    X = []
    y = []

    student_db = get_all_students()

    if not student_db:
        return None

    for student in student_db:

        embedding = student.get("face_embedding")

        # KEEP student_id because this is your database field
        student_id = student.get("student_id")

        if embedding and student_id is not None:

            X.append(
                np.array(embedding)
            )

            y.append(
                student_id
            )

    if len(X) == 0:
        return None

    clf = SVC(
        kernel="linear",
        probability=True,
        class_weight="balanced"
    )

    try:

        clf.fit(
            X,
            y
        )

    except ValueError:

        return None

    return {
        "clf": clf,
        "X": X,
        "y": y
    }


def train_classifier():

    st.cache_resource.clear()

    model_data = get_trained_model()

    return bool(model_data)


def predict_attendance(class_image_np):

    # ========================================================
    # 1. DETECT FACES
    # ========================================================

    encodings = get_face_embeddings(
        class_image_np
    )

    # Temporary debugging
    st.write(
        "Faces detected:",
        len(encodings)
    )

    detected_student = {}

    # ========================================================
    # 2. LOAD TRAINED MODEL
    # ========================================================

    model_data = get_trained_model()

    if not model_data:

        return (
            detected_student,
            [],
            len(encodings)
        )

    X_train = model_data["X"]
    y_train = model_data["y"]

    # ========================================================
    # 3. GET REGISTERED STUDENTS
    # ========================================================

    all_students = sorted(
        list(set(y_train))
    )

    if not all_students:

        return (
            detected_student,
            [],
            len(encodings)
        )

    # ========================================================
    # 4. MATCH EACH DETECTED FACE
    #    AGAINST ALL STORED EMBEDDINGS
    # ========================================================

    for encoding in encodings:

        distances = []

        for train_embedding in X_train:

            distance = np.linalg.norm(
                np.array(train_embedding) - encoding
            )

            distances.append(distance)

        if not distances:
            continue

        # Find closest stored face
        best_index = int(
            np.argmin(distances)
        )

        best_match_score = distances[
            best_index
        ]

        predicted_id = y_train[
            best_index
        ]

        # ====================================================
        # DEBUG INFORMATION
        # ====================================================

        st.write(
            "Predicted student:",
            predicted_id,
            "Face distance:",
            round(best_match_score, 4)
        )

        # ====================================================
        # MATCH THRESHOLD
        # ====================================================

        resemblance_threshold = 0.6

        # ====================================================
        # ACCEPT MATCH
        # ====================================================

        if best_match_score <= resemblance_threshold:

            try:

                student_id = int(
                    predicted_id
                )

            except (TypeError, ValueError):

                continue

            detected_student[
                student_id
            ] = True

    # ========================================================
    # 5. RETURN RESULTS
    # ========================================================

    return (
        detected_student,
        all_students,
        len(encodings)
    )