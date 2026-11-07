# AI-Driven Distraction Detection App for Students

A desktop focus app for Windows that watches the active window during a study
session, uses a zero-shot AI classifier to decide whether the content is
distracting, and intervenes by logging it (and optionally closing it). It adds a
Pomodoro timer, XP-based gamification, daily statistics, and ambient background
music.

**Team:** Coffee Overflow — Om Khanjodkar, Pranav Dabeer, Siddhant Verma, Swara Kulkarni

---

## What it does

- **Pomodoro focus timer** — session length configurable from 10 to 180 minutes,
  with countdown, progress bar, and motivational quotes.
- **AI distraction detection** — a background watcher (`backend.py`) checks the
  active window every 0.25 s and classifies it with
  `facebook/bart-large-mnli` zero-shot classification.
- **Browser-aware checking** — for YouTube tabs in Chrome, Opera, or Edge it
  strips the browser and site from the window title, searches YouTube for the
  video, scrapes its description, and classifies the title plus description.
- **Intervention styles** — `nudge` shows a warning dialog; `auto-close` focuses
  the offending window and sends `Ctrl+W`.
- **Distraction log** — every detection is stored with a timestamp and shown in
  a scrollable viewer with a total and the most frequent distraction.
- **Gamification** — earn 1 XP per 6 minutes of focus, level up every 100 XP, and
  view XP progress and achievements.
- **Ambient music** — five bundled tracks with play, pause, resume, and volume
  control via `pygame.mixer`.
- **Session data** — daily focused minutes, distraction count, session history,
  and XP persisted as JSON.

## Project structure

```
distraction-destroyers/
├── main.py                     # Tkinter GUI: dashboard, timer, settings, XP, logs
├── backend.py                  # AI distraction watcher, started per focus session
├── userData.json               # backendActive flag, Intervention Style, Session Time
├── userSessions.json           # Completed sessions: [minutes, timestamp]
├── userXP.json                 # Accumulated XP
├── distractionHistory.json     # Detected distractions: [window title, timestamp]
└── assets/music/               # ambient1.mp3 - ambient5.mp3
```

## Tech stack

- **GUI:** `tkinter` / `ttk`
- **Audio:** `pygame.mixer`
- **AI/ML:** `transformers`, `torch` with `facebook/bart-large-mnli` (zero-shot
  classification)
- **Window automation:** `pywinauto` (UIA backend), `pyautogui`, `keyboard`
- **Web scraping:** `requests`, `BeautifulSoup`, `re`, `urllib.parse`
- **Storage:** plain JSON files (`json`, `datetime`, `os`)

## Requirements

- Windows (window inspection and automation are Windows-specific)
- Python 3.10+
- Internet access on first run to download the BART model and to look up YouTube
  videos

`backend.py` runs this install line when it starts:

```python
os.system("pip install pywin32 pyautogui pywinauto keyboard transformers torch yt-dlp requests beautifulsoup4")
```

To install manually instead:

```bash
pip install pywin32 pyautogui pywinauto keyboard transformers torch requests beautifulsoup4 pygame
```

The first detection downloads `facebook/bart-large-mnli` (roughly 1.6 GB) and
loads it on CPU, which can take several minutes.

## Running the app

From the project root:

```bash
python main.py
```

The dashboard has four actions:

1. **Distraction History** — scroll through detections and see the summary.
2. **Customize Settings** — choose the intervention style (`nudge` or
   `auto-close`) and the session length.
3. **Gamification & Rewards** — level, XP bar, and achievements.
4. **Open Timer Screen** — start a focus session.

Pressing **Start** begins the countdown, launches `backend.py` in a separate
command window, and sets `backendActive` to `true` in `userData.json`. Pressing
**Stop**, finishing the timer, or the session ending sets it to `false` and
records the session duration and XP. The watcher polls that flag and exits on
its own.

## Dataset

No external dataset was used. The project classifies real-time window titles and
scraped YouTube titles/descriptions with the pre-trained
`facebook/bart-large-mnli` model. Candidate labels are Gaming, Drama, Education,
Technology, Programming, and Sports; a result is treated as safe when the
`Education` or `Programming` score exceeds 0.30, otherwise it is logged as a
distraction.

## How detection works

```
main.py (Start)
   ├──► userData.json  (backendActive = true)
   └──► backend.py
          ├── reads open window titles via pywinauto
          ├── matches hardcoded distracting sites (social media, streaming,
          │   gaming, shopping, clickbait) against the title
          ├── for YouTube tabs: scrape the video description, then classify
          │   title + description with facebook/bart-large-mnli
          ├── logs the window title and timestamp to distractionHistory.json
          └── applies the intervention style
                 ├── nudge      → warning dialog
                 └── auto-close → activate window, send Ctrl+W
```

## Data files

| File | Contents |
| --- | --- |
| `userData.json` | `backendActive`, `Intervention Style`, `Session Time` (minutes) |
| `userSessions.json` | `Sessions`: list of `[duration_minutes, "dd/mm/yy HH:MM:SS"]` |
| `userXP.json` | `XP`: total experience points |
| `distractionHistory.json` | `Distractions`: list of `[window_title, timestamp]` |

## Notes and limitations

- The app is Windows-only and the backend opens its own console window.
- `auto-close` sends `Ctrl+W` to the detected window, so it closes the current
  tab when that window is a browser.
- The bundled `distractionHistory.json`, `userSessions.json`, and `userXP.json`
  contain sample/session data from development and are not reset automatically.
