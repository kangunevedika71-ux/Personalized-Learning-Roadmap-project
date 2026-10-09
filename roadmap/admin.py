from django.contrib import admin
from .models import (
    UserProfile, Skills, UserSkills, Career, CareerSkill,
    LearningPath, PathSkill, StudyLog, SkillSubtopic, SubtopicProgress
)

admin.site.register(UserProfile)
admin.site.register(Skills)
admin.site.register(UserSkills)
admin.site.register(Career)
admin.site.register(CareerSkill)
admin.site.register(LearningPath)
admin.site.register(PathSkill)
admin.site.register(StudyLog)
admin.site.register(SkillSubtopic)
admin.site.register(SubtopicProgress)
