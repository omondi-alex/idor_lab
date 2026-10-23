# Lab: Broken Authorization (IDOR)

** Run everything locally on 127.0.0.1.

## What this is

A tiny SACCO "portal" with two users and two accounts. The
`/account/<acc_id>` endpoint checks that you are *logged in* but never
checks that the account *belongs to you* - the classic IDOR
(Insecure Direct Object Reference) bug from the lecture.

## 1. Set up (once)

```bash
# optional but recommended: a virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
python init_db.py               # creates bank.db with demo data
```

## 2. Run the server

```bash
python app.py
```

Open http://127.0.0.1:5000 in your browser.

Demo accounts:

| Username | Password  | Owns account |
|----------|-----------|--------------|
| alice    | alice123  | 1001         |
| bob      | bob123    | 1002         |

## 3. Reproduce the vulnerability

1. Log in as **alice** (alice / alice123).
2. Click "View my account" - you see account **1001** (Alice's).
3. In the address bar, change the URL to
   `http://127.0.0.1:5000/account/1002` and press Enter.
4. You can now see **Bob's** account and balance - even though you are
   logged in as Alice. That is the IDOR vulnerability.
5. Take a **screenshot** of Alice viewing account 1002.

## 4. Fix it

In `app.py`, comment out the vulnerable `view_account` function and
uncomment the secure one further down (the block marked
"THE SECURE ENDPOINT"). It adds an ownership check:

```python
if acc is None or acc["owner_id"] != current_user():
    abort(403)
```

Save, restart `python app.py`, log in as Alice again, and try
`/account/1002`. You should now get **403 Forbidden**. Take a second
screenshot of the 403 page.

## 5. Deliverable

Submit:
- Screenshot 1: the bug (Alice viewing Bob's account 1002).
- Screenshot 2: the fix (403 Forbidden on the same URL).
- Your before/after `view_account` code.
- A short note (3-4 lines) explaining which vulnerability you closed
  and why the ownership check belongs on the server.
