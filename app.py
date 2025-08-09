from flask import Flask, render_template, request, abort
from process_spectrolight import process_spectrolight_dat_file
from forms import UploadForm
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = "uploaded_files"

# In later possible use, migrate to .env
app.config['SECRET_KEY'] = 'this_is_random_secret_key'


# Error handler registration
@app.errorhandler(400)
def bad_request(error):
    return render_template("400.html", error=error), 400


@app.route('/')
def upload_page():
    form = UploadForm()
    return render_template("upload_page.html", form=form)


@app.route("/upload-and-result", methods=["GET", "POST"])
def upload_and_result():
    form = UploadForm()

    if form.validate_on_submit():
        file = form.file.data  # Safe — already validated by Flask-WTF

        # Store the file
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # Process the .dat file
        sections = process_spectrolight_dat_file(filepath)

        return render_template(
            "spectrolight_results.html",
            sections=sections,
            filename=filename
        )

    # If GET request or validation failed
    return render_template("upload_page.html", form=form)


if __name__ == '__main__':
    app.run()
