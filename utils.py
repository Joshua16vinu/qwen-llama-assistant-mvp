import json
import os
import firebase_admin
from firebase_admin import credentials, firestore

# Firebase initialization
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)
db = firestore.client()

MEMORY_FILE = "memory.json"
GOAL_FILE = "goals.json"
GOAL_COLLECTION = "financial_goals"


# ---------------- Memory ----------------
def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return []
    with open(MEMORY_FILE, "r") as f:
        data = json.load(f)
    if len(data) > 4:
        data = data[-4:]
    return data

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

def sync_chat_to_firebase(memory, user_id="demo_user"):
    try:
        doc_ref = db.collection("users").document(user_id)
        doc_ref.set({"chat_history": memory})
        print("✅ Synced chat memory to Firestore.")
    except Exception as e:
        print(f"❌ Firebase sync failed: {e}")


# ---------------- SIP Calculator ----------------
def calculate_sip(monthly_investment, years, rate=0.12):
    months = years * 12
    r = rate / 12
    future_value = monthly_investment * (((1 + r)**months - 1) / r) * (1 + r)
    return round(future_value, 2)

def sync_sip_to_firebase(monthly, years, rate, result, user_id="demo_user"):
    try:
        doc_ref = db.collection("users").document(user_id).collection("sip_calculations").document()
        doc_ref.set({
            "monthly": monthly,
            "years": years,
            "rate": rate,
            "result": result,
            "timestamp": firestore.SERVER_TIMESTAMP
        })
        print("✅ Synced SIP calculation to Firestore.")
    except Exception as e:
        print(f"❌ SIP sync failed: {e}")


# ---------------- EMI Calculator ----------------
def calculate_emi(principal: float, annual_rate: float, tenure_years: int):
    monthly_rate = annual_rate / (12 * 100)
    months = tenure_years * 12
    if monthly_rate == 0:
        emi = principal / months
    else:
        emi = (principal * monthly_rate * (1 + monthly_rate) ** months) / ((1 + monthly_rate) ** months - 1)
    total_payment = emi * months
    total_interest = total_payment - principal
    return round(emi, 2), round(total_payment, 2), round(total_interest, 2)

def sync_emi_to_firebase(principal, rate, tenure, emi, total_payment, total_interest, user_id="demo_user"):
    try:
        doc_ref = db.collection("users").document(user_id).collection("emi_calculations").document()
        doc_ref.set({
            "principal": principal,
            "rate": rate,
            "tenure_years": tenure,
            "emi": emi,
            "total_payment": total_payment,
            "total_interest": total_interest,
            "timestamp": firestore.SERVER_TIMESTAMP
        })
        print("✅ Synced EMI calculation to Firestore.")
    except Exception as e:
        print(f"❌ EMI sync failed: {e}")


# ---------------- Goal Tracker ----------------
def add_goal(name: str, target: float, duration_months: int):
    doc_ref = db.collection(GOAL_COLLECTION).document()
    doc_ref.set({
        "name": name,
        "target": target,
        "duration_months": duration_months,
        "saved": 0
    })

def load_goals():
    docs = db.collection(GOAL_COLLECTION).stream()
    return [{"id": doc.id, **doc.to_dict()} for doc in docs]

def update_goal(doc_id: str, saved_amount: float):
    db.collection(GOAL_COLLECTION).document(doc_id).update({
        "saved": saved_amount
    })

