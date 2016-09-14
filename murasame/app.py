from bottle import get, route, run, template, request, os
import pandas as pd

@get('/')
def index():
    return """
        <form action="/upload" method="post" enctype="multipart/form-data">
            <input type="file" name="upload">
            <input type="submit" value="upload">
        </form>
    """

@route('/', method='POST')
def upload():
    upload = request.files.get('upload')
    name, ext = os.path.splitext(upload.filename)
    if ext not in ('.xlsx'):
        return "File extension not allowed."

    members = pd.read_excel(upload.file)
    print(list(members.columns))
    return ", ".join(list(members.columns))

run(host='localhost', port=8080, debug=True, reloader=True)