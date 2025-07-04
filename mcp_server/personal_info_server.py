#!/usr/bin/env python3
"""
Personal Info MCP Server
Claude Desktop에서 개인 정보를 조회할 수 있는 MCP Server
"""

import json
import os
import logging
import re
from pathlib import Path
from typing import Dict, Any, Optional

# MCP 라이브러리가 없는 경우를 대비한 기본 구현
try:
    from mcp.server.fastmcp import FastMCP
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("Warning: MCP library not found. Please install: pip install mcp fastmcp")

# 해당 MCP Server는 내 로컬 컴퓨터에서 구동됨 -> Claude Desktop이 subprocess로 실행
# 부모 프로세스인 Claude Desktop이 종료되면 자식 프로세스인 personal_info_server.py 서버도 함께 종료됨

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PersonalInfoServer:
    def __init__(self):
        """개인 정보 서버 초기화"""
        self.data_file = self._get_data_file_path()
        self.person_data = self._load_person_data()
        logger.info(f"Personal Info Server 초기화 완료. 데이터 파일: {self.data_file}")
        
    def _get_data_file_path(self) -> Path:
        """데이터 파일 경로 찾기"""
        # 현재 스크립트 위치에서 상대 경로로 데이터 파일 찾기
        current_dir = Path(__file__).parent
        data_file = current_dir.parent / "data" / "person_info.json"
        return data_file
    
    def _load_person_data(self) -> Dict[str, Any]:
        """JSON 파일에서 개인 정보 데이터 로드"""
        try:
            if not self.data_file.exists():
                logger.error(f"데이터 파일을 찾을 수 없습니다: {self.data_file}")
                return {}
            
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"데이터 로드 완료: {len(data)}명의 정보")
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 오류: {e}")
            return {}
        except Exception as e:
            logger.error(f"데이터 로드 실패: {e}")
            return {}
    
    def extract_person_name(self, query: str) -> Optional[str]:
        """사용자 질문에서 인물명 추출"""
        # 다양한 질문 패턴에서 이름 추출 (정규표현식)
        patterns = [
            r"[\"']([^\"']+)[\"']에?\s*대해",  # "OOO"에 대해
            r"([가-힣]{2,4})에?\s*대해",      # OOO에 대해
            r"([가-힣]{2,4})의?\s*",         # OOO의, OOO
            r"([가-힣]{2,4})는?\s*",         # OOO는, OOO은
            r"([가-힣]{2,4})이?\s*",         # OOO이
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                name = match.group(1) # 괄호 안의 문자열 추출 -> 이름 추출
                if name in self.person_data:
                    return name
        
        # 직접적인 이름 매칭
        for name in self.person_data.keys():
            if name in query:
                return name
        
        return None
    
    def get_person_info(self, query: str) -> str:
        """개인 정보 조회 및 자연어 응답 생성"""
        try:
            # 인물명 추출
            person_name = self.extract_person_name(query)
            
            # 등록된 인물명이 없으면 Claude가 일반적인 답변을 하도록 유도
            if not person_name:
                return "NO_REGISTERED_PERSON_FOUND"
            
            person_info = self.person_data.get(person_name)
            if not person_info:
                return "NO_REGISTERED_PERSON_FOUND"
            
            # 자연어 응답 생성
            response = self._format_person_info(person_name, person_info, query)
            return response
            
        except Exception as e:
            logger.error(f"정보 조회 중 오류: {e}")
            return "NO_REGISTERED_PERSON_FOUND"
    
    def _format_person_info(self, name: str, info: Dict[str, Any], query: str) -> str:
        """개인 정보를 자연어로 포맷팅"""
        response_parts = []
        
        # 인사말
        response_parts.append(f"{name}님에 대해 알려드릴게요!\n")
        
        # 기본 정보
        if "기본정보" in info:
            basic_info = info["기본정보"]
            response_parts.append("**기본 정보**")
            for key, value in basic_info.items():
                emoji_map = {
                    "나이": "🎂",
                    "직업": "💼", 
                    "회사": "🏢",
                    "학력": "🎓",
                    "경력": "⏰"
                }
                emoji = emoji_map.get(key, "•")
                response_parts.append(f"  {emoji} {key}: {value}") # 매핑된 이모지 사용
            response_parts.append("")
        
        # 특정 키워드가 포함된 경우 해당 정보만 표시
        if "취미" in query and "취미" in info:
            response_parts.append("**취미**")
            for hobby in info["취미"]:
                response_parts.append(f"  • {hobby}")
            response_parts.append("")
        elif "특기" in query and "특기" in info:
            response_parts.append("**특기**")
            for skill in info["특기"]:
                response_parts.append(f"  • {skill}")
            response_parts.append("")
        elif "직업" in query or "업무" in query:
            if "업무" in info:
                work_info = info["업무"]
                response_parts.append("**업무 정보**")
                for key, value in work_info.items():
                    if isinstance(value, list):
                        value = ", ".join(value)
                    response_parts.append(f"  • {key.replace('_', ' ')}: {value}")
                response_parts.append("")
        else:
            # 전체 정보 표시
            for section_key, section_data in info.items():
                if section_key == "기본정보":
                    continue  # 이미 표시됨
                
                section_emoji = {
                    "취미": "🎨",
                    "특기": "⭐",
                    "성격": "😊",
                    "최근근황": "📈",
                    "목표": "🎯",
                    "연락처": "📞",
                    "업무": "💼"
                }.get(section_key, "📝")
                
                response_parts.append(f"{section_emoji} **{section_key}**")
                
                if isinstance(section_data, list):
                    for item in section_data:
                        response_parts.append(f"  • {item}")
                elif isinstance(section_data, dict):
                    for key, value in section_data.items():
                        if isinstance(value, list):
                            value = ", ".join(value)
                        response_parts.append(f"  • {key.replace('_', ' ')}: {value}")
                else:
                    response_parts.append(f"  {section_data}")
                
                response_parts.append("")
        
        # 마무리 멘트
        response_parts.append("더 자세한 정보가 필요하시면 'OOO의 취미', 'OOO의 업무' 등으로 구체적으로 질문해보세요!")
        
        return "\n".join(response_parts)

    def get_registered_persons(self) -> list:
        """등록된 인물 목록 반환"""
        return list(self.person_data.keys())

# MCP Server 인스턴스 생성
server = PersonalInfoServer()

if MCP_AVAILABLE:
    # FastMCP 인스턴스 생성
    mcp = FastMCP("personal-info-server", version="1.0.0")
    
    @mcp.tool() # 해당 데코레이터는 도구(호출 되는 기능)를 정의할 떄 사용 됨, 이 데코레이터가 함수를 Claude가 사용할 수 있는 도구로 등록, 도구들은 Claude가 필요할 때만 호출
    def get_person_information(query: str) -> str: # docstring의 중요성 -> 이 설명이 Claude가 언제 이 도구를 사용할지 판단하는 기준이 됨
        """
        사전에 등록된 특정 인물의 개인 정보를 조회합니다.
        
        이 도구는 등록된 인물들에 대한 정보만 제공할 수 있습니다.
        등록된 인물 목록을 확인하려면 list_available_persons 도구를 사용하세요.

        사용 예시:
        - "OOO에 대해 알려줘"
        - "OOO의 취미는?"
        - "OOO의 업무는?"
        
        이 도구를 사용하지 말아야 하는 경우:
        - 위에 나열되지 않은 모든 인물에 대한 질문
        - 일반적인 질문 (날씨, 뉴스, 기술 등)
        - 유명인이나 역사적 인물에 대한 질문
        
        등록되지 않은 인물에 대한 질문에는 이 도구를 사용하지 말고, 
        대신 일반적인 지식으로 답변해주세요.

        Args:
            query: 등록된 인물에 대한 질문
        
        Returns:
            str: 등록된 인물의 상세 정보 또는 "NO_REGISTERED_PERSON_FOUND"
        """
        return server.get_person_info(query)
    
    @mcp.tool()
    def list_available_persons() -> str:
        """
        등록된 인물 목록을 조회합니다.
        
        Returns:
            str: 등록된 인물들의 목록
        """
        if not server.person_data:
            return "등록된 인물 정보가 없습니다."
        
        names = list(server.person_data.keys())
        response = "**등록된 인물 목록**\n\n"
        for i, name in enumerate(names, 1):
            response += f"{i}. {name}\n"
        
        response += f"\n총 {len(names)}명의 정보가 등록되어 있습니다."
        response += "\n예시: 'OOO에 대해 알려줘' 또는 'OOO의 취미는?'"
        
        return response

    def main():
        """MCP Server 실행"""
        logger.info("Personal Info MCP Server 시작...")
        mcp.run() # 서버만 시작하고 계속 대기, 여기서 무한 대기

else:
    def main():
        """MCP 라이브러리가 없는 경우 설치 안내"""
        print("MCP 라이브러리가 설치되지 않았습니다!")
        print("다음 명령어로 설치해주세요:")
        print(" pip install mcp fastmcp")
        print("\n설치 후 Claude Desktop에서 사용할 수 있습니다.")
        print("설정 방법은 config/setup_guide.md를 참고하세요.")
        return

if __name__ == "__main__":
    main()