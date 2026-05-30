# momo_data_app-Team_1

## Team Name
Team 1

## Team Members
1. Aduk Mathiang Ngut Nyang
2. Ntwali Beni David
3. Bol David Garang Dau
4. Ojudun Ayomide Oluwatimilehin

## Project Description
This is an enterprise fullstack web application that processes MTN Mobile Money (MoMo) SMS transaction data. The SMS messages come in XML format, so our app reads through them, cleans the data, sorts each transaction into a category (incoming money, payments, airtime, deposits, withdrawals, and so on), and stores everything in a MySQL database.

Once the data is stored, the app displays it on a simple web dashboard where users can see charts, totals, and trends from their MoMo activity. The goal is to turn raw SMS messages into something useful and easy to understand at a glance.

## Technologies We Plan to Use

- **Python** — for the ETL pipeline (parsing XML, cleaning, categorizing, and loading into the database)
- **MySQL** — as our relational database (chosen for its strong support for CHECK constraints, DECIMAL types for accurate money handling, and referential integrity)
- **HTML, CSS, and JavaScript** — for the dashboard frontend (analysis and visualization)
- **Chart.js** — for displaying the charts and graphs on the dashboard
- **Shell scripts** — to run the ETL pipeline and serve the frontend
- **FastAPI** — for a small API layer between the database and the dashboard

## System Architecture
The diagram below shows how data flows through the system: from the raw `momo.xml` file, through the Python ETL pipeline, into the MySQL database, and finally to the dashboard the user sees in their browser.

![System Architecture](docs/System%20Architecture.png)

![System Architecture Diagram](./Docs/System%20Architecture.png)


![MoMo SMS Database ERD](docs/MoMo%20SMS%20Database%20ERD.png)

## Project Structure

```
momo_data_app-Team_1/
├── README.md
├── .env.example
├── .gitignore
├── requirements.txt
├── index.html
├── api/
│   └── server.py
├── data/
│   ├── raw/
│   │   └── .gitkeep
│   ├── processed/
│   │   └── dashboard.json
│   └── logs/
│       ├── etl.log
│       └── dead_letter/
├── database/
│   └── database_setup.sql
├── docs/
│   ├── api_docs.md
│   ├── openapi.yaml
│   ├── System Architecture.png
│   ├── MoMo SMS Database ERD.png
│   └── MoMo_SMS_Database_Design_Document.pdf
├── dsa/
│   ├── xml_parser.py
│   ├── search.py
│   └── benchmark.py
├── etl/
│   ├── __init__.py
│   ├── config.py
│   ├── parse_xml.py
│   ├── clean_normalize.py
│   ├── categorize.py
│   ├── load_db.py
│   └── run.py
├── examples/
│   ├── json_schemas.json
│   └── mapping.md
├── screenshots/
│   ├── get_authorized.png
│   ├── get_unauthorized.png
│   ├── post_transaction.png
│   ├── put_transaction.png
│   └── delete_transaction.png
├── scripts/
│   ├── run_etl.sh
│   ├── export_json.sh
│   └── serve_frontend.sh
├── tests/
│   ├── test_parse_xml.py
│   ├── test_clean_normalize.py
│   └── test_categorize.py
└── web/
    ├── styles.css
    ├── chart_handler.js
    └── assets/
```

## Project Management
We are using Trello as our Scrum board to plan tasks, track progress, and collaborate as a team. The board has three main columns: **To Do**, **In Progress**, and **Done**.

🔗 **Trello Scrum Board:** [Team Setup and Project Planning](https://trello.com/invite/b/69ff6ce284203e6123d4f091/ATTI16bb612672418866183c0c05bd24307d71C13F25/team-setup-and-project-planning)

## Current Status
We have completed Week 1 setup, Week 2 database design, and Week 3 API implementation. So far we have:

- Created the team GitHub repository and added all members as collaborators
- Organized the project folder structure
- Designed the high-level system architecture diagram
- Set up the Trello Scrum board with our initial tasks
- Analyzed the MoMo SMS XML dataset and identified all transaction types and field availability patterns
- Designed the full ERD with six entities and resolved the many-to-many relationship using a junction table
- Implemented the schema in MySQL with foreign keys, CHECK constraints, indexes, and column comments
- Tested the schema with a full CRUD cycle on the Users table (results documented in the Database Design Document)
- Modeled the schema as JSON for the future dashboard API, including a nested "completed transaction" example
- Built a REST API in plain Python with full CRUD endpoints for transactions
- Secured all endpoints with Basic Authentication (returns 401 for invalid credentials)
- Implemented and compared Linear Search and Dictionary Lookup for transaction retrieval
- Tested all endpoints with curl and documented results with screenshots

## How to Run the API

1. Make sure Python is installed
2. Place `modified_sms_v2.xml` in the `data/raw/` folder
3. Run the server from the project root:

```bash
python api/server.py
```

4. The server starts at `http://localhost:8000`
5. All endpoints require Basic Authentication:
   - Username: `admin`
   - Password: `password123`

Example request:
```bash
curl -u admin:password123 http://localhost:8000/transactions
```

---

## DSA Integration — Search Algorithms

The `dsa/` folder contains two search algorithm implementations for looking up transactions by ID, along with a benchmark to compare their efficiency.

### Files

| File | Description |
|------|-------------|
| `dsa/xml_parser.py` | Parses `modified_sms_v2.xml` and returns transactions as a dict and a list |
| `dsa/search.py` | Implements linear search and dictionary lookup |
| `dsa/benchmark.py` | Benchmarks both methods across 26 IDs × 100 repeats |

### How to Run

Navigate to the `dsa/` folder first:

```bash
cd dsa
```

**One-shot search (command line):**

```bash
# Default — linear search for transaction ID 25
python search.py 25

# Explicit linear search
python search.py 25 linear

# Dictionary lookup
python search.py 25 dict
```

**Interactive mode (no arguments):**

```bash
python search.py
```
Prompts you to choose a method, then lets you search by ID repeatedly until you type `q`.

**Benchmark:**

```bash
python benchmark.py
```

### Benchmark Results

Tested on 1,691 transactions, 26 IDs, 100 repeats each:

| Method | Total Time |
|--------|-----------|
| Linear search | 0.033485 seconds |
| Dictionary lookup | 0.000107 seconds |

**Dict lookup is 311.5× faster than linear search.**

### Why is Dictionary Lookup Faster?

Linear search scans every transaction one by one until it finds a match — O(n) time. With 1,691 records, that means up to 1,691 comparisons per lookup.

Dictionary lookup uses a hash table under the hood. Python computes a hash of the key and jumps directly to the right slot — O(1) average time, regardless of how many records exist.

### Possible Improvements

- **Binary search** on a sorted list — O(log n), faster than linear but still slower than a hash map
- **B-tree index** (as used in MySQL) — efficient for range queries like "all transactions between two dates"
- **Trie** — useful if searching by string prefixes (e.g. partial financial IDs)

### Test Evidence

Screenshots of all four test commands are saved in `screenshots/dsa_linear&dddict_lookup.png`.

---

## API Documentation

Full endpoint documentation (request/response examples, error codes, authentication details) is in [`docs/api_docs.md`](docs/api_docs.md).

---

## Authentication & Security Note

The API uses HTTP Basic Authentication. While functional for development and learning, Basic Auth has known limitations:
- Credentials are only base64-encoded, not encrypted
- Sent on every request, increasing exposure risk
- No token expiry or revocation mechanism

**Stronger alternatives:** JWT (JSON Web Tokens) for stateless auth with expiry, or OAuth 2.0 for delegated access with scopes. See the project report for a full discussion.