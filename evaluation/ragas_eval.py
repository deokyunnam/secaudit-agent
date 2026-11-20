# ragas_eval.py - run_eval.py 결과 파일로 RAGAS 4개 지표를 계산합니다
"""
실행 (minipjt 폴더에서, run_eval.py 를 먼저 실행한 뒤):
    python evaluation/ragas_eval.py --round 1
    → evaluation/results/round1_ragas.json

대상 문항: 근거 문서를 찾아 답하는 유형만 (fact · single_tool · multi_tool · criteria_gap)
           그리고 contexts(도구 결과·검색 문서)가 1개 이상 있는 문항
           guardrail · no_answer · hitl 은 "거절·안내"가 정답이라 RAGAS 대상에서 뺍니다

reference(정답) 는 eval_set.json 의 expected 항목들을 이어 붙여 씁니다.
  → 사람이 쓴 모범 답안이 아니라 "답에 들어가야 할 요소 목록"이므로 context_recall 은 참고값입니다.
"""
import argparse
import json
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")   # ragas 0.4 의 구버전 API 경고 숨김 (import 보다 먼저 해야 효과가 있음)

from dotenv import load_dotenv
from langchain_aws import ChatBedrockConverse, BedrockEmbeddings
from ragas import evaluate, EvaluationDataset
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.metrics import Faithfulness, ResponseRelevancy, LLMContextRecall, LLMContextPrecisionWithReference

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "src"))
from config import CHECK_MODEL, EMBEDDING_MODEL, REGION  # noqa: E402

load_dotenv()

RESULT_DIR = BASE_DIR / "evaluation" / "results"
EVAL_FILE = BASE_DIR / "eval_set.json"
RAGAS_TYPES = ["fact", "single_tool", "multi_tool", "criteria_gap"]


def build_dataset(results: list, eval_set: list) -> tuple[EvaluationDataset, list]:
    expected_by_id = {}
    for item in eval_set:
        expected_by_id[item["id"]] = item["expected"]

    rows = []
    ids = []
    for r in results:
        if r["type"] not in RAGAS_TYPES:
            continue
        if not r["contexts"]:
            continue
        contexts = []
        for c in r["contexts"]:
            contexts.append(c["text"][:2000])   # 너무 긴 문서는 앞부분만 (평가 비용 절약)
        rows.append({
            "user_input": r["question"],
            "response": r["answer"],
            "retrieved_contexts": contexts,
            "reference": " ; ".join(expected_by_id[r["id"]]),
        })
        ids.append(r["id"])
    return EvaluationDataset.from_list(rows), ids


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--round", type=int, default=1)
    args = parser.parse_args()

    with open(RESULT_DIR / f"round{args.round}.json", encoding="utf-8") as f:
        report = json.load(f)
    with open(EVAL_FILE, encoding="utf-8") as f:
        eval_set = json.load(f)

    dataset, ids = build_dataset(report["results"], eval_set)
    print(f"RAGAS 대상 {len(ids)}문항: {ids}")

    # 채점용 LLM 은 빠르고 저렴한 Haiku, 임베딩은 RAG 와 같은 Titan
    llm = LangchainLLMWrapper(ChatBedrockConverse(model=CHECK_MODEL, region_name=REGION, temperature=0))
    embeddings = LangchainEmbeddingsWrapper(BedrockEmbeddings(model_id=EMBEDDING_MODEL, region_name=REGION))

    metrics = [LLMContextRecall(), LLMContextPrecisionWithReference(), Faithfulness(), ResponseRelevancy()]
    result = evaluate(dataset=dataset, metrics=metrics, llm=llm, embeddings=embeddings)

    df = result.to_pandas()
    df.insert(0, "id", ids)
    score_columns = ["context_recall", "llm_context_precision_with_reference", "faithfulness", "answer_relevancy"]

    averages = {}
    for col in score_columns:
        if col in df.columns:
            averages[col] = round(float(df[col].mean(skipna=True)), 3)

    per_item = []
    for _, row in df.iterrows():
        one = {"id": row["id"]}
        for col in score_columns:
            if col in df.columns:
                value = row[col]
                one[col] = None if value != value else round(float(value), 3)   # NaN → None
        per_item.append(one)

    out = {"round": args.round, "count": len(ids), "averages": averages, "per_item": per_item}
    out_path = RESULT_DIR / f"round{args.round}_ragas.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print("\n========== RAGAS 평균 ==========")
    for k, v in averages.items():
        print(f"  {k}: {v}")
    print(f"\n결과 파일: {out_path}")
