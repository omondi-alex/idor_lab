"""Create and seed the demo SQLite database (run once)."""
import sqlite3
import bcrypt

conn = sqlite3.connect("bank.db")
c = conn.cursor()

c.executescript("""
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS accounts;

CREATE TABLE users (
    id        INTEGER PRIMARY KEY,
    username  TEXT UNIQUE,
    pass_hash BLOB,
    acc_id    INTEGER
);

CREATE TABLE accounts (
    acc_id   INTEGER PRIMARY KEY,
    owner_id INTEGER,
    holder   TEXT,
    balance  REAL
);
""")


def h(pw):
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt())


# users
c.execute("INSERT INTO users VALUES (?,?,?,?)",
          (1, "alice", h("alice123"), 1001))
c.execute("INSERT INTO users VALUES (?,?,?,?)",
          (2, "bob", h("bob123"), 1002))

# accounts
c.execute("INSERT INTO accounts VALUES (?,?,?,?)",
          (1001, 1, "Alice Wanjiku", 54000.00))
c.execute("INSERT INTO accounts VALUES (?,?,?,?)",
          (1002, 2, "Bob Otieno", 128500.00))

conn.commit()
conn.close()
print("Database created: bank.db")
print("  alice / alice123  -> account 1001")
print("  bob   / bob123    -> account 1002")
