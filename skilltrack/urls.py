from django.urls import path
from . import  views
urlpatterns=[
    path('dashboard',views.dashboard , name='dashboard'),
    path("trainees/", views.trainee_list, name="trainee_list"),
    path("trainees/add/", views.trainee_create, name="trainee_create"),
    path("trainees/<int:id>/", views.trainee_detail, name="trainee_detail"),
    path("trainees/<int:id>/edit/", views.trainee_update, name="trainee_update"),
    path("trainees/<int:id>/delete/", views.trainee_delete, name="trainee_delete"),
path(
    "register-trainee/",
    views.trainee_register,
    name="trainee_register"
),
path(
    "trainees/<int:id>/verify/",
    views.verify_trainee,
    name="verify_trainee"
),
    path("", views.login_view, name="login"),

path(
    "trainees/<int:id>/reject/",
    views.reject_trainee,
    name="reject_trainee"
),path(
    "trainer-dashboard/",
    views.trainer_dashboard,
    name="trainer_dashboard"
),
path(
    "trainee-dashboard/",
    views.trainee_dashboard,
    name="trainee_dashboard"
),
path(
    "training/add/",
    views.training_create,
    name="training_create"

),
path(
    "training/",
    views.training_list,
    name="training_list"
),
path(
    "training/batches/create/",
    views.training_batch_create,
    name="training_batch_create"
),
path(
    "register-trainer/",
    views.trainer_register,
    name="trainer_register"
),path(
    "trainers/",
    views.trainer_list,
    name="trainer_list"
),

path(
    "trainers/<int:id>/",
    views.trainer_detail,
    name="trainer_detail"
),

path(
    "trainers/<int:id>/verify/",
    views.verify_trainer,
    name="verify_trainer"
),

path(
    "trainers/<int:id>/reject/",
    views.reject_trainer,
    name="reject_trainer"
),
path(
    "courses/",
    views.course_list,
    name="course_list"
),
path(
    "courses/add/",
    views.course_create,
    name="course_create"
),
path(
    "training/batches/add/",
    views.batch_create,
    name="batch_create"
),
path(
    "providers/",
    views.provider_list,
    name="provider_list"
),

path(
    "providers/<int:id>/",
    views.provider_detail,
    name="provider_detail"
),

path(
    "providers/<int:id>/verify/",
    views.verify_provider,
    name="verify_provider"
),

path(
    "providers/<int:id>/reject/",
    views.reject_provider,
    name="reject_provider"
),
path(
    "training/batches/",
    views.batch_list,
    name="batch_list"
),
path(
    "training/batches/<int:id>/assign/",
    views.batch_assign_trainees,
    name="batch_assign_trainees"
),
path(
    "trainer/batches/<int:id>/",
    views.trainer_batch_detail,
    name="trainer_batch_detail"
),
path(
    "trainer/batches/<int:id>/progress/",
    views.trainer_batch_progress,
    name="trainer_batch_progress"
),
path(
    "trainer/batches/<int:id>/complete/",
    views.trainer_complete_batch,
    name="trainer_complete_batch"
),
path("logout/", views.logout_view, name="logout"),
]