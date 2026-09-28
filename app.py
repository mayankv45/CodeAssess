from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    jsonify,
    flash,
    send_file,
)
import psycopg
from psycopg.rows import dict_row
import json
import random
import io
import os
from datetime import datetime

# =========================================================
# APP CONFIGURATION
# =========================================================

app = Flask(__name__)

app.secret_key = os.getenv(
    "SECRET_KEY",
    "codeassess-dev-secret"
)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL environment variable is not set."
    )


# =========================================================
# CONSTANTS
# =========================================================

TOPICS = [
    "Arrays",
    "Strings",
    "Searching",
    "Sorting",
    "Hashing",
    "Linked List",
    "Stack & Queue",
    "Trees",
    "Graphs",
    "Dynamic Programming",
]

DIFFICULTIES = [
    "Easy",
    "Medium",
    "Hard",
]

TEST_TYPES = [
    "Random",
    "Minimum",
    "Maximum",
    "Sorted",
    "Reverse Sorted",
    "All Same",
    "Custom",
]


# =========================================================
# DATABASE HELPERS
# =========================================================

def get_db():
    """Create and return a PostgreSQL database connection."""

    return psycopg.connect(
        DATABASE_URL,
        row_factory=dict_row
    )


def init_db():
    """Create required PostgreSQL tables if they don't exist."""

    conn = get_db()

    try:

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS problems (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                statement TEXT NOT NULL,
                input_format TEXT,
                output_format TEXT,
                constraints TEXT,
                examples TEXT,
                explanation TEXT,
                topic TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                tags TEXT,
                time_limit REAL DEFAULT 1.0,
                memory_limit INTEGER DEFAULT 256,
                solution_cpp TEXT,
                solution_python TEXT,
                complexity TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS test_cases (
                id SERIAL PRIMARY KEY,
                problem_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                input_data TEXT NOT NULL,
                expected_output TEXT,
                test_type TEXT NOT NULL,
                created_at TEXT NOT NULL,

                FOREIGN KEY(problem_id)
                REFERENCES problems(id)
                ON DELETE CASCADE
            )
            """
        )

        conn.commit()

    finally:
        conn.close()


# =========================================================
# DATA MIGRATION / DEMO DATA
# =========================================================

def migrate_demo_data():
    """
    Fix older demo records that stored literal \\n
    instead of real newline characters.
    """

    conn = get_db()

    try:

        row = conn.execute(
            """
            SELECT
                id,
                constraints,
                examples,
                solution_cpp,
                solution_python
            FROM problems
            ORDER BY id
            LIMIT 1
            """
        ).fetchone()

        if row:

            values = [
                row["constraints"],
                row["examples"],
                row["solution_cpp"],
                row["solution_python"],
            ]

            fixed = [
                value.replace("\\n", "\n")
                if value
                else value
                for value in values
            ]

            if fixed != values:

                conn.execute(
                    """
                    UPDATE problems
                    SET
                        constraints=%s,
                        examples=%s,
                        solution_cpp=%s,
                        solution_python=%s,
                        updated_at=%s
                    WHERE id=%s
                    """,
                    (
                        *fixed,
                        datetime.now().isoformat(
                            timespec="seconds"
                        ),
                        row["id"],
                    ),
                )

                conn.commit()

    finally:
        conn.close()


def seed_demo():
    """
    Insert the default demo problem when
    the PostgreSQL database is empty.
    """

    conn = get_db()

    try:

        count = conn.execute(
            """
            SELECT COUNT(*) AS count
            FROM problems
            """
        ).fetchone()["count"]

        if count == 0:

            now = datetime.now().isoformat(
                timespec="seconds"
            )

            cur = conn.execute(
                """
                INSERT INTO problems
                (
                    title,
                    statement,
                    input_format,
                    output_format,
                    constraints,
                    examples,
                    explanation,
                    topic,
                    difficulty,
                    tags,
                    time_limit,
                    memory_limit,
                    solution_cpp,
                    solution_python,
                    complexity,
                    created_at,
                    updated_at
                )
                VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s
                )
                RETURNING id
                """,
                (
                    "Maximum Element in an Array",

                    "Given an array of N integers, find and print "
                    "the maximum element.",

                    "The first line contains N. "
                    "The second line contains N "
                    "space-separated integers.",

                    "Print the maximum element.",

                    "1 ≤ N ≤ 2×10^5\n"
                    "-10^9 ≤ A[i] ≤ 10^9",

                    "Input:\n"
                    "5\n"
                    "3 8 2 10 6\n\n"
                    "Output:\n"
                    "10",

                    "Scan the array once while maintaining "
                    "the largest value seen so far.",

                    "Arrays",

                    "Easy",

                    "array,linear-scan,beginner",

                    1.0,

                    256,

                    "#include <bits/stdc++.h>\n"
                    "using namespace std;\n"
                    "int main(){ "
                    "int n; cin>>n; "
                    "long long x, ans=LLONG_MIN; "
                    "while(n--){cin>>x; "
                    "ans=max(ans,x);} "
                    "cout<<ans; }",

                    "n=int(input())\n"
                    "a=list(map(int,input().split()))\n"
                    "print(max(a))",

                    "O(N) time, O(1) extra space",

                    now,

                    now,
                ),
            )

            pid = cur.fetchone()["id"]

            tests = [

                (
                    "Basic case",
                    "5\n3 8 2 10 6",
                    "10",
                    "Custom",
                ),

                (
                    "Minimum N",
                    "1\n-42",
                    "-42",
                    "Minimum",
                ),

                (
                    "All negative",
                    "4\n-9 -3 -20 -7",
                    "-3",
                    "Edge",
                ),

                (
                    "Maximum values",
                    "3\n1000000000 999999999 1",
                    "1000000000",
                    "Maximum",
                ),
            ]

            for name, inp, out, test_type in tests:

                conn.execute(
                    """
                    INSERT INTO test_cases
                    (
                        problem_id,
                        name,
                        input_data,
                        expected_output,
                        test_type,
                        created_at
                    )
                    VALUES (
                        %s, %s, %s, %s, %s, %s
                    )
                    """,
                    (
                        pid,
                        name,
                        inp,
                        out,
                        test_type,
                        now,
                    ),
                )

            conn.commit()

    finally:
        conn.close()


# =========================================================
# UTILITY FUNCTIONS
# =========================================================

def parse_tags(tags):
    """Convert comma-separated tags into a clean list."""

    return [
        tag.strip()
        for tag in (tags or "").split(",")
        if tag.strip()
    ]


def generate_case(
    test_type,
    n_min=1,
    n_max=20,
    value_min=-100,
    value_max=100,
):

    n_min = max(1, int(n_min))

    n_max = max(
        n_min,
        int(n_max)
    )

    value_min = int(value_min)
    value_max = int(value_max)

    if test_type == "Minimum":

        n = n_min
        arr = [value_min] * n

    elif test_type == "Maximum":

        n = n_max
        arr = [value_max] * n

    elif test_type == "Sorted":

        n = random.randint(
            n_min,
            n_max
        )

        arr = sorted(
            random.randint(
                value_min,
                value_max
            )
            for _ in range(n)
        )

    elif test_type == "Reverse Sorted":

        n = random.randint(
            n_min,
            n_max
        )

        arr = sorted(
            (
                random.randint(
                    value_min,
                    value_max
                )
                for _ in range(n)
            ),
            reverse=True,
        )

    elif test_type == "All Same":

        n = random.randint(
            n_min,
            n_max
        )

        value = random.randint(
            value_min,
            value_max
        )

        arr = [value] * n

    else:

        n = random.randint(
            n_min,
            n_max
        )

        arr = [
            random.randint(
                value_min,
                value_max
            )
            for _ in range(n)
        ]

    return (
        f"{n}\n"
        + " ".join(map(str, arr))
    )


def solve_max_array(input_data):

    try:

        tokens = list(
            map(
                int,
                input_data.split()
            )
        )

        n = tokens[0]

        arr = tokens[
            1:1 + n
        ]

        return (
            str(max(arr))
            if arr
            else ""
        )

    except Exception:

        return ""


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/")
def index():

    conn = get_db()

    try:

        total = conn.execute(
            """
            SELECT COUNT(*) AS count
            FROM problems
            """
        ).fetchone()["count"]

        tests = conn.execute(
            """
            SELECT COUNT(*) AS count
            FROM test_cases
            """
        ).fetchone()["count"]

        easy = conn.execute(
            """
            SELECT COUNT(*) AS count
            FROM problems
            WHERE difficulty='Easy'
            """
        ).fetchone()["count"]

        medium = conn.execute(
            """
            SELECT COUNT(*) AS count
            FROM problems
            WHERE difficulty='Medium'
            """
        ).fetchone()["count"]

        hard = conn.execute(
            """
            SELECT COUNT(*) AS count
            FROM problems
            WHERE difficulty='Hard'
            """
        ).fetchone()["count"]

        recent = conn.execute(
            """
            SELECT *
            FROM problems
            ORDER BY updated_at DESC
            LIMIT 5
            """
        ).fetchall()

    finally:

        conn.close()

    return render_template(
        "index.html",
        total=total,
        tests=tests,
        easy=easy,
        medium=medium,
        hard=hard,
        recent=recent,
    )


# =========================================================
# PROBLEM BANK
# =========================================================

@app.route("/problems")
def problems():

    q = request.args.get(
        "q",
        ""
    ).strip()

    topic = request.args.get(
        "topic",
        ""
    ).strip()

    difficulty = request.args.get(
        "difficulty",
        ""
    ).strip()

    conn = get_db()

    try:

        sql = """
            SELECT *
            FROM problems
            WHERE 1=1
        """

        params = []

        if q:

            sql += """
                AND (
                    title LIKE %s
                    OR tags LIKE %s
                )
            """

            params += [
                f"%{q}%",
                f"%{q}%"
            ]

        if topic:

            sql += """
                AND topic=%s
            """

            params.append(topic)

        if difficulty:

            sql += """
                AND difficulty=%s
            """

            params.append(difficulty)

        sql += """
            ORDER BY updated_at DESC
        """

        rows = conn.execute(
            sql,
            params
        ).fetchall()

    finally:

        conn.close()

    return render_template(
        "problems.html",
        problems=rows,
        topics=TOPICS,
        difficulties=DIFFICULTIES,
        q=q,
        topic=topic,
        difficulty=difficulty,
    )


# =========================================================
# CREATE NEW PROBLEM
# =========================================================

@app.route(
    "/problems/new",
    methods=["GET", "POST"],
)
def new_problem():

    if request.method == "POST":

        data = request.form

        now = datetime.now().isoformat(
            timespec="seconds"
        )

        conn = get_db()

        try:

            cur = conn.execute(
                """
                INSERT INTO problems
                (
                    title,
                    statement,
                    input_format,
                    output_format,
                    constraints,
                    examples,
                    explanation,
                    topic,
                    difficulty,
                    tags,
                    time_limit,
                    memory_limit,
                    solution_cpp,
                    solution_python,
                    complexity,
                    created_at,
                    updated_at
                )
                VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s
                )
                RETURNING id
                """,
                (
                    data["title"],
                    data["statement"],
                    data.get(
                        "input_format",
                        ""
                    ),
                    data.get(
                        "output_format",
                        ""
                    ),
                    data.get(
                        "constraints",
                        ""
                    ),
                    data.get(
                        "examples",
                        ""
                    ),
                    data.get(
                        "explanation",
                        ""
                    ),
                    data["topic"],
                    data["difficulty"],
                    data.get(
                        "tags",
                        ""
                    ),
                    float(
                        data.get(
                            "time_limit"
                        )
                        or 1
                    ),
                    int(
                        data.get(
                            "memory_limit"
                        )
                        or 256
                    ),
                    data.get(
                        "solution_cpp",
                        ""
                    ),
                    data.get(
                        "solution_python",
                        ""
                    ),
                    data.get(
                        "complexity",
                        ""
                    ),
                    now,
                    now,
                ),
            )

            pid = cur.fetchone()["id"]

            conn.commit()

        finally:

            conn.close()

        flash(
            "Problem created successfully.",
            "success",
        )

        return redirect(
            url_for(
                "problem_detail",
                problem_id=pid,
            )
        )

    return render_template(
        "problem_form.html",
        problem=None,
        topics=TOPICS,
        difficulties=DIFFICULTIES,
    )


# =========================================================
# PROBLEM DETAILS
# =========================================================

@app.route(
    "/problems/<int:problem_id>"
)
def problem_detail(problem_id):

    conn = get_db()

    try:

        problem = conn.execute(
            """
            SELECT *
            FROM problems
            WHERE id=%s
            """,
            (problem_id,),
        ).fetchone()

        tests = conn.execute(
            """
            SELECT *
            FROM test_cases
            WHERE problem_id=%s
            ORDER BY id DESC
            """,
            (problem_id,),
        ).fetchall()

    finally:

        conn.close()

    if not problem:

        return (
            "Problem not found",
            404
        )

    return render_template(
        "problem_detail.html",
        problem=problem,
        tests=tests,
        tags=parse_tags(
            problem["tags"]
        ),
    )


# =========================================================
# EDIT PROBLEM
# =========================================================

@app.route(
    "/problems/<int:problem_id>/edit",
    methods=["GET", "POST"],
)
def edit_problem(problem_id):

    conn = get_db()

    problem = conn.execute(
        """
        SELECT *
        FROM problems
        WHERE id=%s
        """,
        (problem_id,),
    ).fetchone()

    if not problem:

        conn.close()

        return (
            "Problem not found",
            404
        )

    if request.method == "POST":

        data = request.form

        now = datetime.now().isoformat(
            timespec="seconds"
        )

        try:

            conn.execute(
                """
                UPDATE problems
                SET
                    title=%s,
                    statement=%s,
                    input_format=%s,
                    output_format=%s,
                    constraints=%s,
                    examples=%s,
                    explanation=%s,
                    topic=%s,
                    difficulty=%s,
                    tags=%s,
                    time_limit=%s,
                    memory_limit=%s,
                    solution_cpp=%s,
                    solution_python=%s,
                    complexity=%s,
                    updated_at=%s
                WHERE id=%s
                """,
                (
                    data["title"],
                    data["statement"],
                    data.get(
                        "input_format",
                        ""
                    ),
                    data.get(
                        "output_format",
                        ""
                    ),
                    data.get(
                        "constraints",
                        ""
                    ),
                    data.get(
                        "examples",
                        ""
                    ),
                    data.get(
                        "explanation",
                        ""
                    ),
                    data["topic"],
                    data["difficulty"],
                    data.get(
                        "tags",
                        ""
                    ),
                    float(
                        data.get(
                            "time_limit"
                        )
                        or 1
                    ),
                    int(
                        data.get(
                            "memory_limit"
                        )
                        or 256
                    ),
                    data.get(
                        "solution_cpp",
                        ""
                    ),
                    data.get(
                        "solution_python",
                        ""
                    ),
                    data.get(
                        "complexity",
                        ""
                    ),
                    now,
                    problem_id,
                ),
            )

            conn.commit()

        finally:

            conn.close()

        flash(
            "Problem updated.",
            "success",
        )

        return redirect(
            url_for(
                "problem_detail",
                problem_id=problem_id,
            )
        )

    conn.close()

    return render_template(
        "problem_form.html",
        problem=problem,
        topics=TOPICS,
        difficulties=DIFFICULTIES,
    )


# =========================================================
# DELETE PROBLEM
# =========================================================

@app.route(
    "/problems/<int:problem_id>/delete",
    methods=["POST"],
)
def delete_problem(problem_id):

    conn = get_db()

    try:

        conn.execute(
            """
            DELETE FROM test_cases
            WHERE problem_id=%s
            """,
            (problem_id,),
        )

        conn.execute(
            """
            DELETE FROM problems
            WHERE id=%s
            """,
            (problem_id,),
        )

        conn.commit()

    finally:

        conn.close()

    flash(
        "Problem deleted.",
        "success",
    )

    return redirect(
        url_for("problems")
    )


# =========================================================
# ADD TEST CASE
# =========================================================

@app.route(
    "/problems/<int:problem_id>/tests/add",
    methods=["POST"],
)
def add_test(problem_id):

    name = request.form.get(
        "name",
        "Custom Test",
    ).strip()

    inp = request.form.get(
        "input_data",
        "",
    ).strip()

    expected = request.form.get(
        "expected_output",
        "",
    ).strip()

    test_type = request.form.get(
        "test_type",
        "Custom",
    )

    if not inp:

        flash(
            "Input data cannot be empty.",
            "error",
        )

        return redirect(
            url_for(
                "problem_detail",
                problem_id=problem_id,
            )
        )

    conn = get_db()

    try:

        conn.execute(
            """
            INSERT INTO test_cases
            (
                problem_id,
                name,
                input_data,
                expected_output,
                test_type,
                created_at
            )
            VALUES (
                %s, %s, %s,
                %s, %s, %s
            )
            """,
            (
                problem_id,
                name,
                inp,
                expected,
                test_type,
                datetime.now().isoformat(
                    timespec="seconds"
                ),
            ),
        )

        conn.commit()

    finally:

        conn.close()

    flash(
        "Test case added.",
        "success",
    )

    return redirect(
        url_for(
            "problem_detail",
            problem_id=problem_id,
        )
    )


# =========================================================
# DELETE TEST CASE
# =========================================================

@app.route(
    "/tests/<int:test_id>/delete",
    methods=["POST"],
)
def delete_test(test_id):

    conn = get_db()

    try:

        row = conn.execute(
            """
            SELECT problem_id
            FROM test_cases
            WHERE id=%s
            """,
            (test_id,),
        ).fetchone()

        if row:

            problem_id = row["problem_id"]

            conn.execute(
                """
                DELETE FROM test_cases
                WHERE id=%s
                """,
                (test_id,),
            )

            conn.commit()

        else:

            problem_id = None

    finally:

        conn.close()

    if problem_id:

        return redirect(
            url_for(
                "problem_detail",
                problem_id=problem_id,
            )
        )

    return redirect(
        url_for("problems")
    )


# =========================================================
# TEST CASE GENERATOR API
# =========================================================

@app.route(
    "/api/generate-tests",
    methods=["POST"],
)
def api_generate_tests():

    data = request.get_json(
        force=True
    )

    test_type = data.get(
        "test_type",
        "Random",
    )

    count = min(
        max(
            int(
                data.get(
                    "count",
                    5
                )
            ),
            1,
        ),
        100,
    )

    n_min = data.get(
        "n_min",
        1,
    )

    n_max = data.get(
        "n_max",
        20,
    )

    value_min = data.get(
        "value_min",
        -100,
    )

    value_max = data.get(
        "value_max",
        100,
    )

    cases = []

    for i in range(count):

        input_data = generate_case(
            test_type,
            n_min,
            n_max,
            value_min,
            value_max,
        )

        expected_output = solve_max_array(
            input_data
        )

        cases.append(
            {
                "name":
                    f"{test_type} Test #{i + 1}",

                "input_data":
                    input_data,

                "expected_output":
                    expected_output,

                "test_type":
                    test_type,
            }
        )

    return jsonify(
        {
            "cases": cases
        }
    )


# =========================================================
# BULK SAVE TEST CASES
# =========================================================

@app.route(
    "/problems/<int:problem_id>/tests/bulk-save",
    methods=["POST"],
)
def bulk_save_tests(problem_id):

    data = request.get_json(
        force=True
    )

    cases = data.get(
        "cases",
        []
    )

    conn = get_db()

    try:

        now = datetime.now().isoformat(
            timespec="seconds"
        )

        for case in cases:

            conn.execute(
                """
                INSERT INTO test_cases
                (
                    problem_id,
                    name,
                    input_data,
                    expected_output,
                    test_type,
                    created_at
                )
                VALUES (
                    %s, %s, %s,
                    %s, %s, %s
                )
                """,
                (
                    problem_id,

                    case.get(
                        "name",
                        "Generated Test"
                    ),

                    case.get(
                        "input_data",
                        ""
                    ),

                    case.get(
                        "expected_output",
                        ""
                    ),

                    case.get(
                        "test_type",
                        "Random"
                    ),

                    now,
                ),
            )

        conn.commit()

    finally:

        conn.close()

    return jsonify(
        {
            "ok": True,
            "saved": len(cases),
        }
    )


# =========================================================
# EXPORT PROBLEM
# =========================================================

@app.route(
    "/problems/<int:problem_id>/export"
)
def export_problem(problem_id):

    conn = get_db()

    try:

        problem = conn.execute(
            """
            SELECT *
            FROM problems
            WHERE id=%s
            """,
            (problem_id,),
        ).fetchone()

        tests = conn.execute(
            """
            SELECT *
            FROM test_cases
            WHERE problem_id=%s
            """,
            (problem_id,),
        ).fetchall()

    finally:

        conn.close()

    if not problem:

        return (
            "Problem not found",
            404
        )

    payload = {

        "problem":
            dict(problem),

        "test_cases":
            [
                dict(test)
                for test in tests
            ],
    }

    data = json.dumps(
        payload,
        indent=2,
        ensure_ascii=False,
    ).encode("utf-8")

    return send_file(
        io.BytesIO(data),
        as_attachment=True,
        download_name=
            f"problem_{problem_id}.json",
        mimetype=
            "application/json",
    )


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

# PostgreSQL is persistent, so these can safely
# run when a new server instance starts.

init_db()
migrate_demo_data()
seed_demo()


# =========================================================
# APPLICATION ENTRY POINT
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )