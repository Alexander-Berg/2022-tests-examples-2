describe('home.color', function () {
    it('should parse different vals and stringify them', function () {
        home.color('#fff').toString().should.equal(home.color('#ffffff').toString());
        var color = home.color('#ababab').setOpacity(0.5).toString();
        color.should.equal('rgba(171,171,171,0.5)');
    });

    it('should convert rgb into rgb and hsl', function () {
        home.color('#fff').rgb.should.deep.equal({r: 255, g: 255, b: 255});
        home.color('#fff').hsl.should.deep.equal({h: 0, s: 0, l: 1});

        home.color('#000').rgb.should.deep.equal({r: 0, g: 0, b: 0});
        home.color('#000').hsl.should.deep.equal({h: 0, s: 0, l: 0});

        home.color('#4eb0da').rgb.should.deep.equal({r: 78, g: 176, b: 218});
        Math.round(home.color('#4eb0da').hsl.h * 360).should.equal(198);
        Math.round(home.color('#4eb0da').hsl.s * 100).should.equal(65);
        Math.round(home.color('#4eb0da').hsl.l * 100).should.equal(58);
    });

    it('should modify colors', function () {
        home.color('#fff').lighter(10).toString().should.equal('#ffffff');
        home.color('#fff').lighter(-10).toString().should.equal('#e6e6e6');
        home.color('#fff').lighter(-10).lighter(-20).toString().should.equal('#b8b8b8');

        home.color('#000').lighter(10).toString().should.equal('#1a1a1a');
        home.color('#000').lighter(-10).toString().should.equal('#000000');

        home.color('#4eb0da').lighter(10).toString().should.equal('#60b8de');
        home.color('#4eb0da').lighter(-10).toString().should.equal('#36a5d5');
    });
});
