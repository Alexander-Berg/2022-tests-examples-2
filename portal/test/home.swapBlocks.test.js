describe('home.swapBlocks', function() {
    var blocksMiddle = [
        'aeroexpress',
        'bridges',
        'timeshift',
        'balance',
        'interesting',
        'news',
        'zen',
        'stocks',
        'market',
        'teaser',
        'teaser_place_first',
        'stream-intro',
        'tv',
        'videos',
        'teaser_place_second',
        'afisha',
        'etrains',
        'schedule',
        'edadeal',
        'places',
        'collections',
        'services',
        'apps'
    ];

    describe('check params', function() {
        it('wrong name, do nothing', function() {
            home.swapBlocks({
                blocks: blocksMiddle,
                swap: [
                    {
                        name: 'etrains123',
                        after: 'schedule'
                    }
                ]
            }).should.deep.equal(blocksMiddle);
        });

        it('wrong after, do nothing', function() {
            home.swapBlocks({
                blocks: blocksMiddle,
                swap: [
                    {
                        name: 'etrains',
                        after: 'schedule123'
                    }
                ]
            }).should.deep.equal(blocksMiddle);
        });
    });

    describe('correct swap', function() {
        it('single swap', function() {
            home.swapBlocks({
                blocks: blocksMiddle,
                swap: [
                    {
                        name: 'etrains',
                        after: 'schedule'
                    }
                ]
            }).should.deep.equal([
                'aeroexpress',
                'bridges',
                'timeshift',
                'balance',
                'interesting',
                'news',
                'zen',
                'stocks',
                'market',
                'teaser',
                'teaser_place_first',
                'stream-intro',
                'tv',
                'videos',
                'teaser_place_second',
                'afisha',
                'schedule',
                'etrains',
                'edadeal',
                'places',
                'collections',
                'services',
                'apps'
            ]);
        });

        it('multiple swap', function() {
            home.swapBlocks({
                blocks: blocksMiddle,
                swap: [
                    {
                        name: 'edadeal',
                        after: 'afisha'
                    },
                    {
                        name: 'etrains',
                        after: 'schedule'
                    }
                ]
            }).should.deep.equal([
                'aeroexpress',
                'bridges',
                'timeshift',
                'balance',
                'interesting',
                'news',
                'zen',
                'stocks',
                'market',
                'teaser',
                'teaser_place_first',
                'stream-intro',
                'tv',
                'videos',
                'teaser_place_second',
                'afisha',
                'edadeal',
                'schedule',
                'etrains',
                'places',
                'collections',
                'services',
                'apps'
            ]);
        });
    });

});

