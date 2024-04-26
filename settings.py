import os, pathlib
import streamlit as st
import os, datetime, json, sys, pathlib, shutil
import pandas as pd
import streamlit as st
from camera_input_live import camera_input_live
import cv2
import face_recognition
import numpy as np
from PIL import Image
import math   
########################################################################################################################
# The Root Directory of the project
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

LOG_CONFIG = os.path.join(ROOT_DIR, 'logging.yml')

STREAMLIT_STATIC_PATH = pathlib.Path(st.__path__[0]) / 'static'

## We create a downloads directory within the streamlit static asset directory and we write output files to it
DOWNLOADS_PATH = (STREAMLIT_STATIC_PATH / "downloads")
if not DOWNLOADS_PATH.is_dir():
    DOWNLOADS_PATH.mkdir()

LOG_DIR = (STREAMLIT_STATIC_PATH / "logs")
if not LOG_DIR.is_dir():
    LOG_DIR.mkdir()

OUT_DIR = (STREAMLIT_STATIC_PATH / "output")
if not OUT_DIR.is_dir():
    OUT_DIR.mkdir()

VISITOR_DB = os.path.join(ROOT_DIR, "visitor_database")
# st.write(VISITOR_DB)

if not os.path.exists(VISITOR_DB):
    os.mkdir(VISITOR_DB)

VISITOR_HISTORY = os.path.join(ROOT_DIR, "visitor_history")
# st.write(VISITOR_HISTORY)

if not os.path.exists(VISITOR_HISTORY):
    os.mkdir(VISITOR_HISTORY)
########################################################################################################################
## Defining Parameters

COLOR_DARK  = (0, 0, 153)
COLOR_WHITE = (255, 255, 255)
COLS_INFO   = ['Name']
COLS_ENCODE = [f'v{i}' for i in range(128)]

## Database
data_path       = VISITOR_DB
file_db         = 'visitors_db.csv'         ## To store user information
file_history    = 'visitors_history.csv'    ## To store visitor history information

## Image formats allowed
allowed_image_type = ['.png', 'jpg', '.jpeg']
################################################### Defining Function ##############################################
def initialize_data():
    if os.path.exists(os.path.join(data_path, file_db)):
        # st.info('Database Found!')
        df = pd.read_csv(os.path.join(data_path, file_db))

    else:
        # st.info('Database Not Found!')
        df = pd.DataFrame(columns=COLS_INFO + COLS_ENCODE)
        df.to_csv(os.path.join(data_path, file_db), index=False)

    return df

#################################################################
def add_data_db(df_visitor_details):
    try:
        df_all = pd.read_csv(os.path.join(data_path, file_db))

        if not df_all.empty:
            # df_all = df_all.append(df_visitor_details, ignore_index=False)
            df_all = pd.concat([df_all, pd.DataFrame(df_visitor_details)], ignore_index=False)
            df_all.drop_duplicates(keep='first', inplace=True)
            df_all.reset_index(inplace=True, drop=True)
            df_all.to_csv(os.path.join(data_path, file_db), index=False)
            # st.success('Details Added Successfully!')
        else:
            df_visitor_details.to_csv(os.path.join(data_path, file_db), index=False)
            st.success('Initiated Data Successfully!')

    except Exception as e:
        st.error(e)

#################################################################
# convert opencv BRG to regular RGB mode
def BGR_to_RGB(image_in_array):
    return cv2.cvtColor(image_in_array, cv2.COLOR_BGR2RGB)

#################################################################
def findEncodings(images):
    encode_list = []

    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encode_list.append(encode)

    return encode_list

#################################################################
def face_distance_to_conf(face_distance, face_match_threshold=0.6):
    if face_distance > face_match_threshold:
        range = (1.0 - face_match_threshold)
        linear_val = (1.0 - face_distance) / (range * 2.0)
        return linear_val
    else:
        range = face_match_threshold
        linear_val = 1.0 - (face_distance / (range * 2.0))
        return linear_val + ((1.0 - linear_val) * np.power(
            (linear_val - 0.5) * 2, 0.2))

#################################################################
def attendance(id, name):
    f_p = os.path.join(VISITOR_HISTORY, file_history)
    # st.write(f_p)

    now = datetime.datetime.now()
    dtString = now.strftime('%Y-%m-%d %H:%M:%S')
    df_attendace_temp = pd.DataFrame(data={ "id"            : [id],
                                            "visitor_name"  : [name],
                                            "Timing"        : [dtString]
                                            })

    if not os.path.isfile(f_p):
        df_attendace_temp.to_csv(f_p, index=False)
        # st.write(df_attendace_temp)
    else:
        df_attendace = pd.read_csv(f_p)
        # df_attendace = df_attendace.append(df_attendace_temp)
        df_attendace = pd.concat([df_attendace, pd.DataFrame(df_attendace_temp)], ignore_index=True)
        df_attendace.to_csv(f_p, index=False)
        # st.write(df_attendace)

#################################################################
def view_attendace():
    f_p = os.path.join(VISITOR_HISTORY, file_history)
    # st.write(f_p)
    df_attendace_temp = pd.DataFrame(columns=["id",
                                              "visitor_name", "Timing"])

    if not os.path.isfile(f_p):
        df_attendace_temp.to_csv(f_p, index=False)
    else:
        df_attendace_temp = pd.read_csv(f_p)

    df_attendace = df_attendace_temp.sort_values(by='Timing',
                                                 ascending=False)
    df_attendace.reset_index(inplace=True, drop=True)

    st.write(df_attendace)

    if df_attendace.shape[0]>0:
        id_chk  = df_attendace.loc[0, 'id']
        id_name = df_attendace.loc[0, 'visitor_name']

        selected_img = st.selectbox('Search Image using ID',
                                    options=['None']+list(df_attendace['id']))

        avail_files = [file for file in list(os.listdir(VISITOR_HISTORY))
                       if ((file.endswith(tuple(allowed_image_type))) &
                                                                              (file.startswith(selected_img) == True))]

        if len(avail_files)>0:
            selected_img_path = os.path.join(VISITOR_HISTORY,
                                             avail_files[0])
            #st.write(selected_img_path)

            ## Displaying Image
            st.image(Image.open(selected_img_path))

########################################################################################################################

def face_confidence(face_distance, face_match_threshold=0.6):
            range_val = (1.0 - face_match_threshold)
            linear_var = (1.0 - face_distance) / (range_val * 2.0)
            
            if face_distance > face_match_threshold:
                return str(round(linear_var * 100, 2)) + '%'
            else:
                value = (linear_var + ((1.0 - linear_var) * (math.pow(linear_var - 0.5, 2) * 2 + 0.2))) * 100
                return str(round(value, 2)) + '%'

class FaceRecognition:
            def __init__(self):
                self.known_face_encodings = []
                self.known_face_names = []
                self.process_current_frame = True
                self.face_locations = []
                self.face_encodings = []
                self.face_names = []
                self.face_confidences = []
                self.encode_faces()

            def encode_faces(self):
                database_data = initialize_data()
                self.known_face_encodings = database_data[COLS_ENCODE].values
                self.known_face_names = database_data[COLS_INFO]

            def run_recognition(self):
                stop_button_pressed = st.button('Stop')
            
                while True:
                    video_capture = cv2.VideoCapture(0)
                    ret, frame = video_capture.read()

                    if self.process_current_frame:
                        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                        # rgb_small_frame = small_frame[:, :, ::-1]
                        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

                        self.face_locations = face_recognition.face_locations(rgb_small_frame)
                        self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)
                        self.face_names = []
                        self.face_confidences = []

                    for face_encoding in self.face_encodings:
                        matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                        name = "Unknown"
                        confidence = "Unknown"

                        face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                        best_match_index = np.argmin(face_distances)

                        if matches[best_match_index]:
                            name = self.known_face_names.loc[best_match_index, 'Name']
                            confidence = face_confidence(face_distances[best_match_index])

                        self.face_names.append(f'{name} ({confidence})')
                        self.face_confidences.append(confidence)

                    self.process_current_frame = not self.process_current_frame
                    for (top, right, bottom, left), name, confidence in zip(self.face_locations, self.face_names, self.face_confidences):
                        top *= 4
                        right *= 4
                        bottom *= 4
                        left *= 4

                        color = (0, 0, 255)
                        if confidence.endswith('%'):
                            confidence_value = float(confidence[:-1])
                            if confidence_value >= 85:
                                color = (0, 255, 0)
                            elif confidence_value >= 75:
                                color = (0, 165, 255)
                            else:
                                color = (0, 0, 255)

                        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, -1)
                        cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)

                    cv2.imshow('Face Recognition', frame)

                    if cv2.waitKey(1) & 0xFF == ord("q") or stop_button_pressed:
                        break

                video_capture.release()
                cv2.destroyAllWindows() 
