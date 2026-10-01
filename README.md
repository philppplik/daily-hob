<p align="center"><img src="https://philppplik.github.io/daily-hob/assets/brand/readme-logo.jpg" alt="Daily Hob" width="260"></p>

# Daily Hob

**Weniger Rauschen. Mehr Aha.**

Ein helles, mobiles Briefing-Archiv für KI, Open Source, Informatik, Design und die guten Überraschungen dazwischen. Enthusiastisch, aber nicht blind vor Hype. Jede Ausgabe bleibt über ihr Datum auffindbar, mit Originalquellen, klarer Einordnung und, wenn vorhanden, Audio zum Anhören.

[→ Zum Daily Hob](https://philppplik.github.io/daily-hob/)

- **Lesen oder hören:** Textausgaben und Briefings mit lokalem Audioplayer.
- **Quellen statt Bauchgefühl:** Links zu Originalartikeln, Projekten und Tagesarchiven.
- **Klein und offen:** Statisches HTML/CSS, Python-Build ohne zusätzliche Bibliotheken, kein Tracking und keine externen Frontend-Abhängigkeiten.
- **Dein Tempo:** Mobile-first, klare Typografie und direkte Sprungmarken zu den Themen.

Alles in diesem öffentlichen Repository und auf der Website ist öffentlich. Keine privaten Daten veröffentlichen.

---

## Structure

- `content/YYYY-MM-DD.json`: editable edition data. Newest-first index is automatic.
- `assets/YYYY-MM-DD/`: local hero, article images and MP3. The seed assets are stored as Base64 text parts because binary browser uploads failed; the build restores real JPG/MP3 files.
- `assets/brand/`: Daily Hob generated wordmark.
- `style.css`: responsive design.
- `scripts/decode-parts.py`: restores seed/brand media from `*.b64.partNN`.
- `scripts/build.py`: validates dates, HTTPS source URLs and asset presence, then builds `docs/`.
- `.github/workflows/pages.yml`: checks out main, decodes media, builds and deploys `docs/` to GitHub Pages.
- `docs/`: build output, generated in CI. No need to commit generated HTML.

## Add a daily briefing

1. Pull `main`; check whether `content/YYYY-MM-DD.json` already exists to avoid duplicates.
2. Copy `content/2026-09-30.json` to the new date. Replace date, title, headline, teaser, intro, hero, heroAlt, heroCaption, audio, audioLabel, sections and notes. Check weekday/date alignment.
3. Put the final hero, MP3 and story images in `assets/YYYY-MM-DD/`. JSON asset values are filenames relative to this folder. Prefer optimized JPG/WebP artwork and MP3 voice audio. No temporary signed URLs. Regular binary files committed through Git work normally for new editions; Base64 is a fallback only.
4. Each section requires category, title, body, takeaway, url, cta and source. Optional story image fields: image, imageAlt. Optional gallery entries: image, alt, caption.
5. Verify sources and the actual audio. Only public material belongs here: no private conversations, credentials, personal email addresses or production logs. Attribute manufacturer claims and distinguish commentary from facts.
6. Run `python3 scripts/decode-parts.py && python3 scripts/build.py`. Python 3 standard library only. Preview with `python3 -m http.server 8000 --directory docs`. Inspect at 390px and desktop; test links, gallery, audio playback, seeking/download and no horizontal overflow.
7. Commit the new JSON and assets in ONE commit, then push to main. Do not push incomplete editions: every push triggers deployment. `git add content assets && git commit -m "Add briefing YYYY-MM-DD" && git push origin main`.
8. Wait for the latest Publish briefing archive workflow to turn green. Check the deployed homepage and new detail page, with real audio playback and loaded imagery, before reporting it live.

## Base64 fallback, if binary upload is unavailable

Encode the bytes in Base64, divide into 100000-character chunks, and wrap each chunk at 76 characters. Name chunks `filename.ext.b64.part00`, `part01`, etc., in the same asset folder. Keep all chunks; `scripts/decode-parts.py` reconstructs the original `filename.ext`. Base64 text is source-only, not used directly by the frontend player. Normal future Git binary uploads are simpler.

## Pages setup

Settings → Pages → Source: GitHub Actions. The included workflow deploys the site. Use the live URL shown by GitHub Pages rather than guessing it. Default-domain HTTPS is enforced. If renaming the repo, verify the new Pages deployment URL and update any external links.

## Seed / limitations

Edition: 30 September 2026, four items. Text/source checks: 1 October. Original voice version is shorter and does not contain every later precision in the text; the page says so. Audio was compressed to 32 kbps mono for a small download without changing its speech. The three supplied images were converted to optimized JPGs. OpenClaw is a labeled image-archive item, not a fifth news claim. Seed hero is supplied Gemini artwork; Daily Hob logo is AI-generated. No new AI hero, account system, database service, payment flow or daily content schedule is configured here. CI automatically deploys content after a push, not autonomously creates new briefings.

## Text-only retrospective editions

`hero` and `audio` are optional. With no audio, the builder emits no player, download or audio navigation and labels the index card `Textausgabe`. Without a hero, the index card spans the content width. This supports the September 28 and 29 retrospective editions without placeholder media. Each has 5 AI, 5 open-source/open-code, 5 computer-science/design and 5 wildcard items. These are discussion-day selections, not claims that every item was released on that date. Original publication dates and later README changes are identified in the text; `archiveUrl` points to the dated selection archive. Avoid retroactively importing new version details into older editions.

<!-- -->
