import asyncio
import sys
import os

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import all models to ensure registry is configured
import app.models 

from app.database import AsyncSessionLocal
from app.models.department import Department
from app.models.jurisdiction import Jurisdiction, JurisdictionType
from app.models.user import User, UserRole
from app.models.official import Official, OfficialRole
from app.models.problem import Problem, ProblemStatus
from app.models.contractor import Contractor, ContractorSpecialization
from app.models.work_order import WorkOrder, WorkOrderStatus
from app.models.media import MediaAttachment, MediaType
from app.models.government_response import GovernmentResponse
from app.core.security import get_password_hash
from sqlalchemy import select
from sqlalchemy.orm import configure_mappers
import uuid
from datetime import datetime, timedelta

import traceback

try:
    # Force configuration of mappers
    configure_mappers()
except Exception:
    traceback.print_exc()
    sys.exit(1)

async def seed_data():
    async with AsyncSessionLocal() as db:
        print("🌱 Seeding Demo Data...")

        # 1. Departments
        print("  -> Creating Departments...")
        depts_data = [
            {
                "name": "Ministry of Housing and Urban Affairs (MoHUA)", 
                "code": "MOHUA-IND", 
                "description": "Urban development, sanitation, and affordable housing.",
                "logo_url": "https://upload.wikimedia.org/wikipedia/en/2/23/Ministry_of_Housing_and_Urban_Affairs.svg"
            },
            {
                "name": "Public Works Department (PWD)", 
                "code": "PWD-IND", 
                "description": "Roads, Bridges, and Government Buildings.",
                "logo_url": "https://upload.wikimedia.org/wikipedia/commons/a/a2/Emblem_of_India.svg"
            },
            {
                "name": "Ministry of Jal Shakti", 
                "code": "JALSHAKTI-IND", 
                "description": "Water resources, river development and Ganga rejuvenation.",
                "logo_url": "https://upload.wikimedia.org/wikipedia/commons/e/e6/Logo_of_Ministry_of_Jal_Shakti.png"
            },
            {
                "name": "Swachh Bharat Mission (Clean India)", 
                "code": "SBM-IND", 
                "description": "Solid waste management and sanitation across India.",
                "logo_url": "https://upload.wikimedia.org/wikipedia/en/d/dd/Swachh_Bharat_Abhiyan_logo.jpg",
                "website_url": "https://swachhbharatmission.gov.in/",
                "wikidata_id": "Q18199573"
            }
        ]
        
        depts = {}
        for d in depts_data:
            stmt = select(Department).where(Department.code == d["code"])
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            if not existing:
                new_dept = Department(**d, sla_config={"critical": 24, "high": 48})
                db.add(new_dept)
                depts[d["code"]] = new_dept
            else:
                depts[d["code"]] = existing
        
        await db.commit()

        # 2. Jurisdictions
        print("  -> Creating Jurisdictions...")
        # City
        stmt = select(Jurisdiction).where(Jurisdiction.name == "Indore Municipal Corporation")
        result = await db.execute(stmt)
        city = result.scalar_one_or_none()
        
        if not city:
            city = Jurisdiction(name="Indore Municipal Corporation", type=JurisdictionType.CITY, parent_id=None)
            db.add(city)
            await db.commit()
            await db.refresh(city)
            
        # Zone
        stmt = select(Jurisdiction).where(Jurisdiction.name == "Zone 1")
        result = await db.execute(stmt)
        zone = result.scalar_one_or_none()
        
        if not zone:
            zone = Jurisdiction(name="Zone 1", type=JurisdictionType.ZONE, parent_id=city.id)
            db.add(zone)
            await db.commit()
            await db.refresh(zone)
            
        # Ward
        stmt = select(Jurisdiction).where(Jurisdiction.name == "Ward 12")
        result = await db.execute(stmt)
        ward = result.scalar_one_or_none()
        
        if not ward:
            ward_polygon = {
                "type": "Polygon",
                "coordinates": [[
                    [75.850, 22.710],
                    [75.870, 22.710],
                    [75.870, 22.730],
                    [75.850, 22.730],
                    [75.850, 22.710]
                ]]
            }
            ward = Jurisdiction(
                name="Ward 12", 
                type=JurisdictionType.WARD, 
                parent_id=zone.id,
                boundary_polygon=ward_polygon
            )
            db.add(ward)
            await db.commit()
            await db.refresh(ward)
        else:
            # Update polygon if missing
            if not ward.boundary_polygon:
                ward.boundary_polygon = {
                    "type": "Polygon",
                    "coordinates": [[
                        [75.850, 22.710],
                        [75.870, 22.710],
                        [75.870, 22.730],
                        [75.850, 22.730],
                        [75.850, 22.710]
                    ]]
                }
                db.add(ward)
                await db.commit()

        # 3. Create Official Users (Functional Seats)
        print(" -> Creating Functional Office Seats...")
        
        # Seat 1: Sanitation Inspector (MoHUA/SWM)
        inspector_email = "sanitation.inspector@indore.gov.in"
        stmt = select(User).where(User.email == inspector_email)
        result = await db.execute(stmt)
        inspector_user = result.scalar_one_or_none()
        
        if not inspector_user:
            inspector_user = User(
                email=inspector_email,
                hashed_password=get_password_hash("Inspector123"),
                full_name="Office of Sanitation Inspector", # Seat Name
                role=UserRole.GOVERNMENT,
                is_active=True
            )
            db.add(inspector_user)
            await db.commit()
            await db.refresh(inspector_user)
            
        # Seat 2: Roads Engineer (PWD)
        engineer_email = "zone1.engineer@pwd.indore.gov.in"
        stmt = select(User).where(User.email == engineer_email)
        result = await db.execute(stmt)
        engineer_user = result.scalar_one_or_none()
        
        if not engineer_user:
            engineer_user = User(
                email=engineer_email,
                hashed_password=get_password_hash("Engineer123"),
                full_name="Office of Zone 1 Engineer",
                role=UserRole.GOVERNMENT,
                is_active=True
            )
            db.add(engineer_user)
            await db.commit()
            await db.refresh(engineer_user)
            
        # 4. Create Official Profiles (Occupant Assignments)
        print("  -> Assigning Human Occupants to Seats...")
        
        # Profile 1: Rajesh at Sanitation
        stmt = select(Official).where(Official.user_id == inspector_user.id)
        result = await db.execute(stmt)
        if not result.scalar_one_or_none():
            p1 = Official(
                user_id=inspector_user.id,
                department_id=depts["MOHUA-IND"].id,
                jurisdiction_id=ward.id,
                role=OfficialRole.FIELD_AGENT,
                badge_number="SWM-IND-77",
                designation="Chief Sanitation Inspector",
                current_occupant_name="Rajesh Kumar",
                is_verified=True
            )
            db.add(p1)

        # Profile 2: Suman at PWD
        stmt = select(Official).where(Official.user_id == engineer_user.id)
        result = await db.execute(stmt)
        if not result.scalar_one_or_none():
            p2 = Official(
                user_id=engineer_user.id,
                department_id=depts["PWD-IND"].id,
                jurisdiction_id=ward.id,
                role=OfficialRole.APPROVER,
                badge_number="PWD-Z1-09",
                designation="Executive Engineer (Roads)",
                current_occupant_name="Suman Rao",
                is_verified=True
            )
            db.add(p2)
            
        await db.commit()

        # 4b. Create Admin User
        print("  -> Creating Admin User...")
        admin_email = "admin@civicos.gov.in"
        stmt = select(User).where(User.email == admin_email)
        result = await db.execute(stmt)
        admin_user = result.scalar_one_or_none()
        
        if not admin_user:
            admin_user = User(
                email=admin_email,
                hashed_password=get_password_hash("Admin123"),
                full_name="System Administrator",
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(admin_user)
            await db.commit()

        # 5. Create Sample Problems
        print("  -> Creating Sample Problems...")
        
        # We need a citizen user to be the author
        citizen_email = "citizen@test.com"
        stmt = select(User).where(User.email == citizen_email)
        result = await db.execute(stmt)
        citizen = result.scalar_one_or_none()
        
        if not citizen:
            citizen = User(
                email=citizen_email,
                hashed_password=get_password_hash("Citizen123"),
                full_name="Amit Sharma",
                role=UserRole.CITIZEN,
                is_active=True
            )
            db.add(citizen)
            await db.commit()
            await db.refresh(citizen)

        problems_data = [
            {
                "title": "Garbage pile near Palasia Square",
                "description": "Large pile of uncollected garbage causing foul smell.",
                "category": "Sanitation",
                "status": ProblemStatus.OPEN,
                "department_id": depts["MOHUA-IND"].id,
                "jurisdiction_id": ward.id,
                "escalation_level": 3,
                "latitude": 22.7196,
                "longitude": 75.8577,
                "address": "Palasia Square, Indore"
            },
            {
                "title": "Pothole on MG Road",
                "description": "Deep pothole causing traffic slowdown.",
                "category": "Roads",
                "status": ProblemStatus.UNDER_REVIEW,
                "department_id": depts["PWD-IND"].id,
                "jurisdiction_id": ward.id,
                "escalation_level": 4,
                "latitude": 22.7199,
                "longitude": 75.8579,
                "address": "MG Road, Indore"
            },
            {
                "title": "Street light not working in Vijayanagar",
                "description": "Street light pole #45 is flickering.",
                "category": "Electricity",
                "status": ProblemStatus.SOLVED,
                "department_id": depts["PWD-IND"].id, 
                "jurisdiction_id": ward.id,
                "escalation_level": 2,
                "latitude": 22.7533,
                "longitude": 75.8937,
                "address": "Vijayanagar, Indore"
            }
        ]

        for p_data in problems_data:
            # Check if exists (simple check by title for demo)
            stmt = select(Problem).where(Problem.title == p_data["title"])
            result = await db.execute(stmt)
            if not result.scalar_one_or_none():
                prob = Problem(
                    **p_data,
                    user_id=citizen.id
                )
                db.add(prob)
                await db.commit()
                await db.refresh(prob)

                # Add Civic Proof: Media Attachment with GPS hardware snapshot
                proof = MediaAttachment(
                    file_url="https://images.unsplash.com/photo-1594498653385-d5172c532c00?q=80&w=600",
                    media_type=MediaType.IMAGE,
                    problem_id=prob.id,
                    latitude=p_data["latitude"],
                    longitude=p_data["longitude"],
                    is_verified_capture=True,
                    device_info="Demo Device (Verified In-App Capture)"
                )
                db.add(proof)

        # 6. Create Work Orders
        print("  -> Creating Work Orders...")
        stmt = select(Problem).where(Problem.title == "Pothole on MG Road")
        result = await db.execute(stmt)
        pothole_prob = result.scalar_one_or_none()
        
        if pothole_prob:
             # Create Contractor
            stmt = select(Contractor).where(Contractor.license_number == "MP-IND-0099")
            result = await db.execute(stmt)
            contractor = result.scalar_one_or_none()
            
            if not contractor:
                contractor = Contractor(
                    name="City Infra Solutions",
                    license_number="MP-IND-0099",
                    specialization=ContractorSpecialization.ROADS,
                    rating=4.5
                )
                db.add(contractor)
                await db.commit()
                await db.refresh(contractor)
                
                # create login for contractor
                contractor_email = "city.infra@contractor.com"
                stmt = select(User).where(User.email == contractor_email)
                result = await db.execute(stmt)
                if not result.scalar_one_or_none():
                    c_user = User(
                        email=contractor_email,
                        hashed_password=get_password_hash("Contractor123"),
                        full_name="City Infra Solutions",
                        role=UserRole.CONTRACTOR,
                        is_active=True
                    )
                    db.add(c_user)
                    await db.commit()

            # Create Contractor 2
            stmt = select(Contractor).where(Contractor.license_number == "MP-Z1-8822")
            result = await db.execute(stmt)
            if not result.scalar_one_or_none():
                c2 = Contractor(
                    name="Indore Smart Lighting",
                    license_number="MP-Z1-8822",
                    specialization=ContractorSpecialization.ELECTRICITY,
                    rating=4.8
                )
                db.add(c2)
                await db.commit()

            # Check if WO exists
            stmt = select(WorkOrder).where(WorkOrder.problem_id == pothole_prob.id)
            result = await db.execute(stmt)
            if not result.scalar_one_or_none():
                wo = WorkOrder(
                    problem_id=pothole_prob.id,
                    contractor_id=contractor.id,
                    estimated_cost=45000.0,
                    status=WorkOrderStatus.APPROVED,
                    official_approver_id=engineer_user.id, 
                    signed_by_name="Suman Rao (Executive Engineer)"
                )
                db.add(wo)
                await db.commit()
                print("     o Created Approved WO for Pothole (Audited Signature)")

                # Create Official Response
                resp = GovernmentResponse(
                    problem_id=pothole_prob.id,
                    official_id=engineer_user.id,
                    response_text="Work order for MG Road pothole repairs has been approved. PWD Zone 1 team is coordinating with the contractor.",
                    action_plan="Immediate cold-mix filling followed by resurfacing.",
                    signed_by_name="Suman Rao (Executive Engineer)"
                )
                db.add(resp)
        
        await db.commit()
        print("✅ Seeding Complete!")

if __name__ == "__main__":
    asyncio.run(seed_data())
