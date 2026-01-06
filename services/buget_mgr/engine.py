import json
import pathlib
import uuid
from typing import List, Optional, Dict, Any

from models._budget import Fund, Goal
from core._const import BASE_DIR, FILE_FUNDS, FILE_GOALS

class BudgetEngine:
    def __init__(self):
        self.funds: List[Fund] = []
        self.goals: List[Goal] = []
        
        # Đảm bảo thư mục data tồn tại
        if not (BASE_DIR / "data").exists():
            (BASE_DIR / "data").mkdir(parents=True, exist_ok=True)
            
        print("🚀 BudgetEngine: Đang khởi tạo...")
        self.load()

    def load(self):
        self._load_funds()
        self._load_goals()

    def save(self):
        self._save_funds()
        self._save_goals()

    def _load_funds(self):
        self.funds = []
        if FILE_FUNDS.exists():
            try:
                content = FILE_FUNDS.read_text(encoding='utf-8').strip()
                if not content: return 

                data = json.loads(content)
                for d in data:
                    if "history" not in d: d["history"] = []
                    self.funds.append(Fund(**d))
                print(f"✅ Loaded: {len(self.funds)} quỹ cá nhân.")
            except Exception as e:
                print(f"❌ Lỗi load Funds: {e}")

    def _save_funds(self):
        try:
            data = [f.to_dict() if hasattr(f, "to_dict") else f.__dict__ for f in self.funds]
            FILE_FUNDS.write_text(json.dumps(data, ensure_ascii=False, indent=4), encoding='utf-8')
            # print("💾 Saved Funds.")
        except Exception as e:
            print(f"❌ Lỗi save Funds: {e}")
    def _load_goals(self):
        self.goals = []
        if FILE_GOALS.exists():
            try:
                content = FILE_GOALS.read_text(encoding='utf-8').strip()
                if not content: return

                data = json.loads(content)
                for d in data:
                    self.goals.append(Goal(**d))
                print(f"✅ Loaded: {len(self.goals)} quỹ nhóm.")
            except Exception as e:
                print(f"❌ Lỗi load Goals: {e}")

    def _save_goals(self):
        try:
            data = [g.to_dict() if hasattr(g, "to_dict") else g.__dict__ for g in self.goals]
            FILE_GOALS.write_text(json.dumps(data, ensure_ascii=False, indent=4), encoding='utf-8')
        except Exception as e:
            print(f"❌ Lỗi save Goals: {e}")

    
    def get_fund_by_id(self, fund_id: str) -> Optional[Fund]:
       
        target = str(fund_id).strip()
        for f in self.funds:
            if str(f.id).strip() == target:
                return f
        print(f"⚠️ Không tìm thấy Fund ID: {fund_id}")
        return None

    def get_total_savings(self) -> float:
       
        return sum(f.current for f in self.funds)

    def summary(self) -> Dict[str, float]:
        
        total_p = self.get_total_savings()
        
        total_g = 0
        for g in self.goals:
            
            if hasattr(g, 'current_amount'):
                total_g += g.current_amount
            elif hasattr(g, 'members'):
                
                 total_g += sum(m.get('contribution', 0) for m in g.members)
                 
        return {
            "personal_saved": total_p, 
            "group_saved": total_g,
            "total": total_p + total_g
        }

    
    def add_fund(self, fund: Fund):
        
        if not fund.id: 
            fund.id = str(uuid.uuid4())
        self.funds.append(fund)
        self._save_funds()
        print(f"✅ Đã thêm quỹ: {fund.name}")

    def update_fund(self, updated_fund: Fund):
        for i, f in enumerate(self.funds):
            if str(f.id) == str(updated_fund.id):
                self.funds[i] = updated_fund
                self._save_funds()
                return
        print(f"❌ Update thất bại: Không tìm thấy Fund {updated_fund.id}")

    def delete_fund(self, fund_id: str):
        original_len = len(self.funds)
        self.funds = [f for f in self.funds if str(f.id) != str(fund_id)]
        if len(self.funds) < original_len:
            self._save_funds()
            print(f"🗑️ Đã xóa quỹ {fund_id}")

    def add_goal(self, goal: Goal):
        if not goal.id: goal.id = str(uuid.uuid4())
        self.goals.append(goal)
        self._save_goals()

    def update_goal(self, updated_goal: Goal):
        for i, g in enumerate(self.goals):
            if str(g.id) == str(updated_goal.id):
                self.goals[i] = updated_goal
                self._save_goals()
                return

    def delete_goal(self, goal_id: str):
        self.goals = [g for g in self.goals if str(g.id) != str(goal_id)]
        self._save_goals()