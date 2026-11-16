from django.conf import settings
from django.http import FileResponse, Http404
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_safe


@never_cache
@require_safe
def index(request):
    path = settings.FRONTEND_DIR / "index.html"
    if not path.is_file():
        raise Http404("Build the frontend before serving the production application.")
    return FileResponse(path.open("rb"), content_type="text/html")
