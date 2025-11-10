# RESTful 쇼핑몰 상품 관리 API

## 목차

- [DDD 설계](#ddd-설계)
  - [전략적 설계](#전략적-설계)
  - [전술적 설계](#전술적-설계)
  - [설계 의도](#설계-의도)
- [아키텍처 구조](#아키텍처-구조)
- [폴더 구조](#폴더-구조)
- [프로젝트 명령어](#프로젝트-명령어)
- [API 명세서 실행 방법](#api-명세서-실행-방법)
- [핵심 코드](#핵심-코드)
  - [Rich Domain Model](#rich-domain-model)
  - [Repository Pattern](#repository-pattern)
- [테스트](#테스트)

---

## DDD 설계

### 전략적 설계

상품 관리 도메인에 대한 유비쿼터스 언어를 정의하였습니다.

**유비쿼터스 언어**:
- **Product (상품)**: 판매 가능한 아이템으로, 가격, 재고, 카테고리 정보를 가지며 할인율이 적용될 수 있음
- **Category (카테고리)**: 상품을 분류하는 체계
- **Coupon (쿠폰)**: 상품 구매 시 할인을 제공하는 정책으로, 유효 기간 내에만 사용 가능
- **Rate Coupon (비율 쿠폰)**: 할인가에 비율 할인을 적용하는 쿠폰
- **Amount Coupon (금액 쿠폰)**: 할인가에서 고정 금액을 차감하는 쿠폰
- **Original Price (원가)**: 할인 전 상품의 원래 가격
- **Discount Rate (할인율)**: 상품에 기본 적용되는 할인 비율
- **Discounted Price (할인가)**: 할인율만 적용한 가격
- **Final Price (최종 판매가)**: 할인율과 쿠폰을 모두 적용한 최종 가격

### 전술적 설계

- **Entity**: 고유 식별자를 가진 도메인 객체 (Product, Category, Coupon)
- **Rich Domain Model**: Entity에 비즈니스 로직 캡슐화 (Product.calculate_final_price)
- **Domain Service**: 여러 Entity 협력이 필요한 복잡한 로직 (PriceCalculator)
- **Repository Pattern**: 도메인 인터페이스(Port)와 인프라 구현(Adapter) 분리
- **Domain/Infrastructure Model 분리**: 순수 도메인 모델과 ORM 모델 분리

### 설계 의도

1. **도메인 로직 독립성**: 헥사고날 아키텍처로 도메인 레이어를 외부 프레임워크(ORM, FastAPI)로부터 완전히 격리하여, 프레임워크 변경 시에도 도메인 로직은 영향받지 않도록 함
2. **비즈니스 로직 캡슐화**: Rich Domain Model 패턴으로 Entity 내부에 비즈니스 규칙을 집중시켜, 비즈니스 로직의 응집도를 높이고 재사용성을 향상시킴
3. **의존성 역전**: 포트(인터페이스)를 통한 의존성 역전 원칙 적용으로, 고수준 모듈(도메인)이 저수준 모듈(인프라)에 의존하지 않고 추상화에 의존하도록 함
4. **테스트 용이성**: 순수 Python 클래스로 구현된 도메인 로직은 외부 의존성 없이 단위 테스트 가능하며, 포트를 통한 의존성 역전으로 테스트 시 Mock 구현체를 쉽게 주입하여 격리된 테스트 작성 가능

---

## 아키텍처 구조

**헥사고날 아키텍처 (Hexagonal Architecture)**: 도메인 로직을 외부 프레임워크나 인프라로부터 완전히 격리하여 독립성과 테스트 용이성을 확보합니다.

**의존성 방향**: `Inbound Adapter → Application Service → Domain ← Outbound Adapter`

**레이어 구조**:
- **Domain Layer (Hexagon)**: 헥사곤 중심부 - 순수한 비즈니스 로직 (ORM, 프레임워크 의존 없음)
- **Application Layer**: Inbound Adapter + Use Case 오케스트레이션 - 외부 요청을 도메인 로직으로 변환
- **Infrastructure Layer**: Outbound Adapter - 도메인 Port 구현체로 외부 시스템(DB, Redis 등)과 통신

---

## 폴더 구조

```
shopping-mall-api/
├── app/
│   ├── domain/              # --- Domain Layer (Hexagon)
│   │   ├── entities/        # Domain Entities
│   │   ├── services/        # Domain Services
│   │   ├── ports/           # Repository Interfaces (Protocol)
│   │   └── exceptions/      # Domain Exceptions
│   ├── application/         # --- Application Layer
│   │   ├── services/        # Application Services
│   │   ├── routers/         # Inbound Adapter (FastAPI)
│   │   ├── schemas/         # API Request/Response DTO
│   │   ├── mappers/         # Domain ↔ API Schema
│   │   ├── dependencies/    # FastAPI DI
│   │   ├── utils/           # Application Utilities (Cache-Aside 등)
│   │   └── main.py          # FastAPI 진입점
│   ├── infrastructure/      # --- Infrastructure Layer
│   │   ├── models/          # ORM Models
│   │   ├── adapters/        # Outbound Adapter
│   │   │   ├── db/          # Repository 구현체
│   │   │   └── cache/       # Redis 어댑터
│   │   ├── mappers/         # Domain ↔ ORM 변환
│   │   └── settings/        # 인프라 설정
├── tests/
│   ├── unit/                  # 단위 테스트
│   │   ├── domain/            # Domain Layer 테스트
│   │   │   ├── entities/      # Domain Entities 테스트
│   │   │   └── services/      # Domain Services 테스트
│   │   └── application/       # Application Layer 테스트
│   │       ├── services/      # Application Services 테스트
│   │       └── mappers/       # Mappers 테스트
│   └── integration/           # 통합 테스트
│       ├── helpers/           # 통합 테스트 헬퍼 모듈
│       │   ├── db_helpers.py  # DB 테스트 헬퍼 (세션, 데이터 생성/정리)
│       │   └── redis_helpers.py # Redis 테스트 헬퍼
│       ├── application/       # Application Layer 통합 테스트
│       │   └── routers/       # API 엔드포인트 테스트
│       └── infrastructure/    # Infrastructure Layer 통합 테스트
│           └── adapters/      # Adapter 통합 테스트
│               ├── db/        # DB Repository 통합 테스트 (CRUD, 연결)
│               └── cache/     # Redis Cache 통합 테스트
└── alembic/                 # DB 마이그레이션
```

---

## 프로젝트 명령어

```bash
# 프로젝트 의존성 설치
# uv를 사용하여 pyproject.toml에 정의된 모든 의존성을 설치합니다.
make install

# 전체 테스트 실행
# pytest를 사용하여 tests/ 디렉토리의 모든 테스트를 실행합니다.
make test

# 애플리케이션 실행
# FastAPI 애플리케이션을 개발 모드로 실행합니다.
# 실행 후 http://localhost:8001/docs 에서 API 문서를 확인할 수 있습니다.
make run

# Docker로 MySQL, Redis 실행
# docker-compose를 사용하여 MySQL과 Redis 컨테이너를 실행합니다.
make docker-up

# Docker 컨테이너 중지
# 실행 중인 MySQL과 Redis 컨테이너를 중지합니다.
make docker-down

# 데이터베이스 마이그레이션 실행
# Alembic을 사용하여 데이터베이스 스키마를 마이그레이션합니다.
make migrate
```

---

## API 명세서 실행 방법

애플리케이션 실행 후 다음 URL에서 API 명세서를 확인할 수 있습니다:

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

```bash
# FastAPI 애플리케이션을 개발 모드로 실행합니다.
make run

# 또는 직접 실행
uv run python run.py
```

---

## 핵심 코드

### Rich Domain Model

비즈니스 로직을 Domain Entity에 캡슐화합니다.

```44:74:app/domain/entities/product.py
    def calculate_final_price(self, coupon: "Coupon | None" = None) -> int:
        """
        할인율과 쿠폰을 적용한 최종 판매가 계산
        
        계산 순서:
        1. 원가에 할인율 적용
        2. 쿠폰 할인 적용
        
        Args:
            coupon: 적용할 쿠폰 (선택적)
            
        Returns:
            최종 판매가 (정수)
        """
        # 1. 할인율 적용
        discounted_price = self.get_discounted_price()
        
        # 2. 쿠폰 할인 적용
        if coupon:
            if coupon.discount_type == "rate":
                # 비율 할인
                final_price = int(discounted_price * (1.0 - coupon.discount_value))
            elif coupon.discount_type == "amount":
                # 금액 할인
                final_price = max(0, discounted_price - int(coupon.discount_value))
            else:
                raise ValueError(f"알 수 없는 쿠폰 할인 유형: {coupon.discount_type}")
        else:
            final_price = discounted_price
        
        return final_price
```

**특징**: 순수 Python 클래스 (ORM 의존 없음), 비즈니스 로직이 Entity 내부에 캡슐화, 테스트 용이 (Mock 불필요)

### Repository Pattern

도메인 인터페이스(Port)와 인프라 구현(Adapter)을 분리합니다.

```7:12:app/domain/ports/product_repository.py
class ProductRepository(Protocol):
    """상품 Repository 인터페이스 (Port)"""
    
    async def find_by_id(self, product_id: int) -> Product | None:
        """상품 ID로 조회"""
        ...
```

```18:27:app/infrastructure/adapters/db/product_repository_impl.py
    async def find_by_id(self, product_id: int) -> Product | None:
        """상품 ID로 조회"""
        stmt = select(ProductModel).where(ProductModel.id == product_id)
        result = await self.session.execute(stmt)
        product_model = result.scalar_one_or_none()
        
        if not product_model:
            return None
        
        return self.mapper.to_domain(product_model)
```

**의존성 방향**: Application Layer는 Protocol에 의존, Infrastructure Layer는 Protocol 구현 (의존성 역전 원칙)

### Application Service

Use Case를 구현하는 Application Service는 Port(인터페이스)에 의존합니다.

```126:167:app/application/services/product_service.py
    async def get_product_detail(
        self,
        product_id: int,
        coupon_code: str | None = None,
    ) -> tuple[Product, Coupon | None]:
        """
        상품 상세 조회 및 쿠폰 조회
        
        Args:
            product_id: 상품 ID
            coupon_code: 쿠폰 코드 (선택적)
            
        Returns:
            (상품, 쿠폰) 튜플
            
        Raises:
            ProductNotFoundException: 상품을 찾을 수 없을 때
            CouponNotFoundException: 쿠폰을 찾을 수 없을 때
            InvalidCouponException: 쿠폰이 유효하지 않을 때
        """
        # 트랜잭션 관리는 Router/Dependencies에서 처리 (get_db_session)
        # 상품 조회
        product = await self.product_repository.find_by_id(product_id)
        if not product:
            raise ProductNotFoundException(product_id)
        
        # 쿠폰 조회 (선택적)
        coupon = None
        if coupon_code:
            if not self.coupon_repository:
                raise CouponNotFoundException(coupon_code)
            
            coupon = await self.coupon_repository.find_by_code(coupon_code)
            if not coupon:
                raise CouponNotFoundException(coupon_code)
            
            # 쿠폰 유효성 검사
            now = datetime.now()
            if coupon.valid_from > now or coupon.valid_to < now:
                raise InvalidCouponException(coupon_code, "쿠폰 유효 기간이 만료되었습니다")
        
        return product, coupon
```

**특징**: Repository를 Protocol로 주입받아 의존성 역전, Cache-Aside 패턴으로 성능 최적화

### Mapper Pattern

Domain Model과 Infrastructure Model 간 변환을 담당합니다.

```11:20:app/infrastructure/mappers/product_mapper.py
    @staticmethod
    def to_domain(product_model: ProductModel) -> Product:
        """Infrastructure Model → Domain Model 변환"""
        return Product(
            id=product_model.id,
            name=product_model.name,
            price=product_model.price,
            stock=product_model.stock,
            category_id=product_model.category_id,
            discount_rate=product_model.discount_rate,
        )
```

**특징**: Domain Layer와 Infrastructure Layer의 결합도 감소, 도메인 모델의 순수성 유지

---

## 테스트

단위 테스트와 통합 테스트를 제공합니다. Domain Layer는 순수 Python 클래스이므로 Mock 없이 테스트 가능하며, Application Layer는 Repository를 Mock하여 테스트합니다.

### 단위 테스트 (Unit Tests)

**Domain Layer**:
- Domain Entity 테스트 (`tests/unit/domain/entities/`)
  - Product 엔티티 테스트
  - Coupon 엔티티 테스트
- Domain Service 테스트 (`tests/unit/domain/services/`)
  - PriceCalculator 서비스 테스트

**Application Layer**:
- Application Service 테스트 (`tests/unit/application/services/`)
  - ProductService 테스트
- API Mapper 테스트 (`tests/unit/application/mappers/`)
  - ProductApiMapper 테스트

### 통합 테스트 (Integration Tests)

**Application Layer**:
- API Router 테스트 (`tests/integration/application/routers/`)
  - Product API 엔드포인트 테스트

**Infrastructure Layer**:
- 데이터베이스 테스트 (`tests/integration/infrastructure/adapters/db/`)
  - 데이터베이스 연결 테스트
  - CRUD 작업 통합 테스트
- 캐시 테스트 (`tests/integration/infrastructure/adapters/cache/`)
  - Redis 연결 테스트

### 테스트 실행

```bash
# pytest를 사용하여 tests/ 디렉토리의 모든 테스트를 실행합니다.
make test
```
