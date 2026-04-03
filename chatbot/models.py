from django.db import models
from django.conf import settings


class ChatMessage(models.Model):
    """Store chatbot conversation messages"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_messages')

    # New schema-friendly fields
    message = models.TextField(blank=True, null=True)
    response = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_user = models.BooleanField(default=True)

    # Legacy compatibility fields used by older parts of the project
    user_message = models.TextField(blank=True, null=True)
    bot_response = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Chat for {self.user.username} - {self.created_at}"

    def save(self, *args, **kwargs):
        # Keep old/new fields synchronized to avoid breaking existing views.
        if not self.message and self.user_message:
            self.message = self.user_message
        if not self.user_message and self.message and self.is_user:
            self.user_message = self.message
        if not self.response and self.bot_response:
            self.response = self.bot_response
        if not self.bot_response and self.response:
            self.bot_response = self.response
        super().save(*args, **kwargs)


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
