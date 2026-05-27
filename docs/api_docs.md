# MoMo SMS Transactions API

A REST API for managing mobile money (MoMo) SMS transactions parsed from XML data. Built with plain Python (`http.server`) — no web framework.

---

## Table of Contents

1. [Overview](#overview)
2. [Base URL](#base-url)
3. [Authentication](#authentication)
4. [Data Model](#data-model)
5. [Endpoints](#endpoints)
   - [List all transactions](#list-all-transactions)
   - [Get one transaction](#get-one-transaction)
   - [Create a transaction](#create-a-transaction)
   - [Update a transaction](#update-a-transaction)
   - [Delete a transaction](#delete-a-transaction)
6. [Error Codes](#error-codes)
7. [Running Locally](#running-locally)

---

## Overview

This API exposes mobile money transaction data extracted from SMS messages. Each transaction includes the amount, sender, receiver, category (e.g. Incoming Money, Airtime Purchase, Bank Deposit), and metadata about when the transaction occurred. All sensitive identifiers (phone numbers, account numbers) are masked before being stored or returned.

The API supports the standard CRUD operations:

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/transactions` | List all transactions |
| `GET` | `/transactions/{id}` | Retrieve a single transaction |
| `POST` | `/transactions` | Create a new transaction |
| `PUT` | `/transactions/{id}` | Update an existing transaction |
| `DELETE` | `/transactions/{id}` | Remove a transaction |

---

## Base URL

```
http://localhost:8000
```

All endpoints in this document are relative to this base URL.

---

## Authentication

The API is protected with **HTTP Basic Authentication**. Every request must include an `Authorization` header containing base64-encoded credentials.

### How to send credentials

```
Authorization: Basic <base64(username:password)>
```

For example, the credentials `admin:password` become:

```
Authorization: Basic YWRtaW46cGFzc3dvcmQ=
```

Most HTTP clients handle this for you. With `curl`:

```bash
curl -u admin:password http://localhost:8000/transactions
```

### Responses

| Scenario | Status | Body |
|----------|--------|------|
| Missing `Authorization` header | `401 Unauthorized` | `{"error": "Authorization required"}` |
| Wrong username or password | `401 Unauthorized` | `{"error": "Invalid credentials"}` |
| Valid credentials | Continues to the requested endpoint | — |

> **Security note:** Basic Auth is suitable for learning and internal tools, but it is **not secure for production use**. Credentials are only base64-encoded (which is trivial to reverse), and they are sent on every request. See the project report for a fuller discussion and stronger alternatives (JWT, OAuth 2.0).

---

## Data Model

Every transaction returned by the API has the following shape:

```json
{
  "transaction_id": 1,
  "financial_id": "76662021700",
  "occurred_at": "2024-05-10 16:30:51",
  "amount": 2000.0,
  "fee": 0.0,
  "new_balance": 2000.0,
  "category": {
    "name": "Incoming Money",
    "type": "credit",
    "direction": "IN"
  },
  "sender": {
    "name": "Jane Smith",
    "identifier": {
      "type": "phone",
      "value": "*********013"
    }
  },
  "receiver": {
    "name": null,
    "identifier": {
      "type": null,
      "value": null
    }
  },
  "body_raw": "You have received 2000 RWF from Jane Smith...",
  "log": {
    "level": "INFO",
    "message": "Transaction parsed successfully.",
    "timestamp": "2024-05-10 16:30:51"
  },
  "is_processed": true
}
```

### Field reference

| Field | Type | Description |
|-------|------|-------------|
| `transaction_id` | integer | Unique server-assigned ID |
| `financial_id` | string \| null | Original transaction ID from the SMS (e.g. TxId) |
| `occurred_at` | string | Timestamp the transaction happened, formatted `YYYY-MM-DD HH:MM:SS` |
| `amount` | number | The transaction amount in RWF |
| `fee` | number | Any fee charged by the provider |
| `new_balance` | number | The account balance after this transaction |
| `category.name` | string | Human-readable category (e.g. `"Incoming Money"`) |
| `category.type` | string | One of `credit`, `debit`, or `unknown` |
| `category.direction` | string | One of `IN`, `OUT`, or `UNK` |
| `sender.name` | string \| null | Sender's name |
| `sender.identifier.type` | string \| null | `phone`, `account_number`, `momo_code`, or `merchant` |
| `sender.identifier.value` | string \| null | The masked identifier value |
| `receiver` | object | Same shape as `sender` |
| `body_raw` | string | The original SMS body |
| `log` | object | Internal log with level, message, and timestamp |
| `is_processed` | boolean | Whether the transaction has been processed |

---

## Endpoints

### List all transactions

Returns every transaction in the system.

**Request**

```http
GET /transactions
Authorization: Basic <credentials>
```

**Example**

```bash
curl -u admin:password http://localhost:8000/transactions
```

**Response — `200 OK`**

```json
[
  {
    "transaction_id": 1,
    "financial_id": "76662021700",
    "occurred_at": "2024-05-10 16:30:51",
    "amount": 2000.0,
    "...": "..."
  },
  {
    "transaction_id": 2,
    "...": "..."
  }
]
```

---

### Get one transaction

Returns a single transaction by ID.

**Request**

```http
GET /transactions/{id}
Authorization: Basic <credentials>
```

| Path parameter | Type | Description |
|----------------|------|-------------|
| `id` | integer | The `transaction_id` of the record |

**Example**

```bash
curl -u admin:password http://localhost:8000/transactions/1
```

**Response — `200 OK`**

```json
{
  "transaction_id": 1,
  "financial_id": "76662021700",
  "occurred_at": "2024-05-10 16:30:51",
  "amount": 2000.0,
  "category": {"name": "Incoming Money", "type": "credit", "direction": "IN"},
  "sender": {"name": "Jane Smith", "identifier": {"type": "phone", "value": "*********013"}},
  "receiver": {"name": null, "identifier": {"type": null, "value": null}},
  "...": "..."
}
```

**Response — `404 Not Found`**

```json
{"error": "Transaction 99999 not found"}
```

---

### Create a transaction

Creates a new transaction. The client only needs to provide the four essential fields — the server fills in the rest (timestamp, log, defaults) automatically.

**Request**

```http
POST /transactions
Authorization: Basic <credentials>
Content-Type: application/json

{
  "amount": 5000,
  "category": "Money Transfer",
  "sender": "John Doe",
  "receiver": "Jane Smith"
}
```

**Required fields**

| Field | Type | Description |
|-------|------|-------------|
| `amount` | number | The transaction amount |
| `category` | string | Category label (e.g. `"Money Transfer"`, `"Incoming Money"`) |
| `sender` | string | Sender's name |
| `receiver` | string | Receiver's name |

**Optional fields** (will use defaults if omitted): `financial_id`, `occurred_at`, `fee`, `new_balance`, `body_raw`.

**Example**

```bash
curl -u admin:password -X POST http://localhost:8000/transactions \
  -H "Content-Type: application/json" \
  -d '{"amount": 5000, "category": "Money Transfer", "sender": "John Doe", "receiver": "Jane Smith"}'
```

**Response — `201 Created`**

```json
{
  "message": "Transaction created",
  "data": {
    "transaction_id": 1693,
    "financial_id": null,
    "occurred_at": "2026-05-27 17:23:45",
    "amount": 5000.0,
    "fee": 0.0,
    "new_balance": 0.0,
    "category": {"name": "Money Transfer", "type": "unknown", "direction": "UNK"},
    "sender": {"name": "John Doe", "identifier": {"type": null, "value": null}},
    "receiver": {"name": "Jane Smith", "identifier": {"type": null, "value": null}},
    "body_raw": "",
    "log": {
      "level": "INFO",
      "message": "Transaction created via API.",
      "timestamp": "2026-05-27 17:23:45"
    },
    "is_processed": true
  }
}
```

**Response — `400 Bad Request`** (missing fields)

```json
{"error": "Missing required fields: category, sender, receiver"}
```

---

### Update a transaction

Partially updates an existing transaction. Only the fields you include in the request body will be changed — everything else stays the same.

**Request**

```http
PUT /transactions/{id}
Authorization: Basic <credentials>
Content-Type: application/json

{
  "amount": 9999
}
```

| Path parameter | Type | Description |
|----------------|------|-------------|
| `id` | integer | The `transaction_id` of the record to update |

**Example**

```bash
curl -u admin:password -X PUT http://localhost:8000/transactions/1 \
  -H "Content-Type: application/json" \
  -d '{"amount": 9999}'
```

**Response — `200 OK`**

```json
{
  "message": "Transaction updated",
  "data": {
    "transaction_id": 1,
    "amount": 9999,
    "...": "..."
  }
}
```

**Response — `404 Not Found`**

```json
{"error": "Transaction 1 not found"}
```

> Note: The `transaction_id` field cannot be changed via PUT. If you include it in the body it will be silently overridden with the ID from the URL.

---

### Delete a transaction

Removes a transaction from the system.

**Request**

```http
DELETE /transactions/{id}
Authorization: Basic <credentials>
```

| Path parameter | Type | Description |
|----------------|------|-------------|
| `id` | integer | The `transaction_id` of the record to delete |

**Example**

```bash
curl -u admin:password -X DELETE http://localhost:8000/transactions/1
```

**Response — `200 OK`**

```json
{"message": "Transaction 1 deleted"}
```

**Response — `404 Not Found`**

```json
{"error": "Transaction 1 not found"}
```

---

## Error Codes

| Status | Meaning | When it happens |
|--------|---------|----------------|
| `200 OK` | Success | Successful GET, PUT, or DELETE |
| `201 Created` | Resource created | Successful POST |
| `400 Bad Request` | Invalid input | Malformed JSON, missing required fields, or invalid transaction ID format |
| `401 Unauthorized` | Authentication failed | Missing or wrong credentials |
| `404 Not Found` | Resource not found | The transaction ID doesn't exist, or the URL doesn't match any route |

All error responses follow this shape:

```json
{"error": "Human-readable description of what went wrong"}
```

---

## Running Locally

### Prerequisites

- Python 3.8 or higher
- The `modified_sms_v2.xml` file in `data/raw/`

### Start the server

From the project root:

```bash
python api/server.py
```

You should see:

```
Server running at http://localhost:8000
Loaded 1692 transactions into memory.
Press Ctrl+C to stop.
```

### Try it out

```bash
# List everything
curl -u admin:password http://localhost:8000/transactions

# Get one
curl -u admin:password http://localhost:8000/transactions/1
```

### Interactive documentation

Open `docs/swagger_ui.html` in a browser for the interactive Swagger UI. It lets you try every endpoint from a web interface without writing any curl commands.

---

## Notes & Limitations

- **In-memory storage.** The API loads transactions from XML once at startup. Any changes you make via POST, PUT, or DELETE are kept in memory only and disappear when the server restarts.
- **No pagination.** `GET /transactions` returns every record at once. With ~1,700 transactions this is fine, but it wouldn't scale.
- **Basic Auth only.** As noted above, this is not production-grade. See the project report for stronger alternatives.