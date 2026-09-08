import calendar
import logging
from datetime import date
from django.http import JsonResponse
from django.utils import timezone

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import CourseForm, EmploymentForm, FollowUpForm, TraineeForm, TrainerRegistrationForm, TrainingBatch,TrainingBatchForm
from .models import Course, Employment, FollowUp, Notification, Provider, Trainee, TrainerRegistration, TrainingBatch, UserProfile,TrainingRegistrationRequest, UANVerification, SelfEmploymentVerification

logger = logging.getLogger(__name__)


def has_role(user, role):
    return user.is_authenticated and (user.is_staff or getattr(getattr(user, "userprofile", None), "role", None) == role)


def authority_required(view):
    return user_passes_test(lambda user: has_role(user, "Authority"))(view)


def trainer_required(view):
    return user_passes_test(lambda user: has_role(user, "Trainer"))(view)


def trainee_required(view):
    return user_passes_test(lambda user: has_role(user, "Trainee"))(view)


def add_months(value, months):
    month = value.month - 1 + months
    year = value.year + month // 12
    month = month % 12 + 1
    return date(year, month, min(value.day, calendar.monthrange(year, month)[1]))


def notify(user, message, notification_type="System", follow_up=None):
    if not user:
        return
    Notification.objects.create(recipient=user, message=message, notification_type=notification_type, follow_up=follow_up)
    if user.email:
        try:
            send_mail("SkillTrack Maharashtra", message, None, [user.email], fail_silently=False)
        except Exception:
            logger.exception("Notification email could not be delivered for user %s", user.pk)


def generate_followups(batch):
    completion_date = batch.completion_date or date.today()
    schedule = [("3 Months", 3), ("6 Months", 6), ("1 Year", 12), ("3 Years", 36), ("5 Years", 60)]
    for trainee in batch.trainees.all():
        employment = Employment.objects.filter(trainee=trainee).first()
        status = employment.status if employment else "Seeking"
        for label, months in schedule:
            follow_up, _ = FollowUp.objects.get_or_create(
                trainee=trainee,
                followup_type=label,
                defaults={"date": add_months(completion_date, months), "employment_status": status},
            )
            profile = UserProfile.objects.filter(trainee=trainee, role="Trainee").select_related("user").first()
            if profile:
                notify(profile.user, f"Your {label.lower()} employment follow-up is scheduled for {follow_up.date:%d %B %Y}.", "Follow-up", follow_up)


def login_view(request):
    if request.user.is_authenticated:
        return redirect_for_user(request.user)
    if request.method == "POST":
        user = authenticate(request, username=request.POST.get("username"), password=request.POST.get("password"))
        if user:
            login(request, user)
            return redirect_for_user(user)
        messages.error(request, "Invalid username or password.")
    return render(request, "login.html")


def redirect_for_user(user):
    role = getattr(getattr(user, "userprofile", None), "role", None)
    if user.is_staff or role == "Authority":
        return redirect("dashboard")
    if role == "Trainer":
        return redirect("trainer_dashboard")
    if role == "Trainee":
        return redirect("trainee_dashboard")
    return redirect("login")


def logout_view(request):
    logout(request)
    return redirect("login")


def trainee_register(request):
    form = TraineeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        trainee = form.save(commit=False)
        trainee.beneficiary_id = f"MH-2026-{(Trainee.objects.order_by('-id').first().id + 1 if Trainee.objects.exists() else 1):06d}"
        trainee.status = "Pending"
        trainee.save()
        return render(request, "trainees/registration_success.html", {"trainee": trainee})
    return render(request, "trainees/trainee_register.html", {"form": form})


def trainer_register(request):
    form = TrainerRegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        trainer = form.save(commit=False)
        trainer.status = "Pending"
        trainer.save()
        messages.success(request, "Registration submitted. The Authority will review it shortly.")
        return redirect("login")
    return render(request, "trainers/trainer_register.html", {"form": form})


@login_required
@authority_required
def dashboard(request):
    trainees = Trainee.objects.all()
    trainers = TrainerRegistration.objects.all()
    providers = Provider.objects.all()
    batches = TrainingBatch.objects.all()
    employments = Employment.objects.all()
    trained = batches.filter(status="Completed").aggregate(total=Count("trainees", distinct=True))["total"]
    employment_total = employments.count()
    context = {
        "total_trainees": trainees.count(), "pending_trainees": trainees.filter(status="Pending").count(), "verified_trainees": trainees.filter(status="Verified").count(),
        "total_trainers": trainers.count(), "verified_trainers": trainers.filter(status="Verified").count(), "total_providers": providers.count(), "verified_providers": providers.filter(status="Verified").count(),
        "total_courses": Course.objects.count(), "active_batches": batches.filter(status="Active").count(), "completed_batches": batches.filter(status="Completed").count(), "trained_trainees": trained,
        "active_training": batches.filter(status="Active").count(), "completed_training": batches.filter(status="Completed").count(),
        "employed": employments.filter(status="Employed").count(), "seeking": employments.filter(status="Seeking").count(), "unemployed": employments.filter(status="Unemployed").count(),
        "employment_rate": round(employments.filter(status="Employed").count() * 100 / employment_total, 1) if employment_total else 0,
        "district_data": list(trainees.values("district").annotate(total=Count("id")).order_by("district")),
        "sector_data": list(Course.objects.values("sector").annotate(total=Count("id")).order_by("sector")),
        "employment_data": list(employments.values("status").annotate(total=Count("id")).order_by("status")),
        "due_followups": FollowUp.objects.filter(completed=False, date__lte=date.today()).select_related("trainee")[:6],
    }
    return render(request, "dashboard.html", context)


@login_required
@authority_required
def trainee_list(request):
    return render(request, "trainees/trainee_list.html", {"trainees": Trainee.objects.all().order_by("-id")})


@login_required
@authority_required
def trainee_detail(request, id):
    return render(request, "trainees/trainee_detail.html", {"trainee": get_object_or_404(Trainee, id=id)})


@login_required
@authority_required
def trainee_create(request):
    form = TraineeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        trainee = form.save(commit=False)
        trainee.beneficiary_id = f"MH-2026-{(Trainee.objects.order_by('-id').first().id + 1 if Trainee.objects.exists() else 1):06d}"
        trainee.save()
        messages.success(request, "Trainee created successfully.")
        return redirect("trainee_list")
    return render(request, "trainees/trainee_form.html", {"form": form})


@login_required
@authority_required
def trainee_update(request, id):
    trainee = get_object_or_404(Trainee, id=id)
    form = TraineeForm(request.POST or None, instance=trainee)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Trainee updated successfully.")
        return redirect("trainee_detail", id=id)
    return render(request, "trainees/trainee_form.html", {"form": form, "trainee": trainee})


@login_required
@authority_required
@require_POST
def verify_trainee(request, id):
    trainee = get_object_or_404(Trainee, id=id)
    trainee.status = "Verified"
    trainee.save(update_fields=["status"])
    user, created = User.objects.get_or_create(username=trainee.beneficiary_id, defaults={"email": trainee.email})
    password = None
    if created:
        password = f"Skill@{trainee.phone[-4:]}"
        user.set_password(password)
        user.save()
    UserProfile.objects.update_or_create(user=user, defaults={"role": "Trainee", "trainee": trainee})
    messages.success(request, "Trainee verified successfully.")
    return render(request, "trainees/account_created.html", {"trainee": trainee, "username": user.username, "password": password, "created": created})


@login_required
@authority_required
@require_POST
def reject_trainee(request, id):
    trainee = get_object_or_404(Trainee, id=id)
    trainee.status = "Rejected"
    trainee.save(update_fields=["status"])
    messages.success(request, "Trainee rejected.")
    return redirect("trainee_detail", id=id)


@login_required
@authority_required
def trainer_list(request):
    return render(request, "trainers/trainer_list.html", {"trainers": TrainerRegistration.objects.all().order_by("-id")})


@login_required
@authority_required
def trainer_detail(request, id):
    return render(request, "trainers/trainer_detail.html", {"trainer": get_object_or_404(TrainerRegistration, id=id)})


@login_required
@authority_required
@require_POST
def verify_trainer(request, id):
    trainer = get_object_or_404(TrainerRegistration, id=id)
    user, created = User.objects.get_or_create(username=trainer.email, defaults={"email": trainer.email})
    if created:
        user.set_password(f"Trainer@{trainer.phone[-4:]}")
        user.save()
    trainer.status, trainer.user = "Verified", user
    trainer.save(update_fields=["status", "user"])
    UserProfile.objects.update_or_create(user=user, defaults={"role": "Trainer", "trainee": None})
    messages.success(request, "Trainer verified successfully.")
    return redirect("trainer_detail", id=id)


@login_required
@authority_required
@require_POST
def reject_trainer(request, id):
    trainer = get_object_or_404(TrainerRegistration, id=id)
    trainer.status = "Rejected"
    trainer.save(update_fields=["status"])
    messages.success(request, "Trainer rejected.")
    return redirect("trainer_detail", id=id)


@login_required
@authority_required
def provider_list(request):
    return render(request, "providers/provider_list.html", {"providers": Provider.objects.all().order_by("-id")})


@login_required
@authority_required
def provider_detail(request, id):
    return render(request, "providers/provider_detail.html", {"provider": get_object_or_404(Provider, id=id)})


@login_required
@authority_required
@require_POST
def verify_provider(request, id):
    provider = get_object_or_404(Provider, id=id)
    provider.status = "Verified"
    provider.save(update_fields=["status"])
    messages.success(request, "Provider verified successfully.")
    return redirect("provider_detail", id=id)


@login_required
@authority_required
@require_POST
def reject_provider(request, id):
    provider = get_object_or_404(Provider, id=id)
    provider.status = "Rejected"
    provider.save(update_fields=["status"])
    messages.success(request, "Provider rejected.")
    return redirect("provider_detail", id=id)


@login_required
@authority_required
def course_list(request):
    return render(request, "course/course_list.html", {"courses": Course.objects.all().order_by("name")})


@login_required
@authority_required
def course_create(request):
    form = CourseForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Course created successfully.")
        return redirect("course_list")
    return render(request, "course/course_form.html", {"form": form})


@login_required
@authority_required
def batch_list(request):
    return render(request, "training/batch_list.html", {"batches": TrainingBatch.objects.select_related("course", "provider", "trainer").all().order_by("-id")})


@login_required
@authority_required
def batch_create(request):
    form = TrainingBatchForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Training batch created successfully.")
        return redirect("batch_list")
    return render(request, "training/batch_form.html", {"form": form})


@login_required
@authority_required
def batch_assign_trainees(request, id):
    batch = get_object_or_404(TrainingBatch, id=id)
    verified_trainees = Trainee.objects.filter(status="Verified").order_by("name")
    if request.method == "POST":
        selected = list(Trainee.objects.filter(id__in=request.POST.getlist("trainees"), status="Verified"))
        if len(selected) > batch.capacity:
            messages.error(request, f"This batch has capacity for {batch.capacity} trainees; select fewer trainees.")
        else:
            batch.trainees.set(selected)
            messages.success(request, "Trainees assigned successfully.")
            return redirect("batch_list")
    return render(request, "training/assign_trainees.html", {"batch": batch, "verified_trainees": verified_trainees})


@login_required
@trainer_required
def trainer_dashboard(request):
    batches = TrainingBatch.objects.filter(trainer=request.user).select_related("course", "provider").order_by("-start_date")
    return render(request, "trainer_dashboard.html", {"batches": batches})


@login_required
@trainer_required
def trainer_batch_detail(request, id):
    batch = get_object_or_404(TrainingBatch.objects.select_related("course", "provider"), id=id, trainer=request.user)
    return render(request, "trainers/trainer_batch_detail.html", {"batch": batch, "trainees": batch.trainees.all().order_by("name")})


@login_required
@trainer_required
def trainer_batch_progress(request, id):
    batch = get_object_or_404(TrainingBatch, id=id, trainer=request.user)
    trainees = batch.trainees.all().order_by("name")
    if request.method == "POST":
        attendance, progress, remarks = batch.attendance or {}, batch.progress or {}, batch.remarks or {}
        for trainee in trainees:
            trainee_id = str(trainee.id)
            attendance[trainee_id] = request.POST.get(f"attendance_{trainee.id}", "Absent")
            progress[trainee_id] = max(0, min(100, int(request.POST.get(f"progress_{trainee.id}", 0) or 0)))
            remarks[trainee_id] = request.POST.get(f"remarks_{trainee.id}", "")
        batch.attendance, batch.progress, batch.remarks = attendance, progress, remarks
        batch.save(update_fields=["attendance", "progress", "remarks"])
        messages.success(request, "Attendance and progress saved.")
        return redirect("trainer_batch_detail", id=id)
    return render(request, "training/trainer_batch_progress.html", {"batch": batch, "trainees": trainees})


@login_required
@trainer_required
@require_POST
def trainer_complete_batch(request, id):
    batch = get_object_or_404(TrainingBatch, id=id, trainer=request.user)
    if batch.status != "Completed":
        batch.status, batch.completion_date = "Completed", date.today()
        batch.save(update_fields=["status", "completion_date"])
        generate_followups(batch)
        for trainee in batch.trainees.all():
            profile = UserProfile.objects.filter(trainee=trainee, role="Trainee").select_related("user").first()
            if profile:
                notify(profile.user, f"Your training batch {batch.name} has been completed.", "Training")
        messages.success(request, "Training marked as completed and follow-ups generated.")
    return redirect("trainer_batch_detail", id=id)


@login_required
@trainee_required
def trainee_dashboard(request):
    trainee = request.user.userprofile.trainee
    batches = TrainingBatch.objects.filter(trainees=trainee).select_related("course", "provider", "trainer").order_by("-start_date")
    return render(request, "trainees/trainee_dashboard.html", {"trainee": trainee, "batches": batches, "employment": Employment.objects.filter(trainee=trainee).first(), "followups": FollowUp.objects.filter(trainee=trainee, completed=False)[:4]})


@login_required
def employment_list(request):
    profile = getattr(request.user, "userprofile", None)
    if request.user.is_staff or getattr(profile, "role", None) == "Authority":
        return render(request, "employment/list.html", {"employments": Employment.objects.select_related("trainee").all().order_by("trainee__name"), "authority": True})
    if not profile or profile.role != "Trainee":
        return redirect("login")
    employment, _ = Employment.objects.get_or_create(trainee=profile.trainee, defaults={"status": "Seeking"})
    form = EmploymentForm(request.POST or None, instance=employment)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Employment information updated.")
        return redirect("employment_list")
    return render(request, "employment/form.html", {"form": form, "employment": employment})


@login_required
def followup_list(request):
    profile = getattr(request.user, "userprofile", None)
    if request.user.is_staff or getattr(profile, "role", None) == "Authority":
        followups = FollowUp.objects.select_related("trainee").all()
        return render(request, "followups/list.html", {"followups": followups, "today": date.today(), "authority": True})
    if not profile or profile.role != "Trainee":
        return redirect("login")
    return render(request, "followups/list.html", {"followups": FollowUp.objects.filter(trainee=profile.trainee), "today": date.today()})


@login_required
@authority_required
def followup_update(request, id):
    followup = get_object_or_404(FollowUp, id=id)
    form = FollowUpForm(request.POST or None, instance=followup)
    if request.method == "POST" and form.is_valid():
        followup = form.save()
        Employment.objects.update_or_create(trainee=followup.trainee, defaults={"status": followup.employment_status})
        messages.success(request, "Follow-up updated.")
        return redirect("followup_list")
    return render(request, "followups/form.html", {"form": form, "followup": followup})


@login_required
def notification_list(request):
    notifications = Notification.objects.filter(recipient=request.user)
    notifications.filter(is_read=False).update(is_read=True)
    return render(request, "notifications/list.html", {"notifications": notifications})


@login_required
@authority_required
def analytics(request):
    course_data = list(TrainingBatch.objects.filter(status="Completed").values("course__name").annotate(total=Count("id")).order_by("course__name"))
    provider_data = list(TrainingBatch.objects.values("provider__name").annotate(total=Count("id")).order_by("provider__name"))
    return render(request, "analytics.html", {"course_data": course_data, "provider_data": provider_data, "employment_data": list(Employment.objects.values("status").annotate(total=Count("id"))), "district_data": list(Trainee.objects.values("district").annotate(total=Count("id")))})
from django.core.mail import send_mail
from django.http import HttpResponse


def test_email(request):
    send_mail(
        "SkillTrack Test Email",
        "This is a test email from my local Django website.",
        None,
        ["vedantpachauri84@gmail.com"],
        fail_silently=False,
    )

    return HttpResponse("Email sent successfully!")
def public_dashboard(request):
    trainees = Trainee.objects.all()
    providers = Provider.objects.filter(status="Verified")
    trainers = TrainerRegistration.objects.filter(status="Verified")
    courses = Course.objects.all()
    batches = TrainingBatch.objects.all()
    employments = Employment.objects.all()

    total_employment = employments.count()
    employed = employments.filter(status="Employed").count()

    context = {
        "total_trainees": trainees.count(),
        "verified_trainees": trainees.filter(status="Verified").count(),

        "total_providers": providers.count(),
        "total_trainers": trainers.count(),
        "total_courses": courses.count(),

        "total_batches": batches.count(),
        "active_batches": batches.filter(status="Active").count(),
        "completed_batches": batches.filter(status="Completed").count(),

        "employed": employed,
        "seeking": employments.filter(status="Seeking").count(),
        "unemployed": employments.filter(status="Unemployed").count(),

        "employment_rate": round(
            employed * 100 / total_employment, 1
        ) if total_employment else 0,

        "district_data": list(
            trainees
            .values("district")
            .annotate(total=Count("id"))
            .order_by("-total")
        ),

        "sector_data": list(
            courses
            .values("sector")
            .annotate(total=Count("id"))
            .order_by("-total")
        ),
    }

    return render(
        request,
        "public_dashboard.html",
        context
    )

@login_required
@trainee_required
def trainee_training_request(request, batch_id):
    """
    Trainee requests to join a specific training batch.
    The request goes to the trainer assigned to that batch.
    """

    trainee = request.user.userprofile.trainee

    batch = get_object_or_404(
        TrainingBatch.objects.select_related(
            "course",
            "provider",
            "trainer"
        ),
        id=batch_id,
        status="Active",
    )

    # Trainee must already be Authority-verified
    if trainee.status != "Verified":
        messages.error(
            request,
            "Your beneficiary profile must be verified by the Authority first."
        )
        return redirect("trainee_dashboard")

    # Check if already enrolled
    if batch.trainees.filter(id=trainee.id).exists():
        messages.info(
            request,
            "You are already enrolled in this batch."
        )
        return redirect("trainee_dashboard")

    # Check if a request already exists
    registration_request = TrainingRegistrationRequest.objects.filter(
        trainee=trainee,
        batch=batch
    ).first()

    if registration_request:
        if registration_request.status == "Pending":
            messages.info(
                request,
                "Your registration request is already pending."
            )
        elif registration_request.status == "Verified":
            messages.info(
                request,
                "Your request has already been verified."
            )
        else:
            messages.info(
                request,
                "Your previous request was rejected."
            )

        return redirect("trainee_dashboard")

    # Check batch capacity
    if batch.trainees.count() >= batch.capacity:
        messages.error(
            request,
            "This training batch is already full."
        )
        return redirect("trainee_dashboard")

    if request.method == "POST":

        registration_request = TrainingRegistrationRequest.objects.create(
            trainee=trainee,
            batch=batch,
            status="Pending",
        )

        # Notify assigned trainer
        if batch.trainer:
            notify(
                batch.trainer,
                f"New trainee registration request: "
                f"{trainee.name} ({trainee.beneficiary_id}) "
                f"requested to join {batch.name}.",
                "Training Registration",
            )

        messages.success(
            request,
            "Training registration request submitted successfully."
        )

        return redirect("trainee_dashboard")

    return render(
        request,
        "trainees/training_request.html",
        {
            "trainee": trainee,
            "batch": batch,
        }
    )


@login_required
@trainer_required
def trainer_verify_trainees(request):
    """
    Shows registration requests belonging only to batches
    assigned to the logged-in trainer.
    """

    registration_requests = (
        TrainingRegistrationRequest.objects
        .filter(batch__trainer=request.user)
        .select_related(
            "trainee",
            "batch",
            "batch__course",
            "batch__provider",
        )
        .order_by("-requested_at")
    )

    pending_count = registration_requests.filter(
        status="Pending"
    ).count()

    return render(
        request,
        "trainers/verify_trainees.html",
        {
            "registration_requests": registration_requests,
            "pending_count": pending_count,
        }
    )


@login_required
@trainer_required
@require_POST
def trainer_verify_request(request, request_id):
    """
    Trainer accepts a trainee's registration request.
    """

    registration_request = get_object_or_404(
        TrainingRegistrationRequest.objects.select_related(
            "trainee",
            "batch",
            "batch__course",
        ),
        id=request_id,
        batch__trainer=request.user,
    )

    if registration_request.status != "Pending":
        messages.warning(
            request,
            "This registration request has already been reviewed."
        )
        return redirect("trainer_verify_trainees")

    batch = registration_request.batch
    trainee = registration_request.trainee

    # Check capacity again before accepting
    if batch.trainees.count() >= batch.capacity:
        messages.error(
            request,
            "This batch is already full. The trainee cannot be added."
        )
        return redirect("trainer_verify_trainees")

    # Add trainee to batch
    batch.trainees.add(trainee)

    registration_request.status = "Verified"
    registration_request.reviewed_at = date.today()
    registration_request.rejection_reason = ""
    registration_request.save(
        update_fields=[
            "status",
            "reviewed_at",
            "rejection_reason",
        ]
    )

    # Notify trainee
    profile = (
        UserProfile.objects
        .filter(
            trainee=trainee,
            role="Trainee"
        )
        .select_related("user")
        .first()
    )

    if profile:
        notify(
            profile.user,
            f"Your registration request for "
            f"{batch.name} has been verified by the trainer.",
            "Training Registration",
        )

    messages.success(
        request,
        f"{trainee.name} has been verified and added to {batch.name}."
    )

    return redirect("trainer_verify_trainees")


@login_required
@trainer_required
@require_POST
def trainer_reject_request(request, request_id):
    """
    Trainer rejects a trainee's registration request.
    """

    registration_request = get_object_or_404(
        TrainingRegistrationRequest.objects.select_related(
            "trainee",
            "batch",
        ),
        id=request_id,
        batch__trainer=request.user,
    )

    if registration_request.status != "Pending":
        messages.warning(
            request,
            "This registration request has already been reviewed."
        )
        return redirect("trainer_verify_trainees")

    trainee = registration_request.trainee
    batch = registration_request.batch

    reason = request.POST.get(
        "rejection_reason",
        ""
    ).strip()

    registration_request.status = "Rejected"
    registration_request.rejection_reason = reason
    registration_request.reviewed_at = date.today()

    registration_request.save(
        update_fields=[
            "status",
            "rejection_reason",
            "reviewed_at",
        ]
    )

    # Notify trainee
    profile = (
        UserProfile.objects
        .filter(
            trainee=trainee,
            role="Trainee"
        )
        .select_related("user")
        .first()
    )

    if profile:
        message = (
            f"Your registration request for {batch.name} "
            f"has been rejected by the trainer."
        )

        if reason:
            message += f" Reason: {reason}"

        notify(
            profile.user,
            message,
            "Training Registration",
        )

    messages.success(
        request,
        f"Registration request for {trainee.name} rejected."
    )

    return redirect("trainer_verify_trainees")



@login_required
@trainer_required
def trainer_attendance(request):

    batches = (
        TrainingBatch.objects
        .filter(trainer=request.user)
        .select_related("course", "provider")
        .order_by("-start_date")
    )

    selected_batch = None
    trainees = []

    batch_id = request.GET.get("batch")

    if batch_id:
        selected_batch = get_object_or_404(
            TrainingBatch.objects.select_related(
                "course",
                "provider"
            ),
            id=batch_id,
            trainer=request.user
        )

        trainees = list(
            selected_batch.trainees.all().order_by("name")
        )

        attendance_data = selected_batch.attendance or {}

        for trainee in trainees:
            trainee.attendance_status = attendance_data.get(
                str(trainee.id),
                "Absent"
            )

    if request.method == "POST":

        batch_id = request.POST.get("batch_id")

        selected_batch = get_object_or_404(
            TrainingBatch,
            id=batch_id,
            trainer=request.user
        )

        trainees = list(
            selected_batch.trainees.all().order_by("name")
        )

        attendance = {}

        for trainee in trainees:
            attendance[str(trainee.id)] = request.POST.get(
                f"attendance_{trainee.id}",
                "Absent"
            )

        selected_batch.attendance = attendance

        selected_batch.save(
            update_fields=["attendance"]
        )

        messages.success(
            request,
            "Attendance updated successfully."
        )

        return redirect(
            f"{request.path}?batch={selected_batch.id}"
        )

    return render(
        request,
        "training/trainer_attendance.html",
        {
            "batches": batches,
            "selected_batch": selected_batch,
            "trainees": trainees,
        }
    )
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .models import Employment


@login_required
def verify_uan(request):
    profile = getattr(request.user, "userprofile", None)

    if not profile or profile.role != "Trainee":
        return redirect("login")

    if request.method == "POST":
        uan = request.POST.get("uan", "").strip()

        # DEMO UAN ONLY
        demo_data = {
            "100000000001": {
                "employer_name": "ABC Technologies Pvt Ltd",
                "job_role": "Software Developer",
                "employment_type": "Full Time",
                "salary": 25000,
                "status": "Employed",
            },
            "100000000002": {
                "employer_name": "Maharashtra IT Solutions",
                "job_role": "Python Developer",
                "employment_type": "Full Time",
                "salary": 32000,
                "status": "Employed",
            },
            "100000000003": {
                "employer_name": "Pune Digital Services",
                "job_role": "Data Entry Operator",
                "employment_type": "Full Time",
                "salary": 22000,
                "status": "Employed",
            },
            "100000000004": {
                "employer_name": "TechVision Solutions",
                "job_role": "Web Developer",
                "employment_type": "Full Time",
                "salary": 35000,
                "status": "Employed",
            },
            "100000000005": {
                "employer_name": "Nashik Engineering Works",
                "job_role": "Technician",
                "employment_type": "Full Time",
                "salary": 28000,
                "status": "Employed",
            },
            "100000000006": {
                "employer_name": "Mumbai Business Solutions",
                "job_role": "Support Executive",
                "employment_type": "Full Time",
                "salary": 24000,
                "status": "Employed",
            },
            "100000000007": {
                "employer_name": "Nagpur Software Labs",
                "job_role": "Junior Software Engineer",
                "employment_type": "Full Time",
                "salary": 30000,
                "status": "Employed",
            },
            "100000000008": {
                "employer_name": "Kolhapur Auto Industries",
                "job_role": "Machine Operator",
                "employment_type": "Full Time",
                "salary": 27000,
                "status": "Employed",
            },
            "100000000009": {
                "employer_name": "Thane Digital Hub",
                "job_role": "Digital Marketing Executive",
                "employment_type": "Full Time",
                "salary": 26000,
                "status": "Employed",
            },
            "100000000010": {
                "employer_name": "Solapur Technology Services",
                "job_role": "Technical Support Engineer",
                "employment_type": "Full Time",
                "salary": 29000,
                "status": "Employed",
            },
        }

        if uan in demo_data:
            data = demo_data[uan]

            employment, _ = Employment.objects.get_or_create(
                trainee=profile.trainee
            )

            employment.uan_demo = uan
            employment.employer_name = data["employer_name"]
            employment.job_role = data["job_role"]
            employment.employment_type = data["employment_type"]
            employment.salary = data["salary"]
            employment.status = data["status"]
            employment.save()

            return render(
                request,
                "employment/uan_result.html",
                {
                    "verified": True,
                    "uan": uan,
                    "data": data,
                },
            )

        return render(
            request,
            "employment/uan_result.html",
            {
                "verified": False,
                "uan": uan,
            },
        )

    return render(request, "employment/verify_uan.html")
@login_required
def employment_list(request):
    profile = getattr(request.user, "userprofile", None)

    # ==============================
    # AUTHORITY
    # ==============================
    if request.user.is_staff or getattr(profile, "role", None) == "Authority":

        employments = Employment.objects.select_related(
            "trainee"
        ).all().order_by("trainee__name")

        return render(
            request,
            "employment/list.html",
            {
                "employments": employments,
                "authority": True,
            }
        )

    # ==============================
    # TRAINEE
    # ==============================
    if not profile or profile.role != "Trainee":
        return redirect("login")

    employment, _ = Employment.objects.get_or_create(
        trainee=profile.trainee,
        defaults={"status": "Seeking"}
    )

    if request.method == "POST":

        form = EmploymentForm(
            request.POST,
            instance=employment
        )

        if form.is_valid():

            status = form.cleaned_data.get("status")

            # =====================================
            # EMPLOYED → UAN MUST BE VERIFIED
            # =====================================

            if status == "Employed":

                uan = form.cleaned_data.get("uan_demo")

                verification = UANVerification.objects.filter(
                    employment=employment,
                    uan=uan,
                    verified=True
                ).first()

                if not verification:

                    form.add_error(
                        "uan_demo",
                        "Please verify this UAN before saving."
                    )

                else:

                    form.save()

                    messages.success(
                        request,
                        "Employment information saved successfully."
                    )

                    return redirect("employment_list")
            # =====================================
            # SELF-EMPLOYED
            # =====================================

            elif status == "Self-Employed":

                registration_number = form.cleaned_data.get(
                    "registration_number"
                )

                verification = SelfEmploymentVerification.objects.filter(
                    employment=employment,
                    registration_number=registration_number,
                    status="Verified"
                ).first()

                if not verification:

                    form.add_error(
                        "registration_number",
                        "Please verify this registration number before saving."
                    )

                else:

                    form.save()

                    messages.success(
                        request,
                        "Self-employment information saved successfully."
                    )

                    return redirect("employment_list")

            # =====================================
            # SEEKING / UNEMPLOYED
            # =====================================

            else:

                form.save()

                messages.success(
                    request,
                    "Employment status updated successfully."
                )

                return redirect("employment_list")

    else:

        form = EmploymentForm(
            instance=employment
        )

    return render(
        request,
        "employment/form.html",
        {
            "form": form,
            "employment": employment,
        }
    )
@login_required
def verify_uan(request):

    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "message": "Invalid request."
        }, status=400)

    profile = getattr(request.user, "userprofile", None)

    if not profile or profile.role != "Trainee":
        return JsonResponse({
            "success": False,
            "message": "Unauthorized."
        }, status=403)

    uan = request.POST.get("uan", "").strip()

    if not uan:
        return JsonResponse({
            "success": False,
            "message": "Please enter UAN."
        })

    employment, _ = Employment.objects.get_or_create(
        trainee=profile.trainee,
        defaults={"status": "Seeking"}
    )

    # ---------------------------------
    # DEMO VERIFICATION
    # ---------------------------------

    if uan == "100000000001":

        verification, created = UANVerification.objects.update_or_create(
            employment=employment,
            defaults={
                "uan": uan,
                "verified": True,
                "verification_message": "UAN verified successfully."
            }
        )

        return JsonResponse({
            "success": True,
            "message": "✓ UAN Verified — Employment record found.",
            "employer_name": "ABC Technologies Pvt Ltd",
            "job_role": "Software Developer",
            "employment_type": "Full Time",
            "salary": 25000,
            "employment_date": "2026-07-01"
        })


    UANVerification.objects.update_or_create(
        employment=employment,
        defaults={
            "uan": uan,
            "verified": False,
            "verification_message": "UAN verification failed."
        }
    )

    return JsonResponse({
        "success": False,
        "message": "✗ UAN Verification Failed."
    })
@login_required
def verify_registration(request):

    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "message": "Invalid request."
        }, status=400)

    profile = getattr(request.user, "userprofile", None)

    if not profile or profile.role != "Trainee":
        return JsonResponse({
            "success": False,
            "message": "Unauthorized."
        }, status=403)

    registration_number = request.POST.get(
        "registration_number",
        ""
    ).strip()

    if not registration_number:
        return JsonResponse({
            "success": False,
            "message": "Please enter registration number."
        })

    employment, _ = Employment.objects.get_or_create(
        trainee=profile.trainee,
        defaults={"status": "Seeking"}
    )

    # ==========================================
    # DEMO VERIFICATION
    # ==========================================
    demo_self_employment = {
        "MH-DEMO-1001": {
            "business_name": "ABC Enterprises",
            "business_type": "Proprietorship",
            "work_description": "Retail Business",
        },
        "MH-DEMO-1002": {
            "business_name": "Pune Digital Services",
            "business_type": "Proprietorship",
            "work_description": "Computer and Digital Services",
        },
        "MH-DEMO-1003": {
            "business_name": "Maharashtra Tailoring House",
            "business_type": "Proprietorship",
            "work_description": "Tailoring and Garment Services",
        },
        "MH-DEMO-1004": {
            "business_name": "Shree Auto Works",
            "business_type": "Partnership",
            "work_description": "Automobile Repair Services",
        },
        "MH-DEMO-1005": {
            "business_name": "Green Solar Solutions",
            "business_type": "Proprietorship",
            "work_description": "Solar Panel Installation",
        },
        "MH-DEMO-1006": {
            "business_name": "Smart Graphic Studio",
            "business_type": "Proprietorship",
            "work_description": "Graphic Design and Printing",
        },
        "MH-DEMO-1007": {
            "business_name": "Maharashtra Mobile Care",
            "business_type": "Partnership",
            "work_description": "Mobile Repair Services",
        },
        "MH-DEMO-1008": {
            "business_name": "Fresh Food Corner",
            "business_type": "Proprietorship",
            "work_description": "Food and Catering Services",
        },
    }

    if registration_number  in demo_self_employment:

        SelfEmploymentVerification.objects.update_or_create(
            employment=employment,
            defaults={
                "registration_number": registration_number,
                "business_name": "ABC Enterprises",
                "business_type": "Proprietorship",
                "work_description": "Retail Business",
                "status": "Verified",
                "verification_message": "Registration verified successfully.",
                "verified_at": timezone.now(),
            }
        )

        return JsonResponse({
            "success": True,
            "message": "✓ Registration Verified — Business record found.",
            "business_name": "ABC Enterprises",
            "business_type": "Proprietorship",
            "work_description": "Retail Business",
        })

    # ==========================================
    # FAILED VERIFICATION
    # ==========================================

    SelfEmploymentVerification.objects.update_or_create(
        employment=employment,
        defaults={
            "registration_number": registration_number,
            "business_name": "",
            "business_type": "",
            "work_description": "",
            "status": "Rejected",
            "verification_message": "Registration verification failed.",
            "verified_at": timezone.now(),
        }
    )

    return JsonResponse({
        "success": False,
        "message": "✗ Registration Verification Failed."
    })