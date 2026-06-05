import os
import sys
import shutil
import random
import json
import time
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Set up PYTHONPATH environment internally if needed, but we will run with PYTHONPATH=.
from lib.config import (
    GATHOS_TIMEOUT,
    VIDEO_WIDTH,
    VIDEO_HEIGHT,
    FPS,
)
from lib.gathos_client import (
    submit_tts_job,
    poll_tts_job,
    submit_image_job,
    poll_image_job,
)

# Output directory config
BASE_OUTPUT_DIR = Path(r"C:\Users\imoh2\Developer\faceless-youtube\hazel\vinegar-test")
BROLL_DIR = BASE_OUTPUT_DIR / "broll"
HAZEL_SHOTS_DIR = BASE_OUTPUT_DIR / "hazel_shots"
BROLL_SHOTS_DIR = BASE_OUTPUT_DIR / "broll_shots"
AUDIO_DIR = BASE_OUTPUT_DIR / "audio"
CLIPS_DIR = BASE_OUTPUT_DIR / "clips"
FINAL_DIR = BASE_OUTPUT_DIR / "final"
HOST_LIBRARY_DIR = Path(r"C:\Users\imoh2\Developer\faceless-youtube\hazel\host_library")

# Create directories
for d in [BASE_OUTPUT_DIR, BROLL_DIR, HAZEL_SHOTS_DIR, BROLL_SHOTS_DIR, AUDIO_DIR, CLIPS_DIR, FINAL_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Mandatory style anchor for B-roll prompts
STYLE_ANCHOR = ", clean 2D flat-illustration style, simple flat shading, soft friendly muted colors, minimal uncluttered background, gentle thin vector outlines, no text, no words, no labels, 16:9"

# B-Roll unique prompts mapping (16 unique images)
BROLL_MAPPING = {
    "broll_cleaning_aisle": "A grocery store aisle filled with colorful plastic spray bottles of cleaning products",
    "broll_vinegar_bottle": "A simple glass bottle of plain white vinegar standing on a clean kitchen counter",
    "broll_expensive_spray": "A single high-end modern plastic spray bottle on a bright surface",
    "broll_towel_stack": "A stack of thick, textured bath towels sitting on a wooden shelf",
    "broll_washing_machine": "A modern front-loading washing machine standing in a utility room",
    "broll_fluffy_towels": "A stack of soft, fluffy clean towels in a basket",
    "broll_window_track_dirty": "A sliding window track with dark grey dust and dirt in the corners",
    "broll_window_fizzing": "Baking soda in a window track fizzing and foaming as clear vinegar hits it",
    "broll_window_track_clean": "A clean sliding window track sparkling and spotless",
    "broll_disposal_drain": "A clean kitchen sink with a circular metal disposal drain",
    "broll_ice_tray": "A simple blue plastic ice cube tray sitting on a clean counter",
    "broll_showerhead_dirty": "A close-up of a metal showerhead with white mineral crust on the nozzles",
    "broll_showerhead_bag": "A plastic bag filled with clear liquid tied around a showerhead with a rubber band",
    "broll_showerhead_clean": "A clean shiny metal showerhead spraying clear streams of water straight down",
    "broll_coffee_maker": "A standard black drip coffee maker sitting on a clean wooden kitchen counter",
    "broll_coffee_brewing": "Fresh dark coffee dripping into a glass coffee carafe"
}

# The approved script and slides list (56 slides)
SLIDES = [
    {
        "slide_number": 1,
        "narration": "Hello there, it's Hazel.",
        "visual_type": "HAZEL",
        "visual_value": "hazel_smile",
        "motion": "zoom_in"
    },
    {
        "slide_number": 2,
        "narration": "You know, every time I walk down the cleaning aisle at the grocery store,",
        "visual_type": "B_ROLL",
        "visual_value": "broll_cleaning_aisle",
        "motion": "zoom_out"
    },
    {
        "slide_number": 3,
        "narration": "I see shelves lined with fifty different colorful plastic spray bottles.",
        "visual_type": "HAZEL",
        "visual_value": "hazel_kitchen",
        "motion": "pan_left"
    },
    {
        "slide_number": 4,
        "narration": "Specialize sprays for glass, sprays for counters, sprays for stainless steel...",
        "visual_type": "B_ROLL",
        "visual_value": "broll_cleaning_aisle",
        "motion": "pan_right"
    },
    {
        "slide_number": 5,
        "narration": "it easily adds up to over a hundred dollars a year.",
        "visual_type": "HAZEL",
        "visual_value": "hazel_concerned",
        "motion": "pan_up"
    },
    {
        "slide_number": 6,
        "narration": "But did you know that one simple, ninety-nine cent bottle of plain white vinegar",
        "visual_type": "B_ROLL",
        "visual_value": "broll_vinegar_bottle",
        "motion": "pan_down"
    },
    {
        "slide_number": 7,
        "narration": "can replace almost all of them?",
        "visual_type": "HAZEL",
        "visual_value": "hazel_approval",
        "motion": "zoom_in"
    },
    {
        "slide_number": 8,
        "narration": "The big cleaning companies certainly won't tell you that—",
        "visual_type": "HAZEL",
        "visual_value": "hazel_thinking",
        "motion": "zoom_out"
    },
    {
        "slide_number": 9,
        "narration": "they'd rather sell you an eight-dollar spray with the exact same active ingredient.",
        "visual_type": "B_ROLL",
        "visual_value": "broll_expensive_spray",
        "motion": "pan_left"
    },
    {
        "slide_number": 10,
        "narration": "Today, I'm sharing five genius uses for white vinegar that most people have completely forgotten.",
        "visual_type": "HAZEL",
        "visual_value": "hazel_present",
        "motion": "pan_right"
    },
    {
        "slide_number": 11,
        "narration": "Make sure to stick around for number one—",
        "visual_type": "HAZEL",
        "visual_value": "hazel_one_finger",
        "motion": "pan_up"
    },
    {
        "slide_number": 12,
        "narration": "it's an old-school kitchen trick that saved me from buying a new appliance last year.",
        "visual_type": "HAZEL",
        "visual_value": "hazel_thinking",
        "motion": "pan_down"
    },
    {
        "slide_number": 13,
        "narration": "Let's start with Number Five: reviving your stiff, scratchy bath towels.",
        "visual_type": "B_ROLL",
        "visual_value": "broll_towel_stack",
        "motion": "zoom_in",
        "number": "#5"
    },
    {
        "slide_number": 14,
        "narration": "Over time, laundry detergents and fabric softeners build up on towel fibers, making them rough and non-absorbent. My mother used to do this with every towel in the house back when I was growing up.",
        "visual_type": "HAZEL",
        "visual_value": "hazel_concerned",
        "motion": "zoom_out"
    },
    {
        "slide_number": 15,
        "narration": "To fix this, just toss your towels into the washing machine",
        "visual_type": "B_ROLL",
        "visual_value": "broll_washing_machine",
        "motion": "pan_left"
    },
    {
        "slide_number": 16,
        "narration": "and add one cup of white vinegar directly to the fabric softener dispenser.",
        "visual_type": "HAZEL",
        "visual_value": "hazel_holding",
        "motion": "pan_right"
    },
    {
        "slide_number": 17,
        "narration": "Run a normal hot cycle without any laundry detergent.",
        "visual_type": "HAZEL",
        "visual_value": "hazel_kitchen",
        "motion": "pan_up"
    },
    {
        "slide_number": 18,
        "narration": "The mild acid in the vinegar breaks down those stubborn chemical residues, leaving your towels soft and fluffy again.",
        "visual_type": "B_ROLL",
        "visual_value": "broll_fluffy_towels",
        "motion": "pan_down"
    },
    {
        "slide_number": 19,
        "narration": "It saves you from throwing away perfectly good towels or buying expensive commercial softeners.",
        "visual_type": "HAZEL",
        "visual_value": "hazel_approval",
        "motion": "zoom_in"
    },
    {
        "slide_number": 20,
        "narration": "Next is Number Four: cleaning your window tracks.",
        "visual_type": "B_ROLL",
        "visual_value": "broll_window_track_dirty",
        "motion": "zoom_out",
        "number": "#4"
    },
    {
        "slide_number": 21,
        "narration": "Have you ever looked down at the bottom of your windows and noticed a thick layer of grey dust and grime?",
        "visual_type": "B_ROLL",
        "visual_value": "broll_window_track_dirty",
        "motion": "pan_left"
    },
    {
        "slide_number": 22,
        "narration": "It is incredibly hard to scrub out.",
        "visual_type": "HAZEL",
        "visual_value": "hazel_concerned",
        "motion": "pan_right"
    },
    {
        "slide_number": 23,
        "narration": "Here is what I do: sprinkle a light layer of baking soda in the track,",
        "visual_type": "HAZEL",
        "visual_value": "hazel_kitchen",
        "motion": "pan_up"
    },
    {
        "slide_number": 24,
        "narration": "and then pour white vinegar over it. It will fizz up immediately.",
        "visual_type": "B_ROLL",
        "visual_value": "broll_window_fizzing",
        "motion": "pan_down"
    },
    {
        "slide_number": 25,
        "narration": "Let it sit for five minutes, then wipe it clean with a simple paper towel or old rag.",
        "visual_type": "HAZEL",
        "visual_value": "hazel_table",
        "motion": "zoom_in"
    },
    {
        "slide_number": 26,
        "narration": "The fizzing action loosens the stubborn grime so it wipes away effortlessly.",
        "visual_type": "B_ROLL",
        "visual_value": "broll_window_track_clean",
        "motion": "zoom_out"
    },
    {
        "slide_number": 27,
        "narration": "It saves you from buying expensive specialized track brushes or harsh chemical sprays.",
        "visual_type": "HAZEL",
        "visual_value": "hazel_confident",
        "motion": "pan_left"
    },
    {
        "slide_number": 28,
        "narration": "Moving on to Number Three: keeping your garbage disposal smelling fresh.",
        "visual_type": "B_ROLL",
        "visual_value": "broll_disposal_drain",
        "motion": "pan_right",
        "number": "#3"
    },
    {
        "slide_number": 29,
        "narration": "If your kitchen sink has developed a strange, sour odor, you don't need fancy deodorizer beads.",
        "visual_type": "HAZEL",
        "visual_value": "hazel_kitchen",
        "motion": "pan_up"
    },
    {
        "slide_number": 30,
        "narration": "Try this instead: fill an empty ice cube tray with half water and half white vinegar, and freeze it.",
        "visual_type": "B_ROLL",
        "visual_value": "broll_ice_tray",
        "motion": "pan_down"
    },
    {
        "slide_number": 31,
        "narration": "Once frozen, toss three or four of these vinegar ice cubes down the disposal",
        "visual_type": "HAZEL",
        "visual_value": "hazel_livingroom",
        "motion": "zoom_in"
    },
    {
        "slide_number": 32,
        "narration": "and turn it on with cold running water.",
        "visual_type": "HAZEL",
        "visual_value": "hazel_kitchen",
        "motion": "zoom_out"
    },
    {
        "slide_number": 33,
        "narration": "The ice sharpens the blades while the vinegar neutralizes the odors deep inside.",
        "visual_type": "HAZEL",
        "visual_value": "hazel_thinking",
        "motion": "pan_left"
    },
    {
        "slide_number": 34,
        "narration": "I started doing this when my kids were small and money was tight, and I still do it today. It's a quick, easy, two-cent solution that keeps your kitchen clean and saves you from buying chemical deodorizers.",
        "visual_type": "HAZEL",
        "visual_value": "hazel_thumb_warm",
        "motion": "pan_right"
    },
    {
        "slide_number": 35,
        "narration": "We are about to get to our top two uses, including my absolute favorite kitchen saver.",
        "visual_type": "HAZEL",
        "visual_value": "hazel_present",
        "motion": "pan_up"
    },
    {
        "slide_number": 36,
        "narration": "But before we do, if you enjoy simple, practical tips that help you run a thrifty home,",
        "visual_type": "HAZEL",
        "visual_value": "hazel_point_right",
        "motion": "pan_down"
    },
    {
        "slide_number": 37,
        "narration": "please take a moment to subscribe to the channel and turn on notifications. It really helps me out, and I appreciate your support.",
        "visual_type": "HAZEL",
        "visual_value": "hazel_laugh",
        "motion": "zoom_in"
    },
    {
        "slide_number": 38,
        "narration": "Now for Number Two: removing hard-water buildup from a showerhead.",
        "visual_type": "B_ROLL",
        "visual_value": "broll_showerhead_dirty",
        "motion": "zoom_out",
        "number": "#2"
    },
    {
        "slide_number": 39,
        "narration": "If your shower has lost its pressure or sprays in wild directions, mineral buildup is clogging the tiny nozzles.",
        "visual_type": "B_ROLL",
        "visual_value": "broll_showerhead_dirty",
        "motion": "pan_left"
    },
    {
        "slide_number": 40,
        "narration": "To fix this, pour a cup of white vinegar into a plastic bag.",
        "visual_type": "HAZEL",
        "visual_value": "hazel_holding",
        "motion": "pan_right"
    },
    {
        "slide_number": 41,
        "narration": "Place the bag over the showerhead so it is submerged, and tie it tight with a rubber band.",
        "visual_type": "B_ROLL",
        "visual_value": "broll_showerhead_bag",
        "motion": "pan_up"
    },
    {
        "slide_number": 42,
        "narration": "Let it soak for about forty-five minutes. I learned this trick years ago from a lovely neighbor when our shower pressure got down to a slow drizzle.",
        "visual_type": "HAZEL",
        "visual_value": "hazel_thinking",
        "motion": "pan_down"
    },
    {
        "slide_number": 43,
        "narration": "Then, remove the bag, run the hot water, and wipe the nozzles clean with a sponge.",
        "visual_type": "B_ROLL",
        "visual_value": "broll_showerhead_clean",
        "motion": "zoom_in"
    },
    {
        "slide_number": 44,
        "narration": "It completely restores the water flow and saves you from replacing a perfectly good showerhead.",
        "visual_type": "HAZEL",
        "visual_value": "hazel_approval",
        "motion": "zoom_out"
    },
    {
        "slide_number": 45,
        "narration": "And finally, Number One: descaling your automatic coffee maker.",
        "visual_type": "B_ROLL",
        "visual_value": "broll_coffee_maker",
        "motion": "pan_left",
        "number": "#1"
    },
    {
        "slide_number": 46,
        "narration": "If your coffee maker is brewing slowly or tastes bitter, mineral buildup from your tap water is clogging the heating elements.",
        "visual_type": "B_ROLL",
        "visual_value": "broll_coffee_maker",
        "motion": "pan_right"
    },
    {
        "slide_number": 47,
        "narration": "Don't buy expensive brand-name descaling powders.",
        "visual_type": "HAZEL",
        "visual_value": "hazel_concerned",
        "motion": "pan_up"
    },
    {
        "slide_number": 48,
        "narration": "Just fill the water reservoir with equal parts white vinegar and water, and run a brewing cycle halfway.",
        "visual_type": "HAZEL",
        "visual_value": "hazel_holding",
        "motion": "pan_down"
    },
    {
        "slide_number": 49,
        "narration": "Turn the machine off, let the vinegar sit inside the elements for thirty minutes, then finish the cycle.",
        "visual_type": "HAZEL",
        "visual_value": "hazel_kitchen",
        "motion": "zoom_in"
    },
    {
        "slide_number": 50,
        "narration": "Run two cycles of plain water after that to rinse it.",
        "visual_type": "B_ROLL",
        "visual_value": "broll_coffee_brewing",
        "motion": "zoom_out"
    },
    {
        "slide_number": 51,
        "narration": "This simple routine dissolves the scale, extends the life of your machine, and keeps your coffee tasting fresh. I learned this the hard way after neglecting my coffee maker for a year and ruining my morning cup.",
        "visual_type": "B_ROLL",
        "visual_value": "broll_coffee_brewing",
        "motion": "pan_left"
    },
    {
        "slide_number": 52,
        "narration": "It saved me from buying a new coffee maker last year.",
        "visual_type": "HAZEL",
        "visual_value": "hazel_thumb_excited",
        "motion": "pan_right"
    },
    {
        "slide_number": 53,
        "narration": "Which of these five vinegar tips are you going to try first?",
        "visual_type": "HAZEL",
        "visual_value": "hazel_smile",
        "motion": "pan_up"
    },
    {
        "slide_number": 54,
        "narration": "Or maybe you have an old-school tip of your own that I missed?",
        "visual_type": "HAZEL",
        "visual_value": "hazel_present",
        "motion": "pan_down"
    },
    {
        "slide_number": 55,
        "narration": "Please let me know in the comments below—I read every single one.",
        "visual_type": "HAZEL",
        "visual_value": "hazel_laugh",
        "motion": "zoom_in"
    },
    {
        "slide_number": 56,
        "narration": "YouTube thinks you will like this next video on the screen, so I will see you over there.",
        "visual_type": "HAZEL",
        "visual_value": "hazel_point_left",
        "motion": "zoom_out"
    }
]

def step1_voiceover():
    print("\n--- STEP 1: Voiceover Generation ---")
    from lib.gathos_client import generate_tts
    # Submit TTS jobs sequentially with robust retries
    for slide in SLIDES:
        num = slide["slide_number"]
        txt = slide["narration"]
        out_name = f"slide-{num:02d}.wav"
        out_path = AUDIO_DIR / out_name
        
        if out_path.exists() and out_path.stat().st_size > 0:
            print(f"  Audio slide-{num:02d}.wav already exists. Skipping API call.")
            continue
            
        print(f"  Generating TTS for slide-{num:02d}... text: '{txt[:30]}...'")
        success = False
        for attempt in range(10):
            try:
                generate_tts(txt, "hazel_2", str(out_path))
                success = True
                time.sleep(3) # rate limit friendly sleep
                break
            except Exception as e:
                print(f"  Warning: TTS generation failed for slide-{num:02d} (attempt {attempt+1}/10): {e}")
                if "429" in str(e):
                    wait_time = 45 # wait 45s for rate limit cooldown
                    print(f"  Rate limit hit. Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                else:
                    time.sleep(5)
        if not success:
            print(f"  ERROR: Failed to generate audio for slide-{num:02d} after 10 attempts.")
            sys.exit(1)

    # Combine all wav files into master voiceover.wav
    print("  Combining slide WAVs into master voiceover.wav...")
    concat_list_path = AUDIO_DIR / "_concat_list.txt"
    with open(concat_list_path, "w") as f:
        for slide in SLIDES:
            num = slide["slide_number"]
            wav_path = AUDIO_DIR / f"slide-{num:02d}.wav"
            f.write(f"file '{wav_path.name}'\n")

    master_voiceover_path = BASE_OUTPUT_DIR / "voiceover.wav"
    # Execute ffmpeg concat
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_list_path),
        "-c", "copy",
        str(master_voiceover_path)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"  ERROR concatenating voiceover files: {res.stderr}")
        sys.exit(1)
    
    # Cleanup concat list
    concat_list_path.unlink(missing_ok=True)
    print(f"  Created master voiceover: {master_voiceover_path}")


def step2_broll():
    print("\n--- STEP 2: B-Roll Image Generation ---")
    from lib.gathos_client import generate_image
    
    # We submit the 16 unique B-rolls sequentially with robust retries
    for key, base_prompt in BROLL_MAPPING.items():
        out_name = f"{key}.jpeg"
        out_path = BROLL_DIR / out_name
        
        if out_path.exists() and out_path.stat().st_size > 0:
            print(f"  B-roll {out_name} already exists. Skipping.")
            continue
            
        full_prompt = base_prompt + STYLE_ANCHOR
        print(f"  Generating B-roll for '{key}'...")
        success = False
        for attempt in range(10):
            try:
                generate_image(full_prompt, str(out_path), width=1344, height=768)
                success = True
                time.sleep(3) # rate limit friendly sleep
                break
            except Exception as e:
                print(f"  Warning: Image generation failed for '{key}' (attempt {attempt+1}/10): {e}")
                if "429" in str(e):
                    wait_time = 45 # wait 45s for rate limit cooldown
                    print(f"  Rate limit hit. Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                else:
                    time.sleep(5)
        if not success:
            print(f"  ERROR: Failed to generate B-roll '{key}' after 10 attempts.")
            sys.exit(1)

    print("  All B-roll images checked/generated.")


def step3_hazel_shots():
    print("\n--- STEP 3: Hazel Poses Copying & Variant-Switching ---")
    used_variants = {} # family -> list of file paths used
    
    # Pre-scan HOST_LIBRARY_DIR for family files
    library_files = list(HOST_LIBRARY_DIR.glob("*.jpeg"))
    
    for slide in SLIDES:
        if slide["visual_type"] == "HAZEL":
            family = slide["visual_value"]
            num = slide["slide_number"]
            dest_path = HAZEL_SHOTS_DIR / f"slide-{num:02d}.jpeg"
            
            # Find matching library files
            matches = [
                f for f in library_files
                if f.name.startswith(family + "_") or f.name == f"{family}.jpeg"
            ]
            
            if not matches:
                print(f"  WARNING: No library files found for family '{family}'!")
                # Fallback to host_REFERENCE.jpeg or any fallback
                matches = [HOST_LIBRARY_DIR / "host_REFERENCE.jpeg"]
            
            # Filter matches to select least used variant
            matches_paths = [str(m) for m in matches]
            # Shuffle options to add randomness
            random.shuffle(matches_paths)
            
            # Choose the one with the minimum usage count in the video
            chosen_path = min(
                matches_paths,
                key=lambda p: used_variants.get(family, []).count(p)
            )
            
            # Track usage
            used_variants.setdefault(family, []).append(chosen_path)
            
            # Copy to destination
            shutil.copy2(chosen_path, dest_path)
            print(f"  Copied {Path(chosen_path).name} to hazel_shots/slide-{num:02d}.jpeg")


def step4_onscreen_numbers():
    print("\n--- STEP 4: Draw Countdown Numbers with Pillow ---")
    
    for slide in SLIDES:
        num = slide["slide_number"]
        dest_path = None
        
        # Prepare B-roll slide-specific copy first so we don't draw on base B-roll
        if slide["visual_type"] == "B_ROLL":
            broll_key = slide["visual_value"]
            src_broll = BROLL_DIR / f"{broll_key}.jpeg"
            dest_path = BROLL_SHOTS_DIR / f"slide-{num:02d}.jpeg"
            shutil.copy2(src_broll, dest_path)
        else:
            dest_path = HAZEL_SHOTS_DIR / f"slide-{num:02d}.jpeg"
            
        # Draw number if required
        number_text = slide.get("number", None)
        if number_text:
            print(f"  Drawing {number_text} on slide-{num:02d}.jpeg...")
            with Image.open(dest_path) as img:
                img = img.convert("RGBA")
                W, H = img.size
                
                # Determine font size (large, approx 10% of height)
                font_size = int(H * 0.10)
                try:
                    font = ImageFont.truetype("arialbd.ttf", font_size)
                except IOError:
                    try:
                        font = ImageFont.truetype("C:\\Windows\\Fonts\\arialbd.ttf", font_size)
                    except IOError:
                        font = ImageFont.load_default()
                        
                draw = ImageDraw.Draw(img)
                
                # Position (top-left margin)
                x = int(W * 0.06)
                y = int(H * 0.06)
                
                # White fill, heavy black outline (Pillow 6.2+)
                draw.text(
                    (x, y),
                    number_text,
                    font=font,
                    fill=(255, 255, 255, 255),
                    stroke_width=int(font_size * 0.08),
                    stroke_fill=(0, 0, 0, 255)
                )
                
                # Save back as RGB
                final_img = img.convert("RGB")
                final_img.save(dest_path, "JPEG")
                print(f"    Saved text onto {dest_path}")


def get_audio_duration(audio_path: str) -> float:
    cmd = [
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", audio_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return 4.0 # default fallback
    import json
    data = json.loads(result.stdout)
    return float(data["format"]["duration"])


def create_slide_clip_custom(image_path: str, audio_path: str, output_path: str, motion: str) -> str:
    """Creates individual slide clip with custom motion parameters."""
    audio_dur = get_audio_duration(audio_path)
    total_frames = int(audio_dur * FPS)
    if total_frames <= 0:
        total_frames = 24
        
    # Scale speed zoom
    zoom_speed = 0.12 / total_frames
    
    # Select motion
    if motion == "zoom_in":
        vf = f"scale=8000:-1,zoompan=z='1+{zoom_speed:.8f}*in':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={total_frames}:s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:fps={FPS}"
    elif motion == "zoom_out":
        vf = f"scale=8000:-1,zoompan=z='1.12-{zoom_speed:.8f}*in':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={total_frames}:s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:fps={FPS}"
    elif motion == "pan_left":
        vf = f"scale=8000:-1,zoompan=z='1.12':x='(1-in/{total_frames})*(iw-iw/zoom)':y='ih/2-(ih/zoom/2)':d={total_frames}:s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:fps={FPS}"
    elif motion == "pan_right":
        vf = f"scale=8000:-1,zoompan=z='1.12':x='(in/{total_frames})*(iw-iw/zoom)':y='ih/2-(ih/zoom/2)':d={total_frames}:s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:fps={FPS}"
    elif motion == "pan_up":
        vf = f"scale=8000:-1,zoompan=z='1.12':x='iw/2-(iw/zoom/2)':y='(1-in/{total_frames})*(ih-ih/zoom)':d={total_frames}:s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:fps={FPS}"
    elif motion == "pan_down":
        vf = f"scale=8000:-1,zoompan=z='1.12':x='iw/2-(iw/zoom/2)':y='(in/{total_frames})*(ih-ih/zoom)':d={total_frames}:s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:fps={FPS}"
    else: # fallback to zoom_in
        vf = f"scale=8000:-1,zoompan=z='1+{zoom_speed:.8f}*in':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={total_frames}:s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:fps={FPS}"

    cmd = [
        "ffmpeg", "-y",
        "-i", image_path,
        "-i", audio_path,
        "-vf", vf,
        "-c:v", "libx264", "-preset", "fast",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        output_path,
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg slide clip failed: {result.stderr}")
    return output_path


def step5_assemble():
    print("\n--- STEP 5: Assembly (FFmpeg Clip Creation + Concat) ---")
    clip_paths = []
    
    for slide in SLIDES:
        num = slide["slide_number"]
        motion = slide["motion"]
        
        # Determine image source path
        if slide["visual_type"] == "B_ROLL":
            img_path = BROLL_SHOTS_DIR / f"slide-{num:02d}.jpeg"
        else:
            img_path = HAZEL_SHOTS_DIR / f"slide-{num:02d}.jpeg"
            
        audio_path = AUDIO_DIR / f"slide-{num:02d}.wav"
        clip_path = CLIPS_DIR / f"clip-{num:02d}.mp4"
        
        print(f"  Creating slide {num} clip with motion '{motion}'...")
        create_slide_clip_custom(str(img_path), str(audio_path), str(clip_path), motion)
        clip_paths.append(str(clip_path))

    # Concat all slides
    print("  Concatenating clips...")
    concat_list_path = CLIPS_DIR / "_concat_list.txt"
    with open(concat_list_path, "w") as f:
        for clip in clip_paths:
            # Must double-escape paths for FFmpeg demuxer
            clean_name = Path(clip).name
            f.write(f"file '{clean_name}'\n")
            
    temp_final_path = FINAL_DIR / "temp_assembled.mp4"
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_list_path),
        "-c", "copy",
        str(temp_final_path)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"  ERROR concatenating video clips: {res.stderr}")
        sys.exit(1)
        
    # Cleanup clip files and concat file
    concat_list_path.unlink(missing_ok=True)
    for clip in clip_paths:
        Path(clip).unlink(missing_ok=True)
        
    print(f"  Assembled raw video: {temp_final_path}")


def split_text_to_chunks(text, max_words=6):
    """Splits a single slide text block into subtitle chunks of 1 or 2 lines (max 6 words per line)."""
    words = text.split()
    chunks = []
    
    # Group words into lines of at most max_words
    lines = []
    current_line = []
    for w in words:
        if len(current_line) < max_words:
            current_line.append(w)
        else:
            lines.append(" ".join(current_line))
            current_line = [w]
    if current_line:
        lines.append(" ".join(current_line))
        
    # Combine lines into 2-line phrase chunks
    for i in range(0, len(lines), 2):
        chunk_lines = lines[i:i+2]
        chunks.append(chunk_lines)
        
    return chunks


def format_srt_time(seconds: float) -> str:
    """Formats float seconds into SRT timestamp string: HH:MM:SS,mmm"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def step6_captions():
    print("\n--- STEP 6: Captions Generation & Outlined Subtitle Burn-In ---")
    
    # Calculate timestamps slide-by-slide
    srt_entries = []
    current_time = 0.0
    subtitle_idx = 1
    
    for slide in SLIDES:
        num = slide["slide_number"]
        audio_path = AUDIO_DIR / f"slide-{num:02d}.wav"
        slide_dur = get_audio_duration(str(audio_path))
        text = slide["narration"]
        
        # Split text into phrase chunks
        chunks = split_text_to_chunks(text, max_words=5) # 5-6 words max per line
        
        # Assign duration to each chunk proportionally based on word count
        total_words = len(text.split())
        if total_words <= 0:
            total_words = 1
            
        chunk_start = current_time
        for chunk in chunks:
            chunk_text = "\n".join(chunk)
            chunk_word_count = sum(len(line.split()) for line in chunk)
            chunk_dur = (chunk_word_count / total_words) * slide_dur
            chunk_end = chunk_start + chunk_dur
            
            # Safeguard end time
            if chunk_end > current_time + slide_dur:
                chunk_end = current_time + slide_dur
                
            start_str = format_srt_time(chunk_start)
            end_str = format_srt_time(chunk_end)
            
            srt_entries.append(
                f"{subtitle_idx}\n{start_str} --> {end_str}\n{chunk_text}\n\n"
            )
            subtitle_idx += 1
            chunk_start = chunk_end
            
        current_time += slide_dur

    srt_path = BASE_OUTPUT_DIR / "captions.srt"
    with open(srt_path, "w", encoding="utf-8") as f:
        f.writelines(srt_entries)
    print(f"  Created SRT captions file: {srt_path}")

    # Burn captions into final video with FFmpeg
    temp_final_path = FINAL_DIR / "temp_assembled.mp4"
    final_output_path = FINAL_DIR / "vinegar_final.mp4"
    
    # Subtitles path escaping for FFmpeg (needs forward slashes and escaped colon on Windows)
    escaped_srt = str(srt_path).replace("\\", "/").replace(":", "\\:")
    
    print("  Burning captions into the video...")
    # Alignment=2 is lower-center, MarginV=25 pulls it up slightly
    # BorderStyle=3 adds a semi-transparent background box, Outline=1 outline
    cmd = [
        "ffmpeg", "-y",
        "-i", str(temp_final_path),
        "-vf", f"subtitles='{escaped_srt}':force_style='Alignment=2,FontSize=18,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,Outline=2,BorderStyle=3,MarginV=25'",
        "-c:a", "copy",
        str(final_output_path)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"  ERROR burning captions: {res.stderr}")
        sys.exit(1)

    # Cleanup temp video file
    temp_final_path.unlink(missing_ok=True)
    print(f"  FINAL VIDEO CREATED: {final_output_path}")


def main():
    print("============================================================")
    print("BUILDING THRIFTYHAZEL VIDEO PIPELINE")
    print("Target: 5 Genius Uses for White Vinegar Most People Forgot")
    print("============================================================")
    
    step1_voiceover()
    step2_broll()
    step3_hazel_shots()
    step4_onscreen_numbers()
    step5_assemble()
    step6_captions()
    
    print("\n============================================================")
    print("PIPELINE COMPLETED SUCCESSFULLY!")
    print(f"Final output is located at: {FINAL_DIR / 'vinegar_final.mp4'}")
    print("============================================================")


if __name__ == "__main__":
    main()
