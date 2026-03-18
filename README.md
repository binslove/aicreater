# AI Creator Backend

AI 기반 콘텐츠 생성 플랫폼의 백엔드 서버입니다.  
이미지 생성 작업(Job) 관리와 미디어 자산(MediaAsset) 저장을 담당합니다.

---

# 1. 핵심 개념

이 서버는 다음 구조로 동작합니다:


Frontend → Backend → Model (ComfyUI 등)
↓
Frontend ← Backend ← Model 결과


---

# 2. 전체 흐름 (중요)


프론트 → 이미지 생성 요청
POST /image-jobs

백엔드 → job 생성 (status = queued)

모델 서버 → job 처리 시작
PATCH /image-jobs/{job_id} (status = running)

모델 → 이미지 생성 + 스토리지 업로드

모델 → 결과 전송
PATCH /image-jobs/{job_id} (status = completed + output_payload)

백엔드 → media_meta 자동 생성

프론트 → 결과 조회
GET /media/project/{project_id}

프론트 → 이미지 렌더링 (public_url)


---

# 3. 인증 방식

모든 요청은 JWT 인증 필요


Authorization: Bearer {ACCESS_TOKEN}


---

# 4. API 명세

---

## 4.1 이미지 생성 Job 생성

### POST /image-jobs

```json
{
  "project_id": "PROJECT_UUID",
  "prompt": "cyberpunk girl",
  "negative_prompt": "blurry",
  "width": 512,
  "height": 512
}
Response
{
  "id": "JOB_UUID",
  "status": "queued",
  "input_payload": {
    "prompt": "cyberpunk girl",
    "width": 512,
    "height": 512
  }
}
4.2 Job 상태 조회
GET /image-jobs/{job_id}
{
  "id": "JOB_UUID",
  "status": "running | completed | failed",
  "output_payload": {...}
}
4.3 Job 상태 변경 (모델 서버 전용)
PATCH /image-jobs/{job_id}
▶ running 상태
{
  "status": "running"
}

자동 동작:

started_at 기록됨

▶ completed 상태 
{
  "status": "completed",
  "output_payload": {
    "filename": "sample.png",
    "storage_path": "generated/2026/03/sample.png",
    "public_url": "https://example.com/sample.png",
    "content_type": "image/png",
    "storage_provider": "firebase",
    "width": 512,
    "height": 512
  }
}

자동 동작:

✔ output_payload 저장
✔ completed_at 기록
✔ media_meta 자동 생성
✔ job_id로 media 연결
▶ failed 상태
{
  "status": "failed",
  "error_message": "generation failed"
}
5. Model Integration Guide

모델 서버는 아래 규칙을 반드시 따라야 합니다.

5.1 해야 할 일
1. job 생성됨 (queued)
2. 모델 서버가 job 처리 시작
3. PATCH → running
4. 이미지 생성
5. 스토리지 업로드
6. public URL 확보
7. PATCH → completed
5.2 반드시 맞춰야 하는 output_payload 형식
{
  "filename": "string",
  "storage_path": "string",
  "public_url": "string",
  "content_type": "image/png",
  "storage_provider": "firebase",
  "width": 512,
  "height": 512
}

⚠️ 이 형식이 틀리면:

media 생성 실패
프론트에서 결과 안 보임
5.3 예시 흐름
PATCH /image-jobs/{job_id}

{
  "status": "running"
}

→ 이미지 생성

PATCH /image-jobs/{job_id}

{
  "status": "completed",
  "output_payload": {...}
}
6. Frontend Integration Guide
6.1 프론트 흐름
1. POST /image-jobs
2. job_id 받기
3. polling (GET /image-jobs/{job_id})
4. status == completed
5. GET /media/project/{project_id}
6. public_url로 이미지 렌더링
6.2 polling 예시
setInterval(async () => {
  const job = await getJob(jobId)

  if (job.status === "completed") {
    const media = await getMedia(projectId)
    render(media)
  }
}, 2000)
7. Media 조회
GET /media/project/{project_id}
{
  "items": [
    {
      "id": "...",
      "public_url": "https://...",
      "width": 512,
      "height": 512
    }
  ]
}
8. 데이터 구조 요약
Job
status:
- queued
- running
- completed
- failed
MediaAsset
job_id → 어떤 job 결과인지 연결됨
public_url → 프론트 렌더링용
storage_path → 내부 저장 위치
9. 환경 변수

.env 파일 생성:

DATABASE_URL=
SECRET_KEY=
ACCESS_TOKEN_EXPIRE_MINUTES=60

# optional
COMFYUI_BASE_URL=
STORAGE_PROVIDER=

10. 실행 방법
venv\Scripts\activate
uvicorn app.main:app --reload

