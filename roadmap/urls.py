from django.urls import path
from . import views

urlpatterns = [
    # template pages
    path('questionnaire/', views.questionnaire_page, name='questionnaire-page'),

    # api
    path('api/skills/', views.SkillListAPIView.as_view(), name='api-skills'),
    path('api/careers/', views.CareerListAPIView.as_view(), name='api-careers'),
    path('api/questionnaire/submit/', views.QuestionnaireSubmitAPIView.as_view(), name='api-questionnaire-submit'),
    path('api/roadmap/mine/', views.MyLearningPathAPIView.as_view(), name='api-roadmap-mine'),
    path('api/roadmap/skill/<int:pk>/complete/', views.CompletePathSkillAPIView.as_view(), name='api-skill-complete'),
    path('api/roadmap/subtopic/<int:pk>/toggle/', views.ToggleSubtopicAPIView.as_view(), name='api-subtopic-toggle'),
    path('api/roadmap/log-hours/', views.LogStudyHoursAPIView.as_view(), name='api-log-hours'),
]
