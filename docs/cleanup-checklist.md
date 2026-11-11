
# AWS 리소스 정리 체크리스트

## 1. 실습 정보

- 프로젝트: Codyssey AWS Cloud Deployment
- 리전: ap-northeast-2 (Seoul)
- VPC: codyssey-vpc
- EC2: codyssey-web-server
- 정리 예정일: 보너스 과제 완료 후

## 2. 리소스 정리 확인

아래 항목은 실제 삭제를 확인한 뒤 체크합니다.

### 컴퓨팅

- [ ] EC2 인스턴스 Terminated 확인
- [ ] 불필요한 추가 EC2 인스턴스 없음

### 스토리지

- [ ] 사용하지 않는 EBS 볼륨 삭제 확인
- [ ] EC2 루트 EBS 볼륨 삭제 확인
- [ ] 불필요한 EBS 스냅샷 확인

### 네트워크

- [ ] Elastic IP 할당 여부 확인 및 필요 시 해제
- [ ] NAT Gateway 생성 여부 확인 및 필요 시 삭제
- [ ] Load Balancer 생성 여부 확인 및 필요 시 삭제
- [ ] Security Group 삭제 확인
- [ ] 사용자 지정 Route Table 삭제 확인
- [ ] Internet Gateway 연결 해제 및 삭제 확인
- [ ] Public Subnet 삭제 확인
- [ ] VPC 삭제 확인

### 기타

- [ ] RDS 생성 여부 확인 및 필요 시 삭제
- [ ] 실습용 EC2 Key Pair 삭제 확인
- [ ] 불필요한 실습용 IAM 권한 정리 여부 확인

### 비용

- [ ] 서울 리전 잔여 리소스 확인
- [ ] Billing Dashboard 확인
- [ ] 비용 및 잔여 과금 가능 항목 기록

## 3. 정리 결과

- 정리 작업 일시:
- 남아 있는 리소스:
- 비용 확인 결과:
- 추가 조치 사항:

## 4. 최종 확인

모든 리소스에 대해 종료 및 삭제 여부를 검증하고,
실습 환경에 불필요한 과금 리소스가
남지 않았는지 확인합니다.
