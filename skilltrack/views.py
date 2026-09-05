from django.shortcuts import render
from .forms import TrainingForm
from django.shortcuts import render, get_object_or_404
from .models import TrainingBatch
from .models import UserProfile
from django.contrib.auth import logout
def logout_view(request):
    logout(request)
    return redirect("login")
from .models import (

    Trainee,
    Course,
    Provider,
    Training,
    Employment,
)
def authority_required(view_func):
    def check_authority(user):
        try:
            return user.userprofile.role == "Authority"
        except UserProfile.DoesNotExist:
            return False

    return user_passes_test(check_authority)(view_func)
from .models import TrainerRegistration
from .forms import TrainerRegistrationForm
from .forms import TrainingBatchForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
def staff_required(view_func):
    return user_passes_test(
        lambda user: user.is_staff
    )(view_func)
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404, redirect

from .models import Trainee, UserProfile
from django.db.models import Count

@login_required
@authority_required
def dashboard(request):
    total_trainees = Trainee.objects.count()
    total_courses = Course.objects.count()
    total_providers = Provider.objects.count()

    active_training = Training.objects.filter(
        status="Training"
    ).count()

    completed_training = Training.objects.filter(
        status="Completed"
    ).count()

    employed = Employment.objects.filter(
        status="Employed"
    ).count()

    employment_rate = (
        (employed / total_trainees) * 100
        if total_trainees > 0 else 0
    )

    # District-wise trainees
    district_data = (
        Trainee.objects
        .values("district")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    # Sector-wise courses
    sector_data = (
        Course.objects
        .values("sector")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    context = {
        "total_trainees": total_trainees,
        "total_courses": total_courses,
        "total_providers": total_providers,
        "active_training": active_training,
        "completed_training": completed_training,
        "employed": employed,
        "employment_rate": round(employment_rate, 1),
        "district_data": district_data,
        "sector_data": sector_data,
    }

    return render(request, "dashboard.html", context)
from django.shortcuts import render, redirect, get_object_or_404
from .forms import TraineeForm
from .models import Trainee

@staff_required
def trainee_list(request):
    trainees = Trainee.objects.all().order_by("-id")

    return render(
        request,
        "trainees/trainee_list.html",
        {"trainees": trainees}
    )

@staff_required
def trainee_create(request):
    if request.method == "POST":
        form = TraineeForm(request.POST)

        if form.is_valid():
            trainee = form.save(commit=False)

            # Generate unique Beneficiary ID
            last_trainee = Trainee.objects.order_by("-id").first()

            if last_trainee:
                next_number = last_trainee.id + 1
            else:
                next_number = 1

            trainee.beneficiary_id = f"MH-2026-{next_number:06d}"

            trainee.save()

            return redirect("trainee_list")

    else:
        form = TraineeForm()

    return render(
        request,
        "trainees/trainee_form.html",
        {"form": form}
    )

@staff_required
def trainee_detail(request, id):
    trainee = get_object_or_404(Trainee, id=id)

    return render(
        request,
        "trainees/trainee_detail.html",
        {"trainee": trainee}
    )

@staff_required
def trainee_update(request, id):
    trainee = get_object_or_404(Trainee, id=id)

    if request.method == "POST":
        form = TraineeForm(request.POST, instance=trainee)

        if form.is_valid():
            form.save()
            return redirect("trainee_detail", id=trainee.id)
    else:
        form = TraineeForm(instance=trainee)

    return render(
        request,
        "trainees/trainee_form.html",
        {
            "form": form,
            "trainee": trainee
        }
    )

@staff_required
def trainee_delete(request, id):
    trainee = get_object_or_404(Trainee, id=id)

    if request.method == "POST":
        trainee.delete()
        return redirect("trainee_list")

    return render(
        request,
        "trainees/trainee_confirm_delete.html",
        {"trainee": trainee}
    )
def trainee_register(request):
    if request.method == "POST":
        form = TraineeForm(request.POST)

        if form.is_valid():
            trainee = form.save(commit=False)

            # Generate Beneficiary ID automatically
            last_trainee = Trainee.objects.order_by("-id").first()

            if last_trainee:
                next_number = last_trainee.id + 1
            else:
                next_number = 1

            trainee.beneficiary_id = f"MH-2026-{next_number:06d}"

            trainee.save()

            return render(
                request,
                "trainees/registration_success.html",
                {"trainee": trainee}
            )

    else:
        form = TraineeForm()

    return render(
        request,
        "trainees/trainee_register.html",
        {"form": form}
    )
@login_required
@staff_required
def verify_trainee(request, id):

    trainee = get_object_or_404(Trainee, id=id)

    if request.method == "POST":

        trainee.status = "Verified"
        trainee.save()

        username = trainee.beneficiary_id

        user, created = User.objects.get_or_create(
            username=username
        )

        password = None

        if created:
            password = f"Skill@{trainee.phone[-4:]}"

            user.set_password(password)
            user.save()

            UserProfile.objects.create(
                user=user,
                role="Trainee",
                trainee=trainee
            )

        return render(
            request,
            "trainees/account_created.html",
            {
                "trainee": trainee,
                "username": username,
                "password": password,
                "created": created,
            }
        )

    return redirect("trainee_detail", id=trainee.id)
@login_required
@staff_required
def reject_trainee(request, id):
    trainee = get_object_or_404(Trainee, id=id)

    if request.method == "POST":
        trainee.status = "Rejected"
        trainee.save()

    return redirect("trainee_detail", id=trainee.id)
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect


from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .models import UserProfile


def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            # Get user's role
            try:
                profile = UserProfile.objects.get(user=user)

                if profile.role == "Authority":
                    return redirect("dashboard")

                elif profile.role == "Trainer":
                    return redirect("trainer_dashboard")

                elif profile.role == "Trainee":
                    return redirect("trainee_dashboard")

            except UserProfile.DoesNotExist:
                return redirect("#")

        else:

            return render(
                request,
                "login.html",
                {
                    "error": "Invalid username or password."
                }
            )

    return render(request, "login.html")
@login_required
def trainee_dashboard(request):
    profile = getattr(request.user, "userprofile", None)

    if not profile or profile.role != "Trainee":
        return redirect("login")

    trainee = profile.trainee

    batches = TrainingBatch.objects.filter(
        trainees=trainee
    ).select_related(
        "course",
        "provider",
        "trainer"
    ).order_by("-start_date")

    return render(
        request,
        "trainees/trainee_dashboard.html",
        {
            "trainee": trainee,
            "batches": batches,
        }
    )
def training_create(request):

    if request.method == "POST":

        form = TrainingForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("training_list")

    else:
        form = TrainingForm()

    return render(
        request,
        "trainers/training_form.html",
        {"form": form}
    )
def training_list(request):
    trainings = Training.objects.all().select_related(
        "trainee",
        "course",
        "provider"
    ).order_by("-id")

    return render(
        request,
        "trainers/training_list.html",
        {"trainings": trainings}
    )
def training_batch_create(request):

    if request.method == "POST":

        form = TrainingBatchForm(request.POST)

        if form.is_valid():

            batch = form.save()

            return redirect("training_batch_list")

    else:
        form = TrainingBatchForm()

    return render(
        request,
        "training/training_batch_form.html",
        {"form": form}
    )
def trainer_register(request):

    if request.method == "POST":

        form = TrainerRegistrationForm(request.POST)

        if form.is_valid():

            trainer = form.save(commit=False)

            trainer.status = "Pending"

            trainer.save()

            return render(
                request,
                "trainers/registration_success.html",
                {
                    "trainer": trainer
                }
            )

    else:
        form = TrainerRegistrationForm()

    return render(
        request,
        "trainers/trainer_register.html",
        {
            "form": form
        }
    )
@authority_required
def trainer_list(request):

    trainers = TrainerRegistration.objects.all().order_by("-id")

    return render(
        request,
        "trainers/trainer_list.html",
        {
            "trainers": trainers
        }
    )
@authority_required
def trainer_detail(request, id):

    trainer = get_object_or_404(
        TrainerRegistration,
        id=id
    )

    return render(
        request,
        "trainers/trainer_detail.html",
        {
            "trainer": trainer
        }
    )
from .models import UserProfile
@authority_required
def verify_trainer(request, id):

    trainer = get_object_or_404(
        TrainerRegistration,
        id=id
    )

    if request.method == "POST":

        trainer.status = "Verified"

        # Create trainer login account
        user, created = User.objects.get_or_create(
            username=trainer.email
        )

        if created:
            password = f"Trainer@{trainer.phone[-4:]}"

            user.set_password(password)
            user.save()

        # Connect registration with Django user
        trainer.user = user
        trainer.save()

        # Create UserProfile if it doesn't exist
        UserProfile.objects.get_or_create(
            user=user,
            defaults={
                "role": "Trainer"
            }
        )

    return redirect(
        "trainer_detail",
        id=trainer.id
    )
@authority_required
def reject_trainer(request, id):

    trainer = get_object_or_404(
        TrainerRegistration,
        id=id
    )

    if request.method == "POST":

        trainer.status = "Rejected"
        trainer.save()

    return redirect(
        "trainer_detail",
        id=trainer.id
    )
@authority_required
def course_list(request):

    courses = Course.objects.all().order_by("name")

    return render(
        request,
        "course/course_list.html",
        {
            "courses": courses
        }
    )
from .forms import CourseForm
@authority_required
def course_create(request):

    if request.method == "POST":

        form = CourseForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect("course_list")

    else:
        form = CourseForm()

    return render(
        request,
        "course/course_form.html",
        {
            "form": form
        }
    )
from .forms import TrainingBatchForm
@login_required
def batch_create(request):

    if request.method == "POST":

        form = TrainingBatchForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect("batch_list")

    else:
        form = TrainingBatchForm()


        form.fields["provider"].queryset = Provider.objects.filter(

        )


        form.fields["trainer"].queryset = User.objects.filter(
            trainerregistration__status="Verified"
        )

    return render(
        request,
        "training/batch_form.html",
        {
            "form": form
        }
    )
@authority_required
def provider_list(request):

    providers = Provider.objects.all().order_by("-id")

    return render(
        request,
        "providers/provider_list.html",
        {
            "providers": providers
        }
    )
@authority_required
def provider_detail(request, id):

    provider = get_object_or_404(
        Provider,
        id=id
    )

    return render(
        request,
        "providers/provider_detail.html",
        {
            "provider": provider
        }
    )
@authority_required
def verify_provider(request, id):

    provider = get_object_or_404(
        Provider,
        id=id
    )

    if request.method == "POST":

        provider.status = "Verified"
        provider.save()

    return redirect(
        "provider_detail",
        id=provider.id
    )
@authority_required
def reject_provider(request, id):

    provider = get_object_or_404(
        Provider,
        id=id
    )

    if request.method == "POST":

        provider.status = "Rejected"
        provider.save()

    return redirect(
        "provider_detail",
        id=provider.id
    )
from .models import TrainingBatch
@login_required
def batch_list(request):

    batches = TrainingBatch.objects.all().order_by("-id")

    return render(
        request,
        "training/batch_list.html",
        {
            "batches": batches
        }
    )
@login_required
def batch_assign_trainees(request, id):

    batch = get_object_or_404(
        TrainingBatch,
        id=id
    )

    verified_trainees = Trainee.objects.filter(
        status="Verified"
    ).order_by("name")

    if request.method == "POST":

        trainee_ids = request.POST.getlist("trainees")

        batch.trainees.set(
            Trainee.objects.filter(
                id__in=trainee_ids,
                status="Verified"
            )
        )

        return redirect(
            "batch_list"
        )

    return render(
        request,
        "training/assign_trainees.html",
        {
            "batch": batch,
            "verified_trainees": verified_trainees,
        }
    )
@login_required
def trainer_dashboard(request):

    batches = TrainingBatch.objects.filter(
        trainer=request.user
    ).order_by("-start_date")

    return render(
        request,
        "trainer_dashboard.html",
        {
            "batches": batches
        }
    )
@login_required
def trainer_batch_detail(request, id):

    batch = get_object_or_404(
        TrainingBatch,
        id=id,
        trainer=request.user
    )

    trainees = batch.trainees.all().order_by("name")

    return render(
        request,
        "trainers/trainer_batch_detail.html",
        {
            "batch": batch,
            "trainees": trainees,
        }
    )
login_required
def trainer_batch_progress(request, id):

    batch = get_object_or_404(
        TrainingBatch,
        id=id,
        trainer=request.user
    )

    trainees = batch.trainees.all().order_by("name")

    if request.method == "POST":

        attendance = batch.attendance or {}
        progress = batch.progress or {}

        remarks = batch.remarks or {}

        for trainee in trainees:
            trainee_id = str(trainee.id)

            attendance[trainee_id] = request.POST.get(
                f"attendance_{trainee.id}",
                "Absent"
            )

            progress[trainee_id] = request.POST.get(
                f"progress_{trainee.id}",
                "0"
            )

            remarks[trainee_id] = request.POST.get(
                f"remarks_{trainee.id}",
                ""
            )

        batch.attendance = attendance
        batch.progress = progress
        batch.remarks = remarks
        batch.save()


        return redirect(
            "trainer_batch_detail",
            id=batch.id
        )

    return render(
        request,
        "training/trainer_batch_progress.html",
        {
            "batch": batch,
            "trainees": trainees,
        }
    )
@login_required
def trainer_complete_batch(request, id):

    batch = get_object_or_404(
        TrainingBatch,
        id=id,
        trainer=request.user
    )

    if request.method == "POST":
        batch.status = "Completed"
        batch.save()

    return redirect(
        "trainer_batch_detail",
        id=batch.id
    )