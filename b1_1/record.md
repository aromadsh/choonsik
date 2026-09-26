# Portfolio Website

HTML CSS JavaScript를 활용하여 제작한 반응형 포트폴리오 웹사이트입니다.

프레임워크나 UI 라이브러리를 사용하지 않고 순수 HTML CSS JavaScript만으로 구현하여 DOM 조작 이벤트 처리 비동기 통신 상태 관리와 반응형 웹의 기본 원리를 학습하는 것을 목표로 제작했습니다.

## 주요 기능

### 반응형 웹

Mobile First 방식으로 구현했으며 768px과 1024px을 기준으로 레이아웃이 변경됩니다.

Navigation에는 Flexbox를 사용했으며 Projects 영역에는 CSS Grid의 auto-fit과 minmax를 적용해 화면 너비에 따라 프로젝트 카드의 열 개수가 자동으로 조정됩니다.

### Navigation

모바일 환경에서는 Hamburger Menu를 사용할 수 있습니다.

Navigation과 Hero 영역의 링크를 클릭하면 JavaScript의 scrollIntoView를 통해 각 Section으로 부드럽게 이동합니다.

### Scroll Interaction

300px 이상 스크롤하면 Scroll Top 버튼이 표시됩니다.

60px 이상 스크롤하면 Header의 배경과 그림자가 변경됩니다.

Intersection Observer를 활용하여 About Skills Projects Contact Section이 화면에 20퍼센트 이상 진입하면 등장 애니메이션이 실행됩니다.

Intersection Observer threshold는 0.2로 설정했습니다.

### Dark Mode

Light Mode와 Dark Mode를 전환할 수 있습니다.

선택한 Theme 상태는 localStorage에 저장되기 때문에 페이지를 새로고침한 이후에도 사용자가 선택한 Theme가 유지됩니다.

### Contact Form Validation

이름 이메일 메시지를 입력받습니다.

JavaScript를 통해 필수 입력 여부를 검사하며 이메일은 정규표현식을 사용하여 형식을 검증합니다.

입력값이 올바르지 않은 경우 각 입력 필드 아래에 오류 메시지를 표시합니다.

현재 Contact Form은 유효성 검증 기능을 구현한 것으로 실제 이메일 전송 기능은 포함하지 않습니다.

### GitHub API

GitHub REST API를 활용하여 사용자의 공개 Repository 데이터를 가져옵니다.

fetch와 async await을 사용해 비동기 요청을 처리하며 try catch와 response.ok를 사용해 오류를 처리합니다.

API 상태는 Loading Success Empty Error로 관리합니다.

API 요청에 실패하면 다시 시도 버튼을 제공합니다.

Fork Repository는 filter를 통해 제외하고 map을 사용하여 Repository 데이터를 Project Card HTML로 변환합니다.

## 사용 기술

HTML5

CSS3

JavaScript ES6+

Git

GitHub API

GitHub Pages

## JavaScript 주요 학습 내용

DOM 선택 및 조작

addEventListener

classList

textContent

innerHTML

Local Storage

Intersection Observer

Form Validation

Regular Expression

fetch

async await

try catch

Array forEach

Array map

Array filter

Object Destructuring

Template Literals

## 프로젝트 구조

```text
portfolio
├── index.html
├── README.md
├── css
│   └── style.css
├── js
│   └── script.js
└── images
    └── profile.png
```

## 이벤트와 상태 흐름

Theme

Click Event에서 Theme 상태를 변경하고 DOM과 localStorage에 반영합니다.

Contact Form

Input 또는 Submit Event에서 입력 상태와 오류 상태를 변경하고 검증 결과를 DOM에 렌더링합니다.

GitHub API

API 요청 전 Loading 상태로 변경하고 요청 결과에 따라 Success Empty Error 상태로 변경한 후 Projects 영역을 다시 렌더링합니다.

## 배포

GitHub Pages를 이용하여 배포했습니다.

배포 URL

YOUR_GITHUB_PAGES_URL

## Screenshot

### Desktop

추후 Desktop Screenshot 추가

### Mobile

추후 Mobile Screenshot 추가

### Dark Mode

추후 Dark Mode Screenshot 추가