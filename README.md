# app_name_server

app_name의 서버 레포지토리입니다.

## 기술 스택

### Frontend

<img src="https://img.shields.io/badge/Flutter-02569B?style=for-the-badge&logo=Flutter&logoColor=white"> <img src="https://img.shields.io/badge/Dart-0175C2?style=for-the-badge&logo=Dart&logoColor=white"> <img src="https://img.shields.io/badge/Material Design-757575?style=for-the-badge&logo=Material-Design&logoColor=white">

### Backend

<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=Python&logoColor=white"> <img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=Django&logoColor=white"> <img src="https://img.shields.io/badge/Django Rest Framework-092E20?style=for-the-badge&logo=Django&logoColor=white">

<img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=PostgreSQL&logoColor=white"> <img src="https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=Redis&logoColor=white">

### InfraStructure

<img src="https://img.shields.io/badge/AWS-232F3E?style=for-the-badge&logo=Amazon AWS&logoColor=white"> <img src="https://img.shields.io/badge/NGINX-269539?style=for-the-badge&logo=NGINX&logoColor=white"> <img src="https://img.shields.io/badge/Gunicorn-342D7E?style=for-the-badge&logo=Gunicorn&logoColor=white"> <img src="https://img.shields.io/badge/Firebase-FFCA28?style=for-the-badge&logo=Firebase&logoColor=black">

<img src="https://img.shields.io/badge/AWS S3-569A31?style=for-the-badge&logo=Amazon AWS&logoColor=white">

### Project Management

<img src="https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=Git&logoColor=white"> <img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=GitHub&logoColor=white"> <img src="https://img.shields.io/badge/Notion-ffffff?style=for-the-badge&logo=Notion&logoColor=black">

## 설계

### WBS

### Requirements

#### Account Requirements

| Feature | Summary | Description | Type | Priority |
| --- | --- | --- | --- | --- |
| 회원가입 | 회원가입 | 사용자는 email과 password, username를 전달해 회원가입을 할 수 있다. | 기능 | 1 |
|| 회원가입 권한 확인 | 로그인하지 않은 사용자만 회원가입을 할 수 있다. | 비기능 | 2 |
|| email 중복 확인 | 중복된 email로 회원가입을 할 수 없다. | 기능 | 1 |
|| email 길이 제한 | email은 50자 이내로 입력해야 한다. | 비기능 | 2 |
|| email 형식 확인 | email 형식에 맞지 않는 email로 회원가입을 할 수 없다. | 비기능 | 3 |
|| password 길이 제한 | password는 8자 이상 20자 이하로 입력해야 한다. | 비기능 | 2 |
|| password 형식 확인 | password 형식에 맞지 않는 password로 회원가입을 할 수 없다. | 비기능 | 3 |
|| username 중복 확인 | 중복된 username으로 회원가입을 할 수 없다. | 기능 | 1 |
|| username 길이 제한 | username은 20자 이내로 입력해야 한다. | 비기능 | 2 |
|| username 형식 확인 | username 형식에 맞지 않는 username으로 회원가입을 할 수 없다. | 비기능 | 3 |
|| 회원가입 성공 | email, password, username을 모두 알맞게 입력하면 회원가입에 성공한다. | 기능 | 1 |
| 로그인 | 로그인 | 사용자는 email과 password를 전달해 로그인을 할 수 있다. | 기능 | 1 |
|| 로그인 실패 by wrong email | 등록되지 않은 email로 로그인을 할 수 없다. | 기능 | 1 |
|| 로그인 실패 by wrong password | 등록된 email과 일치하지 않는 password로 로그인을 할 수 없다. | 기능 | 1 |
|| 로그인 성공 | 등록된 email과 password가 일치하면 로그인에 성공한다. | 기능 | 1 |
|| 로그인 성공 시 JWT 발급 | 로그인에 성공하면 JWT 토큰을 발급받는다. | 기능 | 2 |
|| 토큰 보안 | JWT 토큰은 암호화되어야 한다. | 비기능 | 3 |
|| 토큰 만료 기한 | JWT 토큰은 60분 동안 유효하다. | 기능 | 2 |
|| 로그인 권한 확인 | 로그인하지 않은 사용자만 로그인을 할 수 있다. | 비기능 | 2 |
| 로그아웃 | 로그아웃 | 사용자는 로그아웃을 할 수 있다. | 기능 | 1 |
|| JWT 무효화 | 로그아웃 시 JWT 토큰을 무효화한다. | 기능 | 2 |
|| 로그아웃 권한 확인 | 로그인한 사용자만 로그아웃을 할 수 있다. | 기능 | 2 |
| 프로필 조회 | 자신 프로필 조회 | 로그인한 사용자는 자신의 프로필을 조회할 수 있다. | 기능 | 1 |
|| 프로필 페이지 접근 권한 확인 | 로그인한 사용자만 프로필 페이지에 접근할 수 있다. | 기능 | 1 |
|| 프로필 정보 변경 | 사용자는 자신의 프로필 정보를 변경할 수 있다. | 기능 | 1 |
|| 프로필 정보 변경 실패 by 중복 username | 사용자가 이미 등록된 username으로 프로필 정보를 변경하려 시도하면 실패한다. | 기능 | 1 |
|| 프로필 정보 변경 실패 by username 형식 | 사용자가 형식을 충족하지 않는 username으로 프로필 정보를 변경하려 시도하면 실패한다. | 기능 | 2 |
|| 프로필 정보 변경 실패 by username 길이 | 사용자가 일정 길이 이상의 username으로 프로필 정보를 변경하려 시도하면 실패한다. | 기능 | 2 |
|| 프로필 정보 변경 성공 | 사용자가 프로필 정보 변경 양식을 모두 만족한 상태로 프로필 정보를 변경하려 시도하면 성공한다. | 기능 | 1 |
| 비밀번호 찾기 | 비밀번호 찾기 | 사용자는 email을 전달해 비밀번호 재설정 링크를 받을 수 있다. | 기능 | 3 |
|| 비밀번호 재설정 요청 | 사용자는 비밀번호 재설정 페이지에서 새로운 비밀번호로 비밀번호 재설정 요청을 할 수 있다. | 기능 | 3 |
|| 비밀번호 재설정 실패 by pw 형식 | 사용자가 특정 형식을 충족하지 않는 비밀번호로 비밀번호 재설정을 시도했을 시 실패한다. | 기능 | 3 |
|| 비밀번호 재설정 실패 by pw 길이 | 사용자가 일정 길이 이상의 비밀번호로 비밀번호 재설정을 시도했을 시 실패한다. | 기능 | 3 |
|| 비밀번호 재설정 성공 | 사용자가 비밀번호 재설정 양식을 모두 만족한 상태로 비밀번호 재설정을 시도했을 시 성공한다. | 기능 | 3 |

#### Community Requirements

| Feature | Summary | Description | FunctionalType | Priority |
| --- | --- | --- | --- | --- |
| Post | 게시판 접근 | 사용자는 게시판에서 게시글들에 대한 정보를 확인할 수 있다. | 기능 | 1 |
| | 게시판 접근 권한 확인 | 로그인하지 않은 사용자도 게시판에 접근할 수 있다. | 비기능 | 2 |
| | 게시글 작성 | 사용자는 게시글을 작성할 수 있다. | 기능 | 1 |
| | 게시글 작성 권한 확인 | 로그인한 사용자만 게시글을 작성할 수 있다. | 비기능 | 2 |
| | 게시글 작성 실패 by title 길이 | 게시글의 제목은 50자 이내로 작성해야 한다. | 비기능 | 2 |
| | 게시글 작성 실패 by title 형식 | 게시글의 제목은 특정 형식을 충족해야 한다. | 비기능 | 3 |
| | 게시글 작성 실패 by content 길이 | 게시글의 내용은 6000자 이내로 작성해야 한다. | 비기능 | 2 |
| | 게시글 작성 실패 by content 형식 | 게시글의 내용은 특정 형식을 충족해야 한다. | 비기능 | 3 |
| | 게시글 작성 성공 | 게시글의 제목과 내용을 모두 알맞게 입력하면 게시글 작성에 성공한다. | 기능 | 1 |
| | 게시글 조회 | 사용자는 게시글을 조회할 수 있다. | 기능 | 1 |
| | 게시글 조회 권한 확인 | 로그인하지 않은 사용자도 게시글을 조회할 수 있다. | 비기능 | 2 |
| | 게시글 수정 | 사용자는 자신이 작성한 게시글을 수정할 수 있다. | 기능 | 1 |
| | 게시글 수정 권한 확인 | 로그인한 사용자만 자신이 작성한 게시글을 수정할 수 있다. | 비기능 | 2 |
| | 게시글 수정 실패 by title 길이 | 게시글의 제목은 50자 이내로 작성해야 한다. | 비기능 | 2 |
| | 게시글 수정 실패 by title 형식 | 게시글의 제목은 특정 형식을 충족해야 한다. | 비기능 | 3 |
| | 게시글 수정 실패 by content 길이 | 게시글의 내용은 6000자 이내로 작성해야 한다. | 비기능 | 2 |
| | 게시글 수정 실패 by content 형식 | 게시글의 내용은 특정 형식을 충족해야 한다. | 비기능 | 3 |
| | 게시글 수정 실패 by 타인 요청 | 타인이 작성한 게시글을 수정하려 시도하면 실패한다. | 기능 | 1 |
| | 게시글 수정 성공 | 게시글의 제목과 내용을 모두 알맞게 입력하면 게시글 수정에 성공한다. | 기능 | 1 |
| | 게시글 삭제 | 사용자는 자신이 작성한 게시글을 삭제할 수 있다. | 기능 | 1 |
| | 게시글 삭제 권한 확인 | 로그인한 사용자만 자신이 작성한 게시글을 삭제할 수 있다. | 비기능 | 2 |
| | 게시글 삭제 실패 by 타인 요청 | 타인이 작성한 게시글을 삭제하려 시도하면 실패한다. | 기능 | 1 |
| | 게시글 삭제 성공 | 자신이 작성한 게시글을 삭제하면 게시글 삭제에 성공한다. | 기능 | 1 |
| Comment | 댓글 목록 조회 | 사용자는 게시글에 작성된 댓글들을 조회할 수 있다. | 기능 | 1 |
| | 댓글 작성 | 사용자는 게시글에 댓글을 작성할 수 있다. | 기능 | 1 |
| | 댓글 작성 권한 확인 | 로그인한 사용자만 댓글을 작성할 수 있다. | 비기능 | 2 |
| | 댓글 작성 실패 by content 길이 | 댓글의 내용은 500자 이내로 작성해야 한다. | 비기능 | 2 |
| | 댓글 작성 실패 by content 형식 | 댓글의 내용은 특정 형식을 충족해야 한다. | 비기능 | 3 |
| | 댓글 작성 성공 | 댓글의 내용을 알맞게 입력하면 댓글 작성에 성공한다. | 기능 | 1 |
| | 댓글 수정 | 사용자는 자신이 작성한 댓글을 수정할 수 있다. | 기능 | 1 |
| | 댓글 수정 권한 확인 | 로그인한 사용자만 자신이 작성한 댓글을 수정할 수 있다. | 비기능 | 2 |
| | 댓글 수정 실패 by content 길이 | 댓글의 내용은 500자 이내로 작성해야 한다. | 비기능 | 2 |
| | 댓글 수정 실패 by content 형식 | 댓글의 내용은 특정 형식을 충족해야 한다. | 비기능 | 3 |
| | 댓글 수정 실패 by 타인 요청 | 타인이 작성한 댓글을 수정하려 시도하면 실패한다. | 기능 | 1 |
| | 댓글 수정 성공 | 댓글의 내용을 알맞게 입력하면 댓글 수정에 성공한다. | 기능 | 1 |
| | 댓글 삭제 | 사용자는 자신이 작성한 댓글을 삭제할 수 있다. | 기능 | 1 |
| | 댓글 삭제 권한 확인 | 로그인한 사용자만 자신이 작성한 댓글을 삭제할 수 있다. | 비기능 | 2 |
| | 댓글 삭제 실패 by 타인 요청 | 타인이 작성한 댓글을 삭제하려 시도하면 실패한다. | 기능 | 1 |
| | 댓글 삭제 성공 | 자신이 작성한 댓글을 삭제하면 댓글 삭제에 성공한다. | 기능 | 1 |
| SubComment | 대댓글 목록 조회 | 사용자는 댓글에 작성된 대댓글들을 조회할 수 있다. | 기능 | 1 |
| | 대댓글 작성 | 사용자는 댓글에 대댓글을 작성할 수 있다. | 기능 | 1 |
| | 대댓글 작성 권한 확인 | 로그인한 사용자만 대댓글을 작성할 수 있다. | 비기능 | 2 |
| | 대댓글 작성 실패 by content 길이 | 대댓글의 내용은 500자 이내로 작성해야 한다. | 비기능 | 2 |
| | 대댓글 작성 실패 by content 형식 | 대댓글의 내용은 특정 형식을 충족해야 한다. | 비기능 | 3 |
| | 대댓글 작성 성공 | 대댓글의 내용을 알맞게 입력하면 대댓글 작성에 성공한다. | 기능 | 1 |
| | 대댓글 수정 | 사용자는 자신이 작성한 대댓글을 수정할 수 있다. | 기능 | 1 |
| | 대댓글 수정 권한 확인 | 로그인한 사용자만 자신이 작성한 대댓글을 수정할 수 있다. | 비기능 | 2 |
| | 대댓글 수정 실패 by content 길이 | 대댓글의 내용은 500자 이내로 작성해야 한다. | 비기능 | 2 |
| | 대댓글 수정 실패 by content 형식 | 대댓글의 내용은 특정 형식을 충족해야 한다. | 비기능 | 3 |
| | 대댓글 수정 실패 by 타인 요청 | 타인이 작성한 대댓글을 수정하려 시도하면 실패한다. | 기능 | 1 |
| | 대댓글 수정 성공 | 대댓글의 내용을 알맞게 입력하면 대댓글 수정에 성공한다. | 기능 | 1 |
| | 대댓글 삭제 | 사용자는 자신이 작성한 대댓글을 삭제할 수 있다. | 기능 | 1 |
| | 대댓글 삭제 권한 확인 | 로그인한 사용자만 자신이 작성한 대댓글을 삭제할 수 있다. | 비기능 | 2 |
| | 대댓글 삭제 실패 by 타인 요청 | 타인이 작성한 대댓글을 삭제하려 시도하면 실패한다. | 기능 | 1 |
| | 대댓글 삭제 성공 | 자신이 작성한 대댓글을 삭제하면 대댓글 삭제에 성공한다. | 기능 | 1 |
| Like | 좋아요 | 사용자는 게시글과 댓글에 좋아요를 누를 수 있다. | 기능 | 1 |
| | 좋아요 권한 확인 | 로그인한 사용자만 좋아요를 누를 수 있다. | 비기능 | 2 |
| | 좋아요 실패 by 중복 요청 | 이미 좋아요를 누른 게시글이나 댓글에 다시 좋아요를 누르려 시도하면 실패한다. | 기능 | 2 |

#### MyHealthInfo Requirements

| Feature | Summary | Description | FunctionalType | Priority |
| --- | --- | --- | --- | --- |
| MyHealthInfo | 건강 정보 조회 | 사용자는 최근 1달간의 건강 정보를 조회할 수 있다. | 기능 | 1 |
| | 건강 정보 조회 권한 확인 | 로그인한 사용자만 건강 정보를 조회할 수 있다. | 비기능 | 2 |
| | 건강 정보 생성 | 사용자는 건강 정보를 생성할 수 있다. | 기능 | 1 |
| | 건강 정보 생성 권한 확인 | 로그인한 사용자만 건강 정보를 생성할 수 있다. | 비기능 | 2 |
| | 건강 정보 생성 실패 by weight | 사용자가 부적절한 몸무게로 건강 정보를 생성하려 시도하면 실패한다. | 비기능 | 2 |
| | 건강 정보 생성 실패 by height | 사용자가 부적절한 키로 건강 정보를 생성하려 시도하면 실패한다. | 비기능 | 2 |
| | 건강 정보 생성 실패 by age | 사용자가 부적절한 나이로 건강 정보를 생성하려 시도하면 실패한다. | 비기능 | 2 |
| | 건강 정보 생성 성공 | 사용자가 건강 정보 생성 양식을 모두 만족한 상태로 건강 정보를 생성하려 시도하면 성공한다. | 기능 | 1 |
| | 건강 정보 조회 | 사용자는 건강 정보를 조회할 수 있다. | 기능 | 1 |
| | 건강 정보 조회 권한 확인 | 로그인한 사용자만 건강 정보를 조회할 수 있다. | 비기능 | 2 |
| | 최근 건강 정보 조회 | 사용자는 가장 최근에 등록한 건강 정보를 조회할 수 있다. | 기능 | 1 |
| Diet | 식단 목록 조회 | 사용자는 최근 1달간의 식단을 조회할 수 있다. | 기능 | 1 |
| | 식단 목록 조회 권한 확인 | 로그인한 사용자만 식단을 조회할 수 있다. | 비기능 | 2 |
| | 식단 조회 | 사용자는 식단을 조회할 수 있다. | 기능 | 1 |
| | 식단 조회 권한 확인 | 로그인한 사용자만 식단을 조회할 수 있다. | 비기능 | 2 |
| | 식단 생성 | 사용자는 식단을 생성할 수 있다. | 기능 | 1 |
| | 식단 생성 권한 확인 | 로그인한 사용자만 식단을 생성할 수 있다. | 비기능 | 2 |
| | 식단 생성 실패 by content 길이 | 식단 메뉴 길이는 100자 이내로 작성해야 한다. | 비기능 | 2 |
| | 식단 생성 실패 by content 형식 | 식단 메뉴는 특정 형식을 충족해야 한다. | 비기능 | 3 |
| | 식단 생성 성공 | 사용자가 식단 생성 양식을 모두 만족한 상태로 식단을 생성하려 시도하면 성공한다. | 기능 | 1 |
| Routine | 루틴 목록 조회 | 사용자는 루틴 목록을 조회할 수 있다. | 기능 | 1 |
| | 루틴 목록 조회 권한 확인 | 로그인한 사용자만 루틴 목록을 조회할 수 있다. | 비기능 | 2 |
| | 루틴 생성 | 사용자는 루틴을 생성할 수 있다. | 기능 | 1 |
| | 루틴 생성 권한 확인 | 로그인한 사용자만 루틴을 생성할 수 있다. | 비기능 | 2 |
| | 루틴 생성 실패 by title 길이 | 루틴의 제목은 50자 이내로 작성해야 한다. | 비기능 | 2 |
| | 루틴 생성 실패 by title 형식 | 루틴의 제목은 특정 형식을 충족해야 한다. | 비기능 | 3 |
| | 루틴 좋아요 | 사용자는 루틴에 좋아요를 누를 수 있다. | 기능 | 1 |
| | 루틴 좋아요 권한 확인 | 로그인한 사용자만 루틴에 좋아요를 누를 수 있다. | 비기능 | 2 |
| | 루틴 좋아요 실패 by 중복 요청 | 이미 좋아요를 누른 루틴에 다시 좋아요를 누르려 시도하면 실패한다. | 기능 | 2 |
| | 루틴 좋아요 성공 | 좋아요를 누르지 않은 루틴에 좋아요를 누르면 좋아요 성공한다. | 기능 | 1 |
| WeeklyRoutine | 주간 루틴 목록 조회 | 사용자는 주간 루틴에서 주간 루틴을 조회할 수 있다. | 기능 | 1 |
| | 주간 루틴 목록 조회 권한 확인 | 로그인한 사용자만 주간 루틴 목록을 조회할 수 있다. | 비기능 | 2 |
| | 주간 루틴 조회 실패 by 타인 요청 | 타인이 작성한 주간 루틴을 조회하려 시도하면 실패한다. | 기능 | 1 |
| | 주간 루틴 생성 | 사용자는 주간 루틴을 생성할 수 있다. | 기능 | 1 |
| | 주간 루틴 생성 권한 확인 | 로그인한 사용자만 주간 루틴을 생성할 수 있다. | 비기능 | 2 |
| | 오늘의 루틴 조회 | 사용자는 주간 루틴에서 오늘의 루틴을 조회할 수 있다. | 기능 | 1 |
| | 오늘의 루틴 완료 | 사용자는 오늘의 루틴을 완료할 수 있다. | 기능 | 1 |
| | 오늘의 루틴 완료 권한 확인 | 로그인한 사용자만 오늘의 루틴을 완료할 수 있다. | 비기능 | 2 |
| | 오늘의 루틴 완료 실패 by 타인 요청 | 타인이 작성한 오늘의 루틴을 완료하려 시도하면 실패한다. | 기능 | 1 |

#### ExerciseInfo Requirements

| Feature | Summary | Description | FunctionalType | Priority |
| --- | --- | --- | --- | --- |
| Exercise | 운동 목록 조회 | 사용자는 운동 목록을 조회할 수 있다. | 기능 | 1 |
| | 운동 목록 조회 권한 확인 | 로그인하지 않은 사용자도 운동 목록을 조회할 수 있다. | 비기능 | 2 |
| | 운동 조회 | 사용자는 특정 운동을 조회할 수 있다. | 기능 | 1 |
| | 운동 조회 권한 확인 | 로그인하지 않은 사용자도 특정 운동을 조회할 수 있다. | 비기능 | 2 |
| | 운동 생성 | 관리자만 운동을 생성할 수 있다. | 기능 | 1 |
| | 운동 생성 실패 by title 길이 | 운동의 제목은 50자 이내로 작성해야 한다. | 비기능 | 2 |
| | 운동 생성 실패 by title 형식 | 운동의 제목은 특정 형식을 충족해야 한다. | 비기능 | 3 |
| | 운동 생성 실패 by content 길이 | 운동의 내용은 1000자 이내로 작성해야 한다. | 비기능 | 2 |
| | 운동 생성 실패 by content 형식 | 운동의 내용은 특정 형식을 충족해야 한다. | 비기능 | 3 |
| | 운동 생성 성공 | 관리자가 운동 생성 양식을 모두 만족한 상태로 운동을 생성하려 시도하면 성공한다. | 기능 | 1 |
| | 운동 수정 | 관리자만 운동을 수정할 수 있다. | 기능 | 1 |
| | 운동 수정 실패 by title 길이 | 운동의 제목은 50자 이내로 작성해야 한다. | 비기능 | 2 |
| | 운동 수정 실패 by title 형식 | 운동의 제목은 특정 형식을 충족해야 한다. | 비기능 | 3 |
| | 운동 수정 실패 by content 길이 | 운동의 내용은 1000자 이내로 작성해야 한다. | 비기능 | 2 |
| | 운동 수정 실패 by content 형식 | 운동의 내용은 특정 형식을 충족해야 한다. | 비기능 | 3 |
| | 운동 수정 성공 | 관리자가 운동 수정 양식을 모두 만족한 상태로 운동을 수정하려 시도하면 성공한다. | 기능 | 1 |
| | 운동 삭제 | 관리자만 운동을 삭제할 수 있다. | 기능 | 1 |

### Url Spec

#### App

| App Name | URL | Description |
| --- | --- | --- |
| home | "" | 홈 화면 |
| account | "account/" | 계정 관련 |
| my_health_info | "my-health-info/" | 건강 정보 |
| exercises_info | "exercises-info/" | 운동 정보 |
| community | "community/" | 커뮤니티 |

#### Account App

| URL | Method | Description | Permission |
| --- | --- | --- | --- |
| "register/" | POST | 회원가입 | AllowAny |
| "login/" | POST | 로그인 | AllowAny |
| "logout/" | POST | 로그아웃 | IsAuthenticated |
| "profile/<int:pk>/" | GET | 프로필 조회 | IsAuthenticated |
| "profile/<int:pk>/" | PATCH | 프로필 수정 | IsAuthenticated |
| "deletion/" | DELETE | 회원 탈퇴 | IsAuthenticated |
| "password-reset/<str:email> | POST | 비밀번호 재설정 | AllowAny |

#### MyHealthInfo App

| URL | Method | Description | Permission |
| --- | --- | --- | --- |
| "my-health-info/" | GET | 최근 1달간의 건강정보 조회 | IsAuthenticated |
| "my-health-info/" | POST | 건강정보 생성 | IsAuthenticated |
| "my-health-info/<int:pk>/" | GET | 건강정보 조회 | IsAuthenticated |
| "diets/" | GET | 최근 1달간의 식단 조회 | IsAuthenticated |
| "diets/" | POST | 식단 생성 | IsAuthenticated |
| "diets/<int:pk>/" | GET | 식단 조회 | IsAuthenticated |
| "user_routines/" | GET | 사용자 루틴 조회 | IsAuthenticated |
| "user_routines/" | POST | 사용자 루틴 생성 | IsAuthenticated |
| "user_routines/streak/" | GET | 사용자 루틴 스트릭 조회 | IsAuthenticated |
| "routine/" | GET | 루틴 목록 조회 | IsAuthenticated |
| "routine/" | POST | 루틴 생성 | IsAuthenticated |
| "routine/<int:pk>/" | GET | 루틴 조회 | IsAuthenticated |
| "routine/<int:pk>/" | PATCH | 루틴 수정 | IsAuthenticated |
| "routine/<int:pk>/" | DELETE | 루틴 삭제 | IsAuthenticated |
| "weekly_routine/" | GET | 주간 루틴 목록 조회 | IsAuthenticated |
| "weekly_routine/" | POST | 주간 루틴 생성 | IsAuthenticated |
| "weekly_routine/" | PATCH | 주간 루틴 수정 | IsAuthenticated |
| "weekly_routine/" | DELETE | 주간 루틴 삭제 | IsAuthenticated |
| "weekly_routine/today/" | GET | 오늘의 루틴 조회 | IsAuthenticated |
| "weekly_routine/today/" | POST | 오늘의 루틴 완료 | IsAuthenticated |

#### ExerciseInfo App

| URL | Method | Description | Permission |
| --- | --- | --- | --- |
| "exercises/" | GET | 운동 목록 조회 | AllowAny |
| "exercises/" | POST | 운동 생성 | IsAdminUser |
| "exercises/<int:pk>/" | GET | 운동 조회 | AllowAny |
| "exercises/<int:pk>/" | PATCH | 운동 수정 | IsAdminUser |
| "exercises/<int:pk>/" | DELETE | 운동 삭제 | IsAdminUser |

#### Community App

| URL | Method | Description | Permission |
| --- | --- | --- | --- |
| "posts/" | GET | 게시글 목록 조회 | AllowAny |
| "posts/" | POST | 게시글 생성 | IsAuthenticated |
| "posts/<int:pk>/" | GET | 게시글 조회 | AllowAny |
| "posts/<int:pk>/" | PATCH | 게시글 수정 | IsAuthenticated |
| "posts/<int:pk>/" | DELETE | 게시글 삭제 | IsAuthenticated |
| "posts/?q=title:<str:title>" | GET | 게시글 검색 | AllowAny |
| "posts/?q=author=<str:author>" | GET | 게시글 작성자 검색 | AllowAny |

### Diagrams

#### Entity-Relationship Diagram

```mermaid
erDiagram
    %% 효준
    User {
        int id PK
        str email UK
        str user_name UK
        str password
        int recent_health_info_id FK
        datetime created_at
        datetime updated_at
        bool is_deleted "retrieve 하실때 주의!"
    }

    %% 지석
    HealthInfo {
        int id PK
        int user_id FK
        float weight
        float height
        int age
        float bmi
        datetime created_at
    }

    Routine {
        int id PK
        int creator_id FK
        str routine_name
    }

    RoutineLike {
        int id PK
        int user_id FK
        int routine_id FK
        datetime created_at
    }

    Routine ||--o{ RoutineLike : has

    RoutineStreak {
        int id PK
        int routine_id FK
        int user_id FK
        datetime created_at
        bool is_routine_completed
    }

    User ||--|{ RoutineStreak : has
    Routine ||--o{ RoutineStreak : has

    UsersRoutine {
        int id PK
        int user_id FK
        int routine_id FK
    }

    WeeklyRoutine {
        int id PK
        int user_id FK
        int day_index
        int routine_id FK
    }

    %% 빈
    Exercise {
        int id PK
        str name
        str intensity
        str description
        str video_url
    }

    ExerciseFocusArea {
        int id PK
        int exercise_id FK
        int focus_area_id FK
    }

    FocusArea {
        int id PK
        str name
    }

    Exercise ||--o{ ExerciseFocusArea : has
    FocusArea ||--o{ ExerciseFocusArea : has

    ExerciseAttribute {
        int id PK
        int exercise_id FK
        bool need_set
        bool need_rep
        bool need_weight
        bool need_speed
        bool need_duration
    }

    Exercise ||--o{ ExerciseAttribute : has
    Exercise ||--o{ ExerciseFocusArea : has

    %% 지석

    ExerciseInRoutine {
        int id PK
        int routine_id FK
        int exercise_id FK
    }

    ExerciseInRoutine ||--o{ Exercise : has

    ExerciseInRoutinesAttribute {
        int id PK
        int exercise_in_routine_id FK
        int set
        int rep
        float weight
        float speed
        int duration_sec
    }

    ExerciseInRoutine ||--o{ ExerciseInRoutinesAttribute : has

    %% 수현
    Post {
        int id PK
        int user_id FK
        str title
        str content
        int view_count
        int like_count
        datetime created_at
        datetime updated_at
        bool is_deleted "list retrieve 하실때 주의!"
    }

    Comment {
        int id PK
        int post_id FK
        int user_id FK
        str content
        datetime created_at
        bool is_deleted "list retrieve 하실때 주의!"
    }

    SubComment {
        int id PK
        int comment_id FK
        int user_id FK
        str content
        datetime created_at
        bool is_deleted "list retrieve 하실때 주의!"
    }

    Like {
        int id PK
        int user_id FK
        int post_id FK
        datetime created_at
    }

    Post ||--o{ Like : has

    User ||--o{ HealthInfo : has
    User ||--o{ WeeklyRoutine : plans
    User ||--o{ Post : writes
    User ||--o{ Comment : writes
    User ||--o{ SubComment : writes
    User ||--o{ UsersRoutine : subscribes
    UsersRoutine ||--o{ Routine : subscribed
    Routine ||--o{ ExerciseInRoutine : has
    WeeklyRoutine }|--o{ Routine : uses
    Post ||--o{ Comment : has
    Comment ||--o{ SubComment : has
```
