from django.urls import path, re_path
from drf_spectacular.views import SpectacularAPIView

from literature import api

urlpatterns = [
    path("api/health/", api.health),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/session/", api.session),
    re_path(r"^api/auth/(?P<action>register|login|logout)/$", api.account),
    path("api/profile/", api.profile),
    path("api/search/", api.search),
    path("api/search/record/", api.record_search),
    path("api/advanced/", api.advanced),
    path("api/publications/<str:pmid>/", api.publication),
    re_path(r"^api/publications/(?P<pmid>[^/]+)/(?P<kind>related|cited-by)/$", api.relationships),
    path("api/bookmarks/", api.Bookmarks.as_view(http_method_names=["get", "post"])),
    path("api/bookmarks/<str:pmid>/", api.Bookmarks.as_view(http_method_names=["delete"])),
    path("api/collections/", api.Collections.as_view(http_method_names=["get", "post"])),
    path("api/collections/<int:pk>/", api.CollectionDetail.as_view()),
    path("api/collections/<int:pk>/articles/", api.CollectionArticles.as_view(http_method_names=["post"])),
    path("api/collections/<int:pk>/articles/<str:pmid>/", api.CollectionArticles.as_view(http_method_names=["delete"])),
    path("api/history/", api.history),
    path("api/history/<int:pk>/", api.history_item),
    path("api/saved-searches/", api.saved_searches),
    path("api/saved-searches/<int:pk>/", api.saved_search_item),
    path("api/citations/", api.export),
]
