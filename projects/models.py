from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Project(models.Model):
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200)
    details = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='projects')
    tags = models.ManyToManyField(Tag, blank=True, related_name='projects')
    total_target = models.DecimalField(max_digits=12, decimal_places=2)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_featured = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('projects:detail', args=[self.pk])

    @property
    def total_donated(self):
        return self.donations.aggregate(total=models.Sum('amount'))['total'] or 0

    @property
    def progress_percent(self):
        if not self.total_target:
            return 0
        return min(100, round((self.total_donated / self.total_target) * 100, 1))

    @property
    def is_running(self):
        now = timezone.now()
        return (not self.is_cancelled) and self.start_time <= now <= self.end_time

    @property
    def average_rating(self):
        return self.ratings.aggregate(avg=models.Avg('stars'))['avg'] or 0

    @property
    def can_be_cancelled(self):
        if not self.total_target:
            return True
        return (self.total_donated / self.total_target) * 100 < 25

    @property
    def first_picture(self):
        return self.pictures.first()


class ProjectPicture(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='pictures')
    image = models.ImageField(upload_to='project_pictures/')

    def __str__(self):
        return f"Picture for {self.project.title}"


class Donation(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='donations')
    donor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='donations')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.donor.email} donated {self.amount} to {self.project.title}"


class Comment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author.email} on {self.project.title}"


class Rating(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ratings')
    stars = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('project', 'user')

    def __str__(self):
        return f"{self.user.email} rated {self.project.title}: {self.stars}"


class Report(models.Model):
    REPORT_TYPES = [
        ('project', 'Project'),
        ('comment', 'Comment'),
    ]
    report_type = models.CharField(max_length=10, choices=REPORT_TYPES)
    project = models.ForeignKey(Project, null=True, blank=True, on_delete=models.CASCADE, related_name='reports')
    comment = models.ForeignKey(Comment, null=True, blank=True, on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports')
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report by {self.reporter.email} ({self.report_type})"