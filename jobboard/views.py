# Create your views here.
from django.views.generic import ListView, DetailView
from .models import JobOffer
from django.shortcuts import HttpResponse


class JobList(ListView):
    model = JobOffer

    def get_queryset(self):
        return JobOffer.objects.order_by('pk')

    def get_context_data(self, **kwargs):
        context = super(JobList, self).get_context_data(**kwargs)
        return context


class JobDetail(DetailView):
    model = JobOffer

    def get_context_data(self, **kwargs):
        context = super(JobDetail, self).get_context_data(**kwargs)
        return context