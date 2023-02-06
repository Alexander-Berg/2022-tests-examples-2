function test(obj) {
    //Test optional chaining
    assert_eq(undefined, obj?.non_existant?.another_non_existant);
    assert_eq(undefined, obj?.["non_existant"]?.["non_existant"]);
    assert_eq(undefined, obj?.[100]?.[100]);
    return obj.s1 + (obj.f1 + obj.a1[0] + obj.a1[1] + obj.a1[2]);
}