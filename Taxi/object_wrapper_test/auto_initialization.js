function test(obj) {
    obj.__trx__.o1.o2.a1[4].o3.f1 = 7;

    let ref = obj.o1;
    obj.__commit__();

    assert_eq(ref.o2.a1[4].o3.f1, 7, 'wow!');

    obj.__trx__.o1.o2.a1[2].o3.f1 = 42;
    obj.__trx__.o1.o2.a1.push({ o3: { f1: 8 } });
    obj.__commit__();
    obj.__trx__.o1.o2.a1[0].o3.f1 = null;
    obj.__trx__.o1.o2.a1.push({ o3: { f1: 9 } });
    obj.__commit__();
    obj.__trx__.o1.o2.a1[3].o3 = null;
    obj.__trx__.o1.o2.a1.push({ o3: { f1: 10 } });
    return 42;
}
