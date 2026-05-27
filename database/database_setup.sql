-- MoMo SMS Database Setup

CREATE DATABASE IF NOT EXISTS momo_db;
USE momo_db;

SET FOREIGN_KEY_CHECKS = 0;


-- Transaction_Categories comes first because Transactions depends on it
CREATE TABLE IF NOT EXISTS Transaction_Categories (
    category_id   INT          NOT NULL AUTO_INCREMENT COMMENT 'category primary key',
    name          VARCHAR(50)  NOT NULL                COMMENT 'e.g. Incoming Payment and Transfer Out **',
    type          VARCHAR(50)  NOT NULL                COMMENT 'debit or credit **',
    direction     VARCHAR(3)   NOT NULL                COMMENT 'IN or OUT **',

    CONSTRAINT pk_category   PRIMARY KEY (category_id),
    CONSTRAINT chk_direction CHECK (direction IN ('IN', 'OUT')),
    CONSTRAINT chk_type      CHECK (type IN ('debit', 'credit')) 
);


CREATE TABLE IF NOT EXISTS Users (
    user_id        INT          NOT NULL AUTO_INCREMENT COMMENT 'user primary key',
    name           VARCHAR(100) NOT NULL                COMMENT 'full name',
    phone_full     VARCHAR(15)  NOT NULL                COMMENT 'e.g. +250781234567',
    phone_masked   VARCHAR(15)                          COMMENT 'e.g. +25078***567',
    user_type      VARCHAR(20)  NOT NULL DEFAULT 'personal' COMMENT 'personal, merchant or agent',
    account_number VARCHAR(20)                          COMMENT 'MoMo account number',

    CONSTRAINT pk_user       PRIMARY KEY (user_id),
    CONSTRAINT uq_phone      UNIQUE (phone_full),
    CONSTRAINT chk_user_type CHECK (user_type IN ('personal', 'merchant', 'agent'))
);


-- used transaction_id as PK instead of transaction_date because:
-- transaction_date alone is not safe as a PK since two transactions can happen at the same timestamp
CREATE TABLE IF NOT EXISTS Transactions (
    transaction_id   INT           NOT NULL AUTO_INCREMENT COMMENT 'our surrogate primary key',
    transaction_date BIGINT        NOT NULL               COMMENT 'unix timestamp from our SMS metadata',
    occurred_at      DATETIME      NOT NULL               COMMENT 'when the transaction happened',
    amount           DECIMAL(10,2) NOT NULL               COMMENT 'amount in RWF',
    fee              DECIMAL(10,2) NOT NULL DEFAULT 0.00  COMMENT 'transaction fee',
    new_balance      DECIMAL(10,2) NOT NULL               COMMENT 'balance after transaction',
    category_id      INT           NOT NULL               COMMENT 'links to Transaction_Categories',
    sender_message   TEXT                                 COMMENT 'optional message from sender',
    token            VARCHAR(50)                          COMMENT 'unique transaction token',
    external_txn_id  VARCHAR(50)                          COMMENT 'external reference ID',
    body_raw         TEXT                                 COMMENT 'raw SMS text',

    CONSTRAINT pk_transaction     PRIMARY KEY (transaction_id),
    CONSTRAINT uq_token           UNIQUE (token),
    CONSTRAINT fk_transaction_cat FOREIGN KEY (category_id) REFERENCES Transaction_Categories(category_id)
                                  ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_amount         CHECK (amount > 0),
    CONSTRAINT chk_fee            CHECK (fee >= 0),
    CONSTRAINT chk_new_balance    CHECK (new_balance >= 0)
);


-- junction table - links transactions to the users involved
-- one transaction can have multiple users (sender, receiver, agent)
CREATE TABLE IF NOT EXISTS Transaction_Users (
    transaction_id INT         NOT NULL COMMENT 'links to Transactions',
    user_id        INT         NOT NULL COMMENT 'links to Users',
    role           VARCHAR(20) NOT NULL COMMENT 'sender, receiver or agent',

    CONSTRAINT pk_txn_user     PRIMARY KEY (transaction_id, user_id, role),
    CONSTRAINT fk_txnuser_txn  FOREIGN KEY (transaction_id) REFERENCES Transactions(transaction_id)
                               ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_txnuser_user FOREIGN KEY (user_id) REFERENCES Users(user_id)
                               ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_role        CHECK (role IN ('sender', 'receiver', 'agent'))
);


-- added transaction_id FK so logs can be traced back to a specific transaction
-- this relationship was missing in the original ERD
CREATE TABLE IF NOT EXISTS System_Logs (
    log_id           INT         NOT NULL AUTO_INCREMENT COMMENT 'log primary key',
    timestamp        DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'when the log was created',
    level            VARCHAR(10) NOT NULL               COMMENT 'INFO, WARN or ERROR',
    message          TEXT        NOT NULL               COMMENT 'what happened',
    record_reference VARCHAR(50)                        COMMENT 'related record e.g. transaction token',
    transaction_id   INT                                COMMENT 'links to Transactions if applicable',

    CONSTRAINT pk_log        PRIMARY KEY (log_id),
    CONSTRAINT fk_log_txn    FOREIGN KEY (transaction_id) REFERENCES Transactions(transaction_id)
                             ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT chk_log_level CHECK (level IN ('INFO', 'WARN', 'ERROR'))
);  


-- added user_id FK to link each message to the user it came from
-- also missing from the original ERD
CREATE TABLE IF NOT EXISTS System_Messages (
    received_at BIGINT      NOT NULL  COMMENT 'unix timestamp of received SMS',
    otp_code    VARCHAR(10)           COMMENT 'OTP code if the message contains one',
    full_text   TEXT        NOT NULL  COMMENT 'full raw SMS text',
    user_id     INT                   COMMENT 'links to Users',

    CONSTRAINT pk_sms_message PRIMARY KEY (received_at),
    CONSTRAINT fk_sysmsg_user FOREIGN KEY (user_id) REFERENCES Users(user_id)
                              ON UPDATE CASCADE ON DELETE SET NULL
);


SET FOREIGN_KEY_CHECKS = 1;


-- indexes on columns we expect to filter or join on regularly
CREATE INDEX idx_transactions_occurred_at ON Transactions(occurred_at);
CREATE INDEX idx_transactions_category    ON Transactions(category_id);
CREATE INDEX idx_transactions_token       ON Transactions(token);
CREATE INDEX idx_txn_users_user           ON Transaction_Users(user_id);
CREATE INDEX idx_system_logs_level        ON System_Logs(level);
CREATE INDEX idx_system_logs_timestamp    ON System_Logs(timestamp);
CREATE INDEX idx_system_logs_txn          ON System_Logs(transaction_id);
CREATE INDEX idx_users_phone              ON Users(phone_full);
CREATE INDEX idx_users_type               ON Users(user_type);
CREATE INDEX idx_sysmsg_user              ON System_Messages(user_id);


-- sample data

INSERT INTO Transaction_Categories (name, type, direction) VALUES
('P2P Transfer',     'debit',  'OUT'),
('P2P Receive',      'credit', 'IN'),
('Merchant Payment', 'debit',  'OUT'),
('Airtime Purchase', 'debit',  'OUT'),
('Bank Deposit',     'credit', 'IN'),
('Cash Withdrawal',  'debit',  'OUT'),
('Utility Payment',  'debit',  'OUT');

INSERT INTO Users (name, phone_full, phone_masked, user_type, account_number) VALUES
('Ayo Mensah',      '+250781234567', '+25078***567', 'personal', 'ACC100001'),
('Joy Uwase',       '+250789876543', '+25078***543', 'personal', 'ACC100002'),
('Keza Mutoni',     '+250722345678', '+25072***678', 'merchant', 'ACC100003'),
('Claude Habimana', '+250733456789', '+25073***789', 'agent',    'ACC100004'),
('Diane Ishimwe',   '+250756789012', '+25075***012', 'personal', 'ACC100005'),
('Eric Nkurunziza', '+250768901234', '+25076***234', 'personal', 'ACC100006');

INSERT INTO Transactions (transaction_date, occurred_at, amount, fee, new_balance, category_id, sender_message, token, external_txn_id, body_raw) VALUES
(1714500000, '2024-04-30 10:00:00', 5000.00,  50.00,  45000.00, 1, 'Lunch money',  'TKN-0001', 'EXT-AA001', 'TxId AA001 confirmed. RWF 5000 sent to Joy Uwase.'),
(1714503600, '2024-04-30 11:00:00', 20000.00, 100.00, 80000.00, 2, NULL,           'TKN-0002', 'EXT-AA002', 'You have received RWF 20000 from Ayo Mensah.'),
(1714507200, '2024-04-30 12:00:00', 3500.00,  35.00,  76500.00, 3, 'Grocery shop', 'TKN-0003', 'EXT-AA003', 'Payment of RWF 3500 to Keza Mutoni successful.'),
(1714510800, '2024-04-30 13:00:00', 1000.00,  10.00,  75500.00, 4, NULL,           'TKN-0004', 'EXT-AA004', 'Airtime of RWF 1000 purchased successfully.'),
(1714514400, '2024-04-30 14:00:00', 50000.00, 200.00, 25500.00, 6, NULL,           'TKN-0005', 'EXT-AA005', 'Cash withdrawal of RWF 50000 via agent Claude Habimana.'),
(1714518000, '2024-04-30 15:00:00', 10000.00, 0.00,   35500.00, 5, NULL,           'TKN-0006', 'EXT-AA006', 'Bank deposit of RWF 10000 received.');

INSERT INTO Transaction_Users (transaction_id, user_id, role) VALUES
(1, 1, 'sender'),
(1, 2, 'receiver'),
(2, 2, 'sender'),
(2, 1, 'receiver'),
(3, 5, 'sender'),
(3, 3, 'receiver'),
(4, 5, 'sender'),
(5, 6, 'sender'),
(5, 4, 'agent'),
(6, 1, 'receiver');

INSERT INTO System_Logs (timestamp, level, message, record_reference, transaction_id) VALUES
('2024-04-30 10:00:05', 'INFO',  'Transaction parsed successfully.',      'TKN-0001', 1),
('2024-04-30 11:00:08', 'INFO',  'Transaction parsed successfully.',      'TKN-0002', 2),
('2024-04-30 12:00:03', 'INFO',  'Transaction parsed successfully.',      'TKN-0003', 3),
('2024-04-30 13:00:01', 'WARN',  'Duplicate token check triggered.',      'TKN-0004', 4),
('2024-04-30 14:00:11', 'INFO',  'Agent withdrawal logged.',              'TKN-0005', 5),
('2024-04-30 15:05:00', 'ERROR', 'Failed to parse SMS - unknown format.', NULL,       NULL);

INSERT INTO System_Messages (received_at, otp_code, full_text, user_id) VALUES
(1714499990, NULL,     'TxId AA001 confirmed. RWF 5000 sent to Joy Uwase. New balance: RWF 45000.',  1),
(1714503590, NULL,     'You have received RWF 20000 from Ayo Mensah. New balance: RWF 80000.',       2),
(1714507190, NULL,     'Payment of RWF 3500 to Keza Mutoni successful. New balance: RWF 76500.',     5),
(1714510790, NULL,     'Airtime of RWF 1000 purchased. New balance: RWF 75500.',                    5),
(1714514390, NULL,     'Cash withdrawal of RWF 50000 via agent. New balance: RWF 25500.',           6),
(1714517990, '847291', 'Your OTP code is 847291. Do not share this with anyone.',                   1);


-- CRUD tests

-- all transactions with their category
SELECT
    t.transaction_id,
    t.occurred_at,
    t.amount,
    t.fee,
    t.new_balance,
    c.name AS category,
    c.direction
FROM Transactions t
JOIN Transaction_Categories c ON t.category_id = c.category_id
ORDER BY t.occurred_at;

-- who was involved in each transaction
SELECT
    tu.transaction_id,
    u.name,
    u.phone_full,
    tu.role,
    t.amount,
    t.occurred_at
FROM Transaction_Users tu
JOIN Users u ON tu.user_id = u.user_id
JOIN Transactions t ON tu.transaction_id = t.transaction_id
ORDER BY tu.transaction_id, tu.role;

-- check error logs
SELECT * FROM System_Logs WHERE level = 'ERROR';

-- update account number
UPDATE Users SET account_number = 'ACC200001' WHERE phone_full = '+250781234567';

-- fix a fee that was entered wrong
UPDATE Transactions SET fee = 60.00 WHERE transaction_id = 1;

-- remove a test log entry
DELETE FROM System_Logs WHERE level = 'WARN' AND transaction_id = 4;

-- confirm what is left in logs
SELECT * FROM System_Logs ORDER BY log_id;