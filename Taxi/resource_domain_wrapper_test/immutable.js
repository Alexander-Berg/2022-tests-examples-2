function test(obj) {
    function expect_eq(expected, real) {
        if (expected !== real) {
            throw `expected "${expected}" but got "${real}"`;
        }
    }

    function expect_throw(expected_msg, fn) {
        let thrown = null;
        try {
            fn();
        } catch (e) {
            thrown = e.message;
        }
        expect_eq(expected_msg, thrown);
    }

    expect_eq("dummy resource instance r1", obj.r1);
    expect_eq("dummy resource instance r2", obj.r2);
    expect_eq("dummy resource instance r3", obj.r3);

    expect_throw("JsPipelineResourceDomain is immutable for JS", () => obj.r1 = "r1 changed");
    expect_throw("JsPipelineResourceDomain is immutable for JS", () => obj.r2 = "r2 changed");
    expect_throw("JsPipelineResourceDomain is immutable for JS", () => obj.r3 = "r3 changed");
    expect_throw("JsPipelineResourceDomain is immutable for JS", () => obj.r4 = "r4 changed");

    expect_eq("dummy resource instance r1", obj.r1);
    expect_eq("dummy resource instance r2", obj.r2);
    expect_eq("dummy resource instance r3", obj.r3);
    expect_eq(undefined, obj.r4);

    return "ok";
}