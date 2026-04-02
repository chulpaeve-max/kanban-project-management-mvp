import sqlite3

conn = sqlite3.connect('/app/data/kanban.db')
cursor = conn.cursor()

print("=== TABLES ===")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
for table in tables:
    print(f"\n{table}")

print("\n\n=== USERS TABLE ===")
cursor.execute("SELECT * FROM users")
print("Columns:", [desc[0] for desc in cursor.description])
for row in cursor.fetchall():
    print(row)

print("\n\n=== BOARDS TABLE ===")
cursor.execute("SELECT * FROM boards")
print("Columns:", [desc[0] for desc in cursor.description])
for row in cursor.fetchall():
    print(row)

print("\n\n=== COLUMNS TABLE ===")
cursor.execute("SELECT * FROM columns")
print("Columns:", [desc[0] for desc in cursor.description])
for row in cursor.fetchall():
    print(row)

print("\n\n=== CARDS TABLE ===")
cursor.execute("SELECT * FROM cards")
print("Columns:", [desc[0] for desc in cursor.description])
for row in cursor.fetchall():
    print(row)

conn.close()
