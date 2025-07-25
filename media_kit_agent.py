from textwrap import dedent
from typing import Dict, Optional
import json
import re
import logging

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from firecrawl_tool import FirecrawlTools

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MediaKitSearchAgent:
    """Agent for searching media kits and advertising materials from Korean media outlets"""
    
    def __init__(self, openai_api_key: str, firecrawl_api_key: str, strict_mode: bool = True):
        self.openai_api_key = openai_api_key
        self.firecrawl_tools = FirecrawlTools(api_key=firecrawl_api_key)
        self.strict_mode = strict_mode
        
        # Get instructions based on strict mode
        instructions = self._get_instructions(strict_mode)
        
        # Create the agent with OpenAI o3 model
        self.agent = Agent(
            name="Media Kit Search Agent",
            model=OpenAIChat(id="o3", api_key=openai_api_key),
            instructions=instructions,
            tools=[self.firecrawl_tools],
            markdown=False,
            show_tool_calls=True,
            debug_mode=True,
        )
    
    def _get_instructions(self, strict_mode: bool) -> str:
        """Get instructions based on strict mode setting"""
        
        if strict_mode:
            return self._get_strict_instructions()
        else:
            return self._get_flexible_instructions()
    
    def _get_strict_instructions(self) -> str:
        """Get strict mode instructions (current behavior)"""
        return dedent("""
        한국 사용자가 입력한 매체 이름을 바탕으로, 반드시 각 해당 매체사의 공식 홈페이지에서 실제 사이트맵(sitemap)과 웹페이지 콘텐츠를 직접 탐색하여 광고/상품 소개서(미디어킷, 보도자료, 광고상품 정보 등) 파일을 한국 기준으로 다운로드 받거나, 실제로 파일(소개서 등)이 첨부되어 있거나 링크가 걸려 있는 공식 웹페이지 URL만을 엄밀히 확인 및 출력하세요.

        - 오로지 공식, 신뢰 가능한 경로(매체사 공식 홈페이지, 공식 문서 센터, 공식 광고 안내 등)만 허용합니다. 링크가 변조되었거나 공식 경로가 아닐 경우 해당 링크를 반드시 배제합니다.
        - 사용자의 조회 의도 및 입력 매체 이름이 모호하거나 혼동될 여지는 없는지 우선 체크하고, 내부적으로 가능한 모든 후보를 조사하여 해당 공식 페이지에서 직접 확인 가능한 자료가 있는지 엄밀히 검토합니다.
        - 각 매체의 홈페이지 사이트맵 또는 핵심 메뉴(광고/제휴/미디어킷/자료실 등)를 실제로 확인하여, 다운로드 또는 열람 가능한 주요 광고상품 안내, 미디어킷, 보도자료 URL을 수집합니다.
        - 반드시 링크를 수집한 후, 해당 URL상에서 실제로 광고/상품 소개서 등 파일(다운로드 가능하거나 별도 파일 링크)이 직접 첨부되거나 확인 가능한지 마지막에 반드시 검증하세요. 실제 파일 또는 소개서가 존재하지 않거나 단순 안내 페이지만 있을 시에는 '찾을 수 없음'으로 간주합니다.
        - 어떤 매체도 공식 광고/상품 소개서 URL이 없다면, "찾을 수 없음"으로 명확하게 출력합니다.
        - 검색엔진(구글, 네이버, 다음)의 검색결과 리스트(검색페이지) 링크는 금지합니다. 반드시 직접적으로 파일 혹은 공식 문서가 포함된 매체사 페이지 링크만을 허용합니다.
        - 입력이 추상적이거나 특정 매체 식별이 어려워도, 매체사 공식 홈페이지 및 관련 페이지를 최선을 다해 추가 조사하며, 불충분할 시에는 "찾을 수 없음"을 표기합니다.
        - 여러 후보 자료 중에는 가장 신뢰성 높고 최근의 자료를 선택합니다.
        - 가능하면 PDF 파일(.pdf) URL 대신, 해당 PDF가 링크되거나 다운로드 가능한 공식 웹페이지 URL을 반환하세요. 단, 별도 웹페이지 없이 PDF 파일만 공식적으로 제공되는 경우에 한해 PDF URL을 반환합니다.
        - 반드시 사이트맵 및 실제 컨텐츠를 확인한 후, 매체 이름과 결과 URL 간의 매핑을 JSON 단일 객체(예: {"매체명": "[url 또는 찾을 수 없음]"})로 출력하세요.
        - 내부적으로 절차적/추론적 과정을 충분히 수행한 이후(매체 공식 홈페이지 확인 → 사이트맵/핵심 메뉴 탐색 → 후보 URL 수집 → 최종적으로 실제 파일/소개서 실존 여부 검증 → 신뢰성·최근성 기준 선정) 반드시 마지막으로 파일 실존 여부까지 확인한 후에만 최종 JSON을 단일 결과로 제공하세요.
        - 결과 도출 전 반드시 다음 논리적 추론과정을 내부적으로 수행:
            1. 매체명으로 공식 홈페이지 식별 및 방문
            2. 사이트맵·메뉴·공지·문서센터 등 직접 열람
            3. 파일/안내서가 공식적으로 제공되는지 후보 URL 일차 판단
            4. 해당 페이지에서 실제로 파일(소개서 등)이 첨부/다운로드/링크가 존재하는지 마지막에 재확인
            5. 신뢰성, 최근성, 권위 기준 최종 선정
            6. 없다면 '찾을 수 없음'으로 결정

        # 검색 도구 사용 시 주의사항
        
        - search 도구 사용 시, 효과적인 검색 쿼리를 직접 생성하세요:
          * 매체명과 함께 "미디어킷", "광고", "광고안내", "매체소개", "광고상품" 등의 키워드를 조합
          * 예: "중앙일보 미디어킷", "중앙일보 광고안내", "중앙일보 광고상품"
          * 영문 매체의 경우: "media kit", "advertising", "advertise" 등도 포함
        - 여러 검색어로 시도해보고, 가장 관련성 높은 결과를 선택하세요

        # Output Format

        - 반드시 {"매체명": "[url 또는 찾을 수 없음]"} 형태의 JSON 단일 객체로만 출력할 것.  
        - 그 외 부가 설명이나 Reasoning 텍스트 추가는 금지합니다.

        # Examples

        입력: 중앙일보  
        출력: {"중앙일보": "https://ad.joongang.co.kr/intro/service/mediakit.do"}

        입력: 기자협회보  
        출력: {"기자협회보": "https://www.journalist.or.kr/ad/mediakit.php"}

        입력: 없는신문  
        출력: {"없는신문": "찾을 수 없음"}

        # Notes

        - 반드시 공식 홈페이지 내 사이트맵 또는 실제 웹 페이지 컨텐츠를 직접 열람하여 광고/상품 소개서, 미디어킷 등의 자료 확인 및 URL 도출, 마지막에 해당 URL에서 실제 파일(소개서 등)이 첨부·다운로드·링크로 존재하는지 확인하세요.
        - 부정확하거나 비공식, 간접경로, 검색엔진 노출 페이지 등 부적격 링크를 포함하면 안 됩니다.
        - 항상 절차적/논리적 추론을 모두 마친 뒤 결과 JSON을 단일 객체로 출력하세요.
        - Output에 reasoning을 포함하거나 JSON 외의 결과를 절대 출력하지 마세요.

        [Reminder: 반드시 공식 홈페이지의 사이트맵/컨텐츠 실열람 및 후보 URL 수집 후, 마지막 단계로 해당 URL에 실제 파일(소개서 등) 존재 및 다운로드/링크 가능 여부를 꼭 확인하세요. reasoning→결론(JSON) 순으로 단계별 내부 추론 완료 후 단일 JSON만 출력하세요. Output 외 정보 표기 금지.]

        (중요 절차 및 목적: 반드시 매체 공식 홈페이지 탐색→사이트맵/정보 메뉴 실확인→후보 URL 추출 후 최종적으로 해당 URL에서 실제 파일(소개서 등) 존재 여부를 확인, 그 후에만 JSON으로 출력할 것. Output은 {"매체명": "[url 또는 찾을 수 없음]"} 단일 JSON 뿐!)
        """)
    
    def _get_flexible_instructions(self) -> str:
        """Get flexible mode instructions (allows intermediate hubs)"""
        return dedent("""
        한국 사용자가 입력한 매체 이름을 바탕으로, 광고/상품 소개서(미디어킷, 보도자료, 광고상품 정보 등) 파일이나 관련 정보를 찾아서 다운로드 링크나 웹페이지 URL을 찾아 출력하세요.

        # 검색 전략 (우선순위 순)

        1. **매체사 공식 홈페이지 직접 탐색**
           - 매체사 공식 홈페이지의 사이트맵, 광고/제휴/미디어킷/자료실 메뉴 확인
           - 공식 문서 센터, 광고 안내 페이지 등에서 미디어킷 자료 탐색

        2. **검색엔진을 통한 포괄적 검색**
           - 구글, 네이버, 다음 등 검색엔진을 활용하여 관련 자료 검색
           - "매체명 미디어킷", "매체명 광고안내", "매체명 광고상품" 등의 키워드 조합 사용
           - 영문 매체의 경우 "media kit", "advertising", "advertise" 등 키워드도 포함

        3. **중간 허브 및 집계 사이트 활용**
           - 광고업계 정보 사이트, 미디어 정보 포털 등에서 해당 매체 정보 확인
           - 광고 대행사 사이트나 미디어 데이터베이스에서 관련 정보 수집
           - 업계 자료실이나 공공기관의 미디어 정보에서 해당 매체 자료 탐색

        4. **소셜미디어 및 기타 경로**
           - 매체사의 공식 소셜미디어(페이스북, 인스타그램, 유튜브 등)에서 광고 관련 정보 확인
           - 링크드인, 브런치 등 비즈니스 플랫폼에서 관련 자료 검색

        # 검색 및 수집 원칙

        - **다양한 경로 활용**: 공식 홈페이지뿐만 아니라 검색엔진, 중간 허브, 집계 사이트 등 모든 가능한 경로를 통해 정보 수집
        - **정보의 신뢰성 확인**: 찾은 정보가 해당 매체와 관련이 있고 최신 정보인지 확인
        - **URL 유효성 검증**: 제공하는 URL이 실제로 접근 가능하고 관련 내용을 포함하는지 확인
        - **포괄적 검색**: 여러 검색어와 다양한 접근 방식을 통해 가능한 모든 자료 탐색

        # 허용되는 소스 유형

        - 매체사 공식 홈페이지 및 서브도메인
        - 검색엔진 결과 페이지
        - 광고업계 정보 사이트 및 포털
        - 미디어 관련 데이터베이스 및 정보 사이트
        - 공공기관의 미디어/광고 관련 자료실
        - 광고 대행사 및 마케팅 회사의 자료
        - 매체사 공식 소셜미디어 및 비즈니스 플랫폼
        - PDF 파일 직접 링크 (다운로드 가능한 경우)

        # 검색 도구 사용 가이드

        - **다양한 키워드 조합 사용**:
          * "매체명 미디어킷"
          * "매체명 광고안내"
          * "매체명 광고상품"
          * "매체명 광고요율"
          * "매체명 매체정보"
          * "매체명 광고 문의"
          * 영문: "media name media kit", "media name advertising"

        - **여러 검색 시도**: 첫 번째 검색에서 결과가 없더라도 다른 키워드나 접근법으로 재시도
        - **관련 사이트 탐색**: 직접적인 미디어킷이 없어도 광고 관련 정보나 매체 소개 자료 수집

        # Output Format

        - 반드시 {"매체명": "[url 또는 찾을 수 없음]"} 형태의 JSON 단일 객체로만 출력할 것.
        - 그 외 부가 설명이나 Reasoning 텍스트 추가는 금지합니다.

        # Examples

        입력: 중앙일보  
        출력: {"중앙일보": "https://ad.joongang.co.kr/intro/service/mediakit.do"}

        입력: 지역방송사  
        출력: {"지역방송사": "https://example-media-database.com/local-broadcast-info"}

        입력: 없는신문  
        출력: {"없는신문": "찾을 수 없음"}

        # Notes

        - **포괄적 접근**: 공식 홈페이지에서 찾을 수 없더라도 다양한 경로를 통해 관련 정보 탐색
        - **실용적 결과**: 완벽한 미디어킷이 없더라도 광고 관련 유용한 정보가 있는 페이지 제공
        - **효율성 우선**: 가장 빠르고 효과적인 방법으로 관련 정보에 접근할 수 있는 경로 제공
        - **유연한 해석**: 매체명이 정확하지 않거나 모호해도 가능한 모든 후보를 고려하여 관련 정보 탐색

        [Reminder: 다양한 경로(공식 홈페이지, 검색엔진, 중간 허브, 집계 사이트 등)를 모두 활용하여 광고/미디어킷 관련 정보를 찾고, 가장 유용한 결과를 JSON 형태로 출력하세요.]
        """)

    def search_media_kit(self, media_name: str) -> Dict[str, str]:
        """
        Search for media kit URL for the given media outlet
        
        Args:
            media_name: Name of the Korean media outlet
            
        Returns:
            Dictionary with media name as key and URL or "찾을 수 없음" as value
        """
        mode_text = "STRICT" if self.strict_mode else "FLEXIBLE"
        logger.info(f"\n{'='*50}")
        logger.info(f"[AGENT START] Searching media kit for: {media_name} (Mode: {mode_text})")
        logger.info(f"{'='*50}")
        
        try:
            # Run the agent with the media name
            logger.info("[AGENT] Sending query to o3 model...")
            response = self.agent.run(media_name)
            logger.info(f"[AGENT RESPONSE] Received response from o3 model")
            
            # Extract JSON from the response
            if hasattr(response, 'content'):
                content = response.content
            else:
                content = str(response)
            
            logger.info(f"[AGENT] Raw response: {content[:200]}..." if len(content) > 200 else f"[AGENT] Raw response: {content}")
            
            # Try to parse JSON from the response
            # First, try to find JSON pattern in the response
            json_pattern = r'\{[^}]+\}'
            json_match = re.search(json_pattern, content)
            
            if json_match:
                try:
                    result = json.loads(json_match.group())
                    logger.info(f"[AGENT RESULT] Successfully parsed JSON: {result}")
                    return result
                except json.JSONDecodeError as e:
                    logger.error(f"[AGENT ERROR] JSON decode error: {e}")
            
            # If JSON parsing fails, return error format
            logger.warning(f"[AGENT] Failed to parse JSON, returning default response")
            return {media_name: "찾을 수 없음"}
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"[AGENT ERROR] Unexpected error: {error_msg}")
            
            # Check for specific error types
            if "rate limit" in error_msg.lower():
                return {media_name: f"에러: Rate limit 초과 - {error_msg}"}
            elif "context" in error_msg.lower() and "token" in error_msg.lower():
                return {media_name: f"에러: Context token 초과 - {error_msg}"}
            elif "api" in error_msg.lower() and "key" in error_msg.lower():
                return {media_name: f"에러: API 키 문제 - {error_msg}"}
            else:
                return {media_name: f"에러: {error_msg}"}