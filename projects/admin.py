from django.contrib import admin
from .models import Category, Tag, Project, ProjectPicture, Donation, Comment, Rating, Report


class ProjectPictureInline(admin.TabularInline):
    model = ProjectPicture
    extra = 1


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'category', 'total_target', 'is_featured', 'is_cancelled', 'created_at')
    list_filter = ('category', 'is_featured', 'is_cancelled')
    search_fields = ('title', 'details')
    inlines = [ProjectPictureInline]


admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Donation)
admin.site.register(Comment)
admin.site.register(Rating)
admin.site.register(Report)