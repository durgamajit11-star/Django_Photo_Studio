from django.db import models
from django.conf import settings


class ChatMessage(models.Model):
    """Store chatbot conversation messages"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_messages')
    
    user_message = models.TextField()
    bot_response = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Chat for {self.user.username} - {self.created_at}"


class ChatSession(models.Model):
    """Group related chat messages into sessions"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_sessions')
    
    title = models.CharField(max_length=200, blank=True, null=True)
    ended = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Session for {self.user.username}"


class ChatbotFAQ(models.Model):
    """FAQ entries for the chatbot"""
    question = models.CharField(max_length=300)
    answer = models.TextField()
    category = models.CharField(max_length=100, blank=True, null=True)
    keywords = models.TextField(help_text="Comma-separated keywords for matching")
    
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'question']
        verbose_name = 'Chatbot FAQ'
        verbose_name_plural = 'Chatbot FAQs'

    def __str__(self):
        return self.question
