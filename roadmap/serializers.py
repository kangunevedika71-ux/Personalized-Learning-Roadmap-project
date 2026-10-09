from rest_framework import serializers
from .models import (
    UserProfile, Skills, UserSkills, Career, CareerSkill,
    LearningPath, PathSkill, StudyLog, SkillSubtopic, SubtopicProgress
)


class SkillSubtopicSerializer(serializers.ModelSerializer):
    is_completed = serializers.SerializerMethodField()

    class Meta:
        model = SkillSubtopic
        fields = ['id', 'group', 'title', 'order', 'is_completed']

    def get_is_completed(self, obj):
        completed_ids = self.context.get('completed_subtopic_ids', set())
        return obj.id in completed_ids


class SkillSerializer(serializers.ModelSerializer):
    subtopics = SkillSubtopicSerializer(many=True, read_only=True)

    class Meta:
        model = Skills
        fields = ['id', 'name', 'category', 'description', 'subtopics']


class CareerSerializer(serializers.ModelSerializer):
    name_display = serializers.CharField(source='get_name_display', read_only=True)

    class Meta:
        model = Career
        fields = [
            'id', 'name', 'name_display', 'description', 'stream', 'tagline',
            'example_roles', 'requires_coding',
        ]


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'education', 'experience_level', 'daily_study_time', 'has_completed_onboarding']


class QuestionnaireSubmitSerializer(serializers.Serializer):
    education = serializers.ChoiceField(choices=UserProfile.EDUCATION_CHOICES)
    experience_level = serializers.ChoiceField(choices=UserProfile.EXPERIENCE_CHOICES)
    daily_study_time = serializers.FloatField(min_value=0, max_value=24)
    study_days_per_week = serializers.IntegerField(min_value=1, max_value=7, default=5)
    career = serializers.ChoiceField(choices=Career.CAREER_OPTIONS)
    known_skills = serializers.ListField(
        child=serializers.DictField(), required=False, default=list,
        help_text=(
            "[{'skill_id': 1, 'skill_level': 'BEGINNER', "
            "'fully_known': false, 'known_subtopic_ids': [3, 4, 7]}, ...]"
        )
    )


class PathSkillSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(source='skill.name', read_only=True)
    description = serializers.CharField(source='skill.description', read_only=True)
    category = serializers.CharField(source='skill.category', read_only=True)
    subtopics = serializers.SerializerMethodField()
    subtopics_total = serializers.SerializerMethodField()
    subtopics_completed = serializers.SerializerMethodField()

    class Meta:
        model = PathSkill
        fields = [
            'id', 'skill', 'skill_name', 'description', 'category', 'sequence', 'duration', 'status',
            'completed_at', 'subtopics', 'subtopics_total', 'subtopics_completed'
        ]
        read_only_fields = [
            'id', 'skill', 'skill_name', 'description', 'category', 'sequence', 'duration', 'completed_at',
            'subtopics', 'subtopics_total', 'subtopics_completed'
        ]

    def _subtopic_qs(self, obj):
        # cache per-instance to avoid re-querying for total/completed/list
        if not hasattr(obj, '_cached_subtopics'):
            obj._cached_subtopics = list(obj.skill.subtopics.all())
        return obj._cached_subtopics

    def get_subtopics(self, obj):
        subtopics = self._subtopic_qs(obj)
        return SkillSubtopicSerializer(subtopics, many=True, context=self.context).data

    def get_subtopics_total(self, obj):
        return len(self._subtopic_qs(obj))

    def get_subtopics_completed(self, obj):
        completed_ids = self.context.get('completed_subtopic_ids', set())
        return sum(1 for s in self._subtopic_qs(obj) if s.id in completed_ids)


class LearningPathSerializer(serializers.ModelSerializer):
    career_name = serializers.CharField(source='career.get_name_display', read_only=True)
    career_stream = serializers.CharField(source='career.stream', read_only=True)
    path_skills = PathSkillSerializer(many=True, read_only=True)
    percent_complete = serializers.ReadOnlyField()
    total_skills = serializers.ReadOnlyField()
    completed_skills = serializers.ReadOnlyField()
    is_completed = serializers.ReadOnlyField()

    class Meta:
        model = LearningPath
        fields = [
            'id', 'career', 'career_name', 'career_stream', 'estimated_duration', 'created_at',
            'path_skills', 'percent_complete', 'total_skills', 'completed_skills', 'is_completed'
        ]


class StudyLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyLog
        fields = ['id', 'path_skill', 'hours', 'date']

    def validate_path_skill(self, path_skill):
        request = self.context['request']
        if path_skill.path.user.user != request.user:
            raise serializers.ValidationError("This roadmap step does not belong to you.")
        return path_skill
