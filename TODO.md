# Proof QA Tool - Task List

**Last updated:** 2026-02-13

---

## Completed

- [x] **Rebrand to "Proof by Shawn Hernandez"** — all branding updated, login page logo 50% bigger, tagline with & symbol
- [x] **Add changelog & dev cost calculator to Admin panel** — 12 versions, AI session log, traditional vs AI cost comparison
- [x] **Remove dark mode toggle from navbar** — saved to `dark_mode_reference.md` for future re-implementation
- [x] **Build Timeline X full page** — upload, config (13 formats), style presets, generate, export to DaVinci/FCP/Premiere
- [x] **Build Director X full page** — Claude Vision AI analysis, thoroughness selector, Director Score 0-100, category breakdown, strengths & improvements
- [x] **Navbar reorder** — Photo | Video | Auto Sort | Timeline X BETA | Director X BETA | ConsultationX BETA
- [x] **BETA badge styling** — purple #9461F5 with CSS class
- [x] **Remove lock emoji from Sign in button**
- [x] **Add Local Path tab to Photo Proof** — third tab for local file path on Mac
- [x] **Add Local Path tab to Video Proof** — third tab for local video path
- [x] **Add Local Path tab to Auto Sort (Photo & Video)** — tabs/radio for Dropbox | Local Path
- [x] **Add Local Path tab to Timeline X** — local folder of clips + music file path
- [x] **Add Local Path tab to Director X** — local video path for frame extraction
- [x] **Update homepage** — "Your Work Deserves Better" tagline, trimmed sections, "Ready to Stop Sucking?" dual CTA
- [x] **Fix black-on-black CSS** — Legacy CSS dark-mode colors overriding light mode on tabs, radio buttons, inputs, and cards
- [x] **Fix admin email** — `shawn.keepitcity@gmail.com` is admin, `@aerialcanvas.com` are team, everyone else waitlist
- [x] **Fix auth bypass** — `check_authentication()` had hardcoded domain checks bypassing database; also removed admin email from waitlist table
- [x] **Session persistence** — login + current page now survive browser refresh via localStorage
- [x] **Google OAuth redirect URI** — added localhost:8502 + proof-app.streamlit.app
- [x] **GitHub ownership** — migrated to Keepitcity/proof (personal account)
- [x] **Streamlit Cloud deployment** — live at proof-app.streamlit.app under Keepitcity
- [x] **ConsultationX backend** — AI-powered consultation training tool (`consultation_x.py`)
- [x] **ConsultationX UI integration** — navbar with BETA badge, 3 modes (Phone Call, Text Chat, Email)
- [x] **DiceBear avatars** — unique cartoon faces per client persona
- [x] **Replace emojis with SVG icons** — black & white icons throughout ConsultationX
- [x] **ElevenLabs TTS integration** — API key, secrets, wired into Phone Call mode
- [x] **Credentials reference** — all API keys backed up in `CREDENTIALS_REFERENCE.md` (gitignored)

## In Progress

- [ ] **Phone Call voice — FIX NEEDED** — TTS not audible + speech recognition not working in iframe. See `SESSION_NOTES.md` for details and fix options.

## Future / Backlog

- [ ] Re-implement dark mode (see `dark_mode_reference.md`)
- [ ] Timeline X & Director X page rebuilds (plan in `.claude/plans/`)
- [ ] `local_folder.py` — backend complete, needs UI wiring

---

## Key Files

- `qa_tool.py` — main app (~17,300+ lines)
- `consultation_x.py` — ConsultationX training engine (scenarios, scoring, AI prompts)
- `components/phone_call/index.html` — custom phone call JS component (needs fix)
- `database.py` — user/stats tracking, admin checks
- `local_folder.py` — local folder processor (exists, needs UI integration)
- `timeline_x.py` — timeline assembly engine
- `timeline_x_analyzer.py` — FFprobe/BPM analysis
- `timeline_x_framework.py` — editorial rules/knowledge base
- `dark_mode_reference.md` — saved dark mode code for later
- `.streamlit/secrets.toml` — OAuth + API keys (NEVER commit)
- `CREDENTIALS_REFERENCE.md` — backup of all API keys (NEVER commit)
- `SESSION_NOTES.md` — detailed session log for pickup

## Notes

- **Commit after EVERY change** — non-negotiable after losing hours of work on Feb 12
- **Admin email**: shawn.keepitcity@gmail.com
- **Owner**: Shawn Hernandez (NOT Aerial Canvas)
- **Mac-first** — local path features prioritize macOS, PC secondary
- **Text Chat & Email modes work perfectly** — Phone Call needs voice fix
