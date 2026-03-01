from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required
from accounts.forms import UserUpdateForm
from django.contrib import messages


@login_required
@role_required(['USER'])
def user_dashboard(request):
    return render(request, 'user/dashboard/user_dashboard.html')

@login_required
@role_required(['USER'])
def user_profile(request):

    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
    else:
        form = UserUpdateForm(instance=request.user)

    return render(request, 'user/dashboard/user_profile.html', {'form': form})


@login_required
@role_required(['USER'])
def user_bookings(request):
    return render(request, 'user/dashboard/user_bookings.html')

@login_required
@role_required(['USER'])
def user_recommendations(request):
    return render(request, 'user/dashboard/user_recommendations.html')


@login_required
@role_required(['USER'])
def explore_studios(request):
    return render(request, 'user/dashboard/explore_studios.html')


@login_required
@role_required(['USER'])
def user_reviews(request):
    return render(request, 'user/dashboard/user_reviews.html')


@login_required
@role_required(['USER'])
def user_payments(request):
    return render(request, 'user/dashboard/user_payments.html')


@login_required
@role_required(['USER'])
def user_notifications(request):
    return render(request, 'user/dashboard/user_notifications.html')


@login_required
@role_required(['STUDIO'])
def studio_dashboard(request):
    return render(request, 'studio/dashboard/studio_dashboard.html')


@login_required
@role_required(['ADMIN'])
def admin_dashboard(request):
    return render(request, 'admin/dashboard/admin_dashboard.html')