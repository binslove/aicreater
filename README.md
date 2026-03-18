
# AI Creator Backend

AI 기반 콘텐츠 생성 플랫폼의 백엔드 서버입니다.  
사용자 인증, 프로젝트 관리, 작품(Media) 관리, 좋아요, 댓글, 조회수 통계 기능을 제공합니다.

---

## 1. 프로젝트 개요

이 프로젝트는 AI로 생성되는 이미지/콘텐츠를 저장하고, 사용자들이 작품에 대해 상호작용할 수 있도록 설계된 백엔드 서버입니다.

현재 구현된 핵심 목표는 다음과 같습니다.

- JWT 기반 로그인/인증
- 프로젝트 단위 작업 관리
- 작품(Media) 메타데이터 저장
- 작품 설명 / 공개 여부 관리
- 좋아요 / 댓글 기능
- 조회수 및 통계 집계

---

## 2. 기술 스택

- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- JWT Authentication
- Passlib (bcrypt)
- Uvicorn
- Docker

---

## 3. 현재 구현된 기능

### 3.1 인증
- 회원가입
- 로그인
- JWT 토큰 발급
- `/auth/me`를 통한 현재 사용자 조회
- 인증 기반 API 접근 제어

### 3.2 프로젝트 관리
- 프로젝트 생성
- 프로젝트 조회
- 프로젝트별 작품 관리 기반 구조

### 3.3 작품(Media) 관리
- 작품 메타데이터 저장
- 작품 제목(title) 저장
- 작품 설명(description) 저장
- 공개 여부(visibility) 저장
- 프로젝트별 작품 조회
- 작품 상세 조회

### 3.4 좋아요
- 작품 좋아요 추가
- 작품 좋아요 취소
- 작품 좋아요 수 조회
- 인증 사용자 기준 처리

### 3.5 댓글
- 댓글 작성
- 댓글 목록 조회
- 댓글 수정
- 댓글 삭제
- soft delete 적용
- 본인 댓글만 수정/삭제 가능

### 3.6 통계(Media Stats)
- 조회수(view_count)
- 좋아요 수(like_count)
- 댓글 수(comment_count)
- 북마크 수(bookmark_count)
- 작품 상세 조회 시 조회수 증가
- 좋아요/댓글 변경 시 통계 반영

---

## 4. 프로젝트 구조

```text
backend/
├── app/
│   ├── api/
│   │   ├── deps.py
│   │   └── routes/
│   │       ├── auth.py
│   │       ├── users.py
│   │       ├── projects.py
│   │       ├── media.py
│   │       ├── artwork_likes.py
│   │       ├── comments.py
│   │       ├── follow.py
│   │       └── image_jobs.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── job_constants.py
│   │
│   ├── crud/
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── project.py
│   │   ├── media.py
│   │   ├── artwork_like.py
│   │   ├── comment.py
│   │   ├── follow.py
│   │   └── image_job.py
│   │
│   ├── db/
│   │   ├── database.py
│   │   └── models.py
│   │
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── project.py
│   │   ├── media.py
│   │   ├── artwork_like.py
│   │   ├── comment.py
│   │   ├── follow.py
│   │   └── image_job.py
│   │
│   ├── services/
│   │   ├── image_generation_service.py
│   │   ├── comfyui/
│   │   │   ├── client.py
│   │   │   └── workflow_builder.py
│   │   └── storage/
│   │       ├── base.py
│   │       ├── factory.py
│   │       └── local_storage.py
│   │
│   └── main.py
│
├── alembic/
├── .env
├── .gitignore
└── README.md
