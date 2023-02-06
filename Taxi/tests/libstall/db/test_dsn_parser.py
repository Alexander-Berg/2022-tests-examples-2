import ssl
from libstall.pg import dsn

def test_dsn_plain(tap):
    tap.plan(9)
    dsnc = dsn.PgDsnParser('host=h1 dbname=db1 port=1 user=u1 password=p1')
    tap.ok(dsn, 'dsn распарсен')

    tap.eq(len(dsnc.hosts), 1, 'количество хостов')

    for hostno, item in enumerate(dsnc.hosts):
        tap.eq(item, dsnc.hosts[0], 'хост')

        tap.eq(item['port'], '1', 'port')
        tap.eq(item['host'], 'h1', 'host')
        tap.eq(item['user'], 'u1', 'user')
        tap.eq(item['password'], 'p1', 'password')
        tap.eq(item['dbname'], 'db1', 'db')

        connection_kwargs = dsnc.as_dict(hostno)
        tap.ok('ssl' not in connection_kwargs, 'no ssl')

    tap()


def test_dsn_several_hosts(tap):
    tap.plan(12)
    dsnc = dsn.PgDsnParser('host=h1,h2 dbname=db1 user=u1 password=p1')
    tap.ok(dsnc, 'dsn распарсен')

    tap.eq(len(dsnc.hosts), 2, 'два хоста')

    for item in dsnc.hosts:
        tap.eq(item['port'], '5432', 'port')
        tap.eq(item['user'], 'u1', 'user')
        tap.eq(item['password'], 'p1', 'password')
        tap.eq(item['dbname'], 'db1', 'db')


    tap.eq(dsnc.hosts[0]['host'], 'h1', 'имя хоста 1')
    tap.eq(dsnc.hosts[1]['host'], 'h2', 'имя хоста 2')
    tap()


def test_dsn_several_hosts_ports(tap):
    tap.plan(12)
    dsnc = dsn.PgDsnParser('host=h1:1,h2:2 dbname=db1 user=u1 password=p1')
    tap.ok(dsnc, 'dsn распарсен')

    tap.eq(len(dsnc.hosts), 2, 'два хоста')

    for item in dsnc.hosts:
        tap.eq(item['user'], 'u1', 'user')
        tap.eq(item['password'], 'p1', 'password')
        tap.eq(item['dbname'], 'db1', 'db')


    tap.eq(dsnc.hosts[0]['host'], 'h1', 'имя хоста 1')
    tap.eq(dsnc.hosts[0]['port'], '1', 'имя порта 1')
    tap.eq(dsnc.hosts[1]['host'], 'h2', 'имя хоста 2')
    tap.eq(dsnc.hosts[1]['port'], '2', 'имя порта 2')
    tap()

def test_sslmode_require(tap):
    tap.plan(9)
    dsnc = dsn.PgDsnParser(
        'host=h1 dbname=db1 port=1 user=u1 password=p1 sslmode=require'
    )
    tap.ok(dsn, 'dsn распарсен')

    tap.eq(len(dsnc.hosts), 1, 'количество хостов')

    for hostno, item in enumerate(dsnc.hosts):
        tap.eq(item, dsnc.hosts[0], 'хост')

        tap.eq(item['port'], '1', 'port')
        tap.eq(item['host'], 'h1', 'host')
        tap.eq(item['user'], 'u1', 'user')
        tap.eq(item['password'], 'p1', 'password')
        tap.eq(item['dbname'], 'db1', 'db')

        connection_kwargs = dsnc.as_dict(hostno)
        tap.isa_ok(connection_kwargs['ssl'], ssl.SSLContext, 'ssl')
    tap()

def test_dsn_object(tap):
    tap.plan(12)
    dsnc = dsn.PgDsnParser(
        {'host': 'h1:1, h2:2', 'dbname': 'db1', 'user': 'u1', 'password': 'p1'}
    )
    tap.ok(dsnc, 'dsn распарсен')
    tap.eq(len(dsnc.hosts), 2, 'два хоста')

    for item in dsnc.hosts:
        tap.eq(item['user'], 'u1', 'user')
        tap.eq(item['password'], 'p1', 'password')
        tap.eq(item['dbname'], 'db1', 'db')


    tap.eq(dsnc.hosts[0]['host'], 'h1', 'имя хоста 1')
    tap.eq(dsnc.hosts[0]['port'], '1', 'имя порта 1')
    tap.eq(dsnc.hosts[1]['host'], 'h2', 'имя хоста 2')
    tap.eq(dsnc.hosts[1]['port'], '2', 'имя порта 2')
    tap()

