# Media Kit Search API

한국 매체사의 미디어킷 및 광고 자료를 검색하는 API입니다.

## 주요 기능

- 한국 매체사 이름을 입력받아 공식 홈페이지에서 미디어킷, 광고상품 소개서 등을 검색
- Firecrawl API를 사용하여 실제 웹페이지 콘텐츠 탐색
- OpenAI o3 모델을 사용한 지능형 검색 및 검증
- FastAPI 기반 REST API 제공

## 설치 방법

1. 의존성 설치:
```bash
pip install -r requirements.txt
```

2. 환경 변수 설정:
```bash
cp .env.example .env
# .env 파일을 열어 OPENAI_API_KEY를 설정하세요
```

3. 서버 실행:
```bash
python main.py
```

서버는 http://localhost:8000 에서 실행됩니다.

## API 사용법

### 미디어킷 검색

**Endpoint:** `POST /search`

**Request Body:**
```json
{
  "media_name": "중앙일보"
}
```

**Response:**
```json
{
  "result": {
    "중앙일보": "https://ad.joongang.co.kr/intro/service/mediakit.do"
  }
}
```

또는 찾을 수 없는 경우:
```json
{
  "result": {
    "없는신문": "찾을 수 없음"
  }
}
```

### 예제 사용법 (curl)

```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"media_name": "중앙일보"}'
```

### 예제 사용법 (Python)

```python
import requests

response = requests.post(
    "http://localhost:8000/search",
    json={"media_name": "중앙일보"}
)

print(response.json())
```

## API 문서

서버 실행 후 다음 URL에서 자동 생성된 API 문서를 확인할 수 있습니다:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 주의사항

- OpenAI API 키가 필요합니다 (o3 모델 사용)
- Firecrawl API 키는 기본값이 제공되지만, 자체 키 사용을 권장합니다
- 검색 결과는 매체사 공식 홈페이지의 실제 콘텐츠를 기반으로 합니다