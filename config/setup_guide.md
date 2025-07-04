# Claude Desktop 설정 가이드

Personal Info MCP Server를 Claude Desktop에 연결하는 방법

## 1. Claude Desktop 설치

1. [Claude Desktop 다운로드](https://claude.ai/download)
2. 운영체제에 맞는 버전 설치
3. Claude 계정으로 로그인

## 2. MCP 패키지 설치

터미널/명령 프롬프트에서 다음 명령어 실행:

```bash
cd C:/MyPython/mcpstudy
pip install -r mcp_server/requirements.txt
```

## 3. Claude Desktop 설정 파일 위치

### Windows
```
%APPDATA%\Claude\claude_desktop_config.json
```

### macOS
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

### Linux
```
~/.config/Claude/claude_desktop_config.json
```

## 4. 설정 파일 수정

1. Claude Desktop 종료
2. 위 경로의 `claude_desktop_config.json` 파일 열기 (command 부분에 MCP Server를 구동하기 위한 명령어를 써야함 -> bat 파일 이용)
3. 다음 내용으로 수정 (기존 내용이 있다면 `mcpServers` 섹션에 추가):

```json
{
  "mcpServers": {
    "personal-info": {
      "command": "command": "C:/MyPython/mcpstudy/run_mcp_server.bat",
      "args": ["C:/MyPython/mcpstudy/mcp_server/personal_info_server.py"],
      "env": {}
    }
  }
}
```

**주의**: `C:/MyPython/mcpstudy` 부분을 실제 프로젝트 경로로 수정

### 경로 확인 방법

현재 프로젝트 경로 확인:
```bash
cd mcpstudy
pwd  # macOS/Linux
cd   # Windows
```

## 5. Claude Desktop 재시작

설정 파일 수정 후 Claude Desktop을 완전히 종료하고 다시 시작

## 6. 테스트

Claude Desktop에서 다음과 같이 질문

```
OOO에 대해 알려줘
```

## 7. 문제 해결

가상환경 사용 시 claude_desktop_config.json 파일 작성 유의 -> command 부분에 MCP server를 구동하기 위한 bat 파일 경로 설정

## 8. 사용 예시

성공적으로 설정되면 다음과 같은 질문들 가능:

- "OOO에 대해 알려줘"
- "OOO의 취미는?"
- "OOO의 직업은?"
- "OOO의 특기는?"
- "등록된 사람들이 누구야?"

## 9. 데이터 추가 방법

새로운 인물 정보를 추가하려면:

1. `data/person_info.json` 파일 열기
2. JSON 형식에 맞춰 새로운 인물 정보 추가
3. 파일 저장
4. Claude Desktop에서 바로 사용 가능 (재시작 불필요) 