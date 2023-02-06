install:
	mkdir -p $(DESTDIR)/etc/
	install -D -m 644 $(CURDIR)/mongos.conf $(DESTDIR)/etc/mongos.conf
	install -D -m 644 $(CURDIR)/mongodb.conf $(DESTDIR)/etc/mongodb.conf
	install -D -m 644 $(CURDIR)/mongodbcfg.conf $(DESTDIR)/etc/mongodbcfg.conf
	install -m600 -D key $(DESTDIR)/var/lib/mongodb/key

