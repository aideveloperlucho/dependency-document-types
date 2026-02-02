# Quick Reference Guide

## Starting the Application

### Windows
```bash
start.bat
```

### Linux/Mac
```bash
chmod +x start.sh
./start.sh
```

### Manual Start
```bash
cd backend
python app.py
```

Then open: **http://localhost:5000**

---

## Default Login Credentials

**Email**: `luis.gonzalez@tecnovait.com`  
**Password**: `luis.gonzalez`

---

## How to Upload Excel Files

1. Click the 🔒 button (bottom-right corner)
2. Login with credentials
3. Button changes to 📤
4. Click the 📤 button
5. Select your Excel file (.xlsx or .xls)
6. Click "Subir Archivo"
7. Wait for success message
8. Page reloads automatically with new data

---

## Adding New Users

Edit `backend/users.json`:

```json
{
  "users": [
    {
      "email": "new.user@example.com",
      "password": "their_password"
    },
    {
      "email": "another.user@example.com",
      "password": "another_password"
    }
  ]
}
```

---

## API Endpoints

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| GET | `/` | No | Main visualization page |
| GET | `/api/auth-status` | No | Check login status |
| POST | `/api/login` | No | Login |
| POST | `/api/logout` | No | Logout |
| POST | `/api/upload-excel` | Yes | Upload Excel file |

---

## File Structure

```
backend/
  ├── app.py                 # Flask server
  ├── process_data.py        # Data processing
  ├── users.json             # User credentials
  └── requirements.txt       # Dependencies

frontend/
  ├── index.html             # Visualization
  └── resources/
      └── portals.xlsx       # Excel data

data.json                    # Generated data
```

---

## Common Commands

### Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### Run Server
```bash
cd backend
python app.py
```

### Process Excel Manually
```bash
cd backend
python process_data.py
```

---

## Troubleshooting

### "Module not found" error
```bash
pip install -r backend/requirements.txt
```

### Port 5000 already in use
Edit `backend/app.py`, line ~166:
```python
port = int(os.environ.get('PORT', 5001))
```

### Upload not working
- Check you're logged in
- File must be .xlsx or .xls
- File must be < 16MB
- Check console for errors

### Data not updating
- Check backend terminal for errors
- Verify data.json was updated
- Try hard refresh (Ctrl+F5)

---

## Security Notes

⚠️ **Current Setup**: Passwords stored in plain text  
⚠️ **Production**: Consider hashing passwords and using HTTPS  
⚠️ **Secret Key**: Change `SECRET_KEY` in production  

---

## Support Files

- `README.md` - Full documentation
- `IMPLEMENTATION_SUMMARY.md` - Technical details
- `render.yaml` - Deployment configuration
- `.gitignore` - Git ignore rules

---

## Excel File Format

The Excel file should contain these columns:
- ItemType(AS IS)
- TipoDocumentos(AS IS) CM v1
- TipoDocumentos(AS IS) CM v2
- Plataforma que lo usa
- Cual sistema/portal lo debio haber subido
- Es obligatorio subirlo?
- (and other columns as needed)

---

## Tips

💡 The uploaded Excel file replaces `frontend/resources/portals.xlsx`  
💡 Data is embedded in HTML for offline viewing  
💡 All users see updates after refresh  
💡 Session persists until logout  
💡 File uploads are logged in terminal  

---

## Next Steps After Implementation

1. Test login functionality
2. Test Excel upload
3. Verify data updates
4. Add more users if needed
5. Deploy to production (Render.com)
6. Update secret key for production
7. Consider password hashing for production

---

**Need Help?** Check `IMPLEMENTATION_SUMMARY.md` for detailed information.
