from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .forms import ProjectForm, CommentForm, DonationForm, ReportForm
from .models import Project, ProjectPicture, Category, Donation, Comment, Rating, Report


@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.creator = request.user
            project.save()
            form.save_tags(project)

            for field_name in ['picture1', 'picture2', 'picture3']:
                f = form.cleaned_data.get(field_name)
                if f:
                    ProjectPicture.objects.create(project=project, image=f)

            messages.success(request, "Project created successfully!")
            return redirect('projects:detail', pk=project.pk)
    else:
        form = ProjectForm()
    return render(request, 'projects/project_form.html', {'form': form})


def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)

    comments = project.comments.filter(parent__isnull=True).select_related('author')
    comment_form = CommentForm()
    donation_form = DonationForm()

    user_rating = None
    if request.user.is_authenticated:
        user_rating = Rating.objects.filter(project=project, user=request.user).first()

    similar_projects = Project.objects.filter(
        tags__in=project.tags.all()
    ).exclude(pk=project.pk).distinct()[:4]

    context = {
        'project': project,
        'comments': comments,
        'comment_form': comment_form,
        'donation_form': donation_form,
        'user_rating': user_rating,
        'similar_projects': similar_projects,
    }
    return render(request, 'projects/project_detail.html', context)
@login_required
def project_donate(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            Donation.objects.create(project=project, donor=request.user, amount=form.cleaned_data['amount'])
            messages.success(request, "Thank you for your donation!")
        else:
            messages.error(request, "Please enter a valid amount.")
    return redirect('projects:detail', pk=pk)


@login_required
def project_comment(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.project = project
            comment.author = request.user
            comment.save()
    return redirect('projects:detail', pk=pk)


@login_required
def comment_reply(request, pk, comment_id):
    project = get_object_or_404(Project, pk=pk)
    parent = get_object_or_404(Comment, pk=comment_id, project=project)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.project = project
            reply.author = request.user
            reply.parent = parent
            reply.save()
    return redirect('projects:detail', pk=pk)


@login_required
def project_rate(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        stars = request.POST.get('stars')
        if stars and stars.isdigit() and 1 <= int(stars) <= 5:
            Rating.objects.update_or_create(project=project, user=request.user, defaults={'stars': int(stars)})
    return redirect('projects:detail', pk=pk)


@login_required
def project_cancel(request, pk):
    project = get_object_or_404(Project, pk=pk, creator=request.user)
    if request.method == 'POST':
        if project.can_be_cancelled:
            project.is_cancelled = True
            project.save(update_fields=['is_cancelled'])
            messages.success(request, "Project cancelled.")
        else:
            messages.error(request, "Cannot cancel - donations exceed 25% of the target.")
    return redirect('projects:detail', pk=pk)


@login_required
def project_report(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.report_type = 'project'
            report.project = project
            report.reporter = request.user
            report.save()
            messages.success(request, "Report submitted. Thank you.")
    return redirect('projects:detail', pk=pk)


@login_required
def comment_report(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.report_type = 'comment'
            report.comment = comment
            report.reporter = request.user
            report.save()
            messages.success(request, "Report submitted. Thank you.")
    return redirect('projects:detail', pk=comment.project.pk)


def search(request):
    query = request.GET.get('q', '').strip()
    results = Project.objects.none()
    if query:
        results = Project.objects.filter(
            Q(title__icontains=query) | Q(tags__name__icontains=query)
        ).distinct()
    return render(request, 'projects/search_results.html', {'results': results, 'query': query})


def category_projects(request, pk):
    category = get_object_or_404(Category, pk=pk)
    projects = category.projects.all()
    return render(request, 'projects/category_projects.html', {'category': category, 'projects': projects})