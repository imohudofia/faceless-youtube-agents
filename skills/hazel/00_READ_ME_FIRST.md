# READ ME FIRST — Hazel Pipeline Skills (clean, consolidated v1)

_This folder is the SINGLE SOURCE OF TRUTH for the Hazel channel pipeline. Every file here is final and consistent (no contradictions, no old "doctor/duck" mistakes). Download all files in this folder and place them as instructed below._

---

## WHERE TO PUT THESE FILES
Create a folder called `skills` INSIDE your cloned engine, then drop ALL these `.md` files there:

```
C:\Users\imoh2\Developer\faceless-youtube\faceless-youtube-agents\skills\hazel\
   ├── 00_READ_ME_FIRST.md          (this file)
   ├── 01_channel_brief.md
   ├── 02_content_format.md
   ├── 03_character_and_assets.md
   ├── 04_gathos_generation_rules.md
   ├── 05_assembly_motion_rules.md
   └── 06_compliance_checklist.md
```

> Note: the engine already has its OWN `skills/` folder. We put ours in a `skills\hazel\` subfolder so they don't clash. After placing them, tell Antigravity:
> *"Read all files in `skills\hazel\` and treat them as the binding rules for producing Hazel-channel videos."*

---

## THE WHOLE SYSTEM IN ONE PICTURE (deliberately simple)
ONE engine + your asset library + these rule files. No Hyperframes, no extra repos.

```
Antigravity (you direct it)
  └─ faceless-youtube-agents (THE engine: script → images → voice → FFmpeg → mp4)
       reads rules from → skills\hazel\*.md
       pulls Hazel shots from → C:\Users\imoh2\Developer\faceless-youtube\hazel\host_library\
       generates B-roll via → Gathos image API (2D + style anchor)
       generates voice via → Gathos TTS (voice = hazel_2)
       assembles via → FFmpeg (varied motion, hard cuts)
  └─ YOU upload the finished mp4 + thumbnail manually
```

## WHAT WE DELIBERATELY ARE *NOT* USING (and why)
- **Hyperframes** — motion-graphics tool; overkill for a calm frugality channel. Adds install + failure points for visuals this niche doesn't need. Revisit only if a future channel needs fancy motion graphics.
- **RookCast / shorts-pipeline as code** — NOT forked or run. Their best ideas (hooks, countdown structure, retention) are already distilled into `02_content_format.md`. Use as knowledge, not extra software.
- **ControlNet / ComfyUI** — needs a GPU you don't have; not needed (Hazel consistency = library reuse).
- **YouTube auto-upload** — disabled; you upload manually for quality control.

WHY: the operators who actually succeed "own one workflow" and keep it simple. Fewer tools = fewer breakages = a cleaner, more sellable system. Simplicity is the strategy.

---

## STATUS CHECKLIST (what's done)
- [x] Engine forked + cloned + understood
- [x] .env filled (Gathos image + TTS keys), confirmed git-ignored
- [x] Voice locked: hazel_2
- [x] Hazel library built (~48 images, .jpeg, with variants) in host_library\
- [x] Niche/persona/format locked (see 01 + 02)
- [ ] Place these skill files → tell Antigravity to read them
- [ ] Stage 1: generate vinegar-video script + shot list (approve)
- [ ] Stage 2: customize assembler + generate the test video
- [ ] Review → manual upload
