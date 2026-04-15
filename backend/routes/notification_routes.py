from fastapi import APIRouter

router = APIRouter(prefix="/notifications", tags=["Notifications"])

notifications = []

@router.get("/")
def get_notifications():
    return notifications

@router.post("/")
def create_notification(message: str):
    notifications.append({"message": message})
    return {"msg": "Notification added"}