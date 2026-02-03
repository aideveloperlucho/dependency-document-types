### Architecture & API (from implementation summary)

- `backend/app.py`: Flask app, session-based auth, Excel upload, REST API:
  - `GET /` – main page
  - `GET /api/auth-status` – check login
  - `POST /api/login` – login
  - `POST /api/logout` – logout
  - `POST /api/upload-excel` – upload + process Excel
- `backend/process_data.py`: reads `frontend/resources/portals.xlsx`, writes `data.json` and embeds into `frontend/index.html`
- `frontend/index.html`: visualization, floating button, login & upload modals, notifications.

### Quick commands & troubleshooting (from quick reference)

- Install deps: `pip install -r requirements.txt`
- Run dev server: `cd backend && python app.py`
- Process Excel manually: `cd backend && python process_data.py`
- Default login: `luis.gonzalez@tecnovait.com` / `luis.gonzalez`
- If import error: `pip install -r requirements.txt`
- If port busy: change `port = int(os.environ.get('PORT', 5001))` in `backend/app.py`

