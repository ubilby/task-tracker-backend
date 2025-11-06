### Backend application for ToDo-List
launch:
```bash
uvicorn main:app --reload
```

### To create db with migrations
init alembic
```bash
alembic init alembic
```
create db
```bash
alembic upgrade head
```
make migrations -m "{name}"
```bash
alembic revision --autogenerate -m "init db"
```
apply migrations
```bash
alembic upgrade head
```
