import json
import re

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.http import require_http_methods

from .models import ChatMessage, ChatbotFAQ


ROLE_ALLOWED_INTENTS = {
    'USER': {
        'greeting', 'platform_overview', 'booking_help', 'pricing_help', 'payment_help',
        'review_help', 'profile_help', 'dashboard_help', 'support', 'thanks', 'unknown'
    },
    'STUDIO': {
        'greeting', 'platform_overview', 'booking_help', 'pricing_help', 'payment_help',
        'review_help', 'profile_help', 'dashboard_help', 'studio_ops', 'support', 'thanks', 'unknown'
    },
    'ADMIN': {
        'greeting', 'platform_overview', 'booking_help', 'payment_help', 'dashboard_help',
        'admin_ops', 'support', 'thanks', 'unknown'
    },
}

INTENT_HINT = {
    'studio_ops': 'studio-owner workflows',
    'admin_ops': 'admin workflows',
}


@login_required
@require_http_methods(["GET", "POST"])
def chatbot_messages(request):
    """Backward-compatible chatbot endpoint that auto-selects the user's role."""
    return _chatbot_messages_for_role(request, expected_role=None)


@login_required
@require_http_methods(["GET", "POST"])
def chatbot_messages_user(request):
    return _chatbot_messages_for_role(request, expected_role='USER')


@login_required
@require_http_methods(["GET", "POST"])
def chatbot_messages_studio(request):
    return _chatbot_messages_for_role(request, expected_role='STUDIO')


@login_required
@require_http_methods(["GET", "POST"])
def chatbot_messages_admin(request):
    return _chatbot_messages_for_role(request, expected_role='ADMIN')


def _chatbot_messages_for_role(request, expected_role=None):
    role = get_user_role(request.user)

    if expected_role and role != expected_role:
        return JsonResponse(
            {
                'error': 'Forbidden',
                'message': f'This chatbot endpoint is restricted to {expected_role.lower()} role.'
            },
            status=403,
        )

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()

            if not user_message:
                return JsonResponse({'error': 'Message cannot be empty'}, status=400)

            ChatMessage.objects.create(
                user=request.user,
                message=user_message,
                user_message=user_message,
                is_user=True,
                role_at_message_time=role,
            )

            bot_response, blocked_reason, policy_notice, response_mode = generate_bot_response(user_message, request.user)
            was_blocked = blocked_reason is not None

            ChatMessage.objects.create(
                user=request.user,
                message=bot_response,
                response=bot_response,
                bot_response=bot_response,
                is_user=False,
                role_at_message_time=role,
                policy_blocked=was_blocked,
                blocked_reason=blocked_reason,
                response_mode=response_mode,
            )

            return JsonResponse(
                {
                    'user_message': user_message,
                    'bot_response': bot_response,
                    'success': True,
                    'role': role,
                    'policy_blocked': was_blocked,
                    'policy_notice': policy_notice,
                    'response_mode': response_mode,
                }
            )
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as exc:
            return JsonResponse({'error': str(exc)}, status=500)

    messages = (
        ChatMessage.objects.filter(user=request.user)
        .filter(Q(role_at_message_time=role) | Q(role_at_message_time='UNKNOWN'))
        .order_by('timestamp')[:50]
    )
    message_list = [
        {
            'message': msg.message,
            'is_user': msg.is_user,
            'timestamp': msg.timestamp.isoformat(),
            'role': msg.role_at_message_time,
            'policy_blocked': msg.policy_blocked,
        }
        for msg in messages
    ]
    return JsonResponse({'messages': message_list, 'role': role})


def generate_bot_response(user_message, user):
    """Generate chatbot response based on user message."""

    text = (user_message or '').strip().lower()
    role = get_user_role(user)

    if not text:
        return "Please type a question and I’ll help.", None, None, 'fallback'

    intent = classify_intent(text)
    allowed_intents = ROLE_ALLOWED_INTENTS.get(role, set())
    if intent not in allowed_intents:
        target = INTENT_HINT.get(intent, 'restricted workflows')
        blocked_reason = f'{intent} is not allowed for role {role}.'
        policy_notice = build_policy_notice(role, intent, blocked=True)
        return (
            f"I can’t share {target} in this account. Please use the correct role dashboard for that request.",
            blocked_reason,
            policy_notice,
            'guardrail',
        )

    faq_answer = match_faq_answer(text, role)
    if faq_answer:
        return faq_answer, None, None, 'faq_hit'

    if intent == 'greeting':
        return (
            "Hello! I’m the StudioSync assistant. I can explain the platform, bookings, payments, reviews, "
            "dashboards, and studio-owner tools."
        ), None, None, 'intent_answer'

    if intent == 'platform_overview':
        return platform_overview(user), None, None, 'intent_answer'

    if intent == 'booking_help':
        return (
            "Bookings work like this: browse studios, open a studio profile, choose a date, time slot, and any "
            "extra service, then complete payment to confirm the booking."
        ), None, None, 'intent_answer'

    if intent == 'pricing_help':
        return (
            "Pricing depends on the studio, its hourly rate, services, and any camera add-ons. You can compare "
            "studios by location, rating, and budget before booking."
        ), None, None, 'intent_answer'

    if intent == 'payment_help':
        return (
            "Payments are handled from the booking and payment pages. You can review the amount, choose a "
            "payment method, and request a refund from payment history where supported."
        ), None, None, 'intent_answer'

    if intent == 'review_help':
        return (
            "Reviews can be posted after a confirmed booking. Users can write, edit, or delete their own reviews, "
            "and studio owners can view all client reviews from their dashboard."
        ), None, None, 'intent_answer'

    if intent == 'profile_help':
        return (
            "Your profile settings are in the dashboard. Users manage account details there, and studio owners can "
            "also update studio name, contact details, services, and cover image."
        ), None, None, 'intent_answer'

    if intent == 'dashboard_help':
        return dashboard_overview(user), None, None, 'intent_answer'

    if intent == 'studio_ops':
        return (
            "Studio owners can manage dashboard stats, portfolio uploads, bookings, earnings, reviews, and studio "
            "profile details from the studio panel."
        ), None, None, 'intent_answer'

    if intent == 'admin_ops':
        admin_response = (
            "Admin operations checklist:\n"
            "1. Confirm the target entity (user, studio, booking, or payment).\n"
            "2. Verify supporting evidence and recent activity logs.\n"
            "3. Apply the minimal action required by policy.\n"
            "4. Record reason and outcome in admin notes."
        )
        return admin_response, None, build_policy_notice(role, intent, blocked=False), 'admin_safe'

    if intent == 'support':
        return (
            "If you need help, ask here about bookings, payments, reviews, dashboards, or studio setup. I’ll "
            "translate the platform flow into simple steps."
        ), None, None, 'intent_answer'

    if intent == 'thanks':
        return "You’re welcome. If you want, I can also explain any page or workflow step by step.", None, None, 'intent_answer'

    return platform_overview(user), None, None, 'fallback'


def build_policy_notice(role, intent, blocked):
    if blocked:
        return f'Access boundary enforced: intent {intent} is not available for role {role}.'

    if role == 'ADMIN' and intent == 'admin_ops':
        return 'Safety mode active: validate evidence and record action rationale before administrative changes.'

    return None


def get_user_role(user):
    role = getattr(user, 'role', '')
    role = (role or '').upper()
    if role in ROLE_ALLOWED_INTENTS:
        return role
    return 'USER'


def classify_intent(text):
    if contains_any(text, ['hello', 'hi', 'hey', 'greet', 'good morning', 'good evening']):
        return 'greeting'
    if contains_any(text, ['what can you do', 'platform', 'functionality', 'features', 'how does it work']):
        return 'platform_overview'
    if contains_any(text, ['book', 'booking', 'reserve', 'reservation', 'studio booking']):
        return 'booking_help'
    if contains_any(text, ['price', 'cost', 'rate', 'charges', 'pricing', 'budget']):
        return 'pricing_help'
    if contains_any(text, ['payment', 'pay', 'refund', 'transaction', 'upi']):
        return 'payment_help'
    if contains_any(text, ['review', 'rating', 'feedback']):
        return 'review_help'
    if contains_any(text, ['profile', 'account', 'settings', 'preferences']):
        return 'profile_help'
    if contains_any(text, ['dashboard', 'menu', 'navigation', 'sidebar']):
        return 'dashboard_help'
    if contains_any(text, ['studio owner', 'studio dashboard', 'portfolio', 'earnings']):
        return 'studio_ops'
    if contains_any(text, ['admin', 'moderation', 'manage users', 'manage studios']):
        return 'admin_ops'
    if contains_any(text, ['support', 'contact', 'help', 'issue', 'problem']):
        return 'support'
    if contains_any(text, ['thank', 'thanks', 'appreciate']):
        return 'thanks'
    return 'unknown'


def contains_any(text, phrases):
    return any(phrase in text for phrase in phrases)


def match_faq_answer(text, role):
    faqs = ChatbotFAQ.objects.filter(active=True).filter(Q(role_scope='ALL') | Q(role_scope=role))
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

