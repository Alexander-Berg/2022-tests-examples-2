describe('home.lang', function() {
    it('should return string', function() {
        home.l10n('yandex').should.equal('Яндекс');
        home.l10n('mail.title').should.equal('Почта');
    });

    it('should return array', function() {
        home.l10n('mail.num.mail').should.deep.equal(['письмо', 'письма', 'писем']);
    });

    it('should return empty string if not found', function() {
        home.l10n('some.inexistent.thing').should.equal('');
        home.l10n('mail.some.inexistent.thing').should.equal('');
        home.l10n('__proto__').should.equal('');
        home.l10n('mail.__proto__').should.equal('');
    });

    it('should work with different locales', function() {
        home.l10n('mail.title', 'ua').should.equal('Пошта');
        home.l10n.call({Locale: 'ua'}, 'mail.title').should.equal('Пошта');
    });
});

