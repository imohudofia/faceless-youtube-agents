# 09 — Background Music (apply to every video)

_Binding rules for adding background music to ThriftyHazel videos. The engine does NOT add music automatically (it only does voiceover + Ken Burns + concat), so you (the agent) must add music as a deliberate final step on every video._

---

## GOAL
Add a soft, warm, calm instrumental music bed under Hazel's voiceover — present but barely noticed. It must never compete with or obscure her voice.

## SOURCING (royalty-free only)
- Use ONLY royalty-free / no-attribution-required music (YouTube Audio Library or Pixabay Music). Never use copyrighted or commercial songs — they cause Content ID claims or strikes.
- Choose tracks that are: instrumental, calm, warm, slow-tempo, no vocals, no strong attention-grabbing melody (cozy lifestyle/ambient mood).
- Store reusable tracks in `C:\Users\imoh2\Developer\faceless-youtube\hazel\music\`. Reuse from this folder across videos instead of re-downloading. Rotate among 3–5 tracks so the channel is not always the same tune.

## MIXING RULES
- Hazel's voiceover (hazel_2) is PRIMARY and must always stay clearly intelligible.
- Mix the music FAR under the voice using either method:
  - Simple: set music to ~10–15% of the voice volume for the whole video.
  - Preferred (ducking): apply FFmpeg sidechain compression so the music dips ~10–12 dB whenever Hazel speaks and rises slightly during gaps, intro, and outro.
- Loudness targets: voice ~ -16 LUFS; music ducked to ~ -28 to -32 LUFS.
- Music plays continuously for the full video length. Loop/stitch it to the duration and crossfade the loop seams (~1–2s) so there is no hard jump or silence.
- Optional polish: a small music swell (slightly louder for ~3s) at the very intro and very outro.

## STEPS (perform in the FINAL assembly stage)
1. After the video + voiceover are assembled, select a royalty-free track from `hazel\music\`.
2. Loop the track to the full video duration; crossfade loop seams.
3. Lower the music volume to ~10–15% OR apply sidechain ducking (~10 dB) keyed to the voiceover.
4. Mix music under the voiceover and render the final mp4 in one FFmpeg pass.
5. Verify Hazel's voice is clearly intelligible and the music never spikes over it.

## ONE-TIME PIPELINE UPGRADE
- Add this music-mix step into the assembler (`video_assembler.py`) so future videos perform it automatically without a separate instruction.

## CHECKLIST (before final render)
- [ ] Track is royalty-free (YouTube Audio Library / Pixabay), instrumental, calm
- [ ] Voice stays clearly intelligible
- [ ] Music at ~10–15% volume OR ducked ~10 dB under the voice
- [ ] Music loops/crossfades for full length (no seam, no silence)
- [ ] Track rotated (not the identical tune every video)
- [ ] No copyrighted music used
