from django.shortcuts import render, redirect
from .models import Notification
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required


@login_required
@role_required(['USER'])
def user_notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')

    print("Logged user:", request.user)
    print("Notifications count:", notifications.count())

    return render(request, 'user/dashboard/user_notifications.html', {
        'notifications': notifications
    })

@login_required
@role_required(['USER'])
def mark_as_read(request, id):
    n = Notification.objects.get(id=id)
    n.is_read = True
    n.save()
    return redirect('notifications')