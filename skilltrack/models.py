from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from django.db import models


class Trainee(models.Model):

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Verified", "Verified"),
        ("Rejected", "Rejected"),
    ]

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

    def __str__(self):
        return f"{self.beneficiary_id} - {self.name}"

class Course(models.Model):
    name = models.CharField(max_length=100)
    sector = models.CharField(max_length=100)
    duration = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Provider(models.Model):

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Verified", "Verified"),
        ("Rejected", "Rejected"),
    ]

    name = models.CharField(max_length=150)
    provider_type = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    rating = models.FloatField(default=0)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    def __str__(self):
        return self.name


class Training(models.Model):
    STATUS_CHOICES = [
        ("Training", "Training"),
        ("Completed", "Completed"),
        ("Dropped", "Dropped"),
    ]

    trainee = models.ForeignKey(Trainee, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    completion_percentage = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def __str__(self):
        return f"{self.trainee.name} - {self.course.name}"


class Employment(models.Model):
    STATUS_CHOICES = [
        ("Employed", "Employed"),
        ("Seeking", "Seeking"),
        ("Unemployed", "Unemployed"),
    ]

    trainee = models.OneToOneField(Trainee, on_delete=models.CASCADE)
    uan_demo = models.CharField(max_length=30, blank=True)
    employer_name = models.CharField(max_length=150, blank=True)
    job_role = models.CharField(max_length=100, blank=True)
    employment_type = models.CharField(max_length=50, blank=True)
    salary = models.IntegerField(default=0)
    employment_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def __str__(self):
        return f"{self.trainee.name} - {self.status}"


class FollowUp(models.Model):
    FOLLOWUP_CHOICES = [
        ("6 Months", "6 Months"),
        ("1 Year", "1 Year"),
        ("3 Years", "3 Years"),
        ("5 Years", "5 Years"),
    ]

    trainee = models.ForeignKey(Trainee, on_delete=models.CASCADE)
    followup_type = models.CharField(max_length=20, choices=FOLLOWUP_CHOICES)
    date = models.DateField()
    employment_status = models.CharField(max_length=50)
    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"{self.trainee.name} - {self.followup_type}"
class UserProfile(models.Model):

    ROLE_CHOICES = [
        ("Authority", "Authority"),
        ("Trainer", "Trainer"),
        ("Trainee", "Trainee"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )

    trainee = models.OneToOneField(
        "Trainee",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.role}"
class TrainingBatch(models.Model):

    name = models.CharField(max_length=150)

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE
    )

    provider = models.ForeignKey(
        Provider,
        on_delete=models.CASCADE
    )

    trainer = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    district = models.CharField(max_length=50)

    start_date = models.DateField()

    end_date = models.DateField()

    capacity = models.PositiveIntegerField(default=30)

    trainees = models.ManyToManyField(
        Trainee,
        blank=True
    )
    attendance = models.JSONField(default=dict, blank=True)

    progress = models.JSONField(default=dict, blank=True)
    remarks = models.JSONField(default=dict, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("Active", "Active"),
            ("Completed", "Completed"),
        ],
        default="Active"
    )


    def __str__(self):
        return self.name
class TrainerRegistration(models.Model):

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Verified", "Verified"),
        ("Rejected", "Rejected"),
    ]

    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    organization = models.CharField(max_length=150)
    district = models.CharField(max_length=50)
    qualification = models.CharField(max_length=150)
    experience = models.PositiveIntegerField(default=0)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    registration_date = models.DateField()

    def __str__(self):
        return f"{self.name} - {self.organization}"