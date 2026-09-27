from django.db import models


class FAQ(models.Model):
    question = models.CharField(max_length=255, help_text="The main question, e.g. 'How do I donate?'")
    keywords = models.CharField(
        max_length=255,
        help_text="Comma-separated keywords that should trigger this answer, e.g. donate, donation, give money",
    )
    answer = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.question

    def keyword_list(self):
        return [k.strip().lower() for k in self.keywords.split(',') if k.strip()]