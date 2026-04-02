# Database Schema

## Overview

SQLite database for storing users, boards, columns, and cards. The database will be created automatically if it doesn't exist.

## Database Choice

SQLite is used for simplicity in the MVP:
- Single file database
- No separate server process needed
- Perfect for local development and single-user scenarios
- Easy to package in Docker container

## Schema

### Users Table

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Fields:
- `id`: Primary key
- `username`: Unique username for login
- `password`: Hashed password (for MVP, stored as plain text but structure supports future hashing)
- `created_at`: Account creation timestamp

### Boards Table

```sql
CREATE TABLE boards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL DEFAULT 'My Board',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

Fields:
- `id`: Primary key
- `user_id`: Foreign key to users table
- `title`: Board title
- `created_at`: Board creation timestamp

Constraints:
- One board per user (enforced at application level)
- Cascade delete when user is deleted

### Columns Table

```sql
CREATE TABLE columns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    board_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    position INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (board_id) REFERENCES boards(id) ON DELETE CASCADE
);
```

Fields:
- `id`: Primary key
- `board_id`: Foreign key to boards table
- `title`: Column title (e.g., "Backlog", "In Progress")
- `position`: Display order (0-indexed)
- `created_at`: Column creation timestamp

Constraints:
- Cascade delete when board is deleted
- Position determines display order

### Cards Table

```sql
CREATE TABLE cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    column_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    details TEXT,
    position INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (column_id) REFERENCES columns(id) ON DELETE CASCADE
);
```

Fields:
- `id`: Primary key
- `column_id`: Foreign key to columns table
- `title`: Card title
- `details`: Card description/details
- `position`: Display order within column (0-indexed)
- `created_at`: Card creation timestamp
- `updated_at`: Last modification timestamp

Constraints:
- Cascade delete when column is deleted
- Position determines display order within column

## Relationships

```
users (1) ----< (1) boards
boards (1) ----< (*) columns
columns (1) ----< (*) cards
```

- One user has one board (MVP limitation)
- One board has multiple columns (fixed at 5 for MVP)
- One column has multiple cards

## JSON Representation

Example board data structure:

```json
{
  "id": 1,
  "user_id": 1,
  "title": "My Board",
  "columns": [
    {
      "id": 1,
      "title": "Backlog",
      "position": 0,
      "cards": [
        {
          "id": 1,
          "title": "Align roadmap themes",
          "details": "Draft quarterly themes with impact statements and metrics.",
          "position": 0
        },
        {
          "id": 2,
          "title": "Gather customer signals",
          "details": "Review support tags, sales notes, and churn feedback.",
          "position": 1
        }
      ]
    },
    {
      "id": 2,
      "title": "Discovery",
      "position": 1,
      "cards": []
    }
  ]
}
```

## Indexes

For optimal query performance:

```sql
CREATE INDEX idx_boards_user_id ON boards(user_id);
CREATE INDEX idx_columns_board_id ON columns(board_id);
CREATE INDEX idx_cards_column_id ON cards(column_id);
```

## Initial Data

Default board structure for new users:
- 5 columns: "Backlog", "Discovery", "In Progress", "Review", "Done"
- Sample cards from the frontend demo (optional)

## Database Location

- Development: `/app/data/kanban.db` (Docker volume)
- Persisted via Docker volume mount to `./data` on host
