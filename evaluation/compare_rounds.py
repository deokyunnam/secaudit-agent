# compare_rounds.py - 두 회차 결과를 문항 단위로 비교합니다 (Day 7 심화 compare_eval 방식)
"""
실행 (minipjt 폴더에서):
    python evaluation/compare_rounds.py 1 2
    → {"fixed": [...], "regressed": [...], "delta": int, "safe": bool}

- fixed     : 이전 회차에서 실패했다가 이번 회차에서 통과한 문항 id
- regressed : 이전 회차에서 통과했다가 이번 회차에서 실패한 문항 id
- delta     : 이번 회차 통과 수 - 이전 회차 통과 수
- safe      : regressed 가 비어 있으면 True (통과 수가 늘어도 회귀가 하나라도 있으면 False)
"""
import json
import sys
from pathlib import Path

RESULT_DIR = Path(__file__).resolve().parent / "results"


def load_status(round_no: int) -> dict:
    """{문항 id: 'pass' / 'fail' / 'error'}"""
    with open(RESULT_DIR / f"round{round_no}.json", encoding="utf-8") as f:
        report = json.load(f)
    status = {}
    for r in report["results"]:
        status[r["id"]] = r["status"]
    return status


def compare_eval(before: dict, after: dict) -> dict:
    fixed = []
    regressed = []
    for item_id in after:
        was_pass = before.get(item_id) == "pass"
        now_pass = after[item_id] == "pass"
        if not was_pass and now_pass:
            fixed.append(item_id)
        if was_pass and not now_pass:
            regressed.append(item_id)

    before_passed = sum(1 for s in before.values() if s == "pass")
    after_passed = sum(1 for s in after.values() if s == "pass")
    return {
        "fixed": fixed,
        "regressed": regressed,
        "delta": after_passed - before_passed,
        "safe": len(regressed) == 0,
    }


if __name__ == "__main__":
    before_round = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    after_round = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    result = compare_eval(load_status(before_round), load_status(after_round))
    print(json.dumps(result, ensure_ascii=False, indent=2))
