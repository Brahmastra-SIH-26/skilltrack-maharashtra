from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Course, Employment, FollowUp, Provider, Trainee, TrainerRegistration, Training, TrainingBatch, UserProfile


class CoreWorkflowTests(TestCase):
    def make_authority(self):
        user = User.objects.create_user("authority", password="pass12345")
        UserProfile.objects.create(user=user, role="Authority")
        return user

    def make_trainee(self, status="Verified"):
        user = User.objects.create_user("MH-2026-000001", password="pass12345")
        trainee = Trainee.objects.create(
            user=user, beneficiary_id="MH-2026-000001", name="Asha", phone="9876543210",
            email="asha@example.com", district="Pune", qualification="12th", gender="Female",
            registration_date=date.today(), status=status, consent_given=True,
        )
        UserProfile.objects.create(user=user, role="Trainee", trainee=trainee)
        return user, trainee

    def make_verified_trainer(self):
        user = User.objects.create_user("trainer@example.com", password="pass12345")
        trainer = TrainerRegistration.objects.create(
            user=user, name="Trainer", phone="9876543211", email="trainer@example.com",
            organization="Institute", district="Pune", qualification="Degree", experience=2,
            registration_date=date.today(), status="Verified",
        )
        UserProfile.objects.create(user=user, role="Trainer")
        return user, trainer

    def test_trainee_cannot_access_authority_dashboard(self):
        trainee_user, _ = self.make_trainee()
        self.client.force_login(trainee_user)
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_pending_trainer_cannot_log_in_to_trainer_workflows(self):
        user = User.objects.create_user("pending@example.com", password="pass12345")
        TrainerRegistration.objects.create(
            user=user, name="Pending", phone="9876543212", email="pending@example.com",
            organization="Institute", district="Pune", qualification="Degree", experience=1,
            registration_date=date.today(), status="Pending",
        )
        UserProfile.objects.create(user=user, role="Trainer")
        response = self.client.post(reverse("login"), {"username": "pending@example.com", "password": "pass12345"})
        self.assertContains(response, "pending Authority approval")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_authority_assigns_verified_trainee_and_only_owner_can_open_batch(self):
        authority = self.make_authority()
        trainee_user, trainee = self.make_trainee()
        trainer_user, _ = self.make_verified_trainer()
        other = User.objects.create_user("other@example.com", password="pass12345")
        TrainerRegistration.objects.create(user=other, name="Other", phone="9876543213", email="other@example.com", organization="I", district="Pune", qualification="Degree", experience=1, registration_date=date.today(), status="Verified")
        UserProfile.objects.create(user=other, role="Trainer")
        provider = Provider.objects.create(name="Provider", provider_type="NGO", district="Pune", status="Verified")
        course = Course.objects.create(name="Course", sector="IT", duration="30 days")
        batch = TrainingBatch.objects.create(name="Batch", course=course, provider=provider, trainer=trainer_user, district="Pune", start_date=date.today(), end_date=date.today(), capacity=5)
        self.client.force_login(authority)
        response = self.client.post(reverse("batch_assign_trainees", args=[batch.id]), {"trainees": [trainee.id]})
        self.assertRedirects(response, reverse("batch_list"))
        self.assertTrue(batch.trainees.filter(id=trainee.id).exists())
        self.client.force_login(other)
        self.assertEqual(self.client.get(reverse("trainer_batch_detail", args=[batch.id])).status_code, 404)

    def test_completed_batch_generates_unique_followups(self):
        _, trainee = self.make_trainee()
        trainer_user, _ = self.make_verified_trainer()
        provider = Provider.objects.create(name="Provider", provider_type="NGO", district="Pune", status="Verified")
        course = Course.objects.create(name="Course", sector="IT", duration="30 days")
        batch = TrainingBatch.objects.create(name="Batch", course=course, provider=provider, trainer=trainer_user, district="Pune", start_date=date.today(), end_date=date.today(), capacity=5)
        batch.trainees.add(trainee)
        Training.objects.create(trainee=trainee, course=course, provider=provider, batch=batch, trainer=trainer_user, start_date=date.today(), end_date=date.today(), completion_percentage=100, status="Training")
        self.client.force_login(trainer_user)
        response = self.client.post(reverse("trainer_complete_batch", args=[batch.id]))
        self.assertRedirects(response, reverse("trainer_batch_detail", args=[batch.id]))
        self.assertEqual(FollowUp.objects.filter(trainee=trainee).count(), 5)

    def test_uan_demo_verification_creates_a_verified_outcome_for_its_owner(self):
        trainee_user, trainee = self.make_trainee()
        self.client.force_login(trainee_user)
        response = self.client.post(reverse("verify_uan"), {"uan": "100000000001"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        outcome = Employment.objects.get(trainee=trainee)
        self.assertEqual(outcome.status, "Employed")
        self.assertEqual(outcome.verification_status, "Verified")

# Create your tests here.
