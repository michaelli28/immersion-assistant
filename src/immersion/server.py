from __future__ import annotations

import asyncio
import threading

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from immersion.app import ImmersionApp

app = FastAPI(title="Immersion Assistant API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class OverlaySpanModel(BaseModel):
    bbox: tuple[int, int, int, int]
    source_text: str
    translated_text: str
    pinyin: str | None
    tone_colors: list[str] | None
    glossary_applied: bool


class AppStateModel(BaseModel):
    spans: list[OverlaySpanModel]
    last_updated: float


immersion_app = ImmersionApp()
thread = threading.Thread(target=immersion_app.start, kwargs={"interval": 4.0}, daemon=True)
thread.start()


@app.get("/state", response_model=AppStateModel)
async def get_state() -> AppStateModel:
    state = immersion_app.state
    return AppStateModel(
        spans=[
            OverlaySpanModel(
                bbox=span.bbox,
                source_text=span.source_text,
                translated_text=span.translated_text,
                pinyin=span.pinyin,
                tone_colors=span.tone_colors,
                glossary_applied=span.glossary_applied,
            )
            for span in state.overlay_spans
        ],
        last_updated=state.last_updated,
    )


def run_api() -> None:
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8777, reload=False)


if __name__ == "__main__":
    run_api()
