from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Count

from roadmap.models import Career, Skills, CareerSkill
from .forms import ContactForm


def home(request):
    careers = Career.objects.annotate(skill_count=Count('required_skills')).filter(skill_count__gt=0).order_by('stream', 'name')[:12]
    context = {
        'careers': careers,
        'total_skills': Skills.objects.count(),
        'total_careers': Career.objects.count(),
    }
    return render(request, 'pages/home.html', context)


def about(request):
    return render(request, 'pages/about.html')


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thanks for reaching out — we'll get back to you soon.")
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'pages/contact.html', {'form': form})


def find_your_path(request):
    """Nav entry point: sends logged-in users into their flow, others to sign up."""
    if request.user.is_authenticated:
        return redirect('post-login')
    return redirect('signup')
