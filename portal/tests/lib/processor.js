QUnit.module('processor', {
    setup: function () {
        this.processor = new code();
    },
    teardown: function () {
        this.processor = null;
    }
});

test("addMethods test", function () {
    var method = {
        name: 'first',
        func: function(a){return a}
    },
    method1 = {
        name: 'second',
        func: function(a){return a}
    },
    method2 = {
        name: 'third',
        func: function(a){return a}
    };
    this.processor.addMethods(method);
    equal(this.processor.buildMethods.length, 1, 'Method added');
    equal(this.processor.buildMethods[0], method, 'Method ok');

    this.processor.addMethods([method1, method2]);
    equal(this.processor.buildMethods.length, 3, 'Methods added');
    equal(this.processor.buildMethods[1], method1, 'Method 2 ok');
    equal(this.processor.buildMethods[2], method2, 'Method 3 ok');
});
test("tryToBuild test", function(){
    
});