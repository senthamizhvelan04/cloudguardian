install:
	cd backend && python -m pip install -r requirements.txt

test:
	cd backend && pytest -q

run:
	cd backend && uvicorn app.main:app --reload

lint:
	cd backend && ruff check app tests

format:
	cd backend && ruff format app tests

docker:
	docker compose up --build
