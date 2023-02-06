function test(obj) {
    function expect_eq(expected, real) {
        if (expected !== real) {
            throw `expected "${expected}" but got "${real}"`;
        }
    }


    expect_eq("dummy resource instance r1", obj.r1);
    expect_eq("dummy resource instance r2", obj.r2);
    expect_eq("dummy resource instance r3", obj.r3);
    expect_eq(undefined, obj.r4);


    return "ok";
}