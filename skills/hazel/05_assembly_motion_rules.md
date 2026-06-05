# 05 — Assembly: Motion & Transition Rules (anti-monotony)

_The engine's `lib/video_assembler.py` supports multiple Ken Burns motions + (optional) xfade transitions. Apply these rules._

## MOTION = VARIED PER SLIDE (do this)
- Do NOT use one hardcoded zoom for every slide (monotonous = looks like slop).
- Pass a `motion` parameter to `create_slide_clip`; assign so **no two consecutive slides use the same motion.**
- Rotate among: `zoom_in`, `zoom_out`, `pan_left`, `pan_right`, `pan_up`, `pan_down`.
- **CRITICAL KEN BURNS FIX:** To prevent "vibrating" or subpixel jitter on Ken Burns motion, you MUST pre-scale the image to an enormous internal canvas (e.g. `scale='max(7680,iw*4320/ih)':'max(4320,ih*7680/iw)',crop=7680:4320`) *before* applying the `zoompan` filter.
- Zoom ranges should be exactly a `15%` change over the total slide duration (e.g., `1.0` to `1.15`) for noticeable but smooth motion.

## TRANSITIONS = HARD CUTS (for now)
- Keep the fast `concat -c copy` assembly (clean hard cuts). Fast + professional.
- Reason: varying MOTION already removes monotony; per-slide crossfades require full re-render (slow) and look dated if overused.
- DEFER xfade transitions; later use SELECTIVELY only (e.g., a single crossfade between the intro and the countdown), not on every slide.

## CAPTIONS
- Burn in captions synced to the hazel_2 voiceover (the engine/Whisper handles timing).
- Clean, readable, lower-third. Large enough for older viewers + mobile. No emoji.
- **CRITICAL SUBTITLE BOX:** Use an 88% transparent box so it doesn't block the video. Use ASS style `BackColour=&HE0000000` combined with `BorderStyle=3`.

## AUDIO
- Voiceover (hazel_2) is primary and clear.
- **CRITICAL MUSIC VOLUME:** Set background music volume extremely low (`volume=0.04` in FFmpeg) so it sits underneath Hazel without distracting.

## OUTPUT
- 1920x1080 mp4. Save to `<video-name>\final\`.
- Also export/keep the thumbnail base (a hazel_thumb_* image + text added in code).
- STOP here. No auto-upload. User uploads manually.
