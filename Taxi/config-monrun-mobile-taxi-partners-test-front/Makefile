install:
	mkdir -p $(DESTDIR)/etc/monrun/conf.d
	mkdir -p $(DESTDIR)/usr/bin
	install -D -m 644 $(CURDIR)/src/taxi-partners-front-balancing.conf $(DESTDIR)/etc/monrun/conf.d
	install -D -m 755 $(CURDIR)/src/taxi-partners-front-balancing.sh $(DESTDIR)/usr/bin/taxi-partners-front-balancing.sh
