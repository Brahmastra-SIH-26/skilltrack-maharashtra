from django import forms
from .models import Trainee
from .models import TrainerRegistration


class TrainerRegistrationForm(forms.ModelForm):

    class Meta:
        model = TrainerRegistration

        fields = [
            "name",
            "phone",
            "email",
            "organization",
            "district",
            "qualification",
            "experience",
            "registration_date",
        ]

        widgets = {
            "registration_date": forms.DateInput(
                attrs={"type": "date"}
            ),
        }

class TraineeForm(forms.ModelForm):
    class Meta:
        model = Trainee
        fields = [
            "beneficiary_id",
            "name",
            "phone",
            "email",
            "district",
            "qualification",
            "gender",
            "registration_date",
        ]

        widgets = {
            "registration_date": forms.DateInput(
                attrs={"type": "date"}
            ),
        }
from .models import TrainingBatch, Provider, TrainerRegistration
from django.contrib.auth.models import User
class TraineeForm(forms.ModelForm):
    class Meta:
        model = Trainee

        fields = [
            "name",
            "phone",
            "email",
            "district",
            "qualification",
            "gender",
            "registration_date",
        ]

        widgets = {
            "registration_date": forms.DateInput(
                attrs={"type": "date"}
            ),
        }
from .models import Training


class TrainingForm(forms.ModelForm):

    class Meta:
        model = Training

        fields = [
            "trainee",
            "course",
            "provider",
            "start_date",
            "end_date",
            "completion_percentage",
            "status",
        ]

        widgets = {
            "start_date": forms.DateInput(
                attrs={"type": "date"}
            ),

            "end_date": forms.DateInput(
                attrs={"type": "date"}
            ),

            "completion_percentage": forms.NumberInput(
                attrs={
                    "min": 0,
                    "max": 100
                }
            ),
        }
from .models import TrainingBatch, Trainee


class TrainingBatchForm(forms.ModelForm):

    trainees = forms.ModelMultipleChoiceField(
        queryset=Trainee.objects.filter(status="Verified"),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = TrainingBatch
        fields = [
            "name",
            "course",
            "provider",
            "trainer",
            "district",
            "start_date",
            "end_date",
            "capacity",
            "trainees",
        ]

        widgets = {
            "start_date": forms.DateInput(
                attrs={"type": "date"}
            ),
            "end_date": forms.DateInput(
                attrs={"type": "date"}
            ),
        }
from .models import Course

class CourseForm(forms.ModelForm):

    class Meta:
        model = Course

        fields = [
            "name",
            "sector",
            "duration",
        ]
from .models import TrainingBatch

class TrainingBatchForm(forms.ModelForm):

    class Meta:
        model = TrainingBatch

        fields = [
            "name",
            "course",
            "provider",
            "trainer",
            "district",
            "start_date",
            "end_date",
            "capacity",
        ]

        widgets = {
            "start_date": forms.DateInput(
                attrs={"type": "date"}
            ),
            "end_date": forms.DateInput(
                attrs={"type": "date"}
            ),
        }
class TrainingBatchForm(forms.ModelForm):

    class Meta:
        model = TrainingBatch

        fields = [
            "name",
            "course",
            "provider",
            "trainer",
            "district",
            "start_date",
            "end_date",
            "capacity",
        ]

        widgets = {
            "start_date": forms.DateInput(
                attrs={"type": "date"}
            ),
            "end_date": forms.DateInput(
                attrs={"type": "date"}
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # Only verified providers
        self.fields["provider"].queryset = Provider.objects.filter(
            status="Verified"
        )

        # Only trainers whose registration is verified
        verified_trainer_ids = TrainerRegistration.objects.filter(
            status="Verified",
            user__isnull=False
        ).values_list("user_id", flat=True)

        self.fields["trainer"].queryset = User.objects.filter(
            id__in=verified_trainer_ids
        )