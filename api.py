from flask import Flask, request, jsonify
import sqlite3
import os
from org_1_2907 import DataQualityChecker  # import from your file

app = Flask(__name__)

# SQLite database path
DB_PATH = "test.db"

@app.route("/run-checks", methods=["POST"])
def run_checks():
    """
    Expects 2 uploaded files:
    - data_quality_file (CSV with checks config)
    - system_codes_file (CSV with system codes config)
    """
    if "data_quality_file" not in request.files or "system_codes_file" not in request.files:
        return jsonify({"error": "Please upload both data_quality_file and system_codes_file"}), 400

    # Save uploaded files temporarily
    dq_file = request.files["data_quality_file"]
    sys_file = request.files["system_codes_file"]

    os.makedirs("uploads", exist_ok=True)
    dq_path = os.path.join("uploads", dq_file.filename)
    sys_path = os.path.join("uploads", sys_file.filename)

    dq_file.save(dq_path)
    sys_file.save(sys_path)

    # Connect DB
    conn = sqlite3.connect(DB_PATH)
    checker = DataQualityChecker(conn)

    # Load configs
    checker.load_checks_config(dq_path)
    checker.load_system_codes_config(sys_path)

    # Run checks
    results = checker.run_all_checks()

    # Close DB
    conn.close()

    return jsonify(results)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
