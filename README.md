# Proof by Aerial Canvas

Automated quality assurance for video and photo deliverables.

## Features

### Video QA
- 4K Resolution verification
- Frame rate validation
- Audio levels (clipping/peaking detection)
- Black frame detection
- Log/ungraded footage detection
- Stabilization analysis
- Transition smoothness
- Beat sync (cuts match music)
- Sound design detection
- Flow rating (overall vibe score)

### Photo QA
- Resolution verification
- Sharpness/blur detection
- Noise/grain detection
- Exposure analysis
- Contrast & saturation
- White balance check
- AI over-processing detection
- Reflection detection

### Learning System
- Feedback buttons on every check
- Calibration dashboard
- File browser for batch rating
- Threshold tuning based on feedback

## Deployment

This app is configured for Railway deployment. The necessary files are included:
- `requirements.txt` - Python dependencies
- `Procfile` - Start command
- `railway.json` - Railway config
- `nixpacks.toml` - FFmpeg installation

## Local Development

```bash
pip install -r requirements.txt
streamlit run qa_tool.py
```

## Support

Aerial Canvas internal tool.
