# -*- coding: utf-8 -*-
async def test_execute_js_script(taxi_userver_sample):
    source = """
        function test_fn(args) {
          return "sum of " + args.a + " and " + args.b +
                 " is " + (args.a + args.b);
        }
        """
    params = {'source': source, 'args': {'a': 22, 'b': 20}}
    expected = {'result': 'sum of 22 and 20 is 42'}

    response = await taxi_userver_sample.post('execute-js-script', json=params)
    assert response.status_code == 200
    assert response.encoding == 'utf-8'
    assert response.json() == expected
