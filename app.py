import os
import argparse
import json
from flask import Flask, request, render_template
from user import User


# init flask app and env variables
app = Flask(__name__)
host = os.getenv("HOST")
port = os.getenv("PORT")

app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True

ann_user = User()


@app.route("/")
def main():
    return render_template("main.html")


@app.route("/login/")
def login():
    global ann_user
    name = request.args.get("name", None)
    
    if name:
        ann_user.name = name
        ann_user.load_data()
        curr_data = ann_user.next()
        token_list = curr_data["context_tokens"].split(" ")
        doc_id = ann_user.get_curr_docID()
        doc_total = ann_user.total_num
        if "ann" in curr_data:
            ann_list = curr_data["ann"]
        else:
            ann_list = []
        return render_template("ann.html", doc=token_list, doc_id=doc_id, doc_total=doc_total, ann_list=ann_list)
        # return render_template("test.html")
    else:
        return render_template("main.html")


@app.route('/savepost', methods=['POST'])
def savepost():
    global ann_user
    data = json.loads(request.form.get("data"))
    array = data["array"]
    action = data["action"]
    doc_id = int(data["doc_id"])
    if doc_id < 1:
        doc_id = 1
    if doc_id > ann_user.total_num:
        doc_id = ann_user.total_num

    # save data
    ann_user.update_ann(array)

    # load new data
    curr_data = ann_user.get_data(doc_id)
    token_list = curr_data["context_tokens"].split(" ")
    if "ann" in curr_data:
        ann_list = curr_data["ann"]
    else:
        ann_list = []

    if action == "save":
        ann_user.save()

    return {"token_list": token_list,
            "doc_id": str(doc_id),
            "ann_list": ann_list}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", "-s", action='store_true', help="run as a server")
    parser.add_argument("--port", "-p", default=5000, type=int, help="runnning port")
    args = parser.parse_args()

    if args.server:
        app.run(host='0.0.0.0', port=args.port)
    else:
        app.run(host='127.0.0.1', port=args.port, debug=True)