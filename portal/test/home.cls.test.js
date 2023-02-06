describe('home.cls', function () {
    var generatedClsReq = {
        antiadb_desktop: 1,
        clsGen: true
    };

    generatedClsReq.cls = home.cls(generatedClsReq);

    beforeEach(function () {
        home.cls.setMap(null);
    });

    it('should return non-generated cls on empty req', function () {
        home.cls.setMap({
            list: [
                'row',
                'container__line',
                'heap_direction_column'
            ],
            map: {
                'row': 'r',
                'container': 'c',
                'line': 'l',
                'heap': 'h',
                'direction': 'd',
                'column': 'cl'
            },
            blocks: []
        });

        var cls = home.cls({});

        cls.generated.should.equal(false);
        cls.full('line some__line row, media__row heap_direction_column').should.equal('line some__line row, media__row heap_direction_column');
        cls.part('line some__line row, media__row heap_direction_column').should.equal('line some__line row, media__row heap_direction_column');
    });

    it('should return generated cls on special req', function () {
        home.cls.setMap({
            list: [
                'row',
                'container__line',
                'heap_direction_column'
            ],
            map: {
                'row': 'r',
                'container': 'c',
                'line': 'l',
                'heap': 'h',
                'direction': 'd',
                'column': 'cl'
            },
            blocks: []
        });

        var cls = home.cls(generatedClsReq);

        cls.generated.should.equal(true);
        cls.full('line some__line row, media__row heap_direction_column').should.equal('line some__line r, media__row h_d_cl');
        cls.part('line some__line row, media__row heap_direction_column').should.equal('l some__l r, media__r h_d_cl');
    });

    it('should return generated cls on special req with blocks', function () {
        home.cls.setMap({
            list: [
            ],
            map: {
                'row': 'r',
                'container': 'c',
                'line': 'l',
                'heap': 'h',
                'direction': 'd',
                'column': 'cl'
            },
            blocks: [
                'row',
                'container',
                'heap'
            ]
        });

        var cls = home.cls(generatedClsReq);

        cls.generated.should.equal(true);
        cls.full('line some__line row, media__row heap_direction_column').should.equal('line some__line r, media__row h_direction_column');
        cls.part('line some__line row, media__row heap_direction_column').should.equal('l some__l r, media__r h_d_cl');
    });
});
