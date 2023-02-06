install:
	mkdir -p $(DESTDIR)/etc/
	install -D -m 644 $(CURDIR)/mongos.conf $(DESTDIR)/etc/mongos.conf
	install -D -m 644 $(CURDIR)/mongodb.conf $(DESTDIR)/etc/mongodb.conf
	install -D -m 644 $(CURDIR)/mongodbcfg.conf $(DESTDIR)/etc/mongodbcfg.conf
	install -D -m 400 $(CURDIR)/key $(DESTDIR)/var/lib/mongodb/key
	
