from django import forms
from django.contrib.auth.models import User
from .models import Course, Employment, FollowUp, Provider, Trainee, TrainerRegistration, TrainingBatch


class PortalForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


class TraineeForm(PortalForm):
    class Meta:
        model = Trainee
        fields = ["name", "phone", "email", "district", "qualification", "gender", "registration_date"]
        widgets = {"registration_date": forms.DateInput(attrs={"type": "date"})}


class TrainerRegistrationForm(PortalForm):
    class Meta:
        model = TrainerRegistration
        fields = ["name", "phone", "email", "organization", "district", "qualification", "experience", "registration_date"]
        widgets = {"registration_date": forms.DateInput(attrs={"type": "date"})}


class CourseForm(PortalForm):
    class Meta:
        model = Course
        fields = ["name", "sector", "duration"]


class TrainingBatchForm(PortalForm):
    class Meta:
        model = TrainingBatch
        fields = ["name", "course", "provider", "trainer", "district", "start_date", "end_date", "capacity"]
        widgets = {"start_date": forms.DateInput(attrs={"type": "date"}), "end_date": forms.DateInput(attrs={"type": "date"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["provider"].queryset = Provider.objects.filter(status="Verified").order_by("name")
        self.fields["trainer"].queryset = User.objects.filter(trainerregistration__status="Verified").order_by("username")

    def clean(self):
        data = super().clean()
        if data.get("end_date") and data.get("start_date") and data["end_date"] < data["start_date"]:
            self.add_error("end_date", "End date cannot be before the start date.")
        return data


class EmploymentForm(PortalForm):
    class Meta:
        model = Employment
        fields = ["status", "employer_name", "job_role", "employment_type", "salary", "employment_date", "uan_demo"]
        widgets = {"employment_date": forms.DateInput(attrs={"type": "date"})}


class FollowUpForm(PortalForm):
    class Meta:
        model = FollowUp
        fields = ["employment_status", "remarks", "completed"]
