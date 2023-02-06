const { formatDate } = require('../utils/formatDate');

test('format', function() {
    expect(formatDate(new Date(2020, 1, 1))).toBe('2020-02-01');
    expect(formatDate(new Date(2020, 11, 29))).toBe('2020-12-29');
});
