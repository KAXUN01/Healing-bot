from fastapi import FastAPI, Request
from ddos_detector import predict_ddos

app = FastAPI()

# Set a sensible threshold; you can tune this later
DDOS_THRESHOLD = 0.7

@app.post("/alerts")
async def process_alert(request: Request):
    alert_json = await request.json()
    
    # Extract relevant features for your model from alert_json 
    # *** This part heavily depends on what features you used in training ***
    # Example placeholder:
    features = extract_features_from_alert(alert_json)  # implement this function
    
    ddos_prob = predict_ddos(features)
    
    alert_json['ddos_detection'] = {
        'detected': ddos_prob > DDOS_THRESHOLD,
        'confidence': ddos_prob
    }
    
    # Optionally modify AI prompt or add healing action recommendations here
    
    # ... existing processing logic ...
    
    return {"status": "alert processed", "ddos_prob": ddos_prob}
