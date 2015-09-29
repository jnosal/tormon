from . import views

urlpatterns = [
    (r"/api/stats/", views.StatsHandler),
    (r"/api/urls/", views.UrlsListHandler),
    (r"/api/url/", views.UrlDetailsHandler),
]