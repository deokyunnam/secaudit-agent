# extract_kisa.py - 「주요정보통신기반시설 기술적 취약점 분석·평가 방법 상세가이드」(KISA, 2026) PDF → 항목별 원문 추출
"""
실행 (minipjt 폴더에서):
  python data/extract_kisa.py "data/reference/주요정보통신기반시설 기술적 취약점 분석·평가 방법 상세가이드.pdf"

결과: data/kisa_guide/U-01.md ... (점검항목 1개 = 파일 1개)

- pdftotext 프로그램이 필요합니다. (Git Bash 의 /ucrt64/bin/pdftotext)
- 항목 상세 페이지는 "U-01 (상)" 처럼 '항목코드 (중요도)' 줄로 시작합니다.
- MCP가 실제로 구동되는 대상만 뽑습니다:
    U(Unix 서버), W(Windows 서버), WEB(웹 서비스), D(DBMS), PC(PC), CA(클라우드)
  보안 장비(S)·네트워크 장비(N)·제어시스템(C)·이동통신(M)·가상화 장비(HV)는 제외합니다.
- '점검 및 조치 사례'(OS별 명령어 예시)는 길고 검색에 방해가 되어 빼고,
  개요·점검 목적·보안 위협·점검 대상·판단 기준(양호/취약)·조치 방법까지만 저장합니다.
"""
import re
import subprocess
import sys
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent
OUT_DIR = DATA_DIR / "kisa_guide"

SOURCE = "KISA 「주요정보통신기반시설 기술적 취약점 분석·평가 방법 상세가이드」(2026)"

# 뽑을 항목코드 앞자리 → 분야 이름
TARGET_PREFIXES = {
    "U": "Unix 서버",
    "W": "Windows 서버",
    "WEB": "웹 서비스",
    "D": "DBMS",
    "PC": "PC",
    "CA": "클라우드",
}

# 상세 페이지 첫 줄: "U-01 (상)" 또는 "U-01 (상) 점검 내용 점검 목적 ..."
HEADER_PATTERN = re.compile(r"^([A-Z]{1,3})-(\d{2}) \((상|중|하)\)")

# 분류 경로 줄에 나오는 세부 분류 이름 (긴 이름부터 비교해야 '패치 및 로그 관리'가 '패치 관리'로 잘못 잘리지 않음)
SECTION_NAMES = [
    "파일 및 디렉토리 관리", "파일 및 디렉터리 관리", "패치 및 로그 관리", "가상 리소스 관리",
    "계정 관리", "서비스 관리", "패치 관리", "로그 관리", "보안 관리", "보안 설정",
    "권한 관리", "운영 관리", "접근 관리", "옵션 관리",
]

# 표의 칸 이름만 있는 줄 (본문이 아니므로 지움)
LABEL_WORDS = {"점검", "내용", "목적", "보안", "위협", "참고", "대상", "판단", "기준", "조치", "방법", "시", "영향"}


def pdf_to_text(pdf_path: str) -> str:
    """PDF를 UTF-8 텍스트로 바꿉니다. (-enc UTF-8 이 없으면 한글이 깨짐)"""
    result = subprocess.run(
        ["pdftotext", "-enc", "UTF-8", pdf_path, "-"],
        capture_output=True,
    )
    return result.stdout.decode("utf-8", errors="ignore")


def is_label_line(line: str) -> bool:
    """'점검 내용 점검 목적 보안 위협' 처럼 표의 칸 이름으로만 된 줄인지 확인합니다."""
    words = line.split()
    if not words:
        return False
    for w in words:
        if w not in LABEL_WORDS:
            return False
    return True


def is_noise_line(line: str) -> bool:
    """페이지 번호, 머리말 같은 잡음 줄인지 확인합니다."""
    s = line.strip()
    if s == "":
        return True
    if s.isdigit():
        return True
    if "한국인터넷진흥원" in s:
        return True
    if s.startswith("2026 주요정보통신기반시설"):
        return True
    if re.match(r"^\d{2}\. ", s):        # "01. Unix 서버" 같은 장 제목 머리말
        return True
    return False


def split_items(lines: list) -> list:
    """(항목코드, 중요도, 본문 줄 목록) 리스트를 돌려줍니다."""
    starts = []
    for i, line in enumerate(lines):
        m = HEADER_PATTERN.match(line.strip())
        if m:
            code = f"{m.group(1)}-{m.group(2)}"
            starts.append((i, m.group(1), code, m.group(3)))

    items = []
    for n, (i, prefix, code, level) in enumerate(starts):
        if n + 1 < len(starts):
            end = starts[n + 1][0]
        else:
            end = len(lines)
        if prefix in TARGET_PREFIXES:
            items.append((prefix, code, level, lines[i + 1:end]))
    return items


def parse_item(body_lines: list):
    """본문에서 (세부 분류, 항목 이름, 정리된 본문)을 꺼냅니다."""
    # 1) '점검 및 조치 사례' 앞까지만 사용
    kept = []
    for line in body_lines:
        if line.strip().startswith("점검 및 조치 사례"):
            break
        kept.append(line)

    # 2) 잡음 줄·칸 이름 줄 제거
    cleaned = []
    for line in kept:
        if is_noise_line(line) or is_label_line(line):
            continue
        cleaned.append(line.strip())

    # 3) 'Unix > 1. 계정 관리 항목이름 ...' 줄에서 세부 분류와 항목 이름 찾기
    section = ""
    name = ""
    for idx, line in enumerate(cleaned):
        if " > " not in line:
            continue
        after_arrow = line.split(" > ", 1)[1]            # "1. 계정 관리 비밀번호 관리정책 설정 개요 ..."
        after_number = re.sub(r"^\d+\.\s*", "", after_arrow)
        for sec in SECTION_NAMES:
            if after_number.startswith(sec):
                section = sec
                rest = after_number[len(sec):].strip()
                break
        else:
            rest = after_number
        if rest == "" and idx + 1 < len(cleaned):         # 이름이 다음 줄에 있는 경우 (예: U-01)
            rest = cleaned[idx + 1]
        name = rest.split(" 개요")[0].strip()              # 이름 뒤에 붙은 '개요 ...' 잘라내기
        break

    text = "\n".join(cleaned)
    return section, name, text


def main():
    if len(sys.argv) < 2:
        print('사용법: python data/extract_kisa.py "<상세가이드 PDF 경로>"')
        return

    text = pdf_to_text(sys.argv[1])
    lines = text.split("\n")
    items = split_items(lines)

    OUT_DIR.mkdir(exist_ok=True)
    count_by_prefix = {}
    no_name = []
    for prefix, code, level, body in items:
        section, name, body_text = parse_item(body)
        if name == "":
            no_name.append(code)
        header = f"# 주요정보통신기반시설 {code} {name}"
        meta = (f"- 출처: {SOURCE}\n"
                f"- 분야: {TARGET_PREFIXES[prefix]} > {section}\n"
                f"- 중요도: {level}\n")
        (OUT_DIR / f"{code}.md").write_text(f"{header}\n\n{meta}\n{body_text}\n", encoding="utf-8")
        count_by_prefix[prefix] = count_by_prefix.get(prefix, 0) + 1

    print(f"추출 완료: {len(items)}개 항목 → {OUT_DIR}")
    for prefix, count in count_by_prefix.items():
        print(f"  {prefix} ({TARGET_PREFIXES[prefix]}): {count}개")
    if no_name:
        print(f"  ※ 항목 이름을 찾지 못한 항목: {no_name}")


if __name__ == "__main__":
    main()
