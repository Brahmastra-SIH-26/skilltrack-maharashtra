from importlib.metadata import requires
from typing import Required

from django.contrib.auth.models import User
from django.db import models


from django.db import models
from django.contrib.auth.models import User


class Trainee(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Verified", "Verified"),
        ("Rejected", "Rejected"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="trainee_profile",
        null=True,
        blank=True
    )

    beneficiary_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    district = models.CharField(max_length=50)
    qualification = models.CharField(max_length=100)
    gender = models.CharField(max_length=20)
    registration_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    consent_given = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.beneficiary_id} - {self.name}"


class Course(models.Model):
    name = models.CharField(max_length=100)
    sector = models.CharField(max_length=100)
    duration = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Provider(models.Model):
    STATUS_CHOICES = Trainee.STATUS_CHOICES
    name = models.CharField(max_length=150)
    provider_type = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    rating = models.FloatField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")

    def __str__(self):
        return self.name


class Training(models.Model):
    STATUS_CHOICES = [("Pending", "Pending"),("Training", "Training"), ("Completed", "Completed"), ("Dropped", "Dropped")]
    trainee = models.ForeignKey(Trainee, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    completion_percentage = models.IntegerField(default=0)
    #status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    def __str__(self):
        return f"{self.trainee.name} - {self.course.name}"


class Employment(models.Model):
    STATUS_CHOICES = [("Employed", "Employed"), ("Seeking", "Seeking"), ("Unemployed", "Unemployed"),("Self-Employed", "Self-Employed"),]
    trainee = models.OneToOneField(Trainee, on_delete=models.CASCADE)
    uan_demo = models.CharField(max_length=30, blank=True)
    employer_name = models.CharField(max_length=150, blank=True)
    job_role = models.CharField(max_length=100, blank=True)
    employment_type = models.CharField(max_length=50, blank=True)
    salary = models.IntegerField(default=0)
    employment_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Seeking")

    registration_number = models.CharField(
        max_length=50,
        blank=True
    )

    business_name = models.CharField(
        max_length=150,
        blank=True
    )

    business_type = models.CharField(
        max_length=100,
        blank=True
    )

    work_description = models.CharField(
        max_length=255,
        blank=True
    )



    def __str__(self):
        return f"{self.trainee.name} - {self.status}"




class FollowUp(models.Model):
    FOLLOWUP_CHOICES = [("3 Months", "3 Months"), ("6 Months", "6 Months"), ("1 Year", "1 Year"), ("3 Years", "3 Years"), ("5 Years", "5 Years")]
    trainee = models.ForeignKey(Trainee, on_delete=models.CASCADE)
    followup_type = models.CharField(max_length=20, choices=FOLLOWUP_CHOICES)
    date = models.DateField()
    employment_status = models.CharField(max_length=50, choices=Employment.STATUS_CHOICES, default="Seeking")
    remarks = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    email_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["trainee", "followup_type"], name="unique_trainee_followup_type")]
        ordering = ["date"]

    def __str__(self):
        return f"{self.trainee.name} - {self.followup_type}"


class UserProfile(models.Model):
    ROLE_CHOICES = [("Authority", "Authority"), ("Trainer", "Trainer"), ("Trainee", "Trainee")]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    trainee = models.OneToOneField(Trainee, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


class TrainingBatch(models.Model):
    STATUS_CHOICES = [("Active", "Active"), ("Completed", "Completed")]
    name = models.CharField(max_length=150)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    trainer = models.ForeignKey(User, on_delete=models.CASCADE)
    district = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    capacity = models.PositiveIntegerField(default=30)
    trainees = models.ManyToManyField(Trainee, blank=True)
    attendance = models.JSONField(default=dict, blank=True)
    progress = models.JSONField(default=dict, blank=True)
    remarks = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Active")
    completion_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name


class TrainerRegistration(models.Model):
    STATUS_CHOICES = Trainee.STATUS_CHOICES
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    organization = models.CharField(max_length=150)
    district = models.CharField(max_length=50)
    qualification = models.CharField(max_length=150)
    experience = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    registration_date = models.DateField()

    def __str__(self):
        return f"{self.name} - {self.organization}"


class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="portal_notifications")
    message = models.CharField(max_length=255)
    notification_type = models.CharField(max_length=40, default="System")
    follow_up = models.ForeignKey(FollowUp, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
class TrainingRegistrationRequest(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Verified", "Verified"),
        ("Rejected", "Rejected"),
    ]

    trainee = models.ForeignKey(
        Trainee,
        on_delete=models.CASCADE,
        related_name="training_requests"
    )

    batch = models.ForeignKey(
        TrainingBatch,
        on_delete=models.CASCADE,
        related_name="registration_requests"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    requested_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    rejection_reason = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["trainee", "batch"],
                name="unique_trainee_batch_request"
            )
        ]
        ordering = ["-requested_at"]

    def __str__(self):
        return f"{self.trainee.name} - {self.batch.name} - {self.status}"
class UANVerification(models.Model):
    employment = models.ForeignKey(
        Employment,
        on_delete=models.CASCADE,
        related_name="uan_verifications"
    )
    uan = models.CharField(max_length=30)
    verified = models.BooleanField(default=False)
    verification_message = models.CharField(max_length=255, blank=True)
    verified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.uan} - {'Verified' if self.verified else 'Failed'}"
class SelfEmploymentVerification(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Verified", "Verified"),
        ("Rejected", "Rejected"),
    ]

    employment = models.OneToOneField(
        Employment,
        on_delete=models.CASCADE,
        related_name="self_employment_verification"
    )

    registration_number = models.CharField(max_length=50)
    business_name = models.CharField(max_length=150, blank=True)
    business_type = models.CharField(max_length=100, blank=True)
    work_description = models.CharField(max_length=255, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    verification_message = models.CharField(
        max_length=255,
        blank=True
    )

    verified_at = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.registration_number} - {self.status}"
class TrainingPerformance(models.Model):
    trainee = models.ForeignKey(
        Trainee,
        on_delete=models.CASCADE,
        related_name="performance_records"
    )

    training = models.OneToOneField(
        Training,
        on_delete=models.CASCADE,
        related_name="performance"
    )

    # Attendance
    total_classes = models.PositiveIntegerField(default=0)
    attended_classes = models.PositiveIntegerField(default=0)
    attendance_percentage = models.FloatField(default=0)

    # Assignments
    total_assignments = models.PositiveIntegerField(default=0)
    completed_assignments = models.PositiveIntegerField(default=0)
    assignment_score = models.FloatField(default=0)

    # Assessments
    total_assessments = models.PositiveIntegerField(default=0)
    completed_assessments = models.PositiveIntegerField(default=0)
    assessment_score = models.FloatField(default=0)

    # Practical / Skill evaluation
    practical_score = models.FloatField(default=0)

    # Overall training progress
    progress_percentage = models.FloatField(default=0)

    # Final performance
    final_score = models.FloatField(default=0)

    # Trainer remarks
    trainer_remarks = models.TextField(blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.trainee.name} - {self.training.course.name}"