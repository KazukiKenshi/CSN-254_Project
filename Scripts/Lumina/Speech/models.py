from django.db import models

class ChatMessage(models.Model):
    ROLE_CHOICES = [
        ('system','System'),
        ('user','User'),
        ('assistant','Assistant')
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.timestamp} - {self.role}: {self.content}"
