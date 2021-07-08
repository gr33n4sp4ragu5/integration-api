"""colintmet_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/register', views.Register.as_view()),
    path('login/', views.Login.as_view()),
    path('login/refresh', views.LoginRefresh.as_view()),
    path('surveys/answer', views.PostSurveyAnswer.as_view()),
    path('physiological/data', views.PostPhysiologicalData.as_view()),
    path('profile/data', views.Profile.as_view()),
    path('profile/edit', views.ModifyProfile.as_view()),
    path('surveys/finished', views.FinishedSurveys.as_view()),
    path('physiological/researcher', views.GetPhysiologicalData.as_view()),
    path('projects/researcher', views.PostNewProject.as_view()),
    path('groups/researcher', views.PostNewGroup.as_view()),
    path('register/researcher', views.RegisterResearcher.as_view()),
    path('mongodb/query', views.QueryMongo.as_view()),
    path('surveys/activated', views.ActivatedSurveys.as_view()),
]
