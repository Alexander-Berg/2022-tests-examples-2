const { nonMinifiedPath, isMinified } = require('../utils/minified');

test('isMinified', function() {
    expect(isMinified('test.js')).toBe(false);
    expect(isMinified('test.css')).toBe(false);
    expect(isMinified('test.br.css')).toBe(false);
    expect(isMinified('test.css.br')).toBe(true);
    expect(isMinified('test.css.br2')).toBe(false);
    expect(isMinified('test.css.gz')).toBe(true);
    expect(isMinified('test.css..gz')).toBe(true);
    expect(isMinified('test.css..gz.')).toBe(false);
});

test('nonMinifiedPath', function() {
    expect(nonMinifiedPath('test.js')).toBe('test.js');
    expect(nonMinifiedPath('test.js.js')).toBe('test.js.js');
    expect(nonMinifiedPath('test.js.br')).toBe('test.js');
    expect(nonMinifiedPath('test.js.gz')).toBe('test.js');
    expect(nonMinifiedPath('test.js.gz.gz')).toBe('test.js.gz');
});
