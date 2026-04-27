import json
import logging

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


logger = logging.getLogger('perf.web_vitals')


def _to_float(value, default=0.0):
	try:
		return float(value)
	except (TypeError, ValueError):
		return default


@csrf_exempt
@require_POST
def ingest_web_vitals(request):
	# sendBeacon posts are tiny JSON payloads; reject oversized bodies early.
	if len(request.body or b'') > 8192:
		return JsonResponse({'error': 'payload_too_large'}, status=413)

	try:
		payload = json.loads((request.body or b'{}').decode('utf-8'))
	except (UnicodeDecodeError, json.JSONDecodeError):
		return JsonResponse({'error': 'invalid_json'}, status=400)

	path = str(payload.get('path', ''))[:300]
	if not path.startswith('/'):
		path = request.path

	lcp = max(_to_float(payload.get('lcp')), 0.0)
	inp = max(_to_float(payload.get('inp')), 0.0)
	fcp = max(_to_float(payload.get('fcp')), 0.0)
	cls = max(_to_float(payload.get('cls')), 0.0)

	data = {
		'path': path,
		'lcp_ms': round(lcp, 2),
		'inp_ms': round(inp, 2),
		'fcp_ms': round(fcp, 2),
		'cls': round(cls, 4),
		'user_id': request.user.id if request.user.is_authenticated else None,
		'ip': (request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() or request.META.get('REMOTE_ADDR', '')),
		'ua': str(request.META.get('HTTP_USER_AGENT', ''))[:200],
	}

	logger.info('web_vitals %s', json.dumps(data, separators=(',', ':')))
	return HttpResponse(status=204)
