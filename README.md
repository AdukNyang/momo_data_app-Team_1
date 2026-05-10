# momo_data_app-Team_1


## Team Name
**Team 1**

## Team Members
1. Aduk Mathiang Ngut Nyang
2. Ntwali Beni David
3. Bol David Garang Dau

---

## Project Description

This is an enterprise fullstack web application that processes **MTN Mobile Money (MoMo) SMS transaction data**. 
As the SMS messages come in XML format, our app reads through it, cleans the data, sorts each transaction into categories (e.g deposits, payments, airtime, withdrawals, etc.), and saves everything into a SQLite database.

Once the data is stored, the app shows it on a simple web dashboard where users can see charts, totals, and trends from their MoMo activity. The goal is to turn raw SMS messages into something useful and easy to understand at a glance.

---

## Technologies We Plan to Use

- **Python** — for the ETL pipeline (parsing XML, cleaning, categorizing, and loading into the database)
- **SQLite** — as our relational database
- **HTML, CSS, and JavaScript** — for the dashboard frontend (analysis and visualization)
- **Chart.js** — for ddisplaying the charts and graphs on the dashboard
- **Shell scripts** — to run the ETL pipeline and serve the frontend
- **FastAPI** — for a small API layer between the database and the dashboard

---

## System Architecture

The diagram below shows how data flows through the system: from the raw `momo.xml` file, through the Python ETL pipeline, into the SQLite database, and finally to the dashboard the user sees in their browser.

![System Architecture Diagram](./Docs/System%20Architecture.png)


---

## Project Structure

```
app-Team-1/
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
│   └── System Architecture.png
├── etl/
│   ├── __init__.py
│   ├── config.py
│   ├── parse_xml.py
│   ├── clean_normalize.py
│   ├── categorize.py
│   ├── load_db.py
│   └── run.py
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
    └── chart_handler.js
```


---

## Project Management

We are using **Trello** as our Scrum board to plan tasks, track progress, and collaborate as a team. The board has three main columns: **To Do**, **In Progress**, and **Done**.

🔗 **Trello Scrum Board:** (https://trello.com/invite/b/69ff6ce284203e6123d4f091/ATTI16bb612672418866183c0c05bd24307d71C13F25/team-setup-and-project-planning)

---

## Current Status

We are currently in the **setup and planning phase**. 

So far we have:
- Created the team GitHub repository and added all members as collaborators
- Organized the project folder structure
- Designed the high-level system architecture diagram
- Set up the Trello Scrum board with our initial tasks
