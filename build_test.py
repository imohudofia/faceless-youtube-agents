"""
TEST BUILD — Trimmed pipeline using only slides 1-36 (existing audio).
Skips TTS. Generates only the B-roll needed. Adds background music.
"""
import os
import sys
import shutil
import random
import json
import time
import wave
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from lib.config import VIDEO_WIDTH, VIDEO_HEIGHT, FPS

# FFmpeg binary from imageio-ffmpeg (no system install needed)
FFMPEG = r"C:\Users\imoh2\AppData\Local\Programs\Python\Python311\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
from lib.gathos_client import generate_image

# ── Directories ──────────────────────────────────────────────────────
BASE_OUTPUT_DIR = Path(r"C:\Users\imoh2\Developer\faceless-youtube\hazel\vinegar-test")
BROLL_DIR       = BASE_OUTPUT_DIR / "broll"
HAZEL_SHOTS_DIR = BASE_OUTPUT_DIR / "hazel_shots"
BROLL_SHOTS_DIR = BASE_OUTPUT_DIR / "broll_shots"
AUDIO_DIR       = BASE_OUTPUT_DIR / "audio"
CLIPS_DIR       = BASE_OUTPUT_DIR / "clips"
FINAL_DIR       = BASE_OUTPUT_DIR / "final"
HOST_LIBRARY    = Path(r"C:\Users\imoh2\Developer\faceless-youtube\hazel\host_library")
MUSIC_DIR       = Path(r"C:\Users\imoh2\Developer\faceless-youtube\faceless-youtube-agents\skills\hazel\music")

for d in [BROLL_DIR, HAZEL_SHOTS_DIR, BROLL_SHOTS_DIR, CLIPS_DIR, FINAL_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ── Style anchor (skill 04) ─────────────────────────────────────────
STYLE_ANCHOR = ", clean 2D flat-illustration style, simple flat shading, soft friendly muted colors, minimal uncluttered background, gentle thin vector outlines, no text, no words, no labels, 16:9"

# ── B-Roll prompts needed for slides 1-36 only (11 unique) ──────────
BROLL_NEEDED = {
    "broll_cleaning_aisle":    "A grocery store aisle filled with colorful plastic spray bottles of cleaning products",
    "broll_vinegar_bottle":    "A simple glass bottle of plain white vinegar standing on a clean kitchen counter",
    "broll_expensive_spray":   "A single high-end modern plastic spray bottle on a bright surface",
    "broll_towel_stack":       "A stack of thick, textured bath towels sitting on a wooden shelf",
    "broll_washing_machine":   "A modern front-loading washing machine standing in a utility room",
    "broll_fluffy_towels":     "A stack of soft, fluffy clean towels in a basket",
    "broll_window_track_dirty":"A sliding window track with dark grey dust and dirt in the corners",
    "broll_window_fizzing":    "Baking soda in a window track fizzing and foaming as clear vinegar hits it",
    "broll_window_track_clean":"A clean sliding window track sparkling and spotless",
    "broll_disposal_drain":    "A clean kitchen sink with a circular metal disposal drain",
    "broll_ice_tray":          "A simple blue plastic ice cube tray sitting on a clean counter",
}

# ── Slides 1-36 (the ones we have audio for) ─────────────────────────
SLIDES = [
    {"slide_number": 1,  "narration": "Hello there, it's Hazel.", "visual_type": "HAZEL", "visual_value": "hazel_smile", "motion": "zoom_in"},
    {"slide_number": 2,  "narration": "You know, every time I walk down the cleaning aisle at the grocery store,", "visual_type": "B_ROLL", "visual_value": "broll_cleaning_aisle", "motion": "zoom_out"},
    {"slide_number": 3,  "narration": "I see shelves lined with fifty different colorful plastic spray bottles.", "visual_type": "HAZEL", "visual_value": "hazel_kitchen", "motion": "pan_left"},
    {"slide_number": 4,  "narration": "Specialize sprays for glass, sprays for counters, sprays for stainless steel...", "visual_type": "B_ROLL", "visual_value": "broll_cleaning_aisle", "motion": "pan_right"},
    {"slide_number": 5,  "narration": "it easily adds up to over a hundred dollars a year.", "visual_type": "HAZEL", "visual_value": "hazel_concerned", "motion": "pan_up"},
    {"slide_number": 6,  "narration": "But did you know that one simple, ninety-nine cent bottle of plain white vinegar", "visual_type": "B_ROLL", "visual_value": "broll_vinegar_bottle", "motion": "pan_down"},
    {"slide_number": 7,  "narration": "can replace almost all of them?", "visual_type": "HAZEL", "visual_value": "hazel_approval", "motion": "zoom_in"},
    {"slide_number": 8,  "narration": "The big cleaning companies certainly won't tell you that\u2014", "visual_type": "HAZEL", "visual_value": "hazel_thinking", "motion": "zoom_out"},
    {"slide_number": 9,  "narration": "they'd rather sell you an eight-dollar spray with the exact same active ingredient.", "visual_type": "B_ROLL", "visual_value": "broll_expensive_spray", "motion": "pan_left"},
    {"slide_number": 10, "narration": "Today, I'm sharing five genius uses for white vinegar that most people have completely forgotten.", "visual_type": "HAZEL", "visual_value": "hazel_present", "motion": "pan_right"},
    {"slide_number": 11, "narration": "Make sure to stick around for number one\u2014", "visual_type": "HAZEL", "visual_value": "hazel_one_finger", "motion": "pan_up"},
    {"slide_number": 12, "narration": "it's an old-school kitchen trick that saved me from buying a new appliance last year.", "visual_type": "HAZEL", "visual_value": "hazel_thinking", "motion": "pan_down"},
    {"slide_number": 13, "narration": "Let's start with Number Five: reviving your stiff, scratchy bath towels.", "visual_type": "B_ROLL", "visual_value": "broll_towel_stack", "motion": "zoom_in", "number": "#5"},
    {"slide_number": 14, "narration": "Over time, laundry detergents and fabric softeners build up on towel fibers, making them rough and non-absorbent. My mother used to do this with every towel in the house back when I was growing up.", "visual_type": "HAZEL", "visual_value": "hazel_concerned", "motion": "zoom_out"},
    {"slide_number": 15, "narration": "To fix this, just toss your towels into the washing machine", "visual_type": "B_ROLL", "visual_value": "broll_washing_machine", "motion": "pan_left"},
    {"slide_number": 16, "narration": "and add one cup of white vinegar directly to the fabric softener dispenser.", "visual_type": "HAZEL", "visual_value": "hazel_holding", "motion": "pan_right"},
    {"slide_number": 17, "narration": "Run a normal hot cycle without any laundry detergent.", "visual_type": "HAZEL", "visual_value": "hazel_kitchen", "motion": "pan_up"},
    {"slide_number": 18, "narration": "The mild acid in the vinegar breaks down those stubborn chemical residues, leaving your towels soft and fluffy again.", "visual_type": "B_ROLL", "visual_value": "broll_fluffy_towels", "motion": "pan_down"},
    {"slide_number": 19, "narration": "It saves you from throwing away perfectly good towels or buying expensive commercial softeners.", "visual_type": "HAZEL", "visual_value": "hazel_approval", "motion": "zoom_in"},
    {"slide_number": 20, "narration": "Next is Number Four: cleaning your window tracks.", "visual_type": "B_ROLL", "visual_value": "broll_window_track_dirty", "motion": "zoom_out", "number": "#4"},
    {"slide_number": 21, "narration": "Have you ever looked down at the bottom of your windows and noticed a thick layer of grey dust and grime?", "visual_type": "B_ROLL", "visual_value": "broll_window_track_dirty", "motion": "pan_left"},
    {"slide_number": 22, "narration": "It is incredibly hard to scrub out.", "visual_type": "HAZEL", "visual_value": "hazel_concerned", "motion": "pan_right"},
    {"slide_number": 23, "narration": "Here is what I do: sprinkle a light layer of baking soda in the track,", "visual_type": "HAZEL", "visual_value": "hazel_kitchen", "motion": "pan_up"},
    {"slide_number": 24, "narration": "and then pour white vinegar over it. It will fizz up immediately.", "visual_type": "B_ROLL", "visual_value": "broll_window_fizzing", "motion": "pan_down"},
    {"slide_number": 25, "narration": "Let it sit for five minutes, then wipe it clean with a simple paper towel or old rag.", "visual_type": "HAZEL", "visual_value": "hazel_table", "motion": "zoom_in"},
    {"slide_number": 26, "narration": "The fizzing action loosens the stubborn grime so it wipes away effortlessly.", "visual_type": "B_ROLL", "visual_value": "broll_window_track_clean", "motion": "zoom_out"},
    {"slide_number": 27, "narration": "It saves you from buying expensive specialized track brushes or harsh chemical sprays.", "visual_type": "HAZEL", "visual_value": "hazel_confident", "motion": "pan_left"},
    {"slide_number": 28, "narration": "Moving on to Number Three: keeping your garbage disposal smelling fresh.", "visual_type": "B_ROLL", "visual_value": "broll_disposal_drain", "motion": "pan_right", "number": "#3"},
    {"slide_number": 29, "narration": "If your kitchen sink has developed a strange, sour odor, you don't need fancy deodorizer beads.", "visual_type": "HAZEL", "visual_value": "hazel_kitchen", "motion": "pan_up"},
    {"slide_number": 30, "narration": "Try this instead: fill an empty ice cube tray with half water and half white vinegar, and freeze it.", "visual_type": "B_ROLL", "visual_value": "broll_ice_tray", "motion": "pan_down"},
    {"slide_number": 31, "narration": "Once frozen, toss three or four of these vinegar ice cubes down the disposal", "visual_type": "HAZEL", "visual_value": "hazel_livingroom", "motion": "zoom_in"},
    {"slide_number": 32, "narration": "and turn it on with cold running water.", "visual_type": "HAZEL", "visual_value": "hazel_kitchen", "motion": "zoom_out"},
    {"slide_number": 33, "narration": "The ice sharpens the blades while the vinegar neutralizes the odors deep inside.", "visual_type": "HAZEL", "visual_value": "hazel_thinking", "motion": "pan_left"},
    {"slide_number": 34, "narration": "I started doing this when my kids were small and money was tight, and I still do it today. It's a quick, easy, two-cent solution that keeps your kitchen clean and saves you from buying chemical deodorizers.", "visual_type": "HAZEL", "visual_value": "hazel_thumb_warm", "motion": "pan_right"},
    {"slide_number": 35, "narration": "We are about to get to our top two uses, including my absolute favorite kitchen saver.", "visual_type": "HAZEL", "visual_value": "hazel_present", "motion": "pan_up"},
    {"slide_number": 36, "narration": "But before we do, if you enjoy simple, practical tips that help you run a thrifty home,", "visual_type": "HAZEL", "visual_value": "hazel_point_right", "motion": "pan_down"},
]


# ═══════════════════════════════════════════════════════════════════════
# STEP 2 — B-Roll generation (11 images, sequential, with retries)
# ═══════════════════════════════════════════════════════════════════════
def step2_broll():
    print("\n--- STEP 2: B-Roll Image Generation (11 needed) ---")
    for key, base_prompt in BROLL_NEEDED.items():
        out_path = BROLL_DIR / f"{key}.jpeg"
        if out_path.exists() and out_path.stat().st_size > 0:
            print(f"  {key}.jpeg already exists. Skipping.")
            continue
        full_prompt = base_prompt + STYLE_ANCHOR
        print(f"  Generating '{key}'...")
        success = False
        for attempt in range(10):
            try:
                generate_image(full_prompt, str(out_path), width=1344, height=768)
                success = True
                time.sleep(3)
                break
            except Exception as e:
                msg = str(e)
                print(f"    Attempt {attempt+1}/10 failed: {msg}")
                if "429" in msg:
                    print(f"    Rate limit hit. Waiting 45s...")
                    time.sleep(45)
                else:
                    time.sleep(5)
        if not success:
            print(f"  FATAL: Could not generate '{key}' after 10 attempts. Stopping cleanly.")
            print("  All completed images are saved. Resume later.")
            sys.exit(0)
    print("  All B-roll images ready.")


# ═══════════════════════════════════════════════════════════════════════
# STEP 3 — Copy Hazel shots from host_library with variant switching
# ═══════════════════════════════════════════════════════════════════════
def step3_hazel_shots():
    print("\n--- STEP 3: Hazel Shots (copy from library) ---")
    library_files = list(HOST_LIBRARY.glob("*.jpeg"))
    used_variants = {}

    for slide in SLIDES:
        if slide["visual_type"] != "HAZEL":
            continue
        family = slide["visual_value"]
        num = slide["slide_number"]
        dest = HAZEL_SHOTS_DIR / f"slide-{num:02d}.jpeg"

        matches = [f for f in library_files
                   if f.name.startswith(family + "_") or f.name == f"{family}.jpeg"]
        if not matches:
            print(f"  WARNING: No match for '{family}', using fallback")
            matches = [HOST_LIBRARY / "host_REFERENCE.jpeg"]

        paths = [str(m) for m in matches]
        random.shuffle(paths)
        chosen = min(paths, key=lambda p: used_variants.get(family, []).count(p))
        used_variants.setdefault(family, []).append(chosen)

        shutil.copy2(chosen, dest)
        print(f"  {Path(chosen).name} -> slide-{num:02d}.jpeg")


# ═══════════════════════════════════════════════════════════════════════
# STEP 4 — Copy B-roll to per-slide paths + draw countdown numbers
# ═══════════════════════════════════════════════════════════════════════
def step4_numbers():
    print("\n--- STEP 4: Prepare slide images + countdown numbers ---")
    for slide in SLIDES:
        num = slide["slide_number"]
        if slide["visual_type"] == "B_ROLL":
            src = BROLL_DIR / f"{slide['visual_value']}.jpeg"
            dest = BROLL_SHOTS_DIR / f"slide-{num:02d}.jpeg"
            shutil.copy2(src, dest)
        else:
            dest = HAZEL_SHOTS_DIR / f"slide-{num:02d}.jpeg"

        number_text = slide.get("number")
        if number_text:
            print(f"  Drawing {number_text} on slide-{num:02d}...")
            with Image.open(dest) as img:
                img = img.convert("RGBA")
                W, H = img.size
                font_size = int(H * 0.10)
                try:
                    font = ImageFont.truetype("arialbd.ttf", font_size)
                except IOError:
                    try:
                        font = ImageFont.truetype("C:\\Windows\\Fonts\\arialbd.ttf", font_size)
                    except IOError:
                        font = ImageFont.load_default()
                draw = ImageDraw.Draw(img)
                x, y = int(W * 0.06), int(H * 0.06)
                draw.text((x, y), number_text, font=font,
                          fill=(255, 255, 255, 255),
                          stroke_width=int(font_size * 0.08),
                          stroke_fill=(0, 0, 0, 255))
                img.convert("RGB").save(dest, "JPEG")


# ═══════════════════════════════════════════════════════════════════════
# STEP 5 — Assemble per-slide clips + concat
# ═══════════════════════════════════════════════════════════════════════
def get_audio_duration(path):
    """Get MP3/WAV file duration using ffmpeg probe (handling fake WAVs)."""
    probe_cmd = [FFMPEG, "-i", path, "-f", "null", "-"]
    probe_r = subprocess.run(probe_cmd, capture_output=True, text=True, timeout=120)
    import re
    dur_match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", probe_r.stderr)
    if dur_match:
        return int(dur_match.group(1))*3600 + int(dur_match.group(2))*60 + float(dur_match.group(3))
    return 4.0  # fallback


def make_clip(img, audio, out, motion, pad_dur):
    raw_dur = get_audio_duration(audio)
    dur = raw_dur + pad_dur
    frames = max(int(dur * FPS), 24)
    
    # Scale to cover 4x resolution (7680x4320) first. 
    # This completely eliminates the zoompan "shaking/vibrating" bug caused by sub-pixel rounding on 1080p images!
    scale_crop = "scale='max(7680,iw*4320/ih)':'max(4320,ih*7680/iw)',crop=7680:4320"
    
    # Motion speeds
    z_step = 0.15 / frames
    z_max = 1.15
    pan_zoom = 1.15
    
    motion_map = {
        "zoom_in":   f"{scale_crop},zoompan=z='min(zoom+{z_step}, {z_max})':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:fps={FPS}",
        "zoom_out":  f"{scale_crop},zoompan=z='if(eq(on,1), {z_max}, max(zoom-{z_step}, 1))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:fps={FPS}",
        "pan_left":  f"{scale_crop},zoompan=z='{pan_zoom}':x='(1-on/{frames})*(iw-iw/zoom)':y='ih/2-(ih/zoom/2)':d={frames}:s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:fps={FPS}",
        "pan_right": f"{scale_crop},zoompan=z='{pan_zoom}':x='(on/{frames})*(iw-iw/zoom)':y='ih/2-(ih/zoom/2)':d={frames}:s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:fps={FPS}",
        "pan_up":    f"{scale_crop},zoompan=z='{pan_zoom}':x='iw/2-(iw/zoom/2)':y='(1-on/{frames})*(ih-ih/zoom)':d={frames}:s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:fps={FPS}",
        "pan_down":  f"{scale_crop},zoompan=z='{pan_zoom}':x='iw/2-(iw/zoom/2)':y='(on/{frames})*(ih-ih/zoom)':d={frames}:s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:fps={FPS}",
    }
    vf = motion_map.get(motion, motion_map["zoom_in"])
    
    if pad_dur > 0:
        audio_filter = ["-af", f"apad=pad_dur={pad_dur}"]
    else:
        audio_filter = []
        
    cmd = [FFMPEG, "-y", "-i", img, "-i", audio, "-vf", vf] + audio_filter + [
           "-c:v", "libx264", "-preset", "fast",
           "-c:a", "aac", "-b:a", "192k", "-pix_fmt", "yuv420p",
           "-t", str(dur), out]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        raise RuntimeError(f"FFmpeg clip failed for {out}: {r.stderr[:200]}")


def step5_assemble():
    print("\n--- STEP 5: Assembly ---")
    clip_paths = []
    for slide in SLIDES:
        num = slide["slide_number"]
        if slide["visual_type"] == "B_ROLL":
            img = str(BROLL_SHOTS_DIR / f"slide-{num:02d}.jpeg")
        else:
            img = str(HAZEL_SHOTS_DIR / f"slide-{num:02d}.jpeg")
        audio = str(AUDIO_DIR / f"slide-{num:02d}.wav")
        clip = str(CLIPS_DIR / f"clip-{num:02d}.mp4")
        
        # Only pad slides that end with punctuation, for natural flow
        text = slide["narration"].strip()
        pad = 0.6 if text and text[-1] in ".?!" else 0.0
        
        print(f"  Clip {num} ({slide['motion']}) pad={pad}s...")
        make_clip(img, audio, clip, slide["motion"], pad)
        clip_paths.append(clip)

    # Concat
    print("  Concatenating 36 clips...")
    list_file = CLIPS_DIR / "_list.txt"
    with open(list_file, "w") as f:
        for c in clip_paths:
            f.write(f"file '{Path(c).name}'\n")
    assembled = FINAL_DIR / "temp_assembled.mp4"
    cmd = [FFMPEG, "-y", "-f", "concat", "-safe", "0",
           "-i", str(list_file), "-c", "copy", str(assembled)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        print(f"  ERROR concat: {r.stderr[:300]}")
        sys.exit(1)
    list_file.unlink(missing_ok=True)
    for c in clip_paths:
        Path(c).unlink(missing_ok=True)
    print(f"  Assembled: {assembled}")


# ═══════════════════════════════════════════════════════════════════════
# STEP 6 — Captions (SRT generation + burn-in)
# ═══════════════════════════════════════════════════════════════════════
def fmt_srt(s):
    h = int(s // 3600); m = int((s % 3600) // 60); sec = int(s % 60); ms = int((s - int(s)) * 1000)
    return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"

def step6_captions():
    print("\n--- STEP 6: Captions ---")
    entries = []
    t = 0.0
    idx = 1
    for slide in SLIDES:
        num = slide["slide_number"]
        raw_dur = get_audio_duration(str(AUDIO_DIR / f"slide-{num:02d}.wav"))
        
        text = slide["narration"].strip()
        pad_dur = 0.6 if text and text[-1] in ".?!" else 0.0
        dur = raw_dur + pad_dur # full slide duration including pause
        
        words = slide["narration"].split()
        total_w = max(len(words), 1)
        # chunk into lines of max 5 words, then pairs of lines
        lines = []
        cur = []
        for w in words:
            if len(cur) < 5:
                cur.append(w)
            else:
                lines.append(" ".join(cur))
                cur = [w]
        if cur:
            lines.append(" ".join(cur))
        chunks = [lines[i:i+2] for i in range(0, len(lines), 2)]

        ct = t
        for chunk in chunks:
            text = "\n".join(chunk)
            wc = sum(len(l.split()) for l in chunk)
            cd = (wc / total_w) * raw_dur # Time spans only the raw audio
            ce = min(ct + cd, t + raw_dur)
            entries.append(f"{idx}\n{fmt_srt(ct)} --> {fmt_srt(ce)}\n{text}\n\n")
            idx += 1
            ct = ce
        t += dur # Next slide starts after padded duration

    srt = BASE_OUTPUT_DIR / "captions.srt"
    srt.write_text("".join(entries), encoding="utf-8")
    print(f"  SRT written: {srt}")

    # Burn in: using BackColour=&HE0000000 for 88% transparent box (much lighter!)
    assembled = FINAL_DIR / "temp_assembled.mp4"
    captioned = FINAL_DIR / "temp_captioned.mp4"
    esc = str(srt).replace("\\", "/").replace(":", "\\:")
    cmd = [FFMPEG, "-y", "-i", str(assembled),
           "-vf", f"subtitles='{esc}':force_style='Alignment=2,FontSize=18,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,Outline=2,BorderStyle=3,BackColour=&HE0000000,MarginV=25,Bold=1'",
           "-c:a", "copy", str(captioned)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        print(f"  ERROR burning captions: {r.stderr[:300]}")
        sys.exit(1)
    assembled.unlink(missing_ok=True)
    print(f"  Captioned video: {captioned}")


# ═══════════════════════════════════════════════════════════════════════
# STEP 7 — Background music (loop + mix under voice at ~12%)
# ═══════════════════════════════════════════════════════════════════════
def step7_music():
    print("\n--- STEP 7: Background Music ---")
    tracks = sorted(MUSIC_DIR.glob("*.mp3"))
    if not tracks:
        print("  No music tracks found! Skipping music.")
        # Just rename captioned to final
        src = FINAL_DIR / "temp_captioned.mp4"
        dst = FINAL_DIR / "vinegar_final.mp4"
        shutil.move(str(src), str(dst))
        return

    # Pick first track
    track = tracks[0]
    print(f"  Using track: {track.name}")

    # Get video duration
    captioned = FINAL_DIR / "temp_captioned.mp4"
    # Get video duration via ffmpeg
    probe_cmd = [FFMPEG, "-i", str(captioned), "-f", "null", "-"]
    probe_r = subprocess.run(probe_cmd, capture_output=True, text=True, timeout=120)
    # Parse duration from stderr: "Duration: HH:MM:SS.ss"
    import re
    dur_match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", probe_r.stderr)
    if dur_match:
        vid_dur = int(dur_match.group(1))*3600 + int(dur_match.group(2))*60 + float(dur_match.group(3))
    else:
        vid_dur = 120.0  # fallback
    print(f"  Video duration: {vid_dur:.1f}s")

    # Mix: loop music to video length, set music volume to 4% (significant drop)
    # -stream_loop -1 loops the music, -t trims to video length
    # amix with weights: voice=1.0, music=0.04
    cmd = [
        FFMPEG, "-y",
        "-i", str(captioned),
        "-stream_loop", "-1", "-i", str(track),
        "-filter_complex",
        f"[1:a]atrim=0:{vid_dur:.2f},asetpts=PTS-STARTPTS,volume=0.04[music];"
        f"[0:a][music]amix=inputs=2:duration=first:dropout_transition=2[out]",
        "-map", "0:v", "-map", "[out]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(final)
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        print(f"  ERROR mixing music: {r.stderr[:300]}")
        print("  Falling back to video without music.")
        shutil.move(str(captioned), str(final))
        return

    captioned.unlink(missing_ok=True)
    print(f"  Final with music: {final}")


# ═══════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════
def main():
    print("=" * 60)
    print("TEST BUILD — ThriftyHazel Vinegar Video (slides 1-36)")
    print("=" * 60)

    step2_broll()
    step3_hazel_shots()
    step4_numbers()
    step5_assemble()
    step6_captions()
    step7_music()

    print("\n" + "=" * 60)
    print("DONE!")
    print(f"Final video: {FINAL_DIR / 'vinegar_final.mp4'}")
    print("=" * 60)

if __name__ == "__main__":
    main()
