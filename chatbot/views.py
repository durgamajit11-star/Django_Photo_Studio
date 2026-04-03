from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import ChatMessage
import json


@login_required
@require_http_methods(["GET", "POST"])
def chatbot_messages(request):
    """Handle chatbot messages via AJAX"""
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()
            
            if not user_message:
                return JsonResponse({'error': 'Message cannot be empty'}, status=400)
            
            # Save user message
            chat = ChatMessage.objects.create(
                user=request.user,
                message=user_message,
                user_message=user_message,
                is_user=True
            )
            
            # Generate AI response
            bot_response = generate_bot_response(user_message, request.user)
            
            # Save bot response
            ChatMessage.objects.create(
                user=request.user,
                message=bot_response,
                response=bot_response,
                bot_response=bot_response,
                is_user=False
            )
            
            return JsonResponse({
                'user_message': user_message,
                'bot_response': bot_response,
                'success': True
            })
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    # GET: Retrieve chat history
    if request.method == 'GET':
        messages = ChatMessage.objects.filter(user=request.user).order_by('timestamp')[:50]
        message_list = [
            {
                'message': msg.message,
                'is_user': msg.is_user,
                'timestamp': msg.timestamp.isoformat()
            }
            for msg in messages
        ]
        return JsonResponse({'messages': message_list})
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


def generate_bot_response(user_message, user):
    """Generate chatbot response based on user message"""
    
    user_message_lower = user_message.lower()
    
    # Simple keyword-based responses
    if any(word in user_message_lower for word in ['hello', 'hi', 'hey', 'greet']):
        return f"Hello! 👋 I'm the StudioSync assistant. How can I help you find the perfect photo studio today?"
    
    elif any(word in user_message_lower for word in ['book', 'booking', 'reserve']):
        return "📸 I can help you book a studio! Browse our featured studios or search by location, budget, or photography type."
    
    elif any(word in user_message_lower for word in ['price', 'cost', 'rate', 'charges']):
        return "💰 Pricing varies by studio and service. You can filter studios by price range (Budget, Standard, Premium) in our search filters."
    
    elif any(word in user_message_lower for word in ['cancel', 'refund', 'payment']):
        return "If you need to cancel or modify a booking, please contact the studio directly or visit your bookings page for options."
    
    elif any(word in user_message_lower for word in ['profile', 'account', 'setting']):
        return "⚙️ You can manage your profile, bookings, and preferences from your dashboard. Click on 'Profile' to get started!"
    
    elif any(word in user_message_lower for word in ['help', 'support', 'contact']):
        return "📞 For additional support, please check our FAQ or contact our support team. We're here to help!"
    
    elif any(word in user_message_lower for word in ['review', 'rating', 'feedback']):
        return "⭐ After your shoot, you can leave a review for the studio. This helps other users find great studios!"
    
    elif any(word in user_message_lower for word in ['thank', 'thanks', 'appreciate']):
        return "You're welcome! 🙌 Feel free to ask me anything about finding and booking studios."
    
    elif any(word in user_message_lower for word in ['weather', 'how are you', 'time']):
        return "I'm a photography studio booking assistant. I'm here to help you find the perfect studio for your needs!"
    
    else:
        return "I'm here to help with studio booking, pricing, bookings, and more. What would you like to know?"


@login_required
def clear_chat_history(request):
    """Clear chat history for the current user"""
    try:
        ChatMessage.objects.filter(user=request.user).delete()
        return JsonResponse({'success': True, 'message': 'Chat history cleared'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

