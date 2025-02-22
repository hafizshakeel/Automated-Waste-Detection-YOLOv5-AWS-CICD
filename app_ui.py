import os
import cv2
import time
import subprocess
import streamlit as st
from PIL import Image


# Set page config
st.set_page_config(
    page_title="Waste Detection Application",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Import custom CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("styles.css")


# Session state initialization
if 'camera_active' not in st.session_state:
    st.session_state.camera_active = False

# Navigation
st.sidebar.title("Navigation")
app_mode = st.sidebar.radio("", ["Home", "Image Detection", "Video Detection", "Live Camera"])

# Helper functions
def run_yolo_detection(source_path, output_dir="output"):
    """
    Runs YOLOv5 detection on the given source file.
    """
    command = [
        "python", "yolov5/detect.py",
        "--weights", "weights/best_100.pt",
        # "--weights", "yolov5s.pt"  # To check the live camera functionality using actual model
        "--img", "320",
        "--conf", "0.25",
        "--source", source_path,
        "--project", output_dir,
        "--save-txt"
    ]
    try:
        # st.write(f"Running command: {' '.join(command)}")  # Log the command
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            st.error(f"YOLOv5 detection failed with error:\n{result.stderr}")
            return None
        return result
    except Exception as e:
        st.error(f"An error occurred while running YOLOv5: {str(e)}")
        return None


def get_latest_exp_folder(output_dir):
    """
    Finds the latest exp folder created by YOLOv5 (e.g., exp, exp2, exp3).
    """
    folders = [f for f in os.listdir(output_dir) if f.startswith("exp")]
    if not folders:
        st.error("No exp folder found.")
        return None
    latest_folder = max(folders, key=lambda x: int(x[3:]) if x[3:] else 0)
    latest_exp_path = os.path.join(output_dir, latest_folder)
    # st.write(f"Latest exp folder: {latest_exp_path}")
    # st.write(f"Files in exp folder: {os.listdir(latest_exp_path)}")
    return latest_exp_path


def verify_output(output_path):
    """
    Verifies if the output file exists at the specified path.
    """

    # Check for exact match
    if os.path.exists(output_path):
        return True

    st.error(f"Output not found at: {output_path}")
    return False


def process_image(uploaded_file):
    """
    Processes the uploaded image and saves it to the input_images directory.
    """
    image = Image.open(uploaded_file)
    image_path = f"input_images/{uploaded_file.name}"
    os.makedirs(os.path.dirname(image_path), exist_ok=True)
    image.save(image_path)
    return image, image_path


def process_video(uploaded_file):
    """
    Processes the uploaded video and saves it to the input_videos directory.
    Sanitizes the filename to avoid spaces and special characters.
    """
    base_name = os.path.splitext(uploaded_file.name)[0]
    sanitized_name = "".join(char if char.isalnum() else "_" for char in base_name)
    video_path = f"input_videos/{sanitized_name}.mp4"
    os.makedirs(os.path.dirname(video_path), exist_ok=True)
    with open(video_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return video_path


# Main content
if app_mode == "Home":
    st.title("🚀 Waste Detection Application")
    # st.markdown("### Next-Generation Waste Detection System")
    try:
        st.image("data/ai_vision_banner.jpg", use_container_width=True)
    except FileNotFoundError:
        st.warning("Banner image not found.")
    st.markdown("""
    Welcome to our advanced AI vision platform. This system provides:
    - Real-time object detection
    - Image & video analysis
    - Cloud-ready architecture
    - State-of-the-art YOLOv5 model
    """)

elif app_mode == "Image Detection":
    st.title("📸 Image Detection")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Upload Image")
        uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])
        if uploaded_file:
            image, image_path = process_image(uploaded_file)
            st.image(image, caption="Uploaded Image", use_container_width=True)
    with col2:
        if uploaded_file:
            if st.button("Analyze Image"):
                with st.spinner("Detecting objects..."):
                    start_time = time.time()
                    output_dir = "runs/output/images"
                    os.makedirs(output_dir, exist_ok=True)
                    result = run_yolo_detection(image_path, output_dir=output_dir)
                    
                    # Get the latest exp folder
                    latest_exp_folder = get_latest_exp_folder(output_dir)
                    if not latest_exp_folder:
                        st.error("Failed to locate the output folder.")
                    else:
                        output_image = os.path.join(latest_exp_folder, uploaded_file.name)
                        if verify_output(output_image):
                            st.success(f"Analysis completed in {time.time() - start_time:.2f}s")
                            st.markdown("### Detection Results")

                            st.image(output_image, caption="Processed Image", use_container_width=True)
                            # st.json({
                            #     "objects_detected": 5,  # Replace with actual results
                            #     "confidence_scores": [0.92, 0.88, 0.95],
                            #     "processing_time": f"{time.time() - start_time:.2f}s"
                            # })
 

elif app_mode == "Video Detection":
    st.title("🎥 Video Analysis")
    uploaded_video = st.file_uploader("Upload video", type=["mp4", "mov"])
    if uploaded_video:
        video_path = process_video(uploaded_video)
        st.video(uploaded_video)
        if st.button("Process Video"):
            with st.spinner("Analyzing video frames..."):
                progress_bar = st.progress(0)
                output_dir = "runs/output/videos"
                os.makedirs(output_dir, exist_ok=True)
                result = run_yolo_detection(video_path, output_dir=output_dir)
                for percent_complete in range(100):
                    time.sleep(0.02)
                    progress_bar.progress(percent_complete + 1)

                # Get the latest exp folder
                latest_exp_folder = get_latest_exp_folder(output_dir)
                if not latest_exp_folder:
                    st.error("Failed to locate the output folder.")
                else:
                    # Notify the user about the output location
                    st.success("Video processing complete!")
                    st.info(f"The processed video can be found in: `{latest_exp_folder}`")



elif app_mode == "Live Camera":
    st.title("🎥 Real-time Detection")
    cam_placeholder = st.empty()

    # Buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Start Camera") and not st.session_state.camera_active:
            st.session_state.camera_active = True
    with col2:
        if st.button("Stop Camera") and st.session_state.camera_active:
            st.session_state.camera_active = False

    # Camera loop
    if st.session_state.camera_active:
        cap = cv2.VideoCapture(0)
        output_dir = "runs/output/live"
        temp_image_path = f"{output_dir}/temp_frame.jpg"
        os.makedirs(output_dir, exist_ok=True)

        while st.session_state.camera_active and cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                st.error("Camera frame capture failed")
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            cv2.imwrite(temp_image_path, frame)

            with st.spinner("Detecting objects..."):
                run_yolo_detection(temp_image_path, output_dir=output_dir)
                latest_exp_folder = get_latest_exp_folder(output_dir)
                output_image_path = f"{latest_exp_folder}/temp_frame.jpg" if latest_exp_folder else None
                if output_image_path and os.path.exists(output_image_path):
                    processed_frame = cv2.imread(output_image_path)
                    cam_placeholder.image(cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB), caption="Live Detection")
                else:
                    cam_placeholder.image(frame_rgb, caption="Live Detection (Failed)")

            time.sleep(0.1)  # Prevent overload

        cap.release()
        cv2.destroyAllWindows()
    else:
        cam_placeholder.info("Click 'Start Camera' to begin live detection")



if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("runs/output/images", exist_ok=True)
    os.makedirs("runs/output/videos", exist_ok=True)