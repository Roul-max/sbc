from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
from typing import List, Dict
import tempfile
import shutil
import uuid
from pydub import AudioSegment

app = FastAPI(title="Speech Segmentation API")

# Allow both local development and deployed frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://speech-orcin-ten.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Temporary upload directory
UPLOAD_DIR = Path(tempfile.gettempdir()) / "speech_segments"
UPLOAD_DIR.mkdir(exist_ok=True)


@app.get("/")
async def root():
    return {"message": "Speech Segmentation API is running"}


@app.post("/api/process")
async def process_audio(file: UploadFile = File(...)):
    """
    Process audio/video file and detect speech segments
    """
    try:
        file_id = str(uuid.uuid4())
        file_ext = Path(file.filename).suffix
        temp_file_path = UPLOAD_DIR / f"{file_id}{file_ext}"

        # Save uploaded file
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        segments = detect_speech_segments(str(temp_file_path))

        # Return file_id, segments, and URL for frontend to load waveform
        audio_url = f"/api/audio/{file_id}"
        return JSONResponse(content={
            "file_id": file_id,
            "segments": segments,
            "audioUrl": audio_url,
            "status": "success"
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/audio/{file_id}")
async def get_audio(file_id: str):
    """
    Serve the uploaded audio file for waveform preview
    """
    audio_files = list(UPLOAD_DIR.glob(f"{file_id}.*"))
    if not audio_files:
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(audio_files[0], media_type="audio/mpeg")


def detect_speech_segments(audio_path: str) -> List[Dict]:
    """
    Detect speech segments in audio file using voice activity detection
    This is a mock implementation; replace with real detection in production.
    """
    return [
        {"id": "1", "startTime": 0.5, "endTime": 5.2, "duration": 4.7, "name": "Speech Segment 1"},
        {"id": "2", "startTime": 6.8, "endTime": 15.3, "duration": 8.5, "name": "Speech Segment 2"},
        {"id": "3", "startTime": 16.1, "endTime": 22.7, "duration": 6.6, "name": "Speech Segment 3"},
        {"id": "4", "startTime": 24.2, "endTime": 30.5, "duration": 6.3, "name": "Speech Segment 4"}
    ]


@app.post("/api/extract-segment")
async def extract_segment(
    file_id: str,
    start_time: float,
    end_time: float,
    segment_name: str = "segment"
):
    """
    Extract a specific segment from the audio file using pydub
    """
    audio_files = list(UPLOAD_DIR.glob(f"{file_id}.*"))
    if not audio_files:
        raise HTTPException(status_code=404, detail="Audio file not found")

    audio_path = audio_files[0]
    output_path = UPLOAD_DIR / f"{file_id}_{segment_name}.mp3"

    try:
        extract_audio_segment(str(audio_path), str(output_path), start_time, end_time)
        return FileResponse(
            output_path,
            media_type="audio/mpeg",
            filename=f"{segment_name}.mp3"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def extract_audio_segment(input_path: str, output_path: str, start: float, end: float):
    """
    Extract a segment from the audio file using pydub
    """
    audio = AudioSegment.from_file(input_path)
    start_ms = int(start * 1000)
    end_ms = int(end * 1000)
    segment_audio = audio[start_ms:end_ms]
    segment_audio.export(output_path, format="mp3")


@app.delete("/api/cleanup/{file_id}")
async def cleanup_files(file_id: str):
    """
    Clean up temporary files
    """
    try:
        files = list(UPLOAD_DIR.glob(f"{file_id}*"))
        for file in files:
            file.unlink()
        return {"status": "success", "message": "Files cleaned up"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
