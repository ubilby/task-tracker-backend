### Backend application for ToDo-List
launch:
```bash
uvicorn main:app --reload
```

### To create db with migrations
init alembic\n
create db\n
make migrations -m "{name}"\n
apply migrations\n
```bash
alembic init alembic
alembic upgrade head
alembic revision --autogenerate -m "init db"
alembic upgrade head

```

