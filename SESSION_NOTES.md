# Proof QA Tool — Session Notes (Feb 13, 2026)

**Last session:** Feb 13, 2026
**Last commit:** f57e2e5 — "Rebuild Phone Call mode with custom voice component"

---

## What Got Done Today

### Ownership Migration (Complete)
- GitHub repo moved to `Keepitcity/proof` (personal account)
- Streamlit Cloud deployed at `proof-app.streamlit.app` under Keepitcity
- Google OAuth project: "Proof by Shawn Hernandez" (shawn.keepitcity@gmail.com)
- Redirect URIs: localhost:8502 + proof-app.streamlit.app
- All credentials saved to `CREDENTIALS_REFERENCE.md` (gitignored)

### ConsultationX Feature (Built from scratch)
- **Backend engine** (`consultation_x.py`): 897 lines
  - Groq API (Llama 3.3 70B) plays the simulated client
  - Claude API evaluates and scores the consultation
  - 10 scenario templates (5 PM, 5 Sales)
  - 48 first names, 47 last names, 20 brokerages, 30 cities
  - 6 scoring categories, A+ through D tiers
- **Three modes:** Phone Call, Text Chat, Email
- **UI wired into main app** with navbar link + BETA badge
- **Session persistence** — survives browser refresh

### UI Improvements
- DiceBear avatar faces for contact cards (unique per persona)
- All emojis replaced with black & white SVG icons
- Phone ringing sound when call starts

### API Integrations Added
- Groq API key in secrets.toml + Streamlit Cloud
- ElevenLabs API key in secrets.toml + Streamlit Cloud
- Anthropic already existed

---

## What Needs Work Next (Priority Order)

### 1. Phone Call Voice — NOT WORKING YET
**Problem:** The custom `declare_component` approach has issues:
- **TTS (hearing the client):** ElevenLabs generates audio server-side, but the custom iframe component can't reliably play it. Browser blocks audio autoplay in iframes.
- **Speech recognition (talking back):** Web Speech API doesn't work inside Streamlit's component iframes because the iframe lacks `allow="microphone"` permissions.
- **Current state:** The ringing UI shows, Pick Up / Decline buttons appear, but after picking up you can't hear the client and the "Listening..." indicator hangs.

**What works:** The ring tone plays (Web Audio API in components.html). Text Chat and Email modes work perfectly.

**Next steps to fix Phone Call:**
- Option A: Go back to `components.html()` for TTS playback (proven to work for ring tone) + keep `st.audio_input` for recording. Less elegant but functional.
- Option B: Investigate adding `allow="microphone"` to Streamlit's component iframe (may require patching Streamlit).
- Option C: Build a separate real-time voice page using WebRTC/LiveKit outside of Streamlit. Most work but best result.
- **Recommended:** Option A first (get it working), then Option C later as a v2.

### 2. Text Chat & Email — Working
- Both modes fully functional
- Text Chat: chat bubble UI, type and send
- Email: threaded email UI, compose and send

### 3. Other Pending Items
- Re-implement dark mode (see `dark_mode_reference.md`)
- Push to remote GitHub regularly (now automated)
- Timeline X and Director X page rebuilds (plan exists in `.claude/plans/`)

---

## Key Files

| File | Purpose |
|------|---------|
| `qa_tool.py` | Main app (~17,300+ lines) |
| `consultation_x.py` | ConsultationX backend engine (897 lines) |
| `components/phone_call/index.html` | Custom phone call JS component (NOT working in iframe) |
| `.streamlit/secrets.toml` | All API keys (gitignored) |
| `CREDENTIALS_REFERENCE.md` | Backup of all credentials (gitignored) |
| `TODO.md` | Running task list |
| `dark_mode_reference.md` | Saved dark mode code |

## API Keys & Services

| Service | Account | Used For |
|---------|---------|----------|
| Google OAuth | shawn.keepitcity@gmail.com | Login/auth |
| Dropbox | Aerial Canvas (shared) | File access |
| Anthropic (Claude) | Shawn's personal | Director X, ConsultationX scoring |
| Groq (Llama 3.3) | shawn.keepitcity@gmail.com | ConsultationX client simulation |
| ElevenLabs | shawn.keepitcity@gmail.com | ConsultationX voice (Phone Call) |
| GitHub | Keepitcity | Repo hosting |
| Streamlit Cloud | Keepitcity (via GitHub) | Live deployment |

---

## Commits Today (Feb 13)
1. `95e6302` — Add anthropic to requirements.txt
2. `49caa41` — Add ConsultationX backend framework
3. `197cf3d` — Build ConsultationX engine with Groq + Claude
4. `5498326` — Wire ConsultationX into main app with full UI
5. `69c579d` — Fix f-string backslash syntax error
6. `0cce3f3` — Add 3 training modes: Phone Call, Text Chat, Email
7. `7a3f652` — Replace browser TTS with ElevenLabs TTS
8. `cec4ccb` — Add avatar faces, replace emojis with icons, add ringing
9. `4edf189` — Fix ElevenLabs TTS playback using Web Audio API
10. `f57e2e5` — Rebuild Phone Call mode with custom voice component
