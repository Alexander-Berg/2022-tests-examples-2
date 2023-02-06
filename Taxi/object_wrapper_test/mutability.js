function test(obj) {
    obj.__trx__.o1.o2.p1 += (obj.f1 + obj.a1[0] + obj.a1[1] + obj.a1[2]);
    obj.__trx__.f2 = 2;
    obj.__trx__.a1.push(4);

    assert_eq(obj.a1.length, 4);

    obj.__trx__.a1.push(null);
    obj.__trx__.a1[19] = null;
    assert_eq(obj.a1[19], null);

    var sum = 0;
    var idxs = [];
    for (var i in obj.a1) {
        idxs.push(Number(i));
        sum += obj.a1[i];
    }

    obj.__trx__.a1[19] = 55;

    obj.__trx__.f1 = sum;
    obj.__trx__.s1 = idxs.join(',');
    obj.__commit__();
}
