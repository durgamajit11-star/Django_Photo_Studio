import json
import re

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .models import ChatMessage, ChatbotFAQ


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
    """Generate chatbot response based on user message."""

    text = (user_message or '').strip().lower()
    if not text:
        return "Please type a question and I’ll help."

    faq_answer = match_faq_answer(text)
    if faq_answer:
        return faq_answer

    if contains_any(text, ['hello', 'hi', 'hey', 'greet', 'good morning', 'good evening']):
        return (
            "Hello! I’m the StudioSync assistant. I can explain the platform, bookings, payments, reviews, "
            "dashboards, and studio-owner tools."
        )

    if contains_any(text, ['what can you do', 'help me', 'platform', 'functionality', 'features', 'how does it work']):
        return platform_overview(user)

    if contains_any(text, ['book', 'booking', 'reserve', 'reservation', 'studio booking']):
        return (
            "Bookings work like this: browse studios, open a studio profile, choose a date, time slot, and any "
            "extra service, then complete payment to confirm the booking."
        )

    if contains_any(text, ['price', 'cost', 'rate', 'charges', 'pricing', 'budget']):
        return (
            "Pricing depends on the studio, its hourly rate, services, and any camera add-ons. You can compare "
            "studios by location, rating, and budget before booking."
        )

    if contains_any(text, ['payment', 'pay', 'refund', 'transaction', 'upi']):
        return (
            "Payments are handled from the booking and payment pages. You can review the amount, choose a "
            "payment method, and request a refund from payment history where supported."
        )

    if contains_any(text, ['review', 'rating', 'feedback']):
        return (
            "Reviews can be posted after a confirmed booking. Users can write, edit, or delete their own reviews, "
            "and studio owners can view all client reviews from their dashboard."
        )

    if contains_any(text, ['profile', 'account', 'settings', 'preferences']):
        return (
            "Your profile settings are in the dashboard. Users manage account details there, and studio owners can "
            "also update studio name, contact details, services, and cover image."
        )

    if contains_any(text, ['dashboard', 'menu', 'navigation', 'sidebar']):
        return dashboard_overview(user)

    if contains_any(text, ['studio owner', 'studio dashboard', 'portfolio', 'earnings']):
        return (
            "Studio owners can manage dashboard stats, portfolio uploads, bookings, earnings, reviews, and studio "
            "profile details from the studio panel."
        )

    if contains_any(text, ['admin', 'moderation', 'manage users', 'manage studios']):
        return (
            "Admins can review users, manage admin accounts, approve or reject studios, inspect bookings, and "
            "monitor payment activity from the admin console."
        )

    if contains_any(text, ['support', 'contact', 'help', 'issue', 'problem']):
        return (
            "If you need help, ask here about bookings, payments, reviews, dashboards, or studio setup. I’ll "
            "translate the platform flow into simple steps."
        )

    if contains_any(text, ['thank', 'thanks', 'appreciate']):
        return "You’re welcome. If you want, I can also explain any page or workflow step by step."

    return platform_overview(user)


def contains_any(text, phrases):
    return any(phrase in text for phrase in phrases)


def match_faq_answer(text):
    faqs = ChatbotFAQ.objects.filter(active=True)
    best_score = 0
    best_answer = None

    for faq in faqs:
        score = 0
        question = (faq.question or '').lower()
        keywords = [keyword.strip().lower() for keyword in (faq.keywords or '').split(',') if keyword.strip()]

        for keyword in keywords:
            if keyword and keyword in text:
                score += 3

        for word in re.findall(r'[a-z0-9]+', question):
            if word in text:
                score += 1

        if question and question in text:
            score += 5

        if score > best_score:
            best_score = score
            best_answer = faq.answer

    if best_score >= 2:
        return best_answer

    return None


def platform_overview(user):
    role = getattr(user, 'role', '').upper()

    if role == 'USER':
        return (
            "StudioSync lets users explore studios, compare locations and prices, book time slots, pay online, "
            "track bookings, leave reviews, and manage notifications and profile details from the user dashboard."
        )

    if role == 'STUDIO':
        return (
            "StudioSync helps studio owners manage portfolio images, studio profile details, services, bookings, "
            "earnings, and client reviews from the studio dashboard."
        )

    if role == 'ADMIN':
        return (
            "StudioSync admin tools cover user management, admin moderation, studio approval, booking oversight, "
            "and payment tracking from the admin panel."
        )

    return (
        "StudioSync is a photo studio booking platform. Users can explore studios, book sessions, pay online, and "
        "write reviews, while studio owners and admins manage listings, bookings, and operations from their dashboards."
    )


def dashboard_overview(user):
    role = getattr(user, 'role', '').upper()

    if role == 'USER':
        return (
            "User dashboard features include bookings, recommendations, reviews, payments, notifications, and profile "
            "settings. You can also browse studios from the explore page."
        )

    if role == 'STUDIO':
        return (
            "Studio dashboard features include studio stats, portfolio management, booking approvals, earnings, client "
            "reviews, and profile/service editing."
        )

    if role == 'ADMIN':
        return (
            "Admin dashboard features include user moderation, studio approval, booking monitoring, and payment "
            "tracking."
        )

    return platform_overview(user)


@login_required
def clear_chat_history(request):
    """Clear chat history for the current user"""
    try:
        ChatMessage.objects.filter(user=request.user).delete()
        return JsonResponse({'success': True, 'message': 'Chat history cleared'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

