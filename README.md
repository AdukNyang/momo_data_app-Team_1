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
├── data/
│   ├── raw/
│   │   └── momo.xml
│   └── processed/
│       └── dashboard.json
├── Docs/
│   └── MOMo SMS Database ERD.png
│   └── MoMo_SMS_Database_Design_Document.pdf
│   └── Picture_Evidence.jpeg
│   └── System Architecture.png
├── etl/
│   ├── __init__.py
│   ├── config.py
│   ├── parse_xml.py
│   ├── clean_normalize.py
│   ├── categorize.py
│   ├── load_db.py
│   └── run.py
├── examples/
│   └── json_schemas.json
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
We have completed Week 1 setup and Week 2 database design. So far we have:

- Created the team GitHub repository and added all members as collaborators
- Organized the project folder structure
- Designed the high-level system architecture diagram
- Set up the Trello Scrum board with our initial tasks
- Analyzed the MoMo SMS XML dataset and identified all transaction types and field availability patterns
- Designed the full ERD with six entities and resolved the many-to-many relationship using a junction table
- Implemented the schema in MySQL with foreign keys, CHECK constraints, indexes, and column comments
- Tested the schema with a full CRUD cycle on the Users table (results documented in the Database Design Document)
- Modeled the schema as JSON for the future dashboard API, including a nested "completed transaction" example

## Next Steps
- Build the Python ETL pipeline to parse, clean, categorize, and load `momo.xml` into the database
- Add unit tests for the ETL modules
- Expose the data via a small FastAPI layer
- Build the dashboard frontend with Chart.js to visualize transaction totals, trends, and category breakdowns