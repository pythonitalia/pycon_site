from jobboard import models
from django.contrib import admin
from django import forms
from django_summernote.widgets import SummernoteWidget


class JobsAdminForm(forms.ModelForm):
    class Meta:
        model = models.JobOffer
        widgets = {
            'job_description_en': SummernoteWidget(),
            'job_description_it': SummernoteWidget(),
        }



class JobsAdmin(admin.ModelAdmin):
    form = JobsAdminForm



# class JobsAdminForm(forms.ModelForm):
#     class Meta:
#         model = models.JobOffer
#         widgets = {
#            'job_description_it': RedactorEditor(),
#            'job_description_en': RedactorEditor(),
#         }
#
#
# class JobsAdmin(admin.ModelAdmin):
#     form = JobsAdminForm


admin.site.register(models.JobOffer, JobsAdmin)
