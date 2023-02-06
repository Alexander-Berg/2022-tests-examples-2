function test(obj) {
    function expect_eq(expected, real) {
        if (expected !== real) {
            throw `expected "${expected}" but got "${real}"`;
        }
    }

    for (let i = 0; i < 10; ++i) {
        expect_eq("dummy resource instance r1", obj.r1);
        expect_eq("dummy resource instance r2", obj.r2);
        expect_eq("dummy resource instance r3", obj.r3);
    }

    return "ok";
}