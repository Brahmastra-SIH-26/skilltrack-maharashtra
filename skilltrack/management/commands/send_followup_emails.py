from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone

from skilltrack.models import FollowUp


class Command(BaseCommand):
    help = "Send emails for due trainee follow-ups"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Send all incomplete follow-ups immediately for testing",
        )

    def handle(self, *args, **options):

        force = options["force"]
        today = timezone.localdate()

        if force:
            followups = FollowUp.objects.filter(
                email_sent=False,
                completed=False
            ).select_related("trainee")

            self.stdout.write(
                self.style.WARNING(
                    "FORCE MODE: Sending follow-ups immediately."
                )
            )

        else:
            followups = FollowUp.objects.filter(
                date__lte=today,
                email_sent=False,
                completed=False
            ).select_related("trainee")

        if not followups.exists():
            self.stdout.write(
                self.style.WARNING(
                    "No follow-ups found."
                )
            )
            return

        sent_count = 0

        for followup in followups:

            trainee = followup.trainee

            if not trainee.email:
                self.stdout.write(
                    self.style.WARNING(
                        f"No email address for {trainee.name}"
                    )
                )
                continue

            subject = (
                f"SkillTrack Maharashtra - "
                f"{followup.followup_type} Follow-up"
            )

            message = f"""
Dear {trainee.name},

This is a follow-up reminder from SkillTrack Maharashtra.

Follow-up Type: {followup.followup_type}
Follow-up Date: {followup.date}

Current Employment Status:
{followup.employment_status}

Remarks:
{followup.remarks or "No remarks"}

Please update your employment information.

Regards,
SkillTrack Maharashtra
"""

            try:
                send_mail(
                    subject,
                    message,
                    None,
                    [trainee.email],
                    fail_silently=False
                )

                followup.email_sent = True
                followup.email_sent_at = timezone.now()

                followup.save(
                    update_fields=[
                        "email_sent",
                        "email_sent_at"
                    ]
                )

                sent_count += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Email sent successfully to {trainee.email}"
                    )
                )

            except Exception as e:

                self.stdout.write(
                    self.style.ERROR(
                        f"Email failed for {trainee.name}: {e}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Finished. Emails sent: {sent_count}"
            )
        )