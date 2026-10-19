# Immersion Assistant Architecture

> Where a section describes something not in the code yet (other capture or translation providers, richer dictionary data, SQLite storage, permission prompts, tests), it is planned work, not built.

## Data Flow Overview

1. **Capture**  
   `ScreenCapture` (Quartz on macOS) grabs the current desktop frame. Platform adapters can extend this to per-window or per-application capture as permissions allow.

2. **OCR**  
   `OCRProcessor` runs Tesseract to extract text spans (`OCRSpan`) with bounding boxes and confidence scores. Future work: substitute EasyOCR or PaddleOCR for multilingual robustness, or use on-device transformer vision models.

3. **Translation**  
   `TranslationPipeline` applies a glossary shortcut, then defers to the configured provider (currently `EchoTranslator` placeholder). It caches results (LRU) to avoid redundant requests as the screen changes. Integrate Marian/Mt5/Bloomz-based translators for offline support.

4. **Language Enrichment**  
   `language.py` adds pinyin (tone3 format) and maps syllables to tone colors. Hook into Context7 MCP’s `/theajack/cnchar` dataset for richer dictionary entries, radicals, stroke data, and idioms.

5. **Overlay Modeling**  
   `build_overlay` merges OCR spans, translations, and enrichment into `OverlaySpan` objects that describe everything the UI needs to render tooltips, tone-color text, and glossary flags.

6. **Presentation**  
   `OverlayWindow` (PySide6) draws translucent panels above the original content. The `ImmersionDesktop` runner keeps a background pipeline thread updating an in-memory `ImmersionState` while the UI polls and repaints every 500 ms. FastAPI (`server.py`) mirrors that state for external consumers.

## Extensibility Points

- **Capture providers** – Implement a `ScreenCapture` subclass (e.g., Windows GDI+, Wayland portal) and swap via dependency injection.
- **Translation providers** – Implement `TranslationProvider` interface for Marian, M2M100, DeepL, Google, or custom LLM-based translators. Consider streaming partial translations for smoother overlays.
- **Language services** – Replace `pypinyin` fallback with a dedicated node/Context7 bridge exposing `cnchar` functions for stroke order, radicals, idioms, and names.
- **UX modes** – Build alternative front-ends (browser extension, menu-bar quick look, AR glasses) by consuming the `/state` API or a shared IPC channel.

## Storage & Configuration

- `ImmersionConfig` loads YAML settings (~/.immersion_assistant.yml by default) covering OCR/translation/overlay modules and user glossaries.
- Glossary entries are stored in-memory for now. Persist to SQLite when you introduce spaced repetition, frequency tracking, or collaborative lists.

## Permissions & Privacy

- macOS requires Screen Recording access plus Accessibility permission for mouse/keyboard overlays. Future builds should prompt on first launch and surface a privacy dashboard (conceal content from excluded apps, blur secure fields).
- All processing is local. When you add optional external translation providers, gate them behind explicit opt-in toggles and red privacy notices.

## Testing Strategy

- Unit test each module (`pytest`) with fixtures for synthetic OCR outputs and translation responses.
- Add integration smoke tests using recorded frames to assert overlay shapes and API responses.
- Provide a simulation mode that replays captured frames into the pipeline without live screen access (useful for CI or restricted environments).
