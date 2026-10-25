---
name: mediasift
description: 'Sense a video or audio file (or a web video URL) you cannot watch or hear. One command turns it into a card - a timeline of what changed on screen, which sounds happened and how many times, speech with times, and text that appeared - plus frame sheets to look at and a zoom command for any span. Use when the task involves a video, screen recording or audio file: a bug-repro recording, a UI walkthrough, a tutorial, a lecture, a meeting or podcast, a YouTube link, "what happens in this video", "when does X happen", "what did the error say", "how many times", "what was on screen when they said ...".'
---

# mediasift

You cannot watch video or hear audio. mediasift does both for you, cheaply, and writes down what it
sensed so you can reason over time instead of guessing from a few stills.

## 0. If `mediasift` is not installed

Check with `command -v mediasift`. If it is missing, tell the user and suggest one of these. Do not
install it yourself without asking: it pulls about 1 GB of Python packages.

```bash
uv tool install git+https://github.com/samhvw8/mediasift      # with uv
mise use -g pypi:samhvw8/mediasift                            # with mise (pipx: works too)
```

It also needs `ffmpeg` on PATH (`brew install ffmpeg`, `apt install ffmpeg` or `mise use -g ffmpeg`),
and `yt-dlp` for web URLs. The first run downloads its models: about 60 MB for sound and voices,
more for the speech model of the language it hears.

## 1. Sense it (pick a mode from context, or probe/adapt when unknown)

```bash
mediasift see VIDEO_OR_URL                        # full sense pass (cached by file content)
mediasift see VIDEO_OR_URL --mode adaptive        # unknown video: probes grid+sound+S2T, then runs only relevant passes
mediasift see VIDEO_OR_URL --mode probe           # fast lightweight pass: S2T transcript + 32x18 keyframe sheets + sound tags
```

When the filename, URL, or user prompt tells you what kind of media it is, pick the matching `--mode` so you skip passes that cost time and tokens without helping the task:

| Context / media kind | Command | Active passes | Skipped passes |
|---|---|---|---|
| **Unknown file / link** (want fast transcript + keyframe grid first) | `mediasift see VIDEO --mode probe` | `pic,sounds,speech` | `ocr,harmony,voices,emotion` |
| **Unknown file / link** (want one smart pass) | `mediasift see VIDEO --mode adaptive` | Probes `pic,sounds,speech`, then auto-enables `ocr`, `harmony`, `voices`, or `emotion` from signal | Unneeded heavy passes |
| **Podcast / interview / lecture / meeting / voice note** | `mediasift see VIDEO --mode podcast` | `sounds,speech,voices,emotion` (add `--with pic` if slides/visuals matter) | `pic,ocr,harmony` (saves 60–85% time & 35–45% card lines) |
| **Music video / song / score / beat-synced edit** | `mediasift see VIDEO --mode music` | `pic,sounds,harmony,speech` | `ocr,voices,emotion` |
| **Brain-rot reel / TikTok / YouTube Short / meme** | `mediasift see VIDEO --mode reel` | `pic,ocr,sounds,speech` | `harmony,voices,emotion` |
| **Bug-repro screen recording / UI walkthrough** | `mediasift see VIDEO --mode screen` | `pic,ocr,sounds,speech` | `harmony,voices,emotion` |
| **Full / mixed film** | `mediasift see VIDEO` (or `--mode full`) | `pic,ocr,sounds,harmony,speech,voices,emotion` | none |

### Turning individual functions on or off (`--with` / `--without`)

Every pass can be toggled on any mode (`pic`, `ocr`, `sounds`, `harmony`, `speech`, `voices`, `emotion`):
- **Upgrade a `probe` or `podcast` card incrementally:** if you ran `--mode probe` first and see you need on-screen text or speaker letters, run `mediasift see VIDEO --with ocr,voices`. It reuses the cached transcript and frame grid in `sensed.json` and runs **only** the missing passes.
- **Trim a noisy card:** if a card is already cached and you only want speech and speaker turns without picture or harmony lines, run `mediasift see VIDEO --mode podcast` (or `--without pic,harmony`) to re-render `card.md` in `< 50 ms`.
- `--on HOST` sends speech recognition to a GPU box over ssh (falls back to local if the box does not answer).

## 2. Read the card first

The card's timeline interleaves four kinds of line, all timestamped:

| line | means |
|---|---|
| `pic` | the picture changed: where (`small red area at bottom`), how (`changed`, `flashed ... and changed back`, `moved: left (...)`, `kept changing in place`), how long it stayed (`it lasted 0.7 s`), how many times (`changed 10 times, at ...`), text that appeared (OCR), and a sound that landed with it. `CUTS (n) at ...` lists new shots (`A`, `B`, ... for repeated places). |
| `snd` | a sound: `[music] (scary, electronic; C minor -> Eb major at 01:14, ~120 BPM, cuts sync 5/6)` (mood, genre, key/mode, harmonic shift, tempo, and cut-to-beat sync on music beds >= 5 s), `[siren]`, `[telephone tone, 2 separate bursts]`, `[beep x5] at 1.5, 2.9 ... s (mid-pitched (~1000 Hz), short, sharp)`, `[silence 2.9 s]` |
| `talk` | speaker-relative vocal emotion shift over a segment: `talk A [heated (+3.8 dB, sharp tone)]`, `talk B [subdued (-3.1 dB, 0.7x pace, 3 long pauses)]`, or `[animated (laughter)]` |
| `say` | speech with times; `[voice A, male]`/`[voice B, female]` group lines by speaker (not identity); with one speaker the tag is left out and said once below |

Many questions are answered by the card alone: what an error said, how many times something
happened, which flash came with a beep, where a speaker became heated or hesitant, whether cuts are beat-synced, or what changed after a click.
Counts and times of flashes and short sounds are measured; trust them over your eyes on a sheet.
Region words (colour, position, size) come from pixel statistics: open an image before relying on them.

## 3. Look only where you need to

- **Flow sheets** (`flow_NN.jpg`, listed in the card with the time each covers): 12 frames per image,
  about one per second where the picture moves and one per still stretch, every shot included. Open
  the sheet for the time you need, not all of them.
- **Event sheets** (`ev_NN.jpg`, referenced in `pic` lines): `[where | before | after]` crops of one
  event, for small text and UI detail.
- **Zoom by time or by spoken words**: for a gesture, a face or small text at one moment, do not guess from a flow tile (about one
  small frame a second):
  - `mediasift look VIDEO 11.5-13` gives 8 frames over that time span plus a strip of the sound under them.
  - `mediasift look VIDEO --say "don't stay up late"` jumps directly to the exact word timestamps where that phrase was spoken (even inside a long clause), brackets the words in yellow on the sound strip, and renders 8 frames around the gesture.
  - `-n 2` for a before/after pair, `-n 1` for one moment at full width.

Budget: a question usually needs the card plus one to three images. If two `look` calls do not show
it, answer from what you have and say what you could not confirm.
## 4. Correct a wrong sound name

Sound names come from a tagger and are sometimes wrong (a cough heard as "throat clearing"). When
the user or a frame you looked at shows what a sound really was, record it:

    mediasift fix VIDEO 21.0 "cough"

Only when you know, never as a guess. Repeated agreeing fixes teach later cards
("throat clearing (usually: cough)"); `mediasift feedback` lists them.

## Long videos

For talks over a few minutes the card summarises speech one line per minute and points to
`transcript.txt` (every line with times, and `A:`/`B:` speaker letters when more than one person
speaks): grep it for words or for one speaker, then `look` at the times you find.
Picture lines are capped; quieter stretches appear as `+N smaller changes` with a time range to zoom.

## Other commands (unchanged from earlier versions)

`mediasift frames VIDEO --start A --end B --fps 2 -o DIR` (raw frames), `mediasift analyze` (segments
and keyframes, the old storyboard), `index` / `find` (search frames by meaning, needs llama.cpp),
`split` (cut clips).

Cite moments by time, e.g. `@ 00:11.9`.
