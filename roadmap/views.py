from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import (
    Skills, Career, CareerSkill, UserProfile, UserSkills, LearningPath, PathSkill, StudyLog,
    SkillSubtopic, SubtopicProgress
)
from .serializers import (
    SkillSerializer, CareerSerializer, QuestionnaireSubmitSerializer,
    LearningPathSerializer, StudyLogSerializer
)
from .services import generate_learning_path


# ---------- Template views ----------

def post_login_redirect(request):
    """Sends the user to questionnaire or dashboard depending on onboarding state."""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if profile.has_completed_onboarding:
        return redirect('dashboard-page')
    return redirect('questionnaire-page')


@login_required
def questionnaire_page(request):
    # Only offer careers that actually have a seeded curriculum (CareerSkill rows).
    # Career.CAREER_OPTIONS lists every possible enum value, but a career with no
    # requirements seeded would generate an empty (0-skill) roadmap.
    career_skill_ids = {}
    for career_name, skill_id in CareerSkill.objects.values_list('career__name', 'skill_id'):
        career_skill_ids.setdefault(career_name, []).append(skill_id)

    careers_by_name = {c.name: c for c in Career.objects.all()}
    careers = []
    for value, label in Career.CAREER_OPTIONS:
        if value not in career_skill_ids:
            continue
        obj = careers_by_name.get(value)
        careers.append({
            'value': value,
            'label': label,
            'stream': obj.stream if obj else 'TECHNICAL',
            'tagline': obj.tagline if obj else '',
            'description': obj.description if obj else '',
            'example_roles': [r.strip() for r in obj.example_roles.split(',') if r.strip()] if obj else [],
            'requires_coding': obj.requires_coding if obj else True,
            'skill_ids': career_skill_ids[value],
        })

    educations = [
        {'value': v, 'label': l, 'non_tech': v in UserProfile.NON_TECH_EDUCATION}
        for v, l in UserProfile.EDUCATION_CHOICES
    ]
    return render(request, 'questionnaire.html', {
        'skills': Skills.objects.prefetch_related('subtopics').all(),
        'careers': careers,
        'educations': educations,
        'experiences': UserProfile.EXPERIENCE_CHOICES,
    })


# ---------- API views ----------

class SkillListAPIView(generics.ListAPIView):
    queryset = Skills.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [IsAuthenticated]


class CareerListAPIView(generics.ListAPIView):
    queryset = Career.objects.all()
    serializer_class = CareerSerializer
    permission_classes = [IsAuthenticated]


class QuestionnaireSubmitAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = QuestionnaireSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if not CareerSkill.objects.filter(career__name=data['career']).exists():
            return Response(
                {'career': ["This career path doesn't have a curriculum set up yet. Please choose a different one."]},
                status=status.HTTP_400_BAD_REQUEST
            )

        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        profile.education = data['education']
        profile.experience_level = data['experience_level']
        profile.daily_study_time = data['daily_study_time']
        profile.study_days_per_week = data['study_days_per_week']
        profile.has_completed_onboarding = True
        profile.save()

        known_subtopic_ids_by_skill = {}
        fully_known_skill_ids = set()

        for item in data.get('known_skills', []):
            skill_id = item.get('skill_id')
            if not skill_id:
                continue
            skill_level = item.get('skill_level', 'BEGINNER')
            UserSkills.objects.update_or_create(
                user=profile, skill_id=skill_id,
                defaults={'skill_level': skill_level}
            )

            subtopic_ids = item.get('known_subtopic_ids') or []
            if subtopic_ids:
                known_subtopic_ids_by_skill[skill_id] = set(subtopic_ids)
            if item.get('fully_known'):
                fully_known_skill_ids.add(skill_id)

        career, _ = Career.objects.get_or_create(name=data['career'])
        path = generate_learning_path(
            profile, career,
            known_subtopic_ids_by_skill=known_subtopic_ids_by_skill,
            fully_known_skill_ids=fully_known_skill_ids,
        )

        return Response({
            'message': 'Questionnaire submitted successfully.',
            'learning_path_id': path.id,
        }, status=status.HTTP_201_CREATED)


class MyLearningPathAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        path = LearningPath.objects.filter(user=profile, is_active=True).order_by('-created_at').first()
        if not path:
            return Response({'detail': 'No active learning path found.'}, status=status.HTTP_404_NOT_FOUND)

        completed_subtopic_ids = set(
            SubtopicProgress.objects.filter(user=profile, is_completed=True)
            .values_list('subtopic_id', flat=True)
        )
        serializer = LearningPathSerializer(path, context={'completed_subtopic_ids': completed_subtopic_ids})
        return Response(serializer.data)


class ToggleSubtopicAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            subtopic = SkillSubtopic.objects.select_related('skill').get(pk=pk)
        except SkillSubtopic.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        profile, _ = UserProfile.objects.get_or_create(user=request.user)

        # This subtopic must belong to a skill that's part of the user's active roadmap.
        path_skill = PathSkill.objects.filter(
            path__user=profile, path__is_active=True, skill=subtopic.skill
        ).select_related('path').first()
        if not path_skill:
            return Response({'detail': 'This topic is not part of your current roadmap.'},
                             status=status.HTTP_403_FORBIDDEN)

        completed = request.data.get('completed')
        progress, _ = SubtopicProgress.objects.get_or_create(user=profile, subtopic=subtopic)
        new_state = (not progress.is_completed) if completed is None else bool(completed)
        progress.toggle(new_state)

        # Auto-complete/reopen the parent PathSkill based on subtopic completion.
        all_subtopics = list(subtopic.skill.subtopics.all())
        if all_subtopics:
            completed_count = SubtopicProgress.objects.filter(
                user=profile, subtopic__in=all_subtopics, is_completed=True
            ).count()
            if completed_count == len(all_subtopics) and path_skill.status != 'COMPLETED':
                path_skill.mark_completed()
            elif completed_count < len(all_subtopics) and path_skill.status == 'COMPLETED':
                path_skill.status = 'IN_PROGRESS'
                path_skill.completed_at = None
                path_skill.save()
            elif completed_count > 0 and path_skill.status == 'NOT_STARTED':
                path_skill.status = 'IN_PROGRESS'
                path_skill.save()

        return Response({
            'subtopic_id': subtopic.id,
            'is_completed': progress.is_completed,
            'path_skill_status': path_skill.status,
        })


class CompletePathSkillAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            path_skill = PathSkill.objects.select_related('path__user__user').get(pk=pk)
        except PathSkill.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        if path_skill.path.user.user != request.user:
            return Response({'detail': 'Not allowed.'}, status=status.HTTP_403_FORBIDDEN)

        hours = request.data.get('hours_logged', 0)
        if hours:
            StudyLog.objects.create(
                user=path_skill.path.user, path_skill=path_skill, hours=float(hours)
            )

        path_skill.mark_completed()
        return Response({'message': f'{path_skill.skill.name} marked as completed.'})


class LogStudyHoursAPIView(generics.CreateAPIView):
    serializer_class = StudyLogSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx

    def perform_create(self, serializer):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        serializer.save(user=profile)
