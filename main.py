from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import requests
from datetime import datetime, timezone

app = FastAPI()

@app.middleware("http")
async def add_cors_headers(request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


@app.get("/api/classify")
def classify_name(name: str = Query(default=None)):

    if name is None or name.strip() == "":
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "Name parameter is required"}
        )

    try:
       
        response = requests.get(
            "https://api.genderize.io/",
            params={"name": name},
            timeout=5  # ✅ prevents hanging
        )

        if response.status_code != 200:
            return JSONResponse(
                status_code=502,
                content={"status": "error", "message": "External API error"}
            )

        data = response.json()

        gender = data.get("gender")
        probability = data.get("probability")
        count = data.get("count")

        
        if gender is None or count == 0:
            return JSONResponse(
                status_code=422,
                content={
                    "status": "error",
                    "message": "No prediction available for the provided name"
                }
            )

      
        is_confident = (probability >= 0.7) and (count >= 100)

    
        processed_at = datetime.now(timezone.utc).isoformat()

        return {
            "status": "success",
            "data": {
                "name": name.lower(),
                "gender": gender,
                "probability": probability,
                "sample_size": count, 
                "is_confident": is_confident,
                "processed_at": processed_at
            }
        }

    except requests.exceptions.RequestException:
        return JSONResponse(
            status_code=502,
            content={"status": "error", "message": "External API failure"}
        )

    except Exception:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": "Internal server error"}
        )
