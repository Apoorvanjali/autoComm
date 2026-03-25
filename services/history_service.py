"""
History Service
Simple JSON-backed storage for activity history and favorites.
"""

import json
import os
from datetime import datetime
from threading import Lock
from typing import Dict, List, Optional


class HistoryService:
    def __init__(self, file_path: str = "data/history.json"):
        self.file_path = file_path
        self._lock = Lock()
        self._ensure_store()

    def list_items(self, user: str, module: Optional[str] = None, favorite_only: bool = False) -> List[Dict]:
        with self._lock:
            data = self._load()
            items = [item for item in data.get("items", []) if item.get("user") == user]

            if module:
                items = [item for item in items if item.get("module") == module]

            if favorite_only:
                items = [item for item in items if bool(item.get("favorite"))]

            return sorted(items, key=lambda x: x.get("created_at", ""), reverse=True)

    def add_item(
        self,
        module: str,
        title: str,
        input_preview: str,
        output_preview: str,
        metadata: Dict,
        user: str,
        favorite: bool = False,
    ) -> Dict:
        with self._lock:
            data = self._load()
            next_id = int(data.get("next_id", 1))

            item = {
                "id": next_id,
                "module": module,
                "title": title,
                "input_preview": input_preview,
                "output_preview": output_preview,
                "metadata": metadata or {},
                "favorite": favorite,
                "user": user,
                "created_at": datetime.utcnow().isoformat() + "Z",
            }

            data.setdefault("items", []).append(item)
            data["next_id"] = next_id + 1
            self._save(data)
            return item

    def toggle_favorite(self, item_id: int, user: str) -> Optional[Dict]:
        with self._lock:
            data = self._load()
            for item in data.get("items", []):
                if item.get("id") == item_id and item.get("user") == user:
                    item["favorite"] = not bool(item.get("favorite"))
                    self._save(data)
                    return item
            return None

    def delete_item(self, item_id: int, user: str) -> bool:
        with self._lock:
            data = self._load()
            items = data.get("items", [])
            before = len(items)
            items = [item for item in items if not (item.get("id") == item_id and item.get("user") == user)]
            data["items"] = items
            if len(items) == before:
                return False
            self._save(data)
            return True

    def _ensure_store(self):
        dir_name = os.path.dirname(self.file_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)

        if not os.path.exists(self.file_path):
            self._save({"next_id": 1, "items": []})

    def _load(self) -> Dict:
        if not os.path.exists(self.file_path):
            return {"next_id": 1, "items": []}

        with open(self.file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, data: Dict):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
