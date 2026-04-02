# Testing Scripts - Project Management MVP

## Backend API Testing

### Prerequisites
- Docker container running: `docker-compose up`
- Server accessible at: http://localhost:8000

### 1. Health Check
```bash
curl http://localhost:8000/api/health
```
Expected: `{"status":"ok"}`

### 2. Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"password"}'
```
Expected: `{"token":"...","username":"user"}`

Save the token for subsequent requests.

### 3. Get Current User
```bash
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```
Expected: `{"username":"user"}`

### 4. Get Board
```bash
curl http://localhost:8000/api/board \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```
Expected: Board with 5 columns (Backlog, Discovery, In Progress, Review, Done)

### 5. Rename Column
```bash
curl -X PUT http://localhost:8000/api/columns/1 \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"title":"New Column Name"}'
```
Expected: `{"id":1,"title":"New Column Name"}`

### 6. Create Card
```bash
curl -X POST http://localhost:8000/api/cards \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"column_id":1,"title":"Test Card","details":"Test details"}'
```
Expected: Card object with id, title, details, column_id, position

### 7. Update Card
```bash
curl -X PUT http://localhost:8000/api/cards/1 \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"title":"Updated Title","details":"Updated details"}'
```
Expected: Updated card object

### 8. Move Card
```bash
curl -X PUT http://localhost:8000/api/cards/1/move \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"target_column_id":2,"position":0}'
```
Expected: Card object with updated column_id and position

### 9. Delete Card
```bash
curl -X DELETE http://localhost:8000/api/cards/1 \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```
Expected: `{"message":"Card deleted"}`

### 10. Logout
```bash
curl -X POST http://localhost:8000/api/auth/logout \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```
Expected: `{"message":"Logged out"}`

### 11. Test Unauthorized Access
```bash
curl http://localhost:8000/api/board
```
Expected: 401 Unauthorized

## Frontend Testing

### Prerequisites
- Frontend accessible at: http://localhost:8000

### Manual Test Scenarios

#### Scenario 1: Login Flow
1. Navigate to http://localhost:8000
2. Should see login form
3. Enter username: `user`, password: `password`
4. Click submit
5. Should see Kanban board with 5 columns

#### Scenario 2: Column Rename
1. Click on a column title
2. Edit the text
3. Click outside or press Enter
4. Column title should update

#### Scenario 3: Add Card
1. Click "Add Card" button in any column
2. Enter title and details
3. Click "Add"
4. New card should appear in the column

#### Scenario 4: Delete Card
1. Hover over a card
2. Click the delete button (X)
3. Card should be removed

#### Scenario 5: Drag and Drop Card
1. Click and hold on a card
2. Drag to another column
3. Release
4. Card should move to new column

Note: Known issue - dragging to empty columns may not work at high resolutions

#### Scenario 6: Logout
1. Click logout button
2. Should return to login screen

## Backend Unit Tests

### Run All Tests
```bash
docker run --rm pm-app pytest /app/backend/tests/ -v
```

### Run Specific Test File
```bash
docker run --rm pm-app pytest /app/backend/tests/test_crud.py -v
```

### Run with Coverage
```bash
docker run --rm pm-app pytest /app/backend/tests/ --cov=/app/backend --cov-report=term-missing
```

### Expected Test Results
- test_auth.py: 5 tests passing (91% coverage)
- test_crud.py: 9 tests passing (100% coverage)
- test_database.py: 2 tests passing (93% coverage)
- test_init_db.py: 3 tests passing (80%+ coverage)
- test_main.py: 9 tests passing (80%+ coverage)
- test_models.py: 5 tests passing (100% coverage)

## Frontend Unit Tests

### Run Tests
```bash
cd frontend
npm test
```

### Expected Test Results
- auth.test.ts: All tests passing
- kanban.test.ts: All tests passing (including empty column tests)
- LoginForm.test.tsx: All tests passing
- KanbanBoard.test.tsx: All tests passing

## Integration Testing

### Full Flow Test
1. Start Docker container
2. Login via API and save token
3. Get board via API
4. Create card via API
5. Verify card appears in board
6. Move card via API
7. Verify card moved
8. Delete card via API
9. Verify card deleted
10. Logout via API

### Database Persistence Test
1. Start Docker container
2. Login and create cards via frontend
3. Stop Docker container
4. Start Docker container again
5. Login
6. Verify cards still exist

## Error Scenarios

### Test Invalid Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"wrong","password":"wrong"}'
```
Expected: 401 Unauthorized

### Test Invalid Token
```bash
curl http://localhost:8000/api/board \
  -H "Authorization: Bearer invalid_token"
```
Expected: 401 Unauthorized

### Test Non-existent Card
```bash
curl -X PUT http://localhost:8000/api/cards/9999 \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test"}'
```
Expected: 404 Not Found

### Test Non-existent Column
```bash
curl -X PUT http://localhost:8000/api/columns/9999 \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test"}'
```
Expected: 404 Not Found

## Performance Testing

### Load Test - Multiple Requests
```bash
for i in {1..10}; do
  curl http://localhost:8000/api/health &
done
wait
```

### Concurrent User Simulation
Use tools like Apache Bench or wrk:
```bash
ab -n 100 -c 10 http://localhost:8000/api/health
```

## Database Testing

### Check Database File
```bash
docker exec -it pm-app ls -la /app/data/
```
Expected: kanban.db file exists

### Query Database Directly
```bash
docker exec -it pm-app sqlite3 /app/data/kanban.db "SELECT * FROM users;"
```
Expected: Default user exists

## Troubleshooting

### Container Not Starting
```bash
docker-compose logs
```

### Database Not Initializing
```bash
docker exec -it pm-app cat /app/backend/init_db.py
docker exec -it pm-app python /app/backend/init_db.py
```

### Frontend Not Loading
1. Check if static files exist: `docker exec -it pm-app ls /app/frontend/out/`
2. Check server logs: `docker-compose logs`

### API Returning 500 Errors
```bash
docker-compose logs | grep ERROR
```
