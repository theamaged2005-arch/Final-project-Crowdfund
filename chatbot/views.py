import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .matching import get_answer


@csrf_exempt
@require_POST
def ask(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid request'}, status=400)

    message = (data.get('message') or '').strip()
    if not message:
        return JsonResponse({'error': 'Empty message'}, status=400)

    answer = get_answer(message)
    return JsonResponse({'answer': answer})