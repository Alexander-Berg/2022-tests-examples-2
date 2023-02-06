.PHONY: switch-to-eats
switch-to-eats:
	cp ../docker-compose.yml ../docker-compose.yml.backup
	cp docker-compose.yml ../docker-compose.yml
	cp ../volumes/tools/wait_services.sh ../volumes/tools/wait_services.sh.backup
	cp wait_services.sh ../volumes/tools/wait_services.sh
	cp ../volumes/taximeter-emulator/settings_eats.py ../volumes/taximeter-emulator/settings_tests.py
	./../scripts/check_permissions.sh

.PHONY: switch-to-taxi
switch-to-taxi:
	mv ../docker-compose.yml.backup ../docker-compose.yml
	mv ../volumes/tools/wait_services.sh.backup ../volumes/tools/wait_services.sh
