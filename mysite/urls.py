from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^$', 'rallybench.views.login'), 
    url(r'^rallybench/', include('rallybench.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

