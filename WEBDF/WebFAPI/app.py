from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from moviepy.editor import VideoFileClip
from pathlib import Path
import uuid
import subprocess
import os
import time
import cv2
from ai.inference import process_frame  # 👈 file inference.py chứa model

# Cấu hình thư mục gốc và static
WORK_DIR = Path("/media/sinemu/Lexar/WEBDF/WebFAPI")
STATIC_DIR = WORK_DIR / "static"
TEMP_DIR = STATIC_DIR / "temp"

app = FastAPI(docs_url=None, redoc_url=None)

# Mount static chuẩn để truy cập file trong /static/temp
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=WORK_DIR / "templates")

# Cho phép gọi API từ mọi nguồn
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dữ liệu user mẫu
fake_users = {
    "admin": {"password": "1", "position": "admin"},
    "guest": {"password": "1", "position": "lecture"},
}

# Trang chủ
@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Trang deepfake
@app.get("/deepfake")
async def deepfake(request: Request):
    return templates.TemplateResponse("deepfake.html", {"request": request})

# Đăng nhập
@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    if username in fake_users and fake_users[username]["password"] == password:
        return {
            "success": True,
            "position": fake_users[username]["position"]
        }
    return {
        "success": False,
        "message": "Sai tên đăng nhập hoặc mật khẩu"
    }

# Xử lý video upload
@app.post("/process_ai")
async def process_ai(video: UploadFile = File(...)):
    try:
        # 🧹 1. Dọn thư mục temp
        for file in TEMP_DIR.glob("*"):
            try:
                file.unlink()
            except Exception:
                pass

        os.makedirs(TEMP_DIR, exist_ok=True)

        # 📝 2. Lưu file .webm gốc
        raw_filename = f"{uuid.uuid4().hex}.webm"
        raw_path = TEMP_DIR / raw_filename
        with open(raw_path, "wb") as f:
            f.write(await video.read())

        # 🔄 3. Chuyển sang .mp4
        mp4_filename = raw_filename.replace(".webm", ".mp4")
        mp4_path = TEMP_DIR / mp4_filename
        ffmpeg_cmd = [
            "ffmpeg", "-y", "-i", str(raw_path),
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23",
            str(mp4_path)
        ]
        result = subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            return JSONResponse({"result_text": "❌ Lỗi chuyển định dạng bằng ffmpeg"}, status_code=500)

        # ✂️ 4. Cắt 30s giữa video
        clip = VideoFileClip(str(mp4_path))
        duration = clip.duration
        start = (duration - 30) / 2 if duration > 30 else 0
        cut_clip = clip.subclip(start, start + 30 if duration > 30 else duration)

        # 💾 5. Ghi tạm video cắt ra file
        cut_filename = "cut_" + mp4_filename
        cut_path = TEMP_DIR / cut_filename
        cut_clip.write_videofile(str(cut_path), codec="libx264", audio_codec="aac")

        # 🧠 6. AI xử lý từng frame
        ai_start = time.perf_counter()
        cap = cv2.VideoCapture(str(cut_path))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        ai_filename = "ai_" + mp4_filename
        ai_path = TEMP_DIR / ai_filename
        fps = cap.get(cv2.CAP_PROP_FPS)
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        out = cv2.VideoWriter(str(ai_path), fourcc, fps, (w, h))

        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret or frame is None:
                break
            try:
                processed_frame = process_frame(frame)
                out.write(processed_frame)
                frame_count += 1
            except Exception as e:
                print(f"⚠️ Frame {frame_count} error: {e}")
                continue
        cap.release()
        out.release()
        ai_end = time.perf_counter()
        ai_processing_time = round(ai_end - ai_start, 2)

        if frame_count == 0:
            return JSONResponse({"result_text": "❌ Không có frame nào được xử lý!"}, status_code=500)

        # 🎧 7. Tách audio (nếu có)
        audio_url = None
        if cut_clip.audio is not None:
            audio_filename = cut_filename.replace(".mp4", ".mp3")
            audio_path = TEMP_DIR / audio_filename
            cut_clip.audio.write_audiofile(str(audio_path))
            audio_url = f"/static/temp/{audio_filename}"

        # ✅ 8. Trả kết quả
        return {
            "result_text": "✅ Video đã xử lý bằng AI!",
            "video_url": f"/static/temp/{ai_filename}",
            "audio_url": audio_url,
            "ai_processing_time": ai_processing_time
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse({"result_text": f"❌ Lỗi xử lý video: {str(e)}"}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
