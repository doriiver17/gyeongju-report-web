# 수성구청 경주 현장체험 보고서

교육생이 조 정보, 방문지 3곳, 방문지별 인사이트 2개, 소감을 입력하고 사진을 첨부하면 기존 양식의 한 페이지 PDF를 다운로드합니다.

## 실행

Python 3.11 이상을 설치하고 프로젝트 폴더에서 아래 명령을 실행합니다.

```bash
python -m venv .venv
```

Windows:
```powershell
.venv\Scripts\Activate.ps1
```

macOS / Linux:
```bash
source .venv/bin/activate
```

```bash
pip install -r requirements.txt
python app.py
```

브라우저에서 http://localhost:5000 을 엽니다. 로컬 실행만으로는 교육생이 인터넷에서 접속할 수 없습니다.

## GitHub 업로드 (웹 화면)

1. ZIP 파일을 풀고 `gyeongju-report` 폴더를 엽니다.
2. GitHub 로그인 → 우측 상단 `+` → `New repository`.
3. Repository name에 `gyeongju-report` 입력 → `Create repository`.
4. 새 저장소의 `uploading an existing file` 또는 `Add file → Upload files`를 선택합니다.
5. 폴더 안의 `app.py`, `requirements.txt`, `render.yaml`, `README.md`, `assets`, `templates`를 드래그합니다. ZIP 자체를 업로드하지 않습니다.
6. `Commit changes`를 클릭합니다.
7. 저장소 최상위에 `app.py`가 보이는지 확인합니다. `gyeongju-report/app.py`처럼 한 단계 더 들어가면 배포 때 Root Directory를 지정해야 합니다.

`.gitignore`는 숨김 파일이라 웹에서 누락될 수 있습니다. 누락 시 `Add file → Create new file`로 `.gitignore`를 만들고 제공된 내용을 붙여넣습니다.

## Git 명령으로 업로드 (선택)

본인의 GitHub 저장소 주소로 마지막 URL을 바꿉니다.

```bash
git init
git add .
git commit -m "Create Gyeongju report PDF app"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/gyeongju-report.git
git push -u origin main
```

## Render 배포

1. Render 로그인 → `New → Web Service` → 위 GitHub 저장소 연결.
2. Runtime: Python.
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
5. 배포가 완료되면 제공되는 사이트 주소로 접속해 입력과 PDF 저장을 확인합니다.

`render.yaml`을 이용하는 Blueprint 배포도 가능합니다. 플랫폼 화면과 요금제는 변경될 수 있으므로 실제 화면 안내를 확인하세요. 이 패키지는 배포용 코드이며 실제 GitHub 업로드나 Render 배포는 아직 수행하지 않았습니다.

## 입력·출력 규칙

- 조 번호: 1~99. 숫자 폭을 측정해 괄호와 '조' 사이에 중앙 배치합니다.
- 입력 폰트: Pretendard Medium, 조 번호: ExtraBold. 물결표는 PDF 표시 호환성을 위해 표준 글리프로 출력합니다.
- 조 이름: 중앙 정렬. 조원 이름: 좌측·세로 중앙 정렬.
- 인사이트: 2개 불릿, 좌측·세로 중앙 정렬. 긴 내용은 자동 줄바꿈 및 제한 범위의 글씨 축소.
- 사진: JPG/PNG/WebP, 원본 비율 유지, EXIF 회전 반영. 3장 전체 요청 용량 30MB 이하. HEIC는 JPG로 변환 후 첨부.
- 소감: 좌측·세로 중앙 정렬, 긴 내용 자동 줄바꿈.
- 입력칸마다 남은 글자 수 표시. 서버에서도 제한 확인.
- 다운로드 파일명: `현장체험_보고서_15조_멍멍이냥냥이조.pdf`.
- 개인정보·사진은 디스크에 저장하지 않습니다. PDF 생성 중 서버 메모리에서만 처리합니다.
- 카카오톡 인앱 브라우저는 Chrome/Safari 이용 안내를 표시합니다.

현재 패키지는 **보고서 전용**입니다. 계획서 기능은 포함하지 않습니다.

## 파일 구조

- `app.py`: 입력 검증 및 PDF 생성
- `templates/index.html`: 모바일 입력 화면
- `assets/report.pdf`: 원본 보고서 양식
- `assets/Pretendard-*.otf`: 포함 폰트
- `requirements.txt`: 설치 의존성
- `render.yaml`: Render 배포 설정

Pretendard는 SIL Open Font License 1.1로 배포됩니다. 배포 시 함께 포함한 라이선스 고지를 유지하세요.
