import json
from entities.plan import Plan


def format_plan_to_json(plan: Plan) -> str:
    data = {
        "meta": {"source": plan.source},
        "walls": [
            {"id": w.id, "points": w.points} for w in plan.walls
        ],
        "doors": [
            {"id": d.id, "bbox": d.bbox} for d in plan.doors
        ],
        "windows": [
            {"id": w.id, "bbox": w.bbox} for w in plan.windows
        ]
    }
    return json.dumps(data, ensure_ascii=False, indent=2)
