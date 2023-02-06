insert into
    access_control.restrictions (role_id, handler_path, handler_method, restriction)
values
    (2, '/foo/bar', 'POST', ('{}')),
    (2, '/foo/baz', 'POST', ('{}')),
    (2, '/test/1', 'POST', ('{"meow": 1}')),
    (2, '/test/1', 'GET', ('{"meow": 2}')),
    (2, '/test/1', 'PATCH', ('{"meow": 3}')),
    (5, '/test/1', 'POST', ('{"meow": 4}')),
    (5, '/test/1', 'GET', ('{"meow": 5}')),
    (5, '/test/1', 'PATCH', ('{"meow": 6}'))
;
