# retriever.py - RAG 파이프라인 (문서 → Chroma 벡터 DB)
"""
벡터 DB를 두 개로 나눠서 만듭니다. (판정 근거와 참고자료가 섞이지 않게)

[판정 근거] 컬렉션 secaudit_criteria  → search_criteria 도구가 검색
  1) ISMS-P 인증기준 원문 80개 항목   data/isms_p/*.md   (data/extract_isms.py 로 생성)
  2) 주요정보통신기반시설 기술적 취약점 분석·평가 상세가이드 220개 항목
                                      data/kisa_guide/*.md (data/extract_kisa.py 로 생성)
  3) 사내 점검기준 4종 (가상)          data/policies/*.md

[참고자료] 컬렉션 secaudit_reference → search_reference 도구가 검색
  4) 외부 공개 자료 3종               data/external/*.md
     (MCP 공식 사양 보안 권고, OWASP MCP Top 10, MCP 관련 CVE 사례)
     → 위반·적합 판정에는 쓰지 않고, '기준 공백'의 신규 기준 수립 보고에만 씁니다.

처음 한 번, 그리고 문서를 고칠 때마다 벡터 DB를 다시 만들어야 합니다.
실행: python src/retriever.py
"""
from dotenv import load_dotenv
from langchain_aws import BedrockEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import (ISMS_DIR, KISA_DIR, POLICY_DIR, EXTERNAL_DIR, CHROMA_DIR,
                    COLLECTION_NAME, REFERENCE_COLLECTION_NAME, EMBEDDING_MODEL, REGION)

load_dotenv()

# 사내 점검기준 문서 제목 (답변에 출처를 표기할 때 사용)
POLICY_TITLES = {
    "infra_security_standard.md":    "사내 인프라 보안 점검 기준 (SEC-INFRA-001)",
    "incident_response.md":          "사내 보안 사고 대응 절차 (SEC-IR-003)",
    "network_access_control.md":     "사내 네트워크 접근 통제 및 방화벽 운영 기준 (SEC-NET-004)",
    "security_exception_process.md": "사내 보안 예외 승인 절차 (SEC-EXC-005)",
}

# 외부 참고자료 제목 (모두 '참고자료·판정 근거 아님' 표시를 붙입니다)
EXTERNAL_TITLES = {
    "mcp_security_best_practices.md": "[참고자료] MCP 공식 사양 보안 권고 (2025-11-25)",
    "owasp_mcp_top10.md":             "[참고자료] OWASP MCP Top 10 (2025, 베타)",
    "mcp_cve_cases.md":               "[참고자료] MCP 관련 공개 취약점(CVE) 사례",
}

embeddings = BedrockEmbeddings(model_id=EMBEDDING_MODEL, region_name=REGION)


def load_isms_docs() -> list:
    """ISMS-P 항목 파일을 읽습니다. 첫 줄 '# ISMS-P 2.6.2 정보시스템 접근' 을 제목으로 씁니다."""
    docs = []
    for path in sorted(ISMS_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        title = text.split("\n")[0].replace("# ", "").strip()
        docs.append(Document(
            page_content=text,
            metadata={"source": f"isms_p/{path.name}", "title": title, "kind": "ISMS-P"},
        ))
    return docs


def load_kisa_docs() -> list:
    """주요정보통신기반시설 상세가이드 항목 파일을 읽습니다. 첫 줄 '# 주요정보통신기반시설 U-28 접속 IP 및 포트 제한' 을 제목으로 씁니다."""
    docs = []
    # 상세가이드 원문은 제출본(git)에 포함하지 않으므로 폴더가 없을 수 있습니다
    if not KISA_DIR.exists():
        print("[안내] data/kisa_guide/ 가 없어 상세가이드 원문 없이 벡터 DB를 만듭니다. "
              "(생성: python data/extract_kisa.py <상세가이드 PDF 경로>)")
        return docs
    for path in sorted(KISA_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        title = text.split("\n")[0].replace("# ", "").strip()
        docs.append(Document(
            page_content=text,
            metadata={"source": f"kisa_guide/{path.name}", "title": title, "kind": "주요정보통신기반시설"},
        ))
    return docs


def load_policy_docs() -> list:
    """사내 점검기준 문서를 읽습니다."""
    docs = []
    for file_name, title in POLICY_TITLES.items():
        text = (POLICY_DIR / file_name).read_text(encoding="utf-8")
        docs.append(Document(
            page_content=text,
            metadata={"source": f"policies/{file_name}", "title": title, "kind": "사내기준"},
        ))
    return docs


def load_external_docs() -> list:
    """외부 참고자료 문서를 읽습니다. (판정 근거 아님)"""
    docs = []
    for file_name, title in EXTERNAL_TITLES.items():
        text = (EXTERNAL_DIR / file_name).read_text(encoding="utf-8")
        docs.append(Document(
            page_content=text,
            metadata={"source": f"external/{file_name}", "title": title, "kind": "참고자료"},
        ))
    return docs


def split_into_chunks(docs: list, chunk_size: int) -> list:
    """문서를 청크로 나누고, 각 청크 앞에 [제목]을 붙여 어느 문서인지 검색되게 합니다."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=80)
    chunks = splitter.split_documents(docs)
    for i, chunk in enumerate(chunks):
        chunk.page_content = f"[{chunk.metadata['title']}]\n{chunk.page_content}"
        chunk.metadata["doc_id"] = f"{chunk.metadata['source']}#{i}"
    return chunks


def load_chunks() -> list:
    """판정 근거 문서(ISMS-P + 주요정보통신기반시설 상세가이드 + 사내기준) 청크"""
    return split_into_chunks(load_isms_docs() + load_kisa_docs() + load_policy_docs(), chunk_size=600)


def load_reference_chunks() -> list:
    """참고자료 청크. '## ' 로 시작하는 절 하나(원문 요약 + 기존 점검법과의 차이)를 그대로 한 청크로 만듭니다.
    글자 수로 자르면 권고 내용과 차이 분석이 서로 다른 청크로 갈라질 수 있어서 절 단위로 자릅니다."""
    chunks = []
    i = 0
    for doc in load_external_docs():
        sections = doc.page_content.split("\n## ")
        for n, section in enumerate(sections):
            if n > 0:
                section = "## " + section          # split 으로 사라진 제목 기호를 되돌림
            chunks.append(Document(
                page_content=f"[{doc.metadata['title']}]\n{section.strip()}",
                metadata={**doc.metadata, "doc_id": f"{doc.metadata['source']}#{i}"},
            ))
            i += 1
    return chunks


def rebuild_collection(collection_name: str, chunks: list):
    """컬렉션 하나를 새로 만듭니다. 예전 내용이 섞이지 않도록 기존 컬렉션을 지우고 다시 만듭니다."""
    old = Chroma(
        persist_directory=str(CHROMA_DIR),
        embedding_function=embeddings,
        collection_name=collection_name,
    )
    old.delete_collection()

    db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=collection_name,
        persist_directory=str(CHROMA_DIR),
    )
    print(f"적재 완료: {collection_name} {db._collection.count()}개 청크 → {CHROMA_DIR}")


def build_vectorstore():
    """판정 근거 DB와 참고자료 DB를 둘 다 새로 만듭니다."""
    rebuild_collection(COLLECTION_NAME, load_chunks())
    rebuild_collection(REFERENCE_COLLECTION_NAME, load_reference_chunks())


def get_retriever(k: int = 5):
    """판정 근거(ISMS-P + 주요정보통신기반시설 상세가이드 + 사내기준) 검색기"""
    vectorstore = Chroma(
        persist_directory=str(CHROMA_DIR),
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME,
    )
    return vectorstore.as_retriever(search_kwargs={"k": k})


def get_reference_retriever(k: int = 3):
    """참고자료(외부 공개 자료) 검색기"""
    vectorstore = Chroma(
        persist_directory=str(CHROMA_DIR),
        embedding_function=embeddings,
        collection_name=REFERENCE_COLLECTION_NAME,
    )
    return vectorstore.as_retriever(search_kwargs={"k": k})


if __name__ == "__main__":
    build_vectorstore()

    # 잘 만들어졌는지 검색 테스트
    print("\n[판정 근거 검색] 사용목적과 관계 없는 서비스 제거")
    for doc in get_retriever().invoke("사용목적과 관계 없는 서비스 제거"):
        print("-", doc.metadata["title"], "|", doc.page_content[:60].replace("\n", " "))

    print("\n[참고자료 검색] AI 에이전트 DB 접근 권한 범위")
    for doc in get_reference_retriever().invoke("AI 에이전트 DB 접근 권한 범위"):
        print("-", doc.metadata["title"], "|", doc.page_content[:80].replace("\n", " "))
