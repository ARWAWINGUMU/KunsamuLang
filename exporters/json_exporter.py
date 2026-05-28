from __future__ import annotations

import json
from typing import Any


class JSONExporter:
    def export(self, root: Any) -> str:
        return json.dumps(root.to_dict(), ensure_ascii=False, indent=2)
