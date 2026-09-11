from django.contrib import admin
from .models import TrainerRegistration

# Register your models here.
from django.contrib import admin
from .models import (
    Trainee,
    Course,
    Provider,
    Training,
    Employment,
    FollowUp,
    Notification,
    WageRecord,
    TrainingRelevance,
    RetentionRecord,
    OccupationSkill,
)
admin.site.register(TrainerRegistration)



admin.site.register(Trainee)
admin.site.register(Course)
admin.site.register(Provider)
admin.site.register(Training)
admin.site.register(Employment)
admin.site.register(FollowUp)
admin.site.register(Notification)
admin.site.register(WageRecord)
admin.site.register(TrainingRelevance)
admin.site.register(RetentionRecord)
admin.site.register(OccupationSkill)
