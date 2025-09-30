"""
RAG 서비스 관리 유틸리티
- 지식베이스 관리
- 통계 정보 조회
- 데이터 백업 및 복원
"""

import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

from rag_service import get_rag_service, initialize_rag_service

logger = logging.getLogger(__name__)

class RAGManager:
    """RAG 서비스 관리 클래스"""
    
    def __init__(self):
        self.rag_service = get_rag_service()
    
    def get_knowledge_statistics(self) -> Dict[str, Any]:
        """지식베이스 통계 정보 조회"""
        try:
            stats = self.rag_service.get_knowledge_statistics()
            return {
                "status": "success",
                "data": stats,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"통계 조회 오류: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def search_knowledge(self, query: str, n_results: int = 5, filter_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """지식베이스 검색"""
        try:
            results = self.rag_service.knowledge_base.search_relevant_knowledge(
                query=query,
                n_results=n_results,
                filter_types=filter_types
            )
            return {
                "status": "success",
                "data": results,
                "query": query,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"지식 검색 오류: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def add_custom_knowledge(self, content: str, pii_type: str, category: str, description: str, examples: List[str] = None) -> Dict[str, Any]:
        """사용자 정의 지식 추가"""
        try:
            knowledge_data = [{
                "content": content,
                "metadata": {
                    "type": pii_type,
                    "category": category,
                    "description": description
                },
                "examples": examples or []
            }]
            
            self.rag_service.knowledge_base._add_knowledge_batch(knowledge_data)
            
            return {
                "status": "success",
                "message": "지식이 성공적으로 추가되었습니다.",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"지식 추가 오류: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def export_knowledge_base(self, export_path: str) -> Dict[str, Any]:
        """지식베이스 내보내기"""
        try:
            export_path = Path(export_path)
            export_path.mkdir(parents=True, exist_ok=True)
            
            # 모든 지식 데이터 조회
            all_data = self.rag_service.knowledge_base.collection.get()
            
            # 메타데이터와 함께 저장
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "total_documents": len(all_data["documents"]),
                "documents": []
            }
            
            for i in range(len(all_data["documents"])):
                doc_data = {
                    "id": all_data["ids"][i],
                    "content": all_data["documents"][i],
                    "metadata": all_data["metadatas"][i]
                }
                export_data["documents"].append(doc_data)
            
            # JSON 파일로 저장
            export_file = export_path / f"knowledge_base_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            return {
                "status": "success",
                "message": f"지식베이스가 성공적으로 내보내졌습니다: {export_file}",
                "export_file": str(export_file),
                "total_documents": len(all_data["documents"]),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"지식베이스 내보내기 오류: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_detection_history(self, limit: int = 10) -> Dict[str, Any]:
        """탐지 이력 조회"""
        try:
            # 탐지 결과만 필터링하여 조회
            results = self.rag_service.knowledge_base.search_relevant_knowledge(
                query="탐지 결과",
                n_results=limit,
                filter_types=["detection_result"]
            )
            
            return {
                "status": "success",
                "data": results,
                "limit": limit,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"탐지 이력 조회 오류: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def clear_detection_history(self) -> Dict[str, Any]:
        """탐지 이력 삭제"""
        try:
            # 탐지 결과 문서들 조회
            all_data = self.rag_service.knowledge_base.collection.get()
            detection_ids = []
            
            for i, metadata in enumerate(all_data["metadatas"]):
                if metadata.get("type") == "detection_result":
                    detection_ids.append(all_data["ids"][i])
            
            # 탐지 결과 문서들 삭제
            if detection_ids:
                self.rag_service.knowledge_base.collection.delete(ids=detection_ids)
            
            return {
                "status": "success",
                "message": f"{len(detection_ids)}개의 탐지 이력이 삭제되었습니다.",
                "deleted_count": len(detection_ids),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"탐지 이력 삭제 오류: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }


def main():
    """RAG 관리자 테스트 및 데모"""
    print("RAG 서비스 관리자 데모")
    print("=" * 50)
    
    # RAG 서비스 초기화
    rag_manager = RAGManager()
    
    # 통계 정보 조회
    print("\n1. 지식베이스 통계:")
    stats = rag_manager.get_knowledge_statistics()
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    
    # 지식 검색 테스트
    print("\n2. 지식 검색 테스트:")
    search_result = rag_manager.search_knowledge("주민등록번호", n_results=3)
    print(json.dumps(search_result, ensure_ascii=False, indent=2))
    
    # 탐지 이력 조회
    print("\n3. 탐지 이력:")
    history = rag_manager.get_detection_history(limit=5)
    print(json.dumps(history, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
