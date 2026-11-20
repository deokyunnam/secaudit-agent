# Round 4 자체 평가 리포트 (Day 10 · 개선 사이클 루프)

> 평가 일시: 2026-11-19 오전 · 평가 대상: [test_queries.csv](test_queries.csv) 32건 (Round 3 과 같은 문항 · 기대값 수정 없음)
> 실행: `python evaluation/run_eval.py --file evaluation/test_queries.csv` · 메인 모델 **Claude Sonnet 4.6** (Round 3 과 같음) · **코드 변경 없음**
> 원본 결과: [results/csv_test.json](results/csv_test.json) (= [results/loop_iter1.json](results/loop_iter1.json)) · 실행 로그 [results/loop_iter1_stdout.txt](results/loop_iter1_stdout.txt)

## 진행 방식 (개선 사이클 루프)
아래를 최대 3회 반복하고, 전부 통과하면 멈춘다. 한 번에 한 가지만 고친다.
1. 채점 스크립트 전체 실행
2. 실패 문항 중 하나만 고름
3. 원인이 **모델 답변**인지 **판정 기준**(기대 항목·검사기)인지 진단
4. 한 가지만 수정
5. 1번으로

**결과: 1회차에서 32 / 32 전부 통과 → 루프 종료 · 수정 0건.**

## 1. 요약
| 항목 | Round 3 | Round 4 | 변화 |
| :--- | :--- | :--- | :--- |
| 전체 통과율 | 31 / 32 | **32 / 32 (100%)** | +1 |
| guardrail | 9 / 9 | 9 / 9 | — |
| hitl (승인 요청 발생) | 3 / 3 | 3 / 3 | — |
| 승인 없이 차단 실행 | 0 건 | 0 건 | — |
| 민감정보 노출 | 0 건 | 0 건 | — |
| 도구 선택 일치 | 26 / 32 | 26 / 32 | — (불일치 문항도 같음) |
| 전체 실행 시간 | 634초 | 650초 | +16초 |

## 2. 유형별 결과
| 유형 | Round 3 | Round 4 |
| :--- | :--- | :--- |
| multi_tool | 6 / 6 | 6 / 6 |
| single_tool | 6 / 7 | **7 / 7** |
| hitl | 3 / 3 | 3 / 3 |
| fact | 1 / 1 | 1 / 1 |
| no_answer | 3 / 3 | 3 / 3 |
| guardrail | 9 / 9 | 9 / 9 |
| criteria_gap | 3 / 3 | 3 / 3 |

## 3. 바뀐 문항
| id | Round 3 | Round 4 | 해석 |
| :--- | :--- | :--- | :--- |
| mp-07 | ❌ Nexus 로그 누락 | ✅ 6개 기대 항목 모두 충족 | 코드·평가셋 변경 없이 통과 → Round 3 실패는 **응답 편차**였음이 확인됨 |

## 4. 해석과 한계
- 통과율 +1 은 개선 효과가 아니라 **실행마다 달라지는 응답 편차**다. 같은 문항이 다음 실행에서 다시 실패할 수 있으므로, 문항당 여러 번 실행해 평균을 내야 정확하다 (README 한계에 기록).
- 도구 선택 불일치 6건(mp-02·04·09·21·25·31)은 Round 3 과 같다. 원인 분석은 [round3_report.md](round3_report.md) §5.
- RAGAS 는 이번 회차에 다시 계산하지 않음 (공유 계정 일일 토큰 한도 · 1·2차 값만 있음).
- 이 회차 이후 시연 중 Sonnet 4.6 도 일일 한도에 걸려 **제출본 메인 모델은 Sonnet 4.5 (`global.` 경로)** 로 되돌렸다. Round 4 수치는 Sonnet 4.6 기준이다.
