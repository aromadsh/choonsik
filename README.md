git
버전 관리 시스템 (Version Contral System)
과거 버전을 Save point로 하여 언제든 접속 가능하도록

CLI : Command Line Interface (명령어 기반)
GUI : Graphical User Interface (그래픽 기반)


git에 올리지 않아도 되는 파일
dist(컴파일 과정중 생성되는 파일) / 배포용 / 실행 파일 / 라이브러리 파일 / 저장파일 / 디비

gitignore : Untracked file에서 제외
- 디렉토리: 폴더명/
- 파일명 기준 : 파일명.*  (와일드 카드로 확장자 상관없이 관련 파일명은 모두 제외)
- 파일 기준 : test.py

git add (스테이징에 올리는 명령어)
. 해당 경로의 모든 파일 / 특정파일 명과 확장자

git commit (버전화 및 저장)
-m 커밋 메시지

git status : Untracked file 과 add 한 파일 확인

git log : 커밋한 파일 확인 (해시코드가 있음)