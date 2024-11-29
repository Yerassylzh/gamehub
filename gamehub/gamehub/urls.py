from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static

import gamehub
import club.urls
import authpage.urls

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(authpage.urls)),
    path("club/", include(club.urls)),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if gamehub.settings.DEBUG:
    import debug_toolbar
    print("Added debug toolbar")

    urlpatterns += [
        path(
            "__debug__/",
            include(
                debug_toolbar.urls,
            ),
        ),
    ]
