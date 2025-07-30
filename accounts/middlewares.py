# middleware.py
from django.utils import timezone

class UpdateLastSeenMiddleware:
  def __init__(self, get_response):
    self.get_response = get_response

  def __call__(self, request):
    response = self.get_response(request)

    if request.user.is_authenticated:
      now = timezone.now()
      if not request.user.last_seen or (now - request.user.last_seen).seconds > 60:
        request.user.last_seen = now
        request.user.save(update_fields=['last_seen'])

    return response
