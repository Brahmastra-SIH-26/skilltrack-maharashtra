from datetime import date, timedelta
import random

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.apps import apps
from django.db import transaction


class Command(BaseCommand):
    help = "Creates demo data for SkillTrack Maharashtra"

    @transaction.atomic
    def handle(self, *args, **kwargs):

        # =========================================================
        # LOAD MODELS
        # =========================================================

        Trainee = apps.get_model("skilltrack", "Trainee")
        Course = apps.get_model("skilltrack", "Course")
        Provider = apps.get_model("skilltrack", "Provider")
        Training = apps.get_model("skilltrack", "Training")
        Employment = apps.get_model("skilltrack", "Employment")
        FollowUp = apps.get_model("skilltrack", "FollowUp")
        UserProfile = apps.get_model("skilltrack", "UserProfile")
        TrainingBatch = apps.get_model("skilltrack", "TrainingBatch")
        TrainerRegistration = apps.get_model(
            "skilltrack", "TrainerRegistration"
        )
        Notification = apps.get_model("skilltrack", "Notification")
        TrainingRegistrationRequest = apps.get_model(
            "skilltrack", "TrainingRegistrationRequest"
        )
        UANVerification = apps.get_model(
            "skilltrack", "UANVerification"
        )
        SelfEmploymentVerification = apps.get_model(
            "skilltrack", "SelfEmploymentVerification"
        )

        today = date.today()

        # =========================================================
        # COURSES
        # =========================================================

        course_data = [
            ("Full Stack Web Development", "IT & Software", "6 Months"),
            ("Python Programming", "IT & Software", "3 Months"),
            ("Data Science & Machine Learning", "IT & Software", "6 Months"),
            ("Digital Marketing", "Marketing", "3 Months"),
            ("Electrician", "Electrical", "6 Months"),
            ("Solar Panel Technician", "Renewable Energy", "4 Months"),
            ("Tailoring", "Apparel", "3 Months"),
            ("Beauty & Wellness", "Beauty", "3 Months"),
            ("Automobile Technician", "Automotive", "6 Months"),
            ("Graphic Design", "Media", "4 Months"),
            ("CNC Machine Operator", "Manufacturing", "6 Months"),
            ("Healthcare Assistant", "Healthcare", "6 Months"),
        ]

        courses = []

        for name, sector, duration in course_data:
            course, _ = Course.objects.get_or_create(
                name=name,
                defaults={
                    "sector": sector,
                    "duration": duration,
                },
            )
            courses.append(course)

        # =========================================================
        # PROVIDERS
        # =========================================================

        districts = [
            "Mumbai",
            "Pune",
            "Nagpur",
            "Nashik",
            "Thane",
            "Aurangabad",
            "Kolhapur",
            "Solapur",
        ]

        providers = []

        for i in range(1, 9):
            provider, _ = Provider.objects.get_or_create(
                name=f"Skill Training Centre {i}",
                defaults={
                    "provider_type": (
                        "Government Training Centre"
                        if i % 2 == 0
                        else "Private Training Institute"
                    ),
                    "district": districts[(i - 1) % len(districts)],
                    "rating": round(random.uniform(3.5, 5.0), 1),
                    "status": "Verified",
                },
            )

            providers.append(provider)

        # =========================================================
        # TRAINER USERS
        # =========================================================

        trainers = []

        for i in range(1, 11):

            username = f"demo_trainer_{i}"

            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": f"Trainer{i}",
                    "last_name": "Demo",
                    "email": f"trainer{i}@skilltrack.demo",
                },
            )

            if created:
                user.set_password("Demo@12345")
                user.save()

            UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    "role": "Trainer",
                },
            )

            trainers.append(user)

        # =========================================================
        # TRAINER REGISTRATIONS
        # =========================================================

        for i, trainer in enumerate(trainers, start=1):

            TrainerRegistration.objects.get_or_create(
                name=f"{trainer.first_name} {trainer.last_name}",
                email=f"trainer{i}@skilltrack.demo",
                defaults={
                    "phone": f"90000000{i:02d}",
                    "organization": providers[
                        (i - 1) % len(providers)
                    ].name,
                    "district": districts[
                        (i - 1) % len(districts)
                    ],
                    "qualification": "B.Tech / Diploma",
                    "experience": random.randint(2, 10),
                    "status": "Verified",
                    "user": trainer,
                    "registration_date": today
                    - timedelta(days=random.randint(30, 500)),
                },
            )

        # =========================================================
        # TRAINEES
        # =========================================================

        names = [
            "Aarav Sharma",
            "Aditya Patil",
            "Ananya Singh",
            "Priya Deshmukh",
            "Rohan Kulkarni",
            "Sneha Joshi",
            "Rahul Pawar",
            "Pooja More",
            "Vikas Jadhav",
            "Neha Shinde",
            "Amit Chavan",
            "Kavya Gaikwad",
            "Sahil Thakur",
            "Isha Patil",
            "Akash Yadav",
            "Riya Gupta",
            "Manish Verma",
            "Simran Kaur",
            "Nikhil Desai",
            "Tanvi Shah",
            "Karan Mishra",
            "Meera Joshi",
            "Raj Malhotra",
            "Payal Pawar",
            "Siddharth More",
            "Komal Patil",
            "Abhishek Singh",
            "Muskan Sharma",
            "Harsh Vaidya",
            "Divya Kulkarni",
        ]

        trainees = []

        for i in range(1, 31):

            trainee, _ = Trainee.objects.get_or_create(
                beneficiary_id=f"MHDEMO{i:06d}",
                defaults={
                    "name": names[i - 1],
                    "phone": f"91{9000000000 + i}",
                    "email": f"trainee{i}@skilltrack.demo",
                    "district": districts[
                        (i - 1) % len(districts)
                    ],
                    "qualification": random.choice(
                        [
                            "10th Pass",
                            "12th Pass",
                            "ITI",
                            "Diploma",
                            "Graduate",
                        ]
                    ),
                    "gender": random.choice(
                        ["Male", "Female"]
                    ),
                    "registration_date": today
                    - timedelta(
                        days=random.randint(30, 500)
                    ),
                    "status": "Verified",
                },
            )

            trainees.append(trainee)

        # =========================================================
        # TRAINEE USERS
        # =========================================================

        for i, trainee in enumerate(trainees, start=1):

            username = f"demo_trainee_{i}"

            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": trainee.name.split()[0],
                    "email": trainee.email,
                },
            )

            if created:
                user.set_password("Demo@12345")
                user.save()

            profile, _ = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    "role": "Trainee",
                    "trainee": trainee,
                },
            )

            # In case profile already existed without trainee
            if profile.trainee_id is None:
                profile.trainee = trainee
                profile.save()

        # =========================================================
        # TRAINING BATCHES
        # =========================================================

        batches = []

        for i in range(1, 16):

            course = courses[(i - 1) % len(courses)]
            provider = providers[(i - 1) % len(providers)]
            trainer = trainers[(i - 1) % len(trainers)]

            start = today - timedelta(
                days=random.randint(30, 180)
            )

            end = start + timedelta(
                days=random.randint(90, 180)
            )

            batch, _ = TrainingBatch.objects.get_or_create(
                name=f"{course.name} - Batch {i}",
                defaults={
                    "course": course,
                    "provider": provider,
                    "trainer": trainer,
                    "district": provider.district,
                    "start_date": start,
                    "end_date": end,
                    "capacity": 30,
                    "status": (
                        "Completed"
                        if end < today
                        else "Active"
                    ),
                    "completion_date": (
                        end if end < today else None
                    ),
                },
            )

            batches.append(batch)

        # =========================================================
        # ASSIGN TRAINEES + ATTENDANCE + PROGRESS
        # =========================================================

        for i, trainee in enumerate(trainees):

            batch = batches[i % len(batches)]

            batch.trainees.add(trainee)

            attendance = batch.attendance or {}
            progress = batch.progress or {}
            remarks = batch.remarks or {}

            attendance[str(trainee.id)] = random.choice(
                [
                    "Present",
                    "Present",
                    "Present",
                    "Absent",
                ]
            )

            progress[str(trainee.id)] = random.randint(
                40, 100
            )

            remarks[str(trainee.id)] = "Demo training record"

            batch.attendance = attendance
            batch.progress = progress
            batch.remarks = remarks
            batch.save()

        # =========================================================
        # TRAINING RECORDS
        # =========================================================

        for i, trainee in enumerate(trainees):

            batch = batches[i % len(batches)]

            Training.objects.get_or_create(
                trainee=trainee,
                course=batch.course,
                provider=batch.provider,
                defaults={
                    "start_date": batch.start_date,
                    "end_date": batch.end_date,
                    "completion_percentage": random.randint(
                        40, 100
                    ),
                    "status": random.choice(
                        [
                            "Pending",
                            "Training",
                            "Completed",
                        ]
                    ),
                },
            )

        # =========================================================
        # EMPLOYMENT + UAN
        # =========================================================

        employment_statuses = [
            "Employed",
            "Employed",
            "Employed",
            "Seeking",
            "Unemployed",
            "Self-Employed",
        ]

        for i, trainee in enumerate(
            trainees, start=1
        ):

            status = employment_statuses[
                (i - 1) % len(employment_statuses)
            ]

            employment, _ = Employment.objects.get_or_create(
                trainee=trainee,
                defaults={
                    "status": status,
                },
            )

            # -----------------------------------------------------
            # EMPLOYED
            # -----------------------------------------------------

            if status == "Employed":

                employment.uan_demo = (
                    f"{100000000000 + i}"
                )

                employment.employer_name = random.choice(
                    [
                        "Tata Technologies",
                        "Mahindra Group",
                        "Infosys",
                        "Tech Mahindra",
                        "Larsen & Toubro",
                        "Persistent Systems",
                    ]
                )

                employment.job_role = random.choice(
                    [
                        "Software Developer",
                        "Technician",
                        "Data Entry Operator",
                        "Machine Operator",
                        "Support Executive",
                    ]
                )

                employment.employment_type = "Full Time"

                employment.salary = random.randint(
                    18000, 60000
                )

                employment.employment_date = (
                    today
                    - timedelta(
                        days=random.randint(30, 400)
                    )
                )

                employment.save()

                # UAN DEMO VERIFICATION
                UANVerification.objects.get_or_create(
                    employment=employment,
                    uan=employment.uan_demo,
                    defaults={
                        "verified": True,
                        "verification_message": (
                            "Demo UAN verified successfully"
                        ),
                    },
                )

            # -----------------------------------------------------
            # SELF EMPLOYED
            # -----------------------------------------------------

            elif status == "Self-Employed":

                employment.registration_number = (
                    f"MSME-DEMO-{i:05d}"
                )

                employment.business_name = (
                    f"Demo Enterprise {i}"
                )

                employment.business_type = random.choice(
                    [
                        "Retail",
                        "Repair Services",
                        "Tailoring",
                        "Digital Services",
                    ]
                )

                employment.work_description = (
                    "Demo self-employment record"
                )

                employment.save()

                SelfEmploymentVerification.objects.get_or_create(
                    employment=employment,
                    defaults={
                        "registration_number": (
                            employment.registration_number
                        ),
                        "business_name": (
                            employment.business_name
                        ),
                        "business_type": (
                            employment.business_type
                        ),
                        "work_description": (
                            employment.work_description
                        ),
                        "status": "Verified",
                        "verification_message": (
                            "Demo business verified"
                        ),
                        "verified_at": today,
                    },
                )

        # =========================================================
        # FOLLOW UPS
        # =========================================================

        followup_types = [
            ("3 Months", 90),
            ("6 Months", 180),
            ("1 Year", 365),
            ("3 Years", 1095),
            ("5 Years", 1825),
        ]

        for trainee in trainees:

            employment = Employment.objects.get(
                trainee=trainee
            )

            for follow_type, days in followup_types[:2]:

                FollowUp.objects.get_or_create(
                    trainee=trainee,
                    followup_type=follow_type,
                    defaults={
                        "date": today
                        + timedelta(days=days),
                        "employment_status": (
                            employment.status
                        ),
                        "remarks": (
                            "Demo follow-up record"
                        ),
                        "completed": False,
                    },
                )

        # =========================================================
        # TRAINING REGISTRATION REQUESTS
        # =========================================================

        for i, trainee in enumerate(trainees):

            batch = batches[i % len(batches)]

            TrainingRegistrationRequest.objects.get_or_create(
                trainee=trainee,
                batch=batch,
                defaults={
                    "status": random.choice(
                        [
                            "Pending",
                            "Verified",
                            "Rejected",
                        ]
                    ),
                    "rejection_reason": "",
                },
            )

        # =========================================================
        # NOTIFICATIONS
        # =========================================================

        users = list(
            User.objects.filter(
                username__startswith="demo_"
            )
        )

        for user in users:

            Notification.objects.get_or_create(
                recipient=user,
                message=(
                    "Welcome to SkillTrack Maharashtra "
                    "demo portal."
                ),
                defaults={
                    "notification_type": "System",
                },
            )

        # =========================================================
        # FINAL RESULT
        # =========================================================

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "=============================================="
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                " SkillTrack Maharashtra Demo Data Created!"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "=============================================="
            )
        )

        self.stdout.write(
            f"Trainees: {Trainee.objects.count()}"
        )

        self.stdout.write(
            f"Courses: {Course.objects.count()}"
        )

        self.stdout.write(
            f"Providers: {Provider.objects.count()}"
        )

        self.stdout.write(
            f"Training batches: "
            f"{TrainingBatch.objects.count()}"
        )

        self.stdout.write(
            f"Training records: "
            f"{Training.objects.count()}"
        )

        self.stdout.write(
            f"Employment records: "
            f"{Employment.objects.count()}"
        )

        self.stdout.write(
            f"Follow-ups: "
            f"{FollowUp.objects.count()}"
        )

        self.stdout.write(
            f"UAN verifications: "
            f"{UANVerification.objects.count()}"
        )

        self.stdout.write(
            f"Self-employment verifications: "
            f"{SelfEmploymentVerification.objects.count()}"
        )

        self.stdout.write("")
        self.stdout.write(
            self.style.WARNING(
                "Demo login password: Demo@12345"
            )
        )