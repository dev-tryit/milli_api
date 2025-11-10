# Makefile - RESTful 쇼핑몰 상품 관리 API
# 
# 사용법:
#   make install      - 프로젝트 의존성 설치
#   make test         - 전체 테스트 실행
#   make run          - 애플리케이션 실행
#   make docker-up    - Docker로 MySQL, Redis 실행
#   make docker-down  - Docker 컨테이너 중지
#   make migrate      - 데이터베이스 마이그레이션 실행

.PHONY: install test run docker-up docker-down migrate

# install: 프로젝트 의존성 설치
# uv를 사용하여 pyproject.toml에 정의된 모든 의존성을 설치합니다.
# 실행 예시: make install
install:
	uv sync

# test: 전체 테스트 실행
# pytest를 사용하여 tests/ 디렉토리의 모든 테스트를 실행합니다.
# 실행 예시: make test
test:
	uv run pytest

# run: 애플리케이션 실행
# FastAPI 애플리케이션을 개발 모드로 실행합니다.
# 실행 후 http://localhost:8001/docs 에서 API 문서를 확인할 수 있습니다.
# 실행 예시: make run
run:
	uv run python run.py

# docker-up: Docker로 MySQL, Redis 실행
# docker-compose를 사용하여 MySQL과 Redis 컨테이너를 실행합니다.
# 실행 예시: make docker-up
docker-up:
	docker-compose up -d

# docker-down: Docker 컨테이너 중지
# 실행 중인 MySQL과 Redis 컨테이너를 중지합니다.
# 실행 예시: make docker-down
docker-down:
	docker-compose down

# migrate: 데이터베이스 마이그레이션 실행
# Alembic을 사용하여 데이터베이스 스키마를 마이그레이션합니다.
# 실행 예시: make migrate
migrate:
	uv run alembic upgrade head

