# LightScatter Viewer

A simple Flask web app to upload, parse, and display structured results from dynamic light scattering `.dat` files.

## Requirements

- Python **3.11** or newer
- [Git](https://git-scm.com/) installed

---

## 1. Clone the Repository

```bash
git clone https://github.com/timkadlec/lightscatter_viewer.git
cd lightscatter_viewer
```

---

## 2. Create and Activate a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate   # Mac
venv\Scripts\activate      # Windows
```

---

## 3. Install requirements.txt

```bash
pip install -r requirements.txt
```

---

## 4. Run Application

Flask automatically reads the `.flaskenv` present configuration.

```bash
flask run
```

The app is available at:

```
http://127.0.0.1:7727
```

---

## 5. Have fun


## 6. Notes

- Uploaded files are stored in the `uploaded_files/` directory, it is automatically created if not present.
- The app uses CSRF protection via Flask-WTF. `SECRET_KEY` is now in `app.py`, for later use move to `.env`.
- TailwindCSS styles must be built before serving if you make changes to `static/css`.

---

## License

MIT

