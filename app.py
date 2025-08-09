from flask import Flask, render_template, request, abort
from process_spectrolight import process_spectrolight_dat_file
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = "uploaded_files"


@app.errorhandler(400)
def bad_request(error):
    return render_template("400.html", error=error), 400


@app.route('/')
def upload_file():
    return render_template("upload_page.html")


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    # Check if the file is .dat file
    if not file or not file.filename.endswith(".dat"):
        abort(400, description="You have not uploaded any file.")

    # Store the file
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    # Process the .dat file
    sections = process_spectrolight_dat_file(filepath)

    return render_template("spectrolight_results.html", sections=sections, filename=filename)


if __name__ == '__main__':
    app.run("0.0.0.0", port=7727)
