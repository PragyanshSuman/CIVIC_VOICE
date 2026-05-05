from typing import List
from uuid import UUID

class PushNotificationService:
    """
    Service for sending push notifications.
    Currently a mock adapter ready for Firebase/FCM integration.
    """
    
    def __init__(self):
        # Initialize FCM client here
        # self.fcm = firebase_admin.messaging
        pass

    async def send_to_user(self, user_id: UUID, title: str, body: str, data: dict = None):
        """
        Send a push notification to a specific user.
        In a real implementation, look up user's FCM token from DB and send.
        """
        # mock sending
        print(f"[PUSH] Sending to {user_id}: {title} - {body}")
        
        # Future implementation:
        # device_tokens = await user_repo.get_device_tokens(user_id)
        # for token in device_tokens:
        #     message = networking.Message(
        #         notification=networking.Notification(title=title, body=body),
        #         token=token,
        #         data=data
        #     )
        #     response = self.fcm.send(message)

    async def send_to_topic(self, topic: str, title: str, body: str):
        """
        Send to a topic (e.g. "all_citizens_nyc")
        """
        print(f"[PUSH] Sending to topic {topic}: {title} - {body}")
