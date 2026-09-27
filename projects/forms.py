from django import forms
from .models import Project, Tag, Comment, Report


class BootstrapFormMixin:
    def _apply_bootstrap(self):
        for field in self.fields.values():
            existing = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (existing + ' form-control').strip()


class ProjectForm(BootstrapFormMixin, forms.ModelForm):
    tags_input = forms.CharField(
        required=False,
        help_text="Comma-separated tags, e.g. education, kids, egypt",
    )
    picture1 = forms.ImageField(required=False, label="Picture 1")
    picture2 = forms.ImageField(required=False, label="Picture 2")
    picture3 = forms.ImageField(required=False, label="Picture 3")

    class Meta:
        model = Project
        fields = ['title', 'details', 'category', 'total_target', 'start_time', 'end_time']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'details': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap()

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('start_time')
        end = cleaned.get('end_time')
        if start and end and end <= start:
            raise forms.ValidationError("End time must be after start time.")
        return cleaned

    def save_tags(self, project):
        tags_input = self.cleaned_data.get('tags_input', '')
        names = [t.strip() for t in tags_input.split(',') if t.strip()]
        tag_objects = []
        for name in names:
            tag, _ = Tag.objects.get_or_create(name=name.lower())
            tag_objects.append(tag)
        project.tags.set(tag_objects)


class CommentForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
        widgets = {'body': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Write a comment...'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap()


class DonationForm(BootstrapFormMixin, forms.Form):
    amount = forms.DecimalField(min_value=1, max_digits=12, decimal_places=2)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap()


class ReportForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Report
        fields = ['reason']
        widgets = {'reason': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Why are you reporting this?'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap()