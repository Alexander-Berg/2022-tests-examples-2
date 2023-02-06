describe('home.decline', function() {
    it('работает со странными вызовами', function () {
        home.decline(11, []).should.equal('');
        home.decline(11, ['молоко']).should.equal('молоко');
    });

    it('что-то делает при не очень некорректных вызовах', function () {
        home.decline(-11, ['письмо', 'письма', 'писем']).should.equal('писем');
    });

    it('работает с корректными вызовами', function () {
        home.decline(0, ['письмо', 'письма', 'писем']).should.equal('писем');

        home.decline(1, ['письмо', 'письма', 'писем']).should.equal('письмо');

        home.decline(2, ['письмо', 'письма', 'писем']).should.equal('письма');
        home.decline(3, ['письмо', 'письма', 'писем']).should.equal('письма');
        home.decline(4, ['письмо', 'письма', 'писем']).should.equal('письма');

        home.decline(5, ['письмо', 'письма', 'писем']).should.equal('писем');
        home.decline(6, ['письмо', 'письма', 'писем']).should.equal('писем');
        home.decline(10, ['письмо', 'письма', 'писем']).should.equal('писем');

        home.decline(11, ['письмо', 'письма', 'писем']).should.equal('писем');
        home.decline(12, ['письмо', 'письма', 'писем']).should.equal('писем');
        home.decline(13, ['письмо', 'письма', 'писем']).should.equal('писем');
        home.decline(14, ['письмо', 'письма', 'писем']).should.equal('писем');

        home.decline(20, ['письмо', 'письма', 'писем']).should.equal('писем');
        home.decline(21, ['письмо', 'письма', 'писем']).should.equal('письмо');
        home.decline(22, ['письмо', 'письма', 'писем']).should.equal('письма');
        home.decline(23, ['письмо', 'письма', 'писем']).should.equal('письма');
        home.decline(25, ['письмо', 'письма', 'писем']).should.equal('писем');

        home.decline(100, ['письмо', 'письма', 'писем']).should.equal('писем');
        home.decline(101, ['письмо', 'письма', 'писем']).should.equal('письмо');
        home.decline(102, ['письмо', 'письма', 'писем']).should.equal('письма');
        home.decline(103, ['письмо', 'письма', 'писем']).should.equal('письма');
        home.decline(105, ['письмо', 'письма', 'писем']).should.equal('писем');

        home.decline(110, ['письмо', 'письма', 'писем']).should.equal('писем');
        home.decline(111, ['письмо', 'письма', 'писем']).should.equal('писем');
        home.decline(112, ['письмо', 'письма', 'писем']).should.equal('писем');
        home.decline(115, ['письмо', 'письма', 'писем']).should.equal('писем');
        home.decline(120, ['письмо', 'письма', 'писем']).should.equal('писем');
        home.decline(121, ['письмо', 'письма', 'писем']).should.equal('письмо');
        home.decline(122, ['письмо', 'письма', 'писем']).should.equal('письма');
        home.decline(125, ['письмо', 'письма', 'писем']).should.equal('писем');

        home.decline(0, ['письмо', 'письма', 'писем', 'пусто']).should.equal('пусто');
        home.decline(1, ['письмо', 'письма', 'писем', 'пусто']).should.equal('письмо');
        home.decline(2, ['письмо', 'письма', 'писем', 'пусто']).should.equal('письма');
        home.decline(5, ['письмо', 'письма', 'писем', 'пусто']).should.equal('писем');
    });
});
