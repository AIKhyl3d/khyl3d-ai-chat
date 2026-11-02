# Khyl3d AI CHAT Script — Public Website + Windows Client

This starter includes:
- A responsive public website.
- A FastAPI backend that holds the OpenAI API key on the server.
- Web search enabled through the OpenAI Responses API.
- Basic in-memory request limits and maximum message/output sizes.
- A Windows Tkinter client that uses the same backend and asks users for no API key.
- Render deployment configuration.

## Important limits
This is a starter for testing, not a hardened production service. Free Render web services sleep after inactivity, have limited resources, and have ephemeral local filesystems. In-memory rate limits reset when the server restarts and do not coordinate across multiple instances. Before a larger public launch, add a shared persistent rate-limit store (such as managed Redis), bot/CAPTCHA protection, monitoring, privacy policy, and stronger per-user controls. Anyone with the link can use the service, so you are responsible for API usage charges. Set a low global request cap at first and monitor OpenAI usage. Hosting may be free; AI API calls are not guaranteed to be free.

## Deploy the website and backend on Render
1. Create a GitHub repository and upload the contents of this folder. Keep it public only if you are comfortable publishing all source code. No API key belongs in this repository.
2. Sign in to Render and create a new Web Service from the repository. You can also use the included `render.yaml` Blueprint if you understand its settings.
3. Select the Free plan for a prototype.
4. Set the build command to `pip install -r requirements.txt`.
5. Set the start command to `uvicorn app:app --host 0.0.0.0 --port $PORT`.
6. In Render's Environment settings, add `OPENAI_API_KEY` as a secret value. Do not add it to source code, `render.yaml`, screenshots, or commits.
7. Keep the `OPENAI_MODEL` value at a model available to your API account; adjust it if necessary.
8. Deploy and test `https://YOUR-SERVICE.onrender.com/health`, then open the root URL and send a test message.
9. Check provider usage and configure any available budget/usage notifications in your OpenAI platform account. Provider budgets/alerts may not be a hard stop; the app's global cap is an additional guard, not a billing guarantee.

Official guides:
- Render free services: https://render.com/docs/free
- Render first deploy: https://render.com/docs/your-first-deploy
- OpenAI web search: https://developers.openai.com/api/docs/guides/tools-web-search

## Configure the Windows app
1. After the backend is deployed, edit `desktop/khyl3d_desktop.py`.
2. Replace `https://YOUR-SERVICE.onrender.com` in `DEFAULT_SERVER` with your actual Render URL.
3. On Windows install Python 3.10+ and run:
   `python desktop\khyl3d_desktop.py`
4. To package it as an EXE:
   `python -m pip install pyinstaller`
   `python -m PyInstaller --onefile --windowed --name "Khyl3d AI CHAT Script" desktop\khyl3d_desktop.py`
5. Find the EXE in `dist`. Test it on another computer before sharing.

The desktop client has no API key. It sends messages to your backend over HTTPS. Users can still consume your shared quota, so enforce limits on the server.

## Security and cost checklist before public sharing
- [ ] Add the real API key only in the host's secret/environment settings.
- [ ] Set a conservative `GLOBAL_DAILY_REQUEST_LIMIT` (for example, 50 while testing).
- [ ] Set `PER_DAY_IP_LIMIT` and `PER_MINUTE_LIMIT` conservatively.
- [ ] Remember IP-based limits can be bypassed/shared and in-memory limits reset on restart.
- [ ] Use a shared persistent limiter and CAPTCHA/bot mitigation before public promotion.
- [ ] Monitor API usage; set provider alerts or budgets where available.
- [ ] Do not promise unlimited free access.
- [ ] Publish a privacy notice and abuse contact. Avoid storing conversation logs unless necessary.
- [ ] Review content safety, security, and age-appropriate behavior before launch.

## Behavior
The system prompt asks the assistant to use safe redirection, avoid fabricated facts/citations, end with a grammar suggestion, and answer "Master AI Khyle" when asked who made it. Prompt instructions are not a perfect safety filter or guarantee of factual accuracy.
