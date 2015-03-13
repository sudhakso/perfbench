from django.conf.urls import patterns, url

from rallybench import views

#login, session, per-scenario views
urlpatterns = patterns('',
    url(r'^login/$', views.login, name='login'),    
    url(r'^(?P<username>\w+)/$', views.usersession, name='session'),
    url(r'^(?P<username>\w+)/deployment/$', views.deployment, name='deployment'),
    url(r'^(?P<username>\w+)/scenario/$', views.scenario, name='scenario'),
    url(r'^(?P<username>\w+)/tasklist/$', views.task, name='task'),
    url(r'^(?P<username>\w+)/result/$', views.result, name='result'),
)
