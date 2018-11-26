__author__ = 'ernesto'
from .views import JobList, JobDetail
from django.conf.urls import patterns, url
from django.utils.translation import ugettext_lazy as _


urlpatterns = patterns(
    'jobboard.views',
    url('^$', view=JobList.as_view(), name='job_list'),
    url('detail/(?P<slug>[\w-]+)', JobDetail.as_view(), name='job-detail'),
)