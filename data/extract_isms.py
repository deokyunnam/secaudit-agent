# extract_isms.py - ISMS-P 인증기준 안내서 PDF에서 항목별 원문을 뽑아 data/isms_p/ 에 저장
"""
실행 (minipjt 폴더에서):
    python data/extract_isms.py "★정보보호 및 개인정보보호 관리체계 인증기준 안내서(2023.11).pdf"

준비물: pdftotext (Git Bash 에 포함되어 있음)
    - 반드시 -enc UTF-8 옵션을 써야 한글이 깨지지 않습니다.

결과: data/isms_p/1.1.1.md ~ 2.12.2.md (1장 관리체계 + 2장 보호대책 = 80개 항목)
     3장(개인정보 처리단계별 요구사항)은 이 프로젝트 범위가 아니라 제외합니다.
"""
import re
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
OUT_DIR = BASE / "isms_p"

# 페이지 머리말·꼬리말 등 본문이 아닌 줄
NOISE_LINES = [
    "정보보호 및 개인정보보호 관리체계 인증제도 안내서",
    "제2장 정보보호 및 개인정보보호 관리체계(ISMS-P) 인증기준 설명",
    "인증기준",          # 표의 칸 이름 (내용이 아님)
    "주요 확인사항",
    "관련 법규",
]


def pdf_to_text(pdf_path: str) -> str:
    """pdftotext 로 PDF 전체를 텍스트로 바꿉니다."""
    result = subprocess.run(
        ["pdftotext", "-enc", "UTF-8", pdf_path, "-"],
        capture_output=True,
        check=True,
    )
    return result.stdout.decode("utf-8")


def is_noise(line: str) -> bool:
    """옆 탭 글자(관, 리, 체 ...), 쪽 번호, 머리말 같은 줄이면 True"""
    text = line.strip()
    if text == "":
        return False          # 빈 줄은 문단 구분용으로 남깁니다
    if text in NOISE_LINES:
        return True
    if len(text) <= 3:        # "관", "리", "1", "개 인", "102" 같은 옆 탭·쪽 번호
        return True
    return False


def clean(lines: list) -> str:
    """잡음 줄을 지우고, 글머리 기호를 - 로 바꾸고, 빈 줄이 여러 개면 하나로 줄입니다."""
    kept = []
    for line in lines:
        if is_noise(line):
            continue
        # PDF 전용 글머리 기호(사용자 정의 영역 문자)를 일반 기호로 바꿉니다
        line = line.replace("", "-").replace("", "-").replace("", "-").replace("", " ").rstrip()
        kept.append(line)
    text = "\n".join(kept)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def read_official_names(lines: list) -> dict:
    """안내서 앞쪽 개요의 '1.1.1 경영진의 참여 1.1.2 ...' 한 줄 목록에서 공식 항목 이름을 읽습니다."""
    names = {}
    for line in lines[:500]:
        if line.startswith("1.1.1 ") or line.startswith("2.1.1 ") or line.startswith("2.6.1 "):
            for match in re.finditer(r"([12]\.\d{1,2}\.\d{1,2}) (.+?)(?= [123]\.\d{1,2}\.\d{1,2} |$)", line):
                names[match.group(1)] = match.group(2).strip()
    return names


def find_header_line(lines: list, item_id: str, item_name: str, start: int) -> int:
    """본문에서 항목 제목 줄을 찾습니다. 두 가지 모양이 있습니다.
       (가) '2.6.1 네트워크 접근'          (나) '항 목 2.6.2 정보시스템 접근 1'
    """
    # 목록과 본문의 띄어쓰기가 다른 경우가 있어("권한관리" / "권한 관리") 공백을 빼고 비교합니다
    title = f"{item_id}{item_name}".replace(" ", "")
    for i in range(start, len(lines)):
        text = lines[i].strip().replace(" ", "")
        if text == title:
            return i
        if text.startswith("항목" + title):
            return i
    return -1


def split_items(text: str) -> dict:
    """공식 항목 목록 순서대로 제목 줄을 찾아, 다음 항목 제목 전까지를 본문으로 자릅니다."""
    lines = text.split("\n")
    names = read_official_names(lines)

    # 본문은 개요의 항목 목록(앞 약 350줄) 뒤에서부터 찾습니다
    headers = []   # (줄 번호, 항목 번호, 항목 이름)
    search_from = 350
    for item_id, item_name in names.items():
        line_no = find_header_line(lines, item_id, item_name, search_from)
        if line_no == -1:
            print(f"  [경고] 제목을 못 찾음: {item_id} {item_name}")
            continue
        headers.append((line_no, item_id, item_name))
        search_from = line_no + 1

    # 마지막 항목(2.12.2)은 3장 첫 항목(3.1.1) 전까지
    chapter3 = find_header_line(lines, "3.1.1", "개인정보 수집·이용", search_from)
    if chapter3 == -1:
        chapter3 = len(lines)

    items = {}
    for k, (line_no, item_id, item_name) in enumerate(headers):
        if k + 1 < len(headers):
            end = headers[k + 1][0]
        else:
            end = chapter3
        body = clean(lines[line_no + 1:end])
        items[item_id] = {"name": item_name, "body": body}
    return items


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python data/extract_isms.py <ISMS-P 안내서 PDF 경로>")
        sys.exit(1)

    text = pdf_to_text(sys.argv[1])
    items = split_items(text)

    OUT_DIR.mkdir(exist_ok=True)
    for item_id, item in items.items():
        path = OUT_DIR / f"{item_id}.md"
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"# ISMS-P {item_id} {item['name']}\n\n")
            f.write("- 출처: 정보보호 및 개인정보보호 관리체계 인증기준 안내서 (KISA, 2023.11)\n\n")
            f.write(item["body"] + "\n")

    print(f"추출 완료: {len(items)}개 항목 → {OUT_DIR}")
    print("항목 목록:", ", ".join(items.keys()))
