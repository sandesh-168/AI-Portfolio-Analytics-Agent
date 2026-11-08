import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from src.router import QueryRouter

def test_routing():
    router = QueryRouter()
    with open("ground_truth_dataset.json") as f:
        gt = json.load(f)

    correct = 0
    total = len(gt["questions"])
    for item in gt["questions"]:
        routed = router.route(item["question"])
        expected = item["type"]
        matched = (routed["tool_name"] == expected)
        if matched:
            correct += 1
        print(f"Q{item['id']}: Expected={expected} | Routed={routed['tool_name']} | Matched={matched}")

    print(f"\nFinal Routing Accuracy: {correct}/{total} ({correct/total*100:.1f}%)")

if __name__ == "__main__":
    test_routing()
