### Backend application for ToDo-List
launch:
```bash
uvicorn main:app --reload
```

###To create db with migrations
init alembic
create db
make migrations -m "<name>"
apply migrations:
```bash
alembic init alembic
alembic upgrade head
alembic revision --autogenerate -m "init db"
alembic upgrade head

```

