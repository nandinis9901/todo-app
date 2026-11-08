from flask import Flask, request, jsonify
import json, os, time

app = Flask(__name__)
FILE = "bugs.json"

PAGE = """
<!DOCTYPE html>
<html>
<body>
  <h2>Bug Tracker</h2>
  <input id="title" placeholder="Bug title">
  <select id="priority">
    <option>Low</option>
    <option selected>Medium</option>
    <option>High</option>
  </select>
  <button onclick="addBug()">Add Bug</button>
  <p id="msg" style="color:red"></p>
  <ul id="list"></ul>
  <script>
    async function loadBugs() {
      const res = await fetch('/bugs');
      const bugs = await res.json();
      document.getElementById("list").innerHTML = bugs.map(function(b) {
        let btn = "";
        if (b.status === "Open") {
          btn = ' <button onclick="closeBug(' + b.id + ')">Close</button>';
        }
        btn += ' <button onclick="deleteBug(' + b.id + ')">Delete</button>';
        const pr = b.priority || "Medium";
        return '<li>' + b.title + ' [' + pr + '] - ' + b.status + btn + '</li>';
      }).join("");
    }
    async function addBug() {
      const title = document.getElementById("title").value;
      const priority = document.getElementById("priority").value;
      if (!title) { document.getElementById("msg").textContent = "Type a title first"; return; }
      document.getElementById("msg").textContent = "";
      await fetch('/bugs', {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: title, priority: priority })
      });
      document.getElementById("title").value = "";
      loadBugs();
    }
    async function closeBug(id) {
      await fetch('/bugs/' + id, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: "Closed" })
      });
      loadBugs();
    }
    async function deleteBug(id) {
      await fetch('/bugs/' + id, { method: "DELETE" });
      loadBugs();
    }
    loadBugs();
  </script>
</body>
</html>
"""

def load():
    if os.path.exists(FILE):
        with open(FILE, "r") as f:
            return json.load(f)
    return []

def save(bugs):
    with open(FILE, "w") as f:
        json.dump(bugs, f, indent=2)

@app.route("/")
def home():
    return PAGE

@app.route("/bugs", methods=["GET"])
def get_bugs():
    return jsonify(load())

@app.route("/bugs", methods=["POST"])
def add_bug():
    bugs = load()
    bug = {"id": int(time.time() * 1000), "status": "Open", **request.json}
    bugs.append(bug)
    save(bugs)
    return jsonify(bug)

@app.route("/bugs/<int:bug_id>", methods=["PUT"])
def update_bug(bug_id):
    bugs = load()
    for b in bugs:
        if b["id"] == bug_id:
            b.update(request.json)
            save(bugs)
            return jsonify(b)
    return jsonify({"error": "not found"}), 404

@app.route("/bugs/<int:bug_id>", methods=["DELETE"])
def delete_bug(bug_id):
    bugs = [b for b in load() if b["id"] != bug_id]
    save(bugs)
    return jsonify({"deleted": bug_id})

if __name__ == "__main__":
    app.run(port=5000, debug=True)