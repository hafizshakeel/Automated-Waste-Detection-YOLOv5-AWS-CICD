import os
import glob
import subprocess
import base64
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import JSONResponse
from waste_detection.utils.main_utils import decodeImage, encodeImageIntoBase64

app = FastAPI()

def get_latest_exp_image():
    """Finds the latest processed image from YOLOv5 output."""
    output_dirs = sorted(glob.glob("yolov5/runs/detect/exp*"), key=os.path.getctime, reverse=True)
    if not output_dirs:
        return None
    # Assuming YOLO saves the processed image as inputImage.jpg
    processed_image_path = os.path.join(output_dirs[0], "inputImage.jpg")
    return processed_image_path if os.path.exists(processed_image_path) else None

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        # Save uploaded image temporarily
        temp_file_path = f"data/inputImage.jpg"
        os.makedirs("data", exist_ok=True)
        with open(temp_file_path, "wb") as buffer:
            buffer.write(await file.read())

        # Run YOLOv5 detection
        subprocess.run([
            "python", "yolov5/detect.py",
            "--weights", "weights/best_100.pt",
            "--img", "416",
            "--conf", "0.5",
            "--source", temp_file_path
        ], check=True)

        # Get the latest processed image
        processed_image_path = get_latest_exp_image()
        if not processed_image_path:
            raise HTTPException(status_code=400, detail="Processed image not found.")

        # Read the processed image and encode it as base64
        with open(processed_image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            

        # Return base64-encoded image in JSON response
        return JSONResponse(content={"image": f"data:image/jpeg;base64,{encoded_image}"})

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    