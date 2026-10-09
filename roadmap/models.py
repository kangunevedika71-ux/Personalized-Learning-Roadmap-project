from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    EDUCATION_CHOICES = [
        ('BSC_CS', 'Bsc Computer Science'),
        ('BSC_IT', 'Bsc Information Technology'),
        ('BSC_SE', 'Bsc Software Engineering'),
        ('BSC_CY', 'Bsc Cyber Security'),
        ('BSC_DS', 'Bsc Data Science'),
        ('BSC_AI', 'Bsc Artificial Intelligence'),
        ('BSC_CE', 'Bsc Computer Engineering'),
        ('BCA', 'Bsc Computer Application'),
        ('BCS', 'Bsc Computer Science'),
        ('BTECH', 'Btech (CS/IT/SE)'),
        # Non-technical / business streams
        ('BBA', 'BBA (Bachelor of Business Administration)'),
        ('BCOM', 'B.Com (Commerce)'),
        ('BMS', 'BMS / BBM / BMM'),
        ('BA', 'BA (Arts / Humanities / Economics)'),
        ('MBA', 'MBA / PGDM'),
        ('MCOM', 'M.Com / MA / MSc (non-technical)'),
        ('HSC_COMMERCE', '12th - Commerce'),
        ('HSC_ARTS', '12th - Arts / Humanities'),
        ('OTHER_NON_TECH', 'Other (non-technical)'),
    ]

    # Used by the questionnaire to pre-select the right stream of careers.
    NON_TECH_EDUCATION = {
        'BBA', 'BCOM', 'BMS', 'BA', 'MBA', 'MCOM', 'HSC_COMMERCE', 'HSC_ARTS', 'OTHER_NON_TECH',
    }

    EXPERIENCE_CHOICES = [
        ('BEGINNER', 'Beginner'),
        ('INTERMEDIATE', 'Intermediate'),
        ('ADVANCED', 'Advanced'),
        ('EXPERT', 'Expert'),
    ]

    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    education = models.CharField(max_length=20, choices=EDUCATION_CHOICES, blank=True)
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, blank=True)
    daily_study_time = models.FloatField(help_text='Daily study time in hours', default=0)
    study_days_per_week = models.PositiveSmallIntegerField(default=5, help_text='Days per week the user can study')
    has_completed_onboarding = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_education_display() if self.education else 'N/A'}"


class Skills(models.Model):
    CATEGORY_CHOICES = [
        ('PROGRAMMING', 'Programming'),
        ('WEB_DEVELOPMENT', 'Web Development'),
        ('DATA_SCIENCE', 'Data Science'),
        ('MOBILE_APP_DEVELOPMENT', 'Mobile App Development'),
        ('GAME_DEVELOPMENT', 'Game Development'),
        ('CLOUD_COMPUTING', 'Cloud Computing'),
        ('CYBER_SECURITY', 'Cyber Security'),
        ('ARTIFICIAL_INTELLIGENCE', 'Artificial Intelligence'),
        ('MACHINE_LEARNING', 'Machine Learning'),
        ('BLOCKCHAIN', 'Blockchain'),
        ('DATABASE', 'Database'),
        ('SOFTWARE_ENGINEERING', 'Software Engineering'),
        ('NETWORKING', 'Networking'),
        ('UI_UX_DESIGN', 'UI/UX Design'),
        ('DEVOPS', 'DevOps'),
        ('OS', 'Operating Systems'),
        ('ALGORITHMS', 'Algorithms'),
        ('DATA_STRUCTURES', 'Data Structures'),
        ('AI_ML', 'AI/ML'),
        # Business / non-technical
        ('BUSINESS_FOUNDATION', 'Business Foundations'),
        ('MARKETING', 'Marketing'),
        ('BUSINESS_ANALYSIS', 'Business Analysis'),
        ('HUMAN_RESOURCES', 'Human Resources'),
        ('FINANCE', 'Finance & Accounting'),
        ('SALES', 'Sales'),
        ('PRODUCT_MANAGEMENT', 'Product Management'),
        ('OPERATIONS', 'Operations & Supply Chain'),
        ('ENTREPRENEURSHIP', 'Entrepreneurship'),
        ('CAREER_READINESS', 'Career Readiness'),
    ]

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField(
        blank=True,
        help_text="Plain-language explanation of what this skill is and why it matters "
                  "(shown to beginners on the roadmap)."
    )
    typical_duration_days = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Realistic time to learn this topic, in days. Falls back to a "
                   "level-based estimate on the roadmap if left blank."
    )

    def __str__(self):
        return self.name


class UserSkills(models.Model):
    SKILL_LEVEL_CHOICES = [
        ('BEGINNER', 'Beginner'),
        ('INTERMEDIATE', 'Intermediate'),
        ('ADVANCED', 'Advanced'),
    ]

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='skills')
    skill = models.ForeignKey(Skills, on_delete=models.CASCADE, related_name='user_skills')
    skill_level = models.CharField(max_length=20, choices=SKILL_LEVEL_CHOICES)

    class Meta:
        unique_together = ('user', 'skill')

    def __str__(self):
        return f"{self.user.user.username} - {self.skill.name} ({self.get_skill_level_display()})"


class Career(models.Model):
    CAREER_OPTIONS = [
        ('PROGRAMMING', 'Programming'),
        ('WEB_DEVELOPMENT', 'Web Development'),
        ('DATA_SCIENCE', 'Data Science'),
        ('DATA_ANALYST', 'Data Analyst'),
        ('MOBILE_APP_DEVELOPMENT', 'App Development'),
        ('GAME_DEVELOPMENT', 'Game Development'),
        ('CLOUD_COMPUTING', 'Cloud Computing (AWS)'),
        ('CYBER_SECURITY', 'Cyber Security'),
        ('ARTIFICIAL_INTELLIGENCE', 'Artificial Intelligence'),
        ('MACHINE_LEARNING', 'Machine Learning'),
        ('DEEP_LEARNING', 'Deep Learning'),
        ('BLOCKCHAIN', 'Blockchain'),
        ('DATABASE', 'Database Manager (DBA)'),
        ('SOFTWARE_ENGINEERING', 'Software Engineering'),
        ('NETWORKING', 'Networking'),
        ('UI_UX_DESIGN', 'UI/UX Design'),
        ('DEVOPS', 'DevOps'),
        ('JAVA_DEVELOPER', 'Java Developer'),
        ('BACKEND_DEVELOPER', 'Backend Developer'),
        ('FRONTEND_DEVELOPER', 'Frontend Developer'),
        ('FULL_STACK_DEVELOPER', 'Full Stack Developer (Node.js + React)'),
        ('OS', 'Operating Systems'),
        ('ALGORITHMS', 'Algorithms'),
        ('DATA_STRUCTURES', 'Data Structures'),
        ('AI_ML', 'AI/ML'),
        # Business / non-technical careers
        ('DIGITAL_MARKETING', 'Digital Marketing'),
        ('BUSINESS_ANALYST', 'Business Analyst'),
        ('HR_MANAGEMENT', 'HR / People Management'),
        ('FINANCIAL_ANALYST', 'Finance & Financial Analyst'),
        ('SALES_BIZ_DEV', 'Sales & Business Development'),
        ('PRODUCT_MANAGEMENT', 'Product Management'),
        ('OPERATIONS_SUPPLY_CHAIN', 'Operations & Supply Chain'),
        ('ENTREPRENEURSHIP', 'Entrepreneurship / Startup Founder'),
    ]

    STREAM_CHOICES = [
        ('TECHNICAL', 'Technical'),
        ('BUSINESS', 'Business / Non-technical'),
    ]

    name = models.CharField(max_length=30, choices=CAREER_OPTIONS, unique=True)
    description = models.TextField(blank=True)
    stream = models.CharField(max_length=10, choices=STREAM_CHOICES, default='TECHNICAL')
    tagline = models.CharField(
        max_length=160, blank=True,
        help_text="One-line, jargon-free summary shown on the career card."
    )
    example_roles = models.CharField(
        max_length=300, blank=True,
        help_text="Comma-separated job titles a beginner could aim for."
    )
    requires_coding = models.BooleanField(default=True)

    def __str__(self):
        return self.get_name_display()


class CareerSkill(models.Model):
    REQUIRED_LEVEL_CHOICES = [
        ('BEGINNER', 'Beginner'),
        ('INTERMEDIATE', 'Intermediate'),
        ('ADVANCED', 'Advanced'),
    ]

    id = models.AutoField(primary_key=True)
    career = models.ForeignKey(Career, on_delete=models.CASCADE, related_name='required_skills')
    skill = models.ForeignKey(Skills, on_delete=models.CASCADE, related_name='career_skills')
    required_level = models.CharField(max_length=20, choices=REQUIRED_LEVEL_CHOICES)
    priority = models.IntegerField(default=1)

    class Meta:
        unique_together = ('career', 'skill')
        ordering = ['priority']

    def __str__(self):
        return f"{self.career.name} needs {self.skill.name} ({self.get_required_level_display()})"


class LearningPath(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='learning_paths')
    career = models.ForeignKey(Career, on_delete=models.CASCADE, related_name='learning_paths')
    estimated_duration = models.IntegerField(help_text="Estimated duration in days", default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.user.username} - {self.career.name} ({self.estimated_duration} days)"

    @property
    def total_skills(self):
        return self.path_skills.count()

    @property
    def completed_skills(self):
        return self.path_skills.filter(status='COMPLETED').count()

    @property
    def percent_complete(self):
        total = self.total_skills
        if total == 0:
            return 100
        return round((self.completed_skills / total) * 100, 1)

    @property
    def is_completed(self):
        return self.total_skills > 0 and self.completed_skills == self.total_skills


class PathSkill(models.Model):
    STATUS_CHOICES = [
        ('NOT_STARTED', 'Not Started'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
    ]

    id = models.AutoField(primary_key=True)
    path = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name='path_skills')
    skill = models.ForeignKey(Skills, on_delete=models.CASCADE, related_name='path_skills')
    sequence = models.IntegerField()
    duration = models.IntegerField(help_text="Estimated learning days")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NOT_STARTED')
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('path', 'skill')
        ordering = ['sequence']

    def mark_completed(self):
        self.status = 'COMPLETED'
        self.completed_at = timezone.now()
        self.save()

    def __str__(self):
        return f"{self.path} - Step {self.sequence}: {self.skill.name} ({self.get_status_display()})"


class StudyLog(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='study_logs')
    path_skill = models.ForeignKey(PathSkill, on_delete=models.CASCADE, related_name='logs')
    hours = models.FloatField()
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.user.user.username} - {self.path_skill.skill.name} - {self.hours}h on {self.date}"


class SkillSubtopic(models.Model):
    """
    A specific learning point within a Skill (e.g. Skill='Python Basics' ->
    subtopics = ['Variables', 'Data types', 'Loops', 'Functions', ...]).
    Lets the roadmap show a real syllabus per topic, not just a title.
    """
    id = models.AutoField(primary_key=True)
    skill = models.ForeignKey(Skills, on_delete=models.CASCADE, related_name='subtopics')
    group = models.CharField(
        max_length=100, blank=True,
        help_text="Optional sub-heading, e.g. 'Core Python' or 'Advanced SQL'"
    )
    title = models.CharField(max_length=150)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.skill.name} → {self.title}"


class SubtopicProgress(models.Model):
    """Per-user checkbox state for a SkillSubtopic."""
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='subtopic_progress')
    subtopic = models.ForeignKey(SkillSubtopic, on_delete=models.CASCADE, related_name='progress_entries')
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'subtopic')

    def toggle(self, completed):
        self.is_completed = completed
        self.completed_at = timezone.now() if completed else None
        self.save()

    def __str__(self):
        return f"{self.user.user.username} - {self.subtopic.title} - {'done' if self.is_completed else 'pending'}"
