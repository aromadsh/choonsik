# AWS 리소스 정리 체크리스트

## 1. 프로젝트 정보

- 프로젝트명: Codyssey AWS Cloud Deployment
- AWS 리전: ap-northeast-2 (Seoul)
- VPC: codyssey-vpc
- EC2: codyssey-web-server
- 정리 일시: 실제 완료 일시 기재

## 2. EC2 및 스토리지

- [ ] EC2 인스턴스 Terminated 확인
- [ ] 기존에 종료한 EC2 인스턴스 상태 확인
- [ ] 루트 EBS 볼륨 삭제 확인
- [ ] 미사용 EBS 볼륨 없음 확인
- [ ] 불필요한 EBS 스냅샷 없음 확인

## 3. 네트워크

- [ ] Elastic IP 할당 여부 확인 및 필요 시 해제
- [ ] NAT Gateway 생성 여부 확인 및 필요 시 삭제
- [ ] Load Balancer 생성 여부 확인 및 필요 시 삭제
- [ ] VPC Endpoint 생성 여부 확인 및 필요 시 삭제
- [ ] codyssey-web-sg 삭제 확인
- [ ] codyssey-public-rt 삭제 확인
- [ ] codyssey-igw 삭제 확인
- [ ] codyssey-public-subnet 삭제 확인
- [ ] codyssey-vpc 삭제 확인

## 4. 기타 리소스

- [ ] 실습용 EC2 Key Pair 정리
- [ ] RDS 생성 여부 확인 및 필요 시 삭제
- [ ] IAM 사용자 및 그룹, 정책 정리 여부 확인
- [ ] DuckDNS 도메인 유지 또는 삭제 여부 결정

## 5. 과금 확인

- [ ] 서울 리전의 실습용 잔여 리소스 없음 확인
- [ ] Billing Dashboard 확인
- [ ] 발생 비용 또는 잔여 청구 항목 기록

## 6. 증빙 자료

- EC2 종료: docs/screenshots/step10-cleanup/01-ec2-terminated.png
- EBS 정리: docs/screenshots/step10-cleanup/02-ebs-cleanup.png
- VPC 삭제: docs/screenshots/step10-cleanup/03-vpc-deleted.png
- Billing 확인: docs/screenshots/step10-cleanup/04-billing-check.png

## 7. 최종 결과

- 리소스 삭제 완료 여부: 확인 후 기재
- 잔여 과금 가능 리소스: 확인 후 기재
- Billing 확인 결과: 확인 후 기재
- 추가 조치 사항: 확인 후 기재