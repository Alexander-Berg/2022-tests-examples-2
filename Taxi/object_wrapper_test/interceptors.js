function test(obj) {
    assert(obj instanceof TaxiPipelineObject, 'object prototype chain assert failed');
    assert(obj.a1 instanceof TaxiPipelineArray, 'array prototype chain assert failed');

    try {
        try {
            assert(!(null in obj), 'false positive "in" operator');
            assert('o1' in obj, 'false negative "in" operator');
            assert(!obj.hasOwnProperty(null), 'false positive hasOwnProperty');
            assert(obj.hasOwnProperty('f1'), 'false negative hasOwnProperty');
        } catch (exception) {
            throw 'at object: ' + exception;
        }

        try {
            assert(!(null in obj.a1), 'false positive "in" operator');
            assert(3 in obj.a1, 'false negative "in" operator');
            assert(!obj.a1.hasOwnProperty(null), 'false positive hasOwnProperty');
            assert(obj.a1.hasOwnProperty(0), 'false negative hasOwnProperty');
        } catch (exception) {
            throw 'at array: ' + exception;
        }
    } catch (exception) {
        throw 'at query interceptor: ' + exception;
    }

    try {
        try {
            assert_eq(Object.keys(obj.o1.o2).sort(), ['p1', 'p2'], 'bad object enumerate');
        } catch (exception) {
            throw 'at object: ' + exception;
        }

        try {
            assert_eq(Object.keys(obj.a1), ['0', '1', '2', '3'], 'bad array enumerate');
        } catch (exception) {
            throw 'at array: ' + exception;
        }
    } catch (exception) {
        throw 'at enumerator interceptor: ' + exception;
    }

    {
        let array = [];
        for (let item of obj.a1) {
            array.push(item);
        }

        assert_eq(array, obj.a1, 'bad for...of');
    }

    let values_array = [];
    {
        for (let item of obj.a1.values()) {
            values_array.push(item);
        }

        assert_eq(values_array, obj.a1, 'bad for...of .values()');
    }

    let keys_array = [];
    {
        for (let item of obj.a1.keys()) {
            keys_array.push(item);
        }

        assert_eq(keys_array, [0, 1, 2, 3], 'bad for...of .keys()');
    }

    {
        let entry_keys_array = [];
        let entry_values_array = [];
        for (let entry of obj.a1.entries()) {
            assert(entry instanceof Array, 'bad entry: ' + entry);
            assert(entry.length === 2, 'bad entry: ' + JSON.stringify(entry));

            entry_keys_array.push(entry[0]);
            entry_values_array.push(entry[1]);
        }

        assert_eq(entry_keys_array, keys_array, 'bad for...of .entries() [keys_array]');
        assert_eq(entry_values_array, values_array, 'bad for...of .entries() [values_array]');
    }

    return true;
}
