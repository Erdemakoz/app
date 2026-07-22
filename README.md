# StreamScout

Gratis persoonlijke PWA voor lange IRL-streams.

## Functies
- openbare VOD-link invoeren
- downloaden met yt-dlp
- lokaal transcriberen met faster-whisper
- kansrijke momenten scoren
- verticale MP4-clips exporteren
- op iPhone installeren via Safari > Deel > Zet op beginscherm

## Vereisten
Python 3.11+, FFmpeg en veel vrije schijfruimte. Voor 48 uur video is 100 GB vrije ruimte verstandig.

## Starten
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
Open `http://localhost:8000`. Op iPhone open je `http://IP-VAN-JE-COMPUTER:8000`.

Gebruik alleen content waarvoor je toestemming hebt om die te downloaden en herplaatsen.
