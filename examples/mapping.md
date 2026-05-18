# SQL to JSON Mapping

## Overview
This document is my attempt to explain how the JSON objects in json_schemas.json connect to the tables in our SQL database. The way I understood it, each JSON object is basically how a row of data looks after it leaves the database and gets sent to the frontend. I tried to keep the mapping logical and consistent throughout.

## 1. transaction_category maps to Transaction_Categories table
This one was fairly straightforward for me. The four fields, category_id, name, type, and direction, map directly to the four columns in the Transaction_Categories table. I intentionally kept the naming consistent between the JSON and the table so the relationship is easy to trace.

## 2. user maps to Users table
This one clicked for me pretty quickly. Every field in the user JSON, user_id, name, phone_full, phone_masked, user_type, and account_number, corresponds directly to a column in the Users table. One JSON object represents one user row in the database.

## 3. transaction maps to Transactions table
This maps to the Transactions table. The part that stood out to me here was the category_id field. Instead of repeating all the category details inside every transaction, it just references the right row in the Transaction_Categories table. That is what I understood a foreign key to do, and it made sense to use it here to avoid unnecessary repetition.

## 4. transaction_users maps to Transaction_Users table
This one took me a moment to fully grasp. This JSON represents the junction table that resolves the many-to-many relationship between transactions and users. The role field was important to me here. It tells us whether a user was the sender, receiver, or agent in a given transaction, which I felt was necessary information to capture.

## 5. system_log maps to System_Logs table
This maps directly to the System_Logs table. The transaction_id field links each log entry back to the transaction it belongs to. I included this because I felt it was important to be able to trace what happened during data processing.

## 6. system_message maps to System_Messages table
This maps to the System_Messages table. The user_id field connects each message to the right user. That made sense to me since MoMo sends SMS confirmations to specific users and we needed a way to track those.

## 7. complete_transaction is a Combined object
This was honestly the most interesting one to work on. Unlike the others, this JSON does not come from just one table. It pulls data from four tables, Transactions, Transaction_Categories, Users, and System_Logs, and combines them into one nested response. My thinking was that the dashboard should not have to make multiple separate requests just to display one transaction, so bringing everything together in one object felt like the right approach.
