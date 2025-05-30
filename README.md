# Launch
```bash
uvicorn app.main:app --reload --port 8080
```
# Alembic guide

1. Install alembic and initialize it:
```bash
pip install alembic
alembic init -t async alembic
```

2. Edit `env.py`:
- add `config.set_main_option('sqlalchemy.url', DB_URL)` after `config = context.config`
- edit `target_metadata` from `None` to `Base.metadata`

3. Generate migration and apply it
```bash
alembic revision --message="Some useful comment" --autogenerate
alembic upgrade head
```

# Useful code
## Decode cyrillic symbols
```python
from urllib.parse import unquote

location = 'http://127.0.0.1:8000/hotels?location=%D0%90%D0%BB%D1%82%D0%B0%D0%B9'

decoded_location = unquote(location)
print(decoded_location)
```

## Accept user-agent
```
@app.get("/items/")
async def read_items(user_agent: Annotated[str | None, Header()] = None):
    return {"User-Agent": user_agent}
```

## TODO

- Team collaborations (needs a many-to-many User ↔ Project or Project ↔ TeamMember model)
- Sharing tasks/projects with permission levels
- Assigning projects to specific users or groups
- WebSocket-based real-time updates
- Notifications/reminders
- Labels/tags
- File attachments
- Subscriptions
