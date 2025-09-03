from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .models import LeaveRequest
from .forms import LeaveRequestForm

# employee = normal user (not staff, not superuser)
def is_employee(user):
    return user.is_authenticated and not user.is_staff and not user.is_superuser

# staff = HR (is_staff = True, but not superuser)
def is_staff_user(user):
    return user.is_authenticated and user.is_staff and not user.is_superuser

# superuser (admin)
def is_superuser(user):
    return user.is_authenticated and user.is_superuser


# ---------------- Employee Views ----------------
@login_required
@user_passes_test(is_employee)
def employee_leave_list(request):
    leaves = LeaveRequest.objects.filter(employee=request.user)
    return render(request, "leaves/employee_leave_list.html", {"leaves": leaves})

@login_required
@user_passes_test(is_employee)
def leave_create(request):
    if request.method == "POST":
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.employee = request.user
            leave.save()
            return redirect("employee_leave_list")
    else:
        form = LeaveRequestForm()
    return render(request, "leaves/leave_form.html", {"form": form})


# ---------------- Staff (HR) Views ----------------
@login_required
@user_passes_test(is_staff_user)
def staff_leave_list(request):
    # staff can see only employee leaves (exclude superuser & staff requests)
    leaves = LeaveRequest.objects.filter(employee__is_staff=False, employee__is_superuser=False)
    return render(request, "leaves/staff_leave_list.html", {"leaves": leaves})

@login_required
@user_passes_test(is_staff_user)
def approve_leave(request, pk):
    leave = get_object_or_404(LeaveRequest, pk=pk)

    # staff cannot approve their own requests
    if leave.employee == request.user:
        return redirect("staff_leave_list")

    leave.status = "approved"
    leave.save()
    return redirect("staff_leave_list")

@login_required
@user_passes_test(is_staff_user)
def reject_leave(request, pk):
    leave = get_object_or_404(LeaveRequest, pk=pk)

    if leave.employee == request.user:
        return redirect("staff_leave_list")

    leave.status = "rejected"
    leave.save()
    return redirect("staff_leave_list")


# ---------------- Superuser Views ----------------
@login_required
@user_passes_test(is_superuser)
def admin_leave_list(request):
    leaves = LeaveRequest.objects.all()
    return render(request, "leaves/admin_leave_list.html", {"leaves": leaves})

@login_required
@user_passes_test(is_superuser)
def delete_leave(request, pk):
    leave = get_object_or_404(LeaveRequest, pk=pk)
    leave.delete()
    return redirect("admin_leave_list")
from django.shortcuts import render

def home(request):
    return render(request, "home.html")
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import LeaveRequest
from .forms import LeaveRequestForm

def home(request):
    return redirect("leave-list")

@login_required
def leave_list(request):
    leaves = LeaveRequest.objects.all()
    return render(request, "leaves/leave_list.html", {"leaves": leaves})

@login_required
def leave_detail(request, pk):
    leave = get_object_or_404(LeaveRequest, pk=pk)
    return render(request, "leaves/leave_detail.html", {"leave": leave})

@login_required
def leave_create(request):
    if request.method == "POST":
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.user = request.user
            leave.save()
            return redirect("leave-list")
    else:
        form = LeaveRequestForm()
    return render(request, "leaves/leave_form.html", {"form": form})

@login_required
def leave_delete(request, pk):
    leave = get_object_or_404(LeaveRequest, pk=pk)
    if request.method == "POST":
        leave.delete()
        return redirect("leave-list")
    return render(request, "leaves/leave_confirm_delete.html", {"leave": leave})

@login_required
def leave_update(request, pk):
    leave = get_object_or_404(LeaveRequest, pk=pk, user=request.user)
    if request.method == "POST":
        form = LeaveRequestForm(request.POST, instance=leave)
        if form.is_valid():
            form.save()
            return redirect("leave-list")
    else:
        form = LeaveRequestForm(instance=leave)
    return render(request, "leaves/leave_form.html", {"form": form})
from django.contrib import messages

@login_required
@user_passes_test(lambda u: u.is_superuser)  # ✅ only superuser can approve/reject
def approve_leave(request, pk):
    leave = get_object_or_404(LeaveRequest, pk=pk)
    leave.status = "Approved"
    leave.save()
    messages.success(request, "Leave request approved ✅")
    return redirect("leave-list")


@login_required
@user_passes_test(lambda u: u.is_superuser)  # ✅ only superuser can reject
def reject_leave(request, pk):
    leave = get_object_or_404(LeaveRequest, pk=pk)
    leave.status = "Rejected"
    leave.save()
    messages.warning(request, "Leave request rejected ❌")
    return redirect("leave-list")

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import LeaveRequest
from .forms import LeaveRequestForm

def is_staff(user):
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(is_staff)
def approve_leave(request, pk):
    leave = get_object_or_404(LeaveRequest, pk=pk)
    leave.status = "Approved"
    leave.save()
    messages.success(request, f"Leave request by {leave.employee.username} approved ✅")
    return redirect("leave-list")

@login_required
@user_passes_test(is_staff)
def reject_leave(request, pk):
    leave = get_object_or_404(LeaveRequest, pk=pk)
    leave.status = "Rejected"
    leave.save()
    messages.warning(request, f"Leave request by {leave.employee.username} rejected ❌")
    return redirect("leave-list")


@login_required
@user_passes_test(is_staff)  # staff and superuser allowed
def approve_leave(request, pk):
    leave = get_object_or_404(LeaveRequest, pk=pk)

    # prevent staff from approving their own leave
    if leave.employee == request.user and not request.user.is_superuser:
        messages.error(request, "You cannot approve your own leave ❌")
        return redirect("leave-detail", pk=pk)

    leave.status = "Approved"
    leave.save()
    messages.success(request, f"Leave request by {leave.employee.username} approved ✅")
    return redirect("leave-list")


@login_required
@user_passes_test(is_staff)  # staff and superuser allowed
def reject_leave(request, pk):
    leave = get_object_or_404(LeaveRequest, pk=pk)

    # prevent staff from rejecting their own leave
    if leave.employee == request.user and not request.user.is_superuser:
        messages.error(request, "You cannot reject your own leave ❌")
        return redirect("leave-detail", pk=pk)

    leave.status = "Rejected"
    leave.save()
    messages.warning(request, f"Leave request by {leave.employee.username} rejected ❌")
    return redirect("leave-list")
