from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("register/", views.register, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("history/", views.history, name="history"),
    path("profile/", views.profile, name="profile"),
    path("category/<int:pk>/delete/", views.category_delete, name="category_delete"),
    path("export/csv/", views.export_csv, name="export_csv"),
    path("export/pdf/", views.export_pdf, name="export_pdf"),
    path("export/csv/<int:pk>/", views.export_csv, name="export_csv_pk"),
    path("export/pdf/<int:pk>/", views.export_pdf, name="export_pdf_pk"),
]
