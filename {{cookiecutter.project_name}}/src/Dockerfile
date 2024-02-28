# Python 이미지 사용
FROM python:3.9

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 Python 패키지 설치
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# 프로젝트 파일 복사
COPY . /app/

