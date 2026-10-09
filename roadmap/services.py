from django.utils import timezone
from .models import CareerSkill, LearningPath, PathSkill, SkillSubtopic, SubtopicProgress

DURATION_MAP = {
    'BEGINNER': 5,
    'INTERMEDIATE': 8,
    'ADVANCED': 12,
}


def generate_learning_path(user_profile, career, known_subtopic_ids_by_skill=None, fully_known_skill_ids=None):
    """
    Build a LearningPath for the given user + career.

    Unlike a simple "skip what they know" approach, every required skill for the
    career is added to the roadmap so the user's full skill path is visible --
    but anything they told us they already know (via the questionnaire) is
    pre-marked as completed, at the subtopic level where we have that detail.

    known_subtopic_ids_by_skill: {skill_id: set(subtopic_id, ...)} -- subtopics
        the user says they already know, per skill.
    fully_known_skill_ids: set(skill_id, ...) -- skills the user marked as known
        with no subtopic-level detail available (older/blank questionnaire path).
    """
    known_subtopic_ids_by_skill = known_subtopic_ids_by_skill or {}
    fully_known_skill_ids = fully_known_skill_ids or set()

    # Deactivate any previous active path for this career (fresh start)
    LearningPath.objects.filter(user=user_profile, career=career, is_active=True).update(is_active=False)

    required_skills = CareerSkill.objects.filter(career=career).select_related('skill').order_by('priority')

    path = LearningPath.objects.create(user=user_profile, career=career, estimated_duration=0)

    sequence = 1
    total_days = 0
    path_skills = []
    for req in required_skills:
        duration = req.skill.typical_duration_days or DURATION_MAP.get(req.required_level, 7)
        path_skills.append(PathSkill(
            path=path, skill=req.skill, sequence=sequence, duration=duration
        ))
        sequence += 1
        total_days += duration

    PathSkill.objects.bulk_create(path_skills)

    path.estimated_duration = total_days
    path.save(update_fields=['estimated_duration'])

    _apply_known_progress(user_profile, path, known_subtopic_ids_by_skill, fully_known_skill_ids)

    return path


def _apply_known_progress(user_profile, path, known_subtopic_ids_by_skill, fully_known_skill_ids):
    """Pre-mark subtopics/skills the user already knows as completed on the new path."""
    for path_skill in path.path_skills.select_related('skill').all():
        skill = path_skill.skill
        all_subtopics = list(skill.subtopics.all())
        known_ids = set(known_subtopic_ids_by_skill.get(skill.id, []))

        if all_subtopics:
            progress_to_create = []
            for subtopic in all_subtopics:
                is_known = subtopic.id in known_ids or skill.id in fully_known_skill_ids
                if is_known:
                    progress_to_create.append(SubtopicProgress(
                        user=user_profile, subtopic=subtopic,
                        is_completed=True, completed_at=timezone.now()
                    ))
            if progress_to_create:
                SubtopicProgress.objects.bulk_create(progress_to_create, ignore_conflicts=True)

            completed_count = SubtopicProgress.objects.filter(
                user=user_profile, subtopic__in=all_subtopics, is_completed=True
            ).count()
            if completed_count == len(all_subtopics):
                path_skill.mark_completed()
            elif completed_count > 0:
                path_skill.status = 'IN_PROGRESS'
                path_skill.save(update_fields=['status'])
        elif skill.id in fully_known_skill_ids:
            # No subtopic breakdown exists for this skill -- mark the whole step done.
            path_skill.mark_completed()
