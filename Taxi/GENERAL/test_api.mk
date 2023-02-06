test-api:: test-api-event-push-token

test-api-event-push-token:
	curl -sf \
	  -H "Authorization: Token hello" \
	  -H "Content-Type: application/json" \
	  --data "[]" ${BACKEND_URL}/api/ev/push \
		> /dev/null && echo 'Event push eats token'
