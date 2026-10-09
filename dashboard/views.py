from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render
from django.db.models import Sum, Count
from django.db.models.functions import TruncDate
from django.contrib.auth.decorators import login_required

from roadmap.models import UserProfile, LearningPath, PathSkill, StudyLog, SubtopicProgress
from roadmap.serializers import PathSkillSerializer


@login_required
def dashboard_page(request):
    return render(request, 'dashboard.html')


class DashboardSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        path = LearningPath.objects.filter(user=profile, is_active=True).order_by('-created_at').first()

        if not path:
            return Response({
                'has_roadmap': False,
                'message': 'Complete the questionnaire to generate your roadmap.'
            })

        if path.total_skills == 0:
            # Can happen for accounts created before career curricula were locked down
            # to only seeded careers (a career with no CareerSkill rows generates an
            # empty roadmap). Offer a clear way to recover instead of blank charts.
            return Response({
                'has_roadmap': False,
                'is_empty_career': True,
                'career': path.career.get_name_display(),
                'message': (
                    f"\"{path.career.get_name_display()}\" doesn't have a curriculum set up yet. "
                    "Please retake the questionnaire and choose a different career path."
                )
            })

        total_hours = StudyLog.objects.filter(user=profile).aggregate(total=Sum('hours'))['total'] or 0

        # Hours per day (kept for potential future use)
        hours_per_day = (
            StudyLog.objects.filter(user=profile)
            .values('date')
            .annotate(total=Sum('hours'))
            .order_by('date')
        )

        completed_subtopic_ids = set(
            SubtopicProgress.objects.filter(user=profile, is_completed=True)
            .values_list('subtopic_id', flat=True)
        )
        topics = PathSkillSerializer(
            path.path_skills.all(), many=True,
            context={'completed_subtopic_ids': completed_subtopic_ids}
        ).data

        # Progress-by-skill: % of subtopics completed per skill in THIS roadmap.
        # Works even if the user never manually logs hours -- it's driven by the
        # subtopic checklist, which is how most progress actually happens.
        progress_by_skill = [
            {
                'skill': t['skill_name'],
                'status': t['status'],
                'percent': round((t['subtopics_completed'] / t['subtopics_total']) * 100, 1)
                           if t['subtopics_total'] else (100 if t['status'] == 'COMPLETED' else 0),
            }
            for t in topics
        ]

        # Progress-over-time: cumulative subtopics completed by day, across this roadmap's skills.
        skill_ids_in_path = [t['skill'] for t in topics]
        daily_completions = (
            SubtopicProgress.objects.filter(
                user=profile, is_completed=True, subtopic__skill_id__in=skill_ids_in_path
            )
            .annotate(day=TruncDate('completed_at'))
            .values('day')
            .annotate(count=Count('id'))
            .order_by('day')
        )
        cumulative = 0
        progress_over_time = []
        for row in daily_completions:
            cumulative += row['count']
            progress_over_time.append({'date': row['day'], 'cumulative': cumulative})

        # Next up: first roadmap step that isn't completed yet, in sequence order.
        next_skill = next((t for t in topics if t['status'] != 'COMPLETED'), None)

        return Response({
            'has_roadmap': True,
            'career': path.career.get_name_display(),
            'daily_study_time_goal': profile.daily_study_time,
            'total_hours_spent': total_hours,
            'percent_complete': path.percent_complete,
            'total_skills': path.total_skills,
            'completed_skills': path.completed_skills,
            'is_completed': path.is_completed,
            'next_up': next_skill['skill_name'] if next_skill else None,
            'topics': topics,
            'progress_by_skill': progress_by_skill,
            'progress_over_time': progress_over_time,
            'hours_per_day': [{'date': h['date'], 'hours': h['total']} for h in hours_per_day],
        })
