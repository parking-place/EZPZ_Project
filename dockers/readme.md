# Dockerfiles

## Docker Hub
- [Docker Hub](https://hub.docker.com/repositories/parkingplace) - parkingplace 도커 허브

## Dockerfile
- [ezpz_base](./Dockerfile.base) - 베이스 이미지
- [ezpz_web](./Dockerfile.web) - 웹(장고) 이미지(amd64)
- [ezpz_web:arm](./Dockerfile.web.arm) - 웹(장고) 이미지(arm64)
- [ezpz_torch](./Dockerfile.torch) - 토치/크롤러 이미지(amd64)
- [ezpz_torch:arm](./Dockerfile.torch.arm) - 토치/크롤러 이미지(arm64)

## Docker 관련 문서
- [도커 이미지 풀/푸시 및 컨테이너 실행](./docker.ipynb) - 명령어 및 사용설명 문서

## Docker image change log
<details>
<summary> 1.0 </summary>

<!-- summary 아래 한칸 공백 두어야함 -->
- 이미지 빌드
</details>

<details>
<summary> 1.0.1 </summary>

<!-- summary 아래 한칸 공백 두어야함 -->
- 기존 이미지에 필요 패키지 설치
</details>

<details>
<summary> 1.0.2 </summary>

<!-- summary 아래 한칸 공백 두어야함 -->
- arm64 이미지 추가
</details>