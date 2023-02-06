function test(real_obj) {
    obj = real_obj.__trx__;

    assert_throw_msg_contains(
      () => obj.complex.n1 = Number.NaN,
      'at n1: JS TypeCast error: js number has nonfinite value: nan',
      'check_NaN'
    );

    assert_throw_msg_contains(
      () => obj.complex.n1 = Number.POSITIVE_INFINITY,
      'at n1: JS TypeCast error: js number has nonfinite value: inf',
      'check_Inf'
    );

    assert_throw_msg_contains(
      () => obj.complex.n1 = Number.NEGATIVE_INFINITY,
      'at n1: JS TypeCast error: js number has nonfinite value: -inf',
      'check_-Inf'
    );

    obj.__rollback__();

    assert_throw_msg_contains(
      () => obj.complex = {n1: {a: 1, b: 2}},
      'at complex.n1: Incompatible assignment of value type "object" to value with schema type "number"',
      'check_bad_type'
    );

    obj.num = 3;
    obj.str = 'some string';
    obj.__commit__();

    obj.num = 10;
    obj.str = 'corrupted';

    assert_eq(obj.num, 10);
    assert_eq(obj.str, 'corrupted');

    obj.str = '100'
    let d = obj.str - obj.num;

    assert_eq(d, 90);

    obj.__rollback__();

    obj.num = 10;
    obj.str = 'final word'

    obj.__commit__();

    obj.num = 99;
    assert_throw_msg_contains(
      () => obj.complex = { n1: 'assign str to number', s1: 'five' },
      'at complex.n1: Incompatible assignment of value type "string" to value with schema type "number"'
    )

    obj.__rollback__();
    obj.__commit__();

    return 'ok';
}
