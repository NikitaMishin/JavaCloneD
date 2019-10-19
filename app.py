import os
import threading

from flask import Flask, request, jsonify, abort

from viz_preprocessing.rendering import GraphRenderer

app = Flask(__name__, static_url_path='/static')

current_session_id = 0
lock = threading.Lock()
upload_folder = 'session12'
session_page_name = 'webus.html'
session_page_data = 'data.json'
output_json_name = 'digraph.json'


def error_response(err, session_id):
    return {
        'status': 500,
        'error': '<span>{0}</span>'.format(err),
        'errorkeys': [],
        'id': session_id,
    }


@app.route('/home')
def home():
    """
    Display user input with directory chooser to analyze
    :return: Html page
    """
    return app.send_static_file('static_pages/home.html')


@app.route('/analysis_data/<session_id>', methods=['GET'])
def get_data(session_id):
    try:
        session_id = int(session_id)
        f = os.path.join(upload_folder, str(session_id), session_page_data)
        with open(f) as r:
            return r.read()

    except Exception as e:
        return 404


@app.route('/analysis_result/<session_id>', methods=['GET'])
def serve(session_id):
    """
    Read  file json already readed and give template with
    :param session_id:
    :return:
    """
    session_id = int(session_id)
    global session_page_data
    try:
        f = os.path.join(upload_folder, str(session_id), session_page_name)
        with open(f) as r:
            return r.read()
    except FileNotFoundError as e:
        abort(404, 'No analysis is launch for specified session')


def _atomic_session_inc():
    global lock, current_session_id
    session_id = 0
    with lock:
        session_id = current_session_id
        current_session_id += 1
    return session_id


def _common(session_id):
    is_succeed, err = _analyze(str(session_id))

    if not is_succeed:
        return jsonify(error_response(err, session_id))

    err_msg = generate_self_contained_viz((str(session_id)))

    if err_msg is not None:
        return jsonify(error_response(err_msg, session_id))

    return jsonify({
        'url': '/analysis_result/' + str(session_id),
        'status': 200,
        'id': session_id
    })


@app.route('/analyze_files', methods=['POST'])
def analyze_files():
    """
    Analyze sended files via analyze them and then return user success/not success with his id  and url for see
    :return:
    """
    import shutil
    session_id = _atomic_session_inc()
    uploaded_files = request.files.getlist('files')
    session_dir = os.path.join(upload_folder, str(session_id))
    shutil.rmtree(session_dir, ignore_errors=True)

    for index, file in enumerate(uploaded_files):
        file_name = file.filename
        dir_for_file = os.path.join(upload_folder, str(session_id), str(index))  # for removal of collision problems
        os.makedirs(dir_for_file, exist_ok=True)
        file.save(os.path.join(dir_for_file, file_name))
    return _common(session_id)


@app.route('/analyze_from_zip', methods=['POST'])
def analyze_zip():
    import zipfile, shutil

    session_id = str(_atomic_session_inc())
    session_dir = os.path.join(upload_folder, session_id)
    shutil.rmtree(session_dir, ignore_errors=True)
    os.makedirs(session_dir, exist_ok=True)

    file = request.files['ziparchive']
    filename = file.filename

    file.save(os.path.join(session_dir, filename))

    with zipfile.ZipFile(os.path.join(session_dir, filename), 'r') as zip_ref:
        zip_ref.extractall(os.path.join(upload_folder, session_id))
    os.remove(os.path.join(session_dir, filename))

    return _common(session_id)


@app.route('/analyze_from_github_url', methods=['POST'])
def analyze_github_link():
    import wget, zipfile, shutil
    session_id = str(_atomic_session_inc())
    session_dir = os.path.join(upload_folder, session_id)
    shutil.rmtree(session_dir, ignore_errors=True)
    os.makedirs(session_dir, exist_ok=True)

    github_url = request.get_json()['url']
    filename = wget.download(github_url, out=session_dir)
    with zipfile.ZipFile(filename, 'r') as zip_ref:
        zip_ref.extractall(session_dir)
    os.remove(filename)
    return _common(session_id)


def _analyze(session_id: str) -> ():
    import subprocess, calle_java_command

    path_to_analyze = os.path.join(os.path.dirname(app.instance_path), upload_folder, session_id)
    path_to_save = os.path.join(path_to_analyze, output_json_name)
    cmd = calle_java_command.command + [path_to_analyze, path_to_save]
    print(' '.join(cmd))

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()

    print(output)
    print(error)
    if process.returncode != 0:
        return False, error
    return True, None


def generate_self_contained_viz(session_id: str):
    """
    For specified session_id generate and save self contained page that display page for user
    :param session_id:
    :return:
    """
    from viz_preprocessing import server
    global session_page_name, session_page_data
    try:
        working_file = os.path.join(upload_folder, session_id, output_json_name)
        backend_handler = server.BackendHandler(working_file, GraphRenderer(), session_page_name)
        page_html = backend_handler.render_page()
        backend_handler.save_page(page_html, session_page_data)
        return None
    except Exception as e:
        return e.__str__()


@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


if __name__ == '__main__':
    # 240mb max
    app.config['MAX_CONTENT_LENGTH'] = 300 * 1024 * 1024
    # app.run()
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.run(debug=False, host='0.0.0.0')
