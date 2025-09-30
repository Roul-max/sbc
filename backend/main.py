from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import os
import uuid
import json
from typing import List, Dict
from pathlib import Path
import tempfile
import shutil

app = FastAPI(title="Speech Segmentation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        segments = detect_speech_segments(str(temp_file_path))

        return JSONResponse(content={
            "file_id": file_id,
            "segments": segments,
            "status": "success"
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def detect_speech_segments(audio_path: str) -> List[Dict]:
    """
    Detect speech segments in audio file using voice activity detection
    This is a simplified implementation that returns mock data

    For production, integrate with:
    - librosa for audio processing
    - webrtcvad or silero-vad for voice activity detection
    - pydub for audio manipulation
    """
    segments = [
        {
            "id": "1",
            "startTime": 0.5,
            "endTime": 5.2,
            "duration": 4.7,
            "name": "Speech Segment 1"
        },
        {
            "id": "2",
            "startTime": 6.8,
            "endTime": 15.3,
            "duration": 8.5,
            "name": "Speech Segment 2"
        },
        {
            "id": "3",
            "startTime": 16.1,
            "endTime": 22.7,
            "duration": 6.6,
            "name": "Speech Segment 3"
        },
        {
            "id": "4",
            "startTime": 24.2,
            "endTime": 30.5,
            "duration": 6.3,
            "name": "Speech Segment 4"
        }
    ]

    return segments


@app.post("/api/extract-segment")
async def extract_segment(
    file_id: str,
    start_time: float,
    end_time: float,
    segment_name: str = "segment"
):
    """
    Extract a specific segment from the audio file
    """
    try:
        audio_files = list(UPLOAD_DIR.glob(f"{file_id}.*"))
        if not audio_files:
            raise HTTPException(status_code=404, detail="Audio file not found")

        audio_path = audio_files[0]
        output_path = UPLOAD_DIR / f"{file_id}_{segment_name}.mp3"

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
    Extract audio segment using pydub
    For production, install: pip install pydub
    """
    pass


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
