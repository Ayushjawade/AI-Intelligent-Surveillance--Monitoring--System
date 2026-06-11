import streamlit as st
import cv2
import pandas as pd
import time
from PIL import Image
from number_plate import NumberPlateRecognizer
from vehicle_database import (
    init_vehicle_db,
    add_vehicle_record,
    get_vehicle_record,
    insert_vehicle_log,
    fetch_vehicle_records,
    fetch_vehicle_logs)


from config import PROJECT_NAME, ADMIN_USERNAME, ADMIN_PASSWORD
from detector import SurveillanceDetector
from database import init_db, fetch_logs, count_by_threat
from telegram_alert import send_telegram_alert, send_telegram_photo_alert


# -------------------------------
# Page Configuration
# -------------------------------
st.set_page_config(
    page_title="AI Surveillance Admin",
    page_icon="🛡️",
    layout="wide"
)

init_db()
init_vehicle_db()


# -------------------------------
# Custom CSS
# -------------------------------
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #020617, #111827, #1E293B);
        padding: 28px;
        border-radius: 18px;
        border: 1px solid #334155;
        margin-bottom: 24px;
        box-shadow: 0px 4px 20px rgba(0,0,0,0.35);
    }

    .main-title {
        font-size: 34px;
        font-weight: 900;
        color: #F8FAFC;
        text-align: center;
        margin-bottom: 6px;
    }

    .main-subtitle {
        font-size: 16px;
        color: #CBD5E1;
        text-align: center;
    }

    .metric-card {
        background: linear-gradient(180deg, #111827, #020617);
        border: 1px solid #334155;
        padding: 20px;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0px 4px 16px rgba(0,0,0,0.25);
    }

    .metric-title {
        color: #CBD5E1;
        font-size: 15px;
        font-weight: 600;
    }

    .metric-value {
        color: #F8FAFC;
        font-size: 34px;
        font-weight: 900;
        margin-top: 8px;
    }

    .section-card {
        background-color: #111827;
        border: 1px solid #334155;
        padding: 22px;
        border-radius: 16px;
        margin-bottom: 18px;
        box-shadow: 0px 4px 16px rgba(0,0,0,0.25);
    }

    .green-box {
        background: linear-gradient(90deg, #064E3B, #047857);
        color: white;
        padding: 18px;
        border-radius: 14px;
        text-align: center;
        font-size: 24px;
        font-weight: bold;
        border: 1px solid #10B981;
    }

    .orange-box {
        background: linear-gradient(90deg, #7C2D12, #C2410C);
        color: white;
        padding: 18px;
        border-radius: 14px;
        text-align: center;
        font-size: 24px;
        font-weight: bold;
        border: 1px solid #FB923C;
    }

    .red-box {
        background: linear-gradient(90deg, #7F1D1D, #B91C1C);
        color: white;
        padding: 18px;
        border-radius: 14px;
        text-align: center;
        font-size: 24px;
        font-weight: bold;
        border: 1px solid #F87171;
    }

    .login-box {
        background: linear-gradient(180deg, #111827, #020617);
        border: 1px solid #334155;
        padding: 28px;
        border-radius: 18px;
        box-shadow: 0px 4px 20px rgba(0,0,0,0.35);
    }
</style>
""", unsafe_allow_html=True)


# -------------------------------
# Header
# -------------------------------
def page_header():
    st.markdown(f"""
    <div class="main-header">
        <div class="main-title">🛡️ {PROJECT_NAME}</div>
        <div class="main-subtitle">
            Real-Time Object Detection | Threat Classification | Telegram Alert | Detection Logs
        </div>
    </div>
    """, unsafe_allow_html=True)


# -------------------------------
# Login Page
# -------------------------------
def login_page():
    page_header()

    col1, col2, col3 = st.columns([1, 1.1, 1])

    with col2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)

        st.subheader("🔐 Admin Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login to Dashboard", use_container_width=True):
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                st.session_state.logged_in = True
                st.success("Login successful.")
                st.rerun()
            else:
                st.error("Invalid username or password.")

        st.markdown("</div>", unsafe_allow_html=True)


# -------------------------------
# Sidebar
# -------------------------------
def sidebar_panel():
    with st.sidebar:
        st.markdown("""
        <div style="
            text-align: center;
            padding: 10px 5px 5px 5px;
        ">
            <h2 style="
                font-size: 22px;
                margin-bottom: 6px;
                color: #F8FAFC;
                font-weight: 800;
            ">
                🛡️ Control Center
            </h2>
            <p style="
                font-size: 13px;
                color: #94A3B8;
                margin-top: 0px;
            ">
                AI Surveillance Command Dashboard
            </p>
        </div>
        """, unsafe_allow_html=True)

        try:
            logo_img = Image.open("assets/logo.png")
            st.image(
                logo_img,
                caption=None,
                use_container_width=True
            )
        except Exception:
            st.info("Add project logo as assets/logo.png")

        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #0F172A, #1E293B);
            border: 1px solid #334155;
            border-radius: 14px;
            padding: 14px;
            margin-top: 12px;
            margin-bottom: 18px;
            text-align: center;
        ">
            <h4 style="
                color: #F8FAFC;
                margin-bottom: 6px;
                font-size: 16px;
            ">
                AI-Based Surveillance
            </h4>
            <p style="
                color: #CBD5E1;
                font-size: 12px;
                margin-bottom: 0px;
                line-height: 1.5;
            ">
                Threat Detection • Vehicle Verification • Smart Alerts
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### Navigation")

        menu = st.radio(
            "",
            [
                "Dashboard Home",
                "Live Detection",
                "Detection Logs",
                "Alert Center",
                "Camera Settings",
                "Number Plate Scanner",
                "Vehicle Watchlist",
                "Vehicle Logs",
                "Admin Profile",
                "About Project"
            ]
        )

        st.divider()

        st.markdown("""
        <div style="
            background-color: #111827;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 12px;
            margin-bottom: 12px;
        ">
            <p style="
                color: #94A3B8;
                font-size: 12px;
                margin-bottom: 4px;
            ">
                Logged in as
            </p>
            <p style="
                color: #F8FAFC;
                font-size: 14px;
                font-weight: 700;
                margin-bottom: 0px;
            ">
                Ayush S. Jawade
            </p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.run_detection = False
            st.session_state.plate_scanner_running = False
            st.rerun()

    return menu

# -------------------------------
# Dashboard Home
# -------------------------------
def dashboard_home():
    st.subheader("📌 Security Control Dashboard")

    logs = fetch_logs(limit=500)
    threat_counts = count_by_threat()

    total_logs = len(logs)
    green_count = threat_counts.get("GREEN", 0)
    orange_count = threat_counts.get("ORANGE", 0)
    red_count = threat_counts.get("RED", 0)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Detections</div>
            <div class="metric-value">{total_logs}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">GREEN Logs</div>
            <div class="metric-value">{green_count}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">ORANGE Logs</div>
            <div class="metric-value">{orange_count}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">RED Alerts</div>
            <div class="metric-value">{red_count}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    col_a, col_b = st.columns([1.2, 1])

    with col_a:
        st.markdown("""
        <div class="section-card">
            <h3>🧠 System Overview</h3>
            <p>
            This dashboard monitors live camera feeds using YOLOv8 object detection.
            Detected objects are classified into GREEN, ORANGE, and RED threat levels.
            RED alerts are sent to the authorized person through Telegram.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        detection_status = "Running" if st.session_state.get("run_detection", False) else "Stopped"

        st.markdown(f"""
        <div class="section-card">
            <h3>⚙️ System Status</h3>
            <p><b>Detection Status:</b> {detection_status}</p>
            <p><b>Database:</b> Connected</p>
            <p><b>Alert System:</b> Telegram Ready</p>
            <p><b>Admin:</b> Ayush S. Jawade</p>
        </div>
        """, unsafe_allow_html=True)

    if logs:
        st.subheader("🕒 Recent Detection Activity")

        df = pd.DataFrame(
            logs[:10],
            columns=[
                "ID",
                "Timestamp",
                "Camera Source",
                "Detected Object",
                "Confidence",
                "Threat Level",
                "Snapshot Path"
            ]
        )

        st.dataframe(df, use_container_width=True)
    else:
        st.info("No detections yet. Start live detection to generate logs.")


# -------------------------------
# Live Detection Page
# -------------------------------
def live_detection_page():
    st.subheader("📹 Live Detection Center")

    camera_type = st.selectbox(
        "Select Camera Source",
        [
            "Laptop Webcam",
            "Phone Camera on Same Wi-Fi",
            "USB / C-Type Phone Camera",
            "Custom Camera URL"
        ]
    )

    camera_source = None
    camera_label = ""

    if camera_type == "Laptop Webcam":
        camera_source = 0
        camera_label = "Laptop Webcam"

    elif camera_type == "Phone Camera on Same Wi-Fi":
        st.info("Use IP Webcam app. Connect phone and laptop to same Wi-Fi, then enter video URL.")
        ip_url = st.text_input(
            "Phone IP Camera URL",
            value="http://192.168.1.5:8080/video"
        )
        camera_source = ip_url
        camera_label = ip_url

    elif camera_type == "USB / C-Type Phone Camera":
        st.info("For Iriun/DroidCam, try camera index 0, 1, 2, 3, 4 until the correct camera opens.")
        usb_index = st.number_input(
            "Camera Index",
            min_value=0,
            max_value=10,
            value=1
        )
        camera_source = int(usb_index)
        camera_label = f"USB / Virtual Camera Index {usb_index}"

    elif camera_type == "Custom Camera URL":
        custom_url = st.text_input("Enter RTSP / HTTP Camera URL", value="")
        camera_source = custom_url
        camera_label = custom_url

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("▶ Start Detection", use_container_width=True):
            st.session_state.run_detection = True

    with col2:
        if st.button("⏹ Stop Detection", use_container_width=True):
            st.session_state.run_detection = False

    with col3:
        st.write("Camera Source:")
        st.code(camera_label)

    status_placeholder = st.empty()
    threat_placeholder = st.empty()
    frame_placeholder = st.empty()
    detection_placeholder = st.empty()

    if st.session_state.run_detection:
        status_placeholder.success("Detection Running...")

        detector = SurveillanceDetector()
        cap = cv2.VideoCapture(camera_source)

        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 15)

        if not cap.isOpened():
            st.error("Camera not opened. Check camera source, camera index, Iriun app, or IP URL.")
            st.session_state.run_detection = False
            return

        while st.session_state.run_detection:
            ret, frame = cap.read()

            if not ret:
                st.error("Frame not captured. Check camera connection.")
                break

            frame, threat_level, detected_items = detector.process_frame(
                frame,
                camera_label
            )

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            frame_placeholder.image(
                frame_rgb,
                channels="RGB",
                use_container_width=True
            )

            if threat_level == "RED":
                threat_placeholder.markdown(
                    '<div class="red-box">🚨 RED ALERT - HIGH RISK OBJECT DETECTED</div>',
                    unsafe_allow_html=True
                )

            elif threat_level == "ORANGE":
                threat_placeholder.markdown(
                    '<div class="orange-box">⚠️ ORANGE ALERT - SUSPICIOUS OBJECT DETECTED</div>',
                    unsafe_allow_html=True
                )

            else:
                threat_placeholder.markdown(
                    '<div class="green-box">✅ GREEN - NORMAL ACTIVITY</div>',
                    unsafe_allow_html=True
                )

            if detected_items:
                detection_placeholder.write(detected_items)
            else:
                detection_placeholder.info("No object detected in current frame.")

            time.sleep(0.03)

        cap.release()

    else:
        status_placeholder.warning("Detection Stopped")


# -------------------------------
# Detection Logs Page
# -------------------------------
def logs_page():
    st.subheader("📊 Detection Logs")

    logs = fetch_logs(limit=500)

    if not logs:
        st.info("No detection logs found yet.")
        return

    df = pd.DataFrame(
        logs,
        columns=[
            "ID",
            "Timestamp",
            "Camera Source",
            "Detected Object",
            "Confidence",
            "Threat Level",
            "Snapshot Path"
        ]
    )

    threat_filter = st.selectbox(
        "Filter by Threat Level",
        ["All", "GREEN", "ORANGE", "RED"]
    )

    if threat_filter != "All":
        df = df[df["Threat Level"] == threat_filter]

    threat_counts = count_by_threat()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("GREEN Logs", threat_counts.get("GREEN", 0))

    with col2:
        st.metric("ORANGE Logs", threat_counts.get("ORANGE", 0))

    with col3:
        st.metric("RED Logs", threat_counts.get("RED", 0))

    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download Logs as CSV",
        csv,
        "detection_logs.csv",
        "text/csv",
        use_container_width=True
    )


# -------------------------------
# Alert Center
# -------------------------------
def alert_center_page():
    st.subheader("🚨 Alert Center")

    logs = fetch_logs(limit=500)

    if not logs:
        st.info("No alert logs found.")
        return

    df = pd.DataFrame(
        logs,
        columns=[
            "ID",
            "Timestamp",
            "Camera Source",
            "Detected Object",
            "Confidence",
            "Threat Level",
            "Snapshot Path"
        ]
    )

    red_df = df[df["Threat Level"] == "RED"]
    orange_df = df[df["Threat Level"] == "ORANGE"]

    col1, col2 = st.columns(2)

    with col1:
        st.error(f"RED Alerts: {len(red_df)}")

    with col2:
        st.warning(f"ORANGE Alerts: {len(orange_df)}")

    st.markdown("### RED Alert History")
    if not red_df.empty:
        st.dataframe(red_df, use_container_width=True)
    else:
        st.success("No RED alert detected.")

    st.markdown("### ORANGE Alert History")
    if not orange_df.empty:
        st.dataframe(orange_df, use_container_width=True)
    else:
        st.info("No ORANGE alert detected.")


# -------------------------------
# Camera Settings
# -------------------------------
def camera_settings_page():
    st.subheader("⚙️ Camera Settings & Index Tester")

    st.markdown("""
    ### Camera Source Guide

    | Camera Option | Use |
    |---|---|
    | Laptop Webcam | Built-in laptop camera |
    | USB / C-Type Phone Camera | Iriun/DroidCam virtual webcam |
    | Phone Camera on Same Wi-Fi | IP Webcam stream URL |
    | Custom Camera URL | RTSP/HTTP CCTV camera URL |

    ---
    """)

    st.markdown("## 🔍 Camera Index Tester")

    st.info(
        "Use this tester to check which camera index opens your laptop webcam, Iriun camera, or external webcam."
    )

    test_index = st.number_input(
        "Enter Camera Index to Test",
        min_value=0,
        max_value=10,
        value=0,
        step=1
    )

    col1, col2 = st.columns(2)

    with col1:
        test_camera_btn = st.button("📷 Test Camera Index", use_container_width=True)

    with col2:
        stop_test_btn = st.button("⏹ Stop Camera Test", use_container_width=True)

    if "test_camera_running" not in st.session_state:
        st.session_state.test_camera_running = False

    if test_camera_btn:
        st.session_state.test_camera_running = True

    if stop_test_btn:
        st.session_state.test_camera_running = False

    camera_preview_placeholder = st.empty()
    camera_status_placeholder = st.empty()

    if st.session_state.test_camera_running:
        camera_status_placeholder.success(f"Testing Camera Index: {test_index}")

        cap = cv2.VideoCapture(int(test_index))

        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 15)

        if not cap.isOpened():
            camera_status_placeholder.error(
                f"Camera index {test_index} is not available. Try another index."
            )
            st.session_state.test_camera_running = False
            cap.release()
            return

        while st.session_state.test_camera_running:
            ret, frame = cap.read()

            if not ret:
                camera_status_placeholder.error(
                    f"Cannot read frame from camera index {test_index}."
                )
                break

            frame = cv2.resize(frame, (640, 480))

            cv2.putText(
                frame,
                f"Camera Index: {test_index}",
                (30, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            camera_preview_placeholder.image(
                frame_rgb,
                channels="RGB",
                use_container_width=True
            )

            time.sleep(0.03)

        cap.release()
        camera_status_placeholder.warning("Camera test stopped.")

    st.markdown("---")

    st.markdown("""
    ## 📌 How to Use the Camera Index Tester

    1. Enter camera index `0`
    2. Click **Test Camera Index**
    3. Check which camera opens
    4. Click **Stop Camera Test**
    5. Try index `1`, `2`, `3`, etc.

    ### Common Camera Index Pattern

    | Index | Possible Device |
    |---|---|
    | 0 | Laptop webcam or Iriun virtual camera |
    | 1 | Laptop webcam or Iriun virtual camera |
    | 2 | USB/external camera |
    | 3 | Other virtual camera |

    ### For Iriun Webcam

    Iriun usually appears as a virtual webcam. So use:

    ```txt
    USB / C-Type Phone Camera
    ```

    and try indexes:

    ```txt
    0, 1, 2, 3, 4
    ```

    ### For Wi-Fi Phone Camera

    Use IP Webcam app and enter URL like:

    ```txt
    http://PHONE_IP:8080/video
    ```

    ### Speed Optimization Used

    ```python
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 15)
    ```
    """)
# -------------------------------
# Number Plate Scanner Page
# -------------------------------
# -------------------------------
# Number Plate Scanner Page
# -------------------------------
# -------------------------------
# Number Plate Scanner Page
# -------------------------------
def number_plate_scanner_page():
    st.subheader("🚘 Number Plate Scanner")

    st.info(
        "This module reads vehicle number plates using OCR and matches them with the local vehicle watchlist database."
    )

    camera_type = st.selectbox(
        "Select Camera Source for Plate Scanner",
        [
            "Laptop Webcam",
            "USB / C-Type Phone Camera",
            "Custom Camera URL"
        ],
        key="plate_camera_type"
    )

    camera_source = None
    camera_label = ""

    if camera_type == "Laptop Webcam":
        camera_source = 0
        camera_label = "Laptop Webcam"

    elif camera_type == "USB / C-Type Phone Camera":
        plate_usb_index = st.number_input(
            "Camera Index",
            min_value=0,
            max_value=10,
            value=1,
            step=1,
            key="plate_usb_index"
        )
        camera_source = int(plate_usb_index)
        camera_label = f"USB / Virtual Camera Index {plate_usb_index}"

    elif camera_type == "Custom Camera URL":
        custom_url = st.text_input(
            "Enter RTSP / HTTP Camera URL",
            value="",
            key="plate_custom_url"
        )
        camera_source = custom_url
        camera_label = custom_url

    col1, col2 = st.columns(2)

    with col1:
        if st.button("▶ Start Plate Scanner", use_container_width=True):
            st.session_state.plate_scanner_running = True

    with col2:
        if st.button("⏹ Stop Plate Scanner", use_container_width=True):
            st.session_state.plate_scanner_running = False

    frame_placeholder = st.empty()
    result_placeholder = st.empty()
    status_placeholder = st.empty()

    if st.session_state.plate_scanner_running:
        status_placeholder.success("Number Plate Scanner Running...")

        recognizer = NumberPlateRecognizer()
        cap = cv2.VideoCapture(camera_source)

        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 15)

        if not cap.isOpened():
            st.error("Camera not opened. Check camera index or camera source.")
            st.session_state.plate_scanner_running = False
            return

        last_plate = None
        last_scan_time = 0

        while st.session_state.plate_scanner_running:
            ret, frame = cap.read()

            if not ret:
                st.error("Frame not captured.")
                break

            frame = cv2.resize(frame, (640, 480))
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            frame_placeholder.image(
                frame_rgb,
                channels="RGB",
                use_container_width=True
            )

            current_time = time.time()

            # OCR every 3 seconds because OCR is heavy
            if current_time - last_scan_time > 3:
                last_scan_time = current_time

                plate_number, ocr_confidence = recognizer.read_plate_from_frame(frame)

                if plate_number:
                    last_plate = plate_number
                    vehicle_record = get_vehicle_record(plate_number)

                    snapshot_path = ""

                    try:
                        snapshot_path = f"snapshots/plate_{plate_number}_{int(time.time())}.jpg"
                        cv2.imwrite(snapshot_path, frame)
                    except Exception:
                        snapshot_path = ""

                    if vehicle_record:
                        plate, owner_name, vehicle_type, department, status, remarks = vehicle_record

                        insert_vehicle_log(
                            camera_source=camera_label,
                            plate_number=plate,
                            owner_name=owner_name,
                            vehicle_type=vehicle_type,
                            department=department,
                            status=status,
                            snapshot_path=snapshot_path
                        )

                        if status == "RED":
                            result_placeholder.error(
                                f"🚨 BLACKLISTED VEHICLE DETECTED: {plate} | Record: {owner_name} | {remarks}"
                            )

                            current_time_alert = time.time()
                            last_alert_time = st.session_state.last_vehicle_alert_time.get(plate, 0)

                            if current_time_alert - last_alert_time > 30:
                                st.session_state.last_vehicle_alert_time[plate] = current_time_alert

                                alert_caption = f"""
🚨 <b>BLACKLISTED VEHICLE DETECTED</b>

<b>Project:</b> AI Surveillance Monitoring System
<b>Plate Number:</b> {plate}
<b>Record Name:</b> {owner_name}
<b>Vehicle Type:</b> {vehicle_type}
<b>Department:</b> {department}
<b>Camera Source:</b> {camera_label}
<b>Status:</b> RED
<b>Remarks:</b> {remarks}
<b>Date & Time:</b> {time.strftime("%Y-%m-%d %H:%M:%S")}

Immediate vehicle verification required.
"""

                                if snapshot_path:
                                    send_telegram_photo_alert(snapshot_path, alert_caption)
                                else:
                                    send_telegram_alert(alert_caption)

                            else:
                                result_placeholder.info(
                                    f"RED vehicle already alerted recently: {plate}. Waiting before sending another Telegram alert."
                                )

                        elif status == "ORANGE":
                            result_placeholder.warning(
                                f"⚠️ VISITOR / VERIFY VEHICLE: {plate} | Record: {owner_name} | {remarks}"
                            )

                        else:
                            result_placeholder.success(
                                f"✅ AUTHORIZED VEHICLE: {plate} | Record: {owner_name} | {department}"
                            )

                    else:
                        insert_vehicle_log(
                            camera_source=camera_label,
                            plate_number=plate_number,
                            owner_name="Unknown",
                            vehicle_type="Unknown",
                            department="Unknown",
                            status="ORANGE",
                            snapshot_path=snapshot_path
                        )

                        result_placeholder.warning(
                            f"⚠️ UNKNOWN VEHICLE DETECTED: {plate_number} | Not found in watchlist database"
                        )

                else:
                    if last_plate:
                        result_placeholder.info(f"Last detected plate: {last_plate}")
                    else:
                        result_placeholder.info("No number plate detected yet.")

            time.sleep(0.03)

        cap.release()
        status_placeholder.warning("Number Plate Scanner Stopped.")

    else:
        status_placeholder.warning("Number Plate Scanner Stopped.")

# -------------------------------
# Vehicle Logs Page
# -------------------------------
def vehicle_logs_page():
    st.subheader("📋 Vehicle Detection Logs")

    logs = fetch_vehicle_logs(limit=500)

    if not logs:
        st.info("No vehicle logs found yet.")
        return

    df = pd.DataFrame(
        logs,
        columns=[
            "ID",
            "Timestamp",
            "Camera Source",
            "Plate Number",
            "Owner / Record Name",
            "Vehicle Type",
            "Department",
            "Status",
            "Snapshot Path"
        ]
    )

    status_filter = st.selectbox(
        "Filter by Vehicle Status",
        ["All", "GREEN", "ORANGE", "RED"]
    )

    if status_filter != "All":
        df = df[df["Status"] == status_filter]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.success(f"GREEN Vehicles: {len(df[df['Status'] == 'GREEN'])}")

    with col2:
        st.warning(f"ORANGE Vehicles: {len(df[df['Status'] == 'ORANGE'])}")

    with col3:
        st.error(f"RED Vehicles: {len(df[df['Status'] == 'RED'])}")

    st.dataframe(df, use_container_width=True)

    st.markdown("---")
    st.markdown("### Vehicle Evidence Preview")

    for _, row in df.head(10).iterrows():
        with st.expander(
            f"{row['Status']} | {row['Plate Number']} | {row['Timestamp']}",
            expanded=False
        ):
            col_a, col_b = st.columns([1, 1.2])

            with col_a:
                st.markdown(f"""
                **Log ID:** {row["ID"]}  
                **Time:** {row["Timestamp"]}  
                **Camera:** {row["Camera Source"]}  
                **Plate:** {row["Plate Number"]}  
                **Owner / Record:** {row["Owner / Record Name"]}  
                **Vehicle Type:** {row["Vehicle Type"]}  
                **Department:** {row["Department"]}  
                **Status:** {row["Status"]}
                """)

            with col_b:
                snapshot_path = row["Snapshot Path"]

                if snapshot_path:
                    try:
                        st.image(
                            snapshot_path,
                            caption=f"Vehicle Snapshot - {row['Plate Number']}",
                            use_container_width=True
                        )
                    except Exception:
                        st.warning("Snapshot file not found.")
                else:
                    st.info("No snapshot available.")

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download Vehicle Logs CSV",
        csv,
        "vehicle_logs.csv",
        "text/csv",
        use_container_width=True
    )

    # -------------------------------
# Admin Profile Page
# -------------------------------
def admin_profile_page():
    st.subheader("👤 Admin Profile")

    col1, col2 = st.columns([1, 1.6])

    with col1:
        try:
            admin_img = Image.open("assets/admin_photo.jpg")
            st.image(admin_img, caption="Ayush S. Jawade", use_container_width=True)
        except Exception:
            st.info("Add your photo as assets/admin_photo.jpg")

    with col2:
        st.markdown("""
        ## Ayush S. Jawade

        **Role:** System Admin & Project Developer  
        **Project:** AI-Based Intelligent Surveillance Monitoring System  
        **Domain:** Artificial Intelligence | Computer Vision | Security Surveillance  
        **Academic Field:** Diploma in Computer Engineering  

        ---

        ### Project Responsibilities

        - Designed and developed the professional Streamlit admin dashboard
        - Integrated YOLOv8-based real-time object detection
        - Implemented GREEN, ORANGE, and RED threat classification
        - Added Telegram text and image alert system for RED threats
        - Implemented repeated alert control to avoid alert spam
        - Developed SQLite-based detection logs and alert evidence storage
        - Added Alert Center with snapshot preview
        - Added Camera Index Tester for webcam, Iriun, and external camera testing
        - Integrated Number Plate Scanner using OCR
        - Developed Vehicle Watchlist and Vehicle Logs modules
        - Added blacklisted vehicle detection with Telegram image alert
        - Added anti-spam control for repeated blacklisted vehicle alerts

        ---

        ### Technical Skills Used

        - Python
        - OpenCV
        - YOLOv8
        - Streamlit
        - SQLite
        - EasyOCR
        - Telegram Bot API
        - Computer Vision
        - Real-Time Camera Processing
        """)

    st.markdown("---")

    st.markdown("""
    ### Admin Statement

    This project was developed as an AI-powered intelligent surveillance platform for real-time security monitoring, threat detection, evidence logging, and automated alert generation.

    The system is designed to support institutional security, restricted-area monitoring, defence-style surveillance demonstrations, and smart security control-room applications.
    """)
# -------------------------------
# About Project
# -------------------------------
def about_page():
    st.subheader("ℹ️ About Project")

    st.markdown("""
    ## AI-Based Intelligent Surveillance Monitoring System

    This project is designed to monitor live video feeds and identify suspicious objects
    or activities using AI-based object detection.

    ### Main Features

    - Real-time object detection using YOLOv8
    - Laptop webcam support
    - Phone camera support using Iriun / Wi-Fi / USB
    - GREEN, ORANGE, RED threat classification
    - Telegram RED alert system
    - SQLite detection logs
    - Admin dashboard
    - CSV report download

    ### Threat Classification

    | Threat Level | Meaning | Example |
    |---|---|---|
    | GREEN | Normal activity/object | Person, chair, laptop |
    | ORANGE | Suspicious object | Backpack, suitcase, scissors |
    | RED | High-risk object | Knife, weapon |

    ### Developed By

    **Ayush S. Jawade**  
    Backend Developer & Project Lead  
    Diploma in Computer Engineering
    """)


# -------------------------------
# Dashboard Controller
# -------------------------------
def vehicle_watchlist_page():
    st.title("🚗 Vehicle Watchlist")
    st.write("Vehicle Watchlist Module")

def dashboard():
    page_header()

    menu = sidebar_panel()

    if menu == "Dashboard Home":
        dashboard_home()

    elif menu == "Live Detection":
        live_detection_page()

    elif menu == "Detection Logs":
        logs_page()

    elif menu == "Alert Center":
        alert_center_page()

    elif menu == "Camera Settings":
        camera_settings_page()

    elif menu == "Number Plate Scanner":
        number_plate_scanner_page()

    elif menu == "Vehicle Watchlist":
        vehicle_watchlist_page()

    elif menu == "Vehicle Logs":
        vehicle_logs_page()

    elif menu == "Admin Profile":
        admin_profile_page()

    elif menu == "About Project":
        about_page()
# -------------------------------
# Main Controller
# -------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "run_detection" not in st.session_state:
    st.session_state.run_detection = False

if "plate_scanner_running" not in st.session_state:
    st.session_state.plate_scanner_running = False

if "last_vehicle_alert_time" not in st.session_state:
    st.session_state.last_vehicle_alert_time = {}

if st.session_state.logged_in:
    dashboard()
else:
    login_page()