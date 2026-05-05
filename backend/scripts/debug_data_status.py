import asyncio
import sys
import os
from sqlalchemy import select, func

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import AsyncSessionLocal
from app.models.user import User
from app.models.problem import Problem
from app.models.work_order import WorkOrder
from app.models.solution import Solution
from app.models.problem import ProblemStatus

async def check_data():
    async with AsyncSessionLocal() as db:
        users = await db.scalar(select(func.count(User.id)))
        problems = await db.scalar(select(func.count(Problem.id)))
        solutions = await db.scalar(select(func.count(Solution.id)))
        work_orders = await db.scalar(select(func.count(WorkOrder.id)))
        
        with open("debug_results.log", "w", encoding="utf-8") as f:
            f.write(f"--- Database Status ---\n")
            f.write(f"Users: {users}\n")
            f.write(f"Problems: {problems}\n")
            f.write(f"Solutions: {solutions}\n")
            f.write(f"Work Orders: {work_orders}\n")
            
            # Simulate Stats
            try:
                active = await db.scalar(select(func.count(Problem.id)).where(Problem.status != ProblemStatus.SOLVED))
                resolved = await db.scalar(select(func.count(Problem.id)).where(Problem.status == ProblemStatus.SOLVED))
                upvotes = await db.scalar(select(func.sum(Solution.upvotes_count))) or 0
                avg_impact = await db.scalar(select(func.avg(Solution.overall_score))) or 0.0
                
                f.write(f"--- Stats Calculation ---\n")
                f.write(f"Active: {active}\n")
                f.write(f"Resolved: {resolved}\n")
                f.write(f"Upvotes: {upvotes}\n")
                f.write(f"Avg Impact: {avg_impact}\n")
            except Exception as e:
                f.write(f"Stats Calculation Failed: {e}\n")

            if work_orders > 0:
                stmt = select(WorkOrder)
                result = await db.execute(stmt)
                wos = result.scalars().all()
                for wo in wos:
                    f.write(f"WO ID: {wo.id}, Status: {wo.status}, Est. Cost: {wo.estimated_cost}\n")

if __name__ == "__main__":
    asyncio.run(check_data())
