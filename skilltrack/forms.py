from django import forms
from django.contrib.auth.models import User
from .models import Course, Employment, FollowUp, Provider, Trainee, TrainerRegistration, TrainingBatch


class PortalForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


class TraineeForm(PortalForm):
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Create a password"
        }),
        min_length=8
    )

    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Confirm your password"
        })
    )

    consent_given = forms.BooleanField(
        label="I consent to the collection and use of my information for registration, training, employment tracking, and verification purposes. I confirm that the information provided by me is accurate.",
        required=True
    )

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
            )
        }

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError(
                "Passwords do not match."
            )

        return cleaned_data


from django import forms
from django.contrib.auth.password_validation import validate_password

class TrainerRegistrationForm(PortalForm):

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Create your password"
            }
        ),
        validators=[validate_password]
    )

    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Confirm your password"
            }
        )
    )

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
            )
        }

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(username=email).exists():
            raise forms.ValidationError(
                "An account with this email already exists."
            )

        return email

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password:
            if password != confirm_password:
                self.add_error(
                    "confirm_password",
                    "Passwords do not match."
                )

        return cleaned_data
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




    def clean(self):
        cleaned_data = super().clean()

        status = cleaned_data.get("status")
        uan = cleaned_data.get("uan_demo")

        # UAN is required only for employed trainees
        if status == "Employed" and not uan:
            self.add_error(
                "uan_demo",
                "UAN is required for employed trainees."
            )

        # Remove UAN for other employment statuses
        if status != "Employed":
            cleaned_data["uan_demo"] = ""

        return cleaned_data


class FollowUpForm(PortalForm):
    class Meta:
        model = FollowUp
        fields = ["employment_status", "remarks", "completed"]
class EmploymentForm(PortalForm):
    class Meta:
        model = Employment
        fields = [
            "status",
            "employer_name",
            "job_role",
            "employment_type",
            "salary",
            "employment_date",
            "uan_demo",
            "registration_number",
            "business_name",
            "business_type",
            "work_description",
        ]

        widgets = {
            "employment_date": forms.DateInput(
                attrs={"type": "date"}
            ),
        }

    def clean(self):
        cleaned_data = super().clean()

        status = cleaned_data.get("status")

        # -----------------------------
        # EMPLOYED
        # -----------------------------
        if status == "Employed":

            if not cleaned_data.get("uan_demo"):
                self.add_error(
                    "uan_demo",
                    "UAN is required for employed trainees."
                )

            # Clear self-employment data
            cleaned_data["registration_number"] = ""
            cleaned_data["business_name"] = ""
            cleaned_data["business_type"] = ""
            cleaned_data["work_description"] = ""

        # -----------------------------
        # SELF EMPLOYED
        # -----------------------------
        elif status == "Self-Employed":

            if not cleaned_data.get("registration_number"):
                self.add_error(
                    "registration_number",
                    "Registration number is required for self-employed trainees."
                )

            # Clear employment/UAN data
            cleaned_data["uan_demo"] = ""
            cleaned_data["employer_name"] = ""
            cleaned_data["job_role"] = ""
            cleaned_data["employment_type"] = ""
            cleaned_data["salary"] = 0
            cleaned_data["employment_date"] = None

        # -----------------------------
        # SEEKING / UNEMPLOYED
        # -----------------------------
        else:

            cleaned_data["uan_demo"] = ""

            cleaned_data["employer_name"] = ""
            cleaned_data["job_role"] = ""
            cleaned_data["employment_type"] = ""
            cleaned_data["salary"] = 0
            cleaned_data["employment_date"] = None

            cleaned_data["registration_number"] = ""
            cleaned_data["business_name"] = ""
            cleaned_data["business_type"] = ""
            cleaned_data["work_description"] = ""

        return cleaned_data