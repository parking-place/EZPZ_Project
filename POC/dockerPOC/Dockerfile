# 작업 환경 깡통 이미지

# 베이스 이미지 설정
FROM ubuntu:22.04

# 기본 환경 설치 명령어
RUN apt-get update && apt-get install -y python3.10 python3-pip

# openssh 서버 설치
RUN apt-get install -y openssh-server

# git 설치
RUN apt-get install -y git

# vim 설치
RUN apt-get install -y vim

# # pkg-config 설치
RUN apt-get install -y pkg-config && \
apt-get install -y libcairo2-dev && \
apt-get install -y libgirepository1.0-dev

# cuda 지원 pytorch 설치
RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 장고 설치
RUN pip3 install django && pip3 install djangorestframework

# # 작업 디렉토리 생성
RUN mkdir -p /home/workspaces

# # 작업 디렉토리 설정
WORKDIR /home/workspaces

# # requirements_docker.txt 복사
COPY requirements_docker.txt /home/workspaces

# # requirements_docker.txt 설치
RUN pip3 install -r requirements_docker.txt

# 크롬 설치
RUN apt-get install wget -y
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
RUN apt-get update -y && apt-get install google-chrome-stable -y
RUN wget http://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_114.0.5735.198-1_amd64.deb && \
dpkg -i google-chrome-stable_114.0.5735.198-1_amd64.deb && \
apt-mark hold google-chrome-stable