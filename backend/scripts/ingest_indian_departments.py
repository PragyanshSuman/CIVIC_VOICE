import asyncio
import sys
import os
import httpx
from sqlalchemy import select
from sqlalchemy.orm import configure_mappers
import uuid

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import AsyncSessionLocal
from app.models.department import Department

# Wikidata SPARQL Endpoint
WIKIDATA_URL = "https://query.wikidata.org/sparql"

SPARQL_QUERY = """
SELECT ?item ?itemLabel ?logo ?website ?description WHERE {
  ?item (wdt:P31/wdt:P279*) wd:Q26553; # Instance of or subclass of government agency
        wdt:P17 wd:Q668.               # In India
  OPTIONAL { ?item wdt:P154 ?logo. }
  OPTIONAL { ?item wdt:P856 ?website. }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
  OPTIONAL {
    ?item schema:description ?description.
    FILTER(LANG(?description) = "en")
  }
}
LIMIT 100
"""

async def ingest_departments():
    print("🚀 Connecting to Wikidata SPARQL Engine...")
    headers = {
        "User-Agent": "CivicOS-Bot/1.0 (https://github.com/example/civic-platform)",
        "Accept": "application/sparql-results+json"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(WIKIDATA_URL, params={'query': SPARQL_QUERY}, headers=headers)
        if response.status_code != 200:
            print(f"❌ Failed to fetch data: {response.status_code}")
            return
        
        data = response.json()
        results = data['results']['bindings']
        print(f"📦 Received {len(results)} potential departments from Wikidata.")

        async with AsyncSessionLocal() as db:
            for row in results:
                wikidata_url = row['item']['value']
                wikidata_id = wikidata_url.split('/')[-1]
                name = row['itemLabel']['value']
                logo_url = row.get('logo', {}).get('value')
                website_url = row.get('website', {}).get('value')
                description = row.get('description', {}).get('value', f"Official department: {name}")

                # Create a unique code based on name
                code = "".join(filter(str.isalnum, name.upper()))[:20] + "-" + wikidata_id

                # Check if exists
                stmt = select(Department).where(Department.wikidata_id == wikidata_id)
                res = await db.execute(stmt)
                existing = res.scalar_one_or_none()

                if not existing:
                    print(f"✨ Adding: {name}")
                    new_dept = Department(
                        name=name,
                        code=code,
                        description=description,
                        logo_url=logo_url,
                        website_url=website_url,
                        wikidata_id=wikidata_id,
                        sla_config={"default": 48},
                        workflow_config={"default": ["OPEN", "IN_PROGRESS", "RESOLVED"]}
                    )
                    db.add(new_dept)
                else:
                    # Update existing with latest info
                    existing.logo_url = logo_url
                    existing.website_url = website_url
                    existing.description = description
                    print(f"🔄 Updated: {name}")

            await db.commit()
            print("✅ Master Ingest Complete!")

if __name__ == "__main__":
    asyncio.run(ingest_departments())
