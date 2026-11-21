from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf.urls.static import static
from django.conf import settings
from django.http import HttpResponse, Http404, FileResponse
import mimetypes
from pathlib import Path


REACT_BUILD_DIR = settings.BASE_DIR / "frontend" / "build"


def react_app(request, *args, **kwargs):
    index_file = REACT_BUILD_DIR / "index.html"
    if not index_file.exists():
        raise Http404("React build not found. Run npm run build.")
    return HttpResponse(index_file.read_text(encoding="utf-8"), content_type="text/html")


def react_or_django_static(request, path):
    build_file = REACT_BUILD_DIR / "static" / path
    if build_file.is_file():
        content_type, _ = mimetypes.guess_type(str(build_file))
        return HttpResponse(build_file.read_bytes(), content_type=content_type or "application/octet-stream")

    django_static = settings.BASE_DIR / "frontend" / "static" / path
    if django_static.is_file():
        content_type, _ = mimetypes.guess_type(str(django_static))
        return FileResponse(django_static.open("rb"), content_type=content_type)

    raise Http404()


def react_css(request, filename):
    file = REACT_BUILD_DIR / "static" / "css" / filename
    if not file.is_file():
        raise Http404()
    return HttpResponse(file.read_bytes(), content_type="text/css")


def react_js(request, filename):
    file = REACT_BUILD_DIR / "static" / "js" / filename
    if not file.is_file():
        raise Http404()
    return HttpResponse(file.read_bytes(), content_type="application/javascript")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('djangoapp/', include('djangoapp.urls')),
    path('', TemplateView.as_view(template_name="Home.html")),
    path('login', react_app),
    path('login/', react_app),
    path('register', react_app),
    path('register/', react_app),
    path('dealers', react_app),
    path('dealers/', react_app),
    path('dealer/<int:dealer_id>', react_app),
    path('dealer/<int:dealer_id>/', react_app),
    path('postreview/<int:dealer_id>', react_app),
    path('postreview/<int:dealer_id>/', react_app),
    path('about/', TemplateView.as_view(template_name="About.html")),
    path('about', TemplateView.as_view(template_name="About.html")),
    path('contact/', TemplateView.as_view(template_name="Contact.html")),
    path('contact', TemplateView.as_view(template_name="Contact.html")),
]

urlpatterns += [
    path('static/css/<str:filename>', react_css),
    path('static/js/<str:filename>', react_js),
    path('static/<path:path>', react_or_django_static),
]
