## python-fast-api


## Docker

For having mongodb on port 27017 please run:
```bash
docker-compose up
```

## create venv

preparation:
```bash
python3 -m venv .venv
pip install -r requirements.txt
```

run:
```bash
source .venv/bin/activate
fastapi dev main.py
```

You should see:

* Server started at http://127.0.0.1:8000
* Documentation at http://127.0.0.1:8000/docs

