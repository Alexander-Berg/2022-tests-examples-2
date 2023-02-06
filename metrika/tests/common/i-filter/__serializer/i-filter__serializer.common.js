describe('i-filter__serializer', function () {
    var tree,
        serialize = function (filter) {
            return BN('i-filter').buildFilter(filter, tree, true);
        };

    before(function (done) {
        var counter = BN('m-counter').create({
            id: 101500,
            apiId: 101500,
            type: 'single'
        });
        counter
            .fetch()
            .then(function () {
                tree = BN('m-segment-tree').create({table: 'visits', counter: counter});
                return tree.fetch();
            })
            .then(function () {
                done();
            })
            .fail(function (err) {
                done(err);
            });
    });
    it('should handle empty filters', function () {
        expect(serialize([])).to.be.equal('');
    });
    describe('boolean segment', function () {
        it('should handle Yes', function () {
            expect(serialize([{id: 'ym:s:bounce', value: 'Yes'}]))
                .to.be.equal('(ym:s:bounce==\'Yes\')');
        });
        it('should handle No', function () {
            expect(serialize([{id: 'ym:s:bounce', value: 'No'}]))
                .to.be.equal('(ym:s:bounce==\'No\')');
        });
        it('should work in user-centric mode', function () {
            expect(serialize([{id: 'ym:s:hasGCLID-usercentric', value: 'No', userCentric: true}]))
                .to.be.equal('(EXISTS ym:s:specialUser WITH (ym:s:hasGCLID==\'No\'))');
            expect(serialize([{id: 'ym:s:hasGCLID-usercentric', value: 'Yes', userCentric: true}]))
                .to.be.equal('(EXISTS ym:s:specialUser WITH (ym:s:hasGCLID==\'Yes\'))');
            expect(serialize([{
                id: 'ym:s:hasGCLID-usercentric',
                value: 'Yes',
                userCentric: true,
                date1: '2015-02-02'
            }]))
            .to.be.equal(
                '(EXISTS ym:s:specialUser WITH ((ym:s:hasGCLID==\'Yes\') and ym:s:specialDefaultDate==\'2015-02-02\'))'
            );
            expect(serialize([{
                id: 'ym:s:hasGCLID-usercentric',
                value: 'Yes',
                userCentric: true,
                date1: '2015-02-02',
                date2: '2016-02-02'
            }]))
            .to.be.equal(
                '(EXISTS ym:s:specialUser WITH ((ym:s:hasGCLID==\'Yes\') and' +
                    ' ym:s:specialDefaultDate>=\'2015-02-02\' and ym:s:specialDefaultDate<=\'2016-02-02\'))'
            );
        });
    });
    describe('uid segment', function () {
        it('should work', function () {
            expect(serialize([{id: 'ym:s:userIDHash', value: 12345}]))
                .to.be.equal('(ym:s:userIDHash==12345)');
        });
        //there are no user-centric segments of uid type -- so no tests
    });
    describe('goal segment', function () {
        describe('include mode', function () {
            it('should work with one value', function () {
                expect(serialize([{id: 'ym:s:goal', items: [{id: 12345}]}]))
                    .to.be.equal('(ym:s:goal12345IsReached==\'Yes\')');
            });
            it('should work with manuy values', function () {
                expect(serialize([{
                    id: 'ym:s:goal',
                    items: [{id: 12345}, {id: 54321}]
                }])).to.be.equal(
                    '(ym:s:goal12345IsReached==\'Yes\' or ym:s:goal54321IsReached==\'Yes\')'
                );
            });
        });
        describe('exclude mode', function () {
            it('should work with one value', function () {
                expect(serialize([{id: 'ym:s:goal', items: [{id: 12345}], exclude: true}]))
                    .to.be.equal('(ym:s:goal12345IsReached==\'No\')');
            });
            it('should work with manuy values', function () {
                expect(serialize([{
                    id: 'ym:s:goal',
                    items: [{id: 12345}, {id: 54321}],
                    exclude: true
                }])).to.be.equal(
                    '(ym:s:goal12345IsReached==\'No\' and ym:s:goal54321IsReached==\'No\')'
                );
            });
        });
        //there are no user-centric segments of goals type -- so no tests
    });
    describe('number segment', function () {
        it('should serialize expression with == operator', function () {
            expect(serialize([{id: 'ym:s:productPrice', value: 5, op: '=='}]))
                .to.be.equal('(ym:s:productPrice==5)');
        });
        it('should serialize expression with > operator', function () {
            expect(serialize([{id: 'ym:s:productPrice', value: 15, op: '>'}]))
                .to.be.equal('(ym:s:productPrice>15)');
        });
        it('should serialize expression with < operator', function () {
            expect(serialize([{id: 'ym:s:productPrice', value: 95, op: '<'}]))
                .to.be.equal('(ym:s:productPrice<95)');
        });
        it('should serialize expression with <> operator', function () {
            expect(serialize([{id: 'ym:s:productPrice', value: [10, 100], op: '<>'}]))
                .to.be.equal('(ym:s:productPrice>=10 and ym:s:productPrice<=100)');
        });
        describe('should work in user-centric mode', function () {
            it('should work without date', function () {
                expect(serialize([{
                    id: 'ym:u:daysSinceFirstVisitOneBased-usercentric',
                    value: 5,
                    op: '==',
                    userCentric: true
                }]))
                    .to.be.equal('(EXISTS ym:u:userID WITH (ym:u:daysSinceFirstVisitOneBased==5))');
            });
            it('should work with one date', function () {
                expect(serialize([{
                    id: 'ym:u:userVisits-usercentric',
                    value: 5,
                    op: '==',
                    userCentric: true,
                    date1: '2011-10-11'
                }]))
                .to.be.equal(
                    '(EXISTS ym:u:userID WITH ((ym:u:userVisits==5) and ym:u:specialDefaultDate==\'2011-10-11\'))'
                );
            });
            it('should work with date-range', function () {
                expect(serialize([{
                    id: 'ym:u:userVisits-usercentric',
                    value: 5,
                    op: '==',
                    userCentric: true,
                    date1: '2011-10-11',
                    date2: '2012-10-11'
                }]))
                .to.be.equal(
                    '(EXISTS ym:u:userID WITH ((ym:u:userVisits==5) and' +
                        ' ym:u:specialDefaultDate>=\'2011-10-11\' and ym:u:specialDefaultDate<=\'2012-10-11\'))'
                );
            });
        });
    });
    describe('date segment', function () {
        it('should serialize expression with <> operator', function () {
            expect(serialize([{
                id: 'ym:s:previousVisitDate',
                from: '2015-01-01',
                to: '2016-01-01'
            }]))
            .to.be.equal('(ym:s:previousVisitDate>=\'2015-01-01\' and ym:s:previousVisitDate<=\'2016-01-01\')');
        });
        describe('should work in user-centric mode', function () {
            it('should work without date', function () {
                expect(serialize([{
                    id: 'ym:s:date-usercentric',
                    from: '2016-03-08',
                    to: '2016-03-09',
                    userCentric: true
                }]))
                .to.be.equal(
                    '(EXISTS ym:s:specialUser WITH (ym:s:date>=\'2016-03-08\' and ym:s:date<=\'2016-03-09\'))'
                );
            });
            it('should work with one date', function () {
                //have no idea what this filter means, but it's good example to check
                expect(serialize([{
                    id: 'ym:s:date-usercentric',
                    from: '2016-03-08',
                    to: '2016-03-09',
                    userCentric: true,
                    date1: '2011-10-11'
                }]))
                .to.be.equal(
                    '(EXISTS ym:s:specialUser WITH ((ym:s:date>=\'2016-03-08\' and ym:s:date<=\'2016-03-09\') and' +
                        ' ym:s:specialDefaultDate==\'2011-10-11\'))'
                );
            });
            it('should work with date-range', function () {
                expect(serialize([{
                    id: 'ym:s:date-usercentric',
                    from: '2016-03-08',
                    to: '2016-03-09',
                    userCentric: true,
                    date1: '2011-10-11',
                    date2: '2011-12-11'
                }]))
                .to.be.equal(
                    '(EXISTS ym:s:specialUser WITH ((ym:s:date>=\'2016-03-08\' and ym:s:date<=\'2016-03-09\') and' +
                        ' ym:s:specialDefaultDate>=\'2011-10-11\' and ym:s:specialDefaultDate<=\'2011-12-11\'))'
                );
            });
        });
    });
    describe('multiline segment', function () {
        describe('disjunction mode', function () {
            it('should work with single line', function () {
                expect(serialize([{id: 'ym:s:searchPhrase', items: ['zzz']}]))
                    .to.be.equal('(ym:s:searchPhrase=*\'zzz\')');
            });
            it('should work with single line with ~ operator', function () {
                expect(serialize([{id: 'ym:s:searchPhrase', items: ['~zzz']}]))
                    .to.be.equal('(ym:s:searchPhrase=~\'zzz\')');
            });
            it('should work with single line with @ operator', function () {
                expect(serialize([{id: 'ym:s:searchPhrase', items: ['@zzz']}]))
                    .to.be.equal('(ym:s:searchPhrase=@\'zzz\')');
            });
            it('should work with single line with !@ operator', function () {
                expect(serialize([{id: 'ym:s:searchPhrase', items: ['!@zzz']}]))
                    .to.be.equal('(ym:s:searchPhrase!@\'zzz\')');
            });
            it('should work with single line with !~ operator', function () {
                expect(serialize([{id: 'ym:s:searchPhrase', items: ['!~zzz']}]))
                    .to.be.equal('(ym:s:searchPhrase!~\'zzz\')');
            });
            it('should work with single line with ! operator', function () {
                expect(serialize([{id: 'ym:s:searchPhrase', items: ['!zzz']}]))
                    .to.be.equal('(ym:s:searchPhrase!*\'zzz\')');
            });
            it('should work with many lines', function () {
                expect(serialize([{
                    id: 'ym:s:searchPhrase',
                    items: [
                        'qwerty',
                        '!asdf',
                        '@qaz',
                        '~wsx',
                        '!@edc',
                        '!~rfv'
                    ]
                }])).to.be.equal('(' + [
                    'ym:s:searchPhrase=*\'qwerty\'',
                    'ym:s:searchPhrase!*\'asdf\'',
                    'ym:s:searchPhrase=@\'qaz\'',
                    'ym:s:searchPhrase=~\'wsx\'',
                    'ym:s:searchPhrase!@\'edc\'',
                    'ym:s:searchPhrase!~\'rfv\''
                ].join(' or ') + ')');
            });
        });
        describe('conjunction mode', function () {
            it('should work with many lines', function () {
                expect(serialize([{
                    id: 'ym:s:searchPhrase',
                    conjunction: true,
                    items: [
                        'qwerty',
                        '!asdf',
                        '@qaz',
                        '~wsx',
                        '!@edc',
                        '!~rfv'
                    ]
                }])).to.be.equal('(' + [
                    'ym:s:searchPhrase=*\'qwerty\'',
                    'ym:s:searchPhrase!*\'asdf\'',
                    'ym:s:searchPhrase=@\'qaz\'',
                    'ym:s:searchPhrase=~\'wsx\'',
                    'ym:s:searchPhrase!@\'edc\'',
                    'ym:s:searchPhrase!~\'rfv\''
                ].join(' and ') + ')');
            });
        });
        describe('user-centric mode', function () {
            describe('disjunction mode', function () {
                it('should work without dates', function () {
                    expect(serialize([{
                        id: 'ym:u:firstSearchPhrase-usercentric',
                        userCentric: true,
                        items: [
                            'qwerty',
                            '!asdf',
                            '@qaz',
                            '~wsx',
                            '!@edc',
                            '!~rfv'
                        ]
                    }])).to.be.equal('(EXISTS ym:u:userID WITH (' + [
                        'ym:u:firstSearchPhrase=*\'qwerty\'',
                        'ym:u:firstSearchPhrase!*\'asdf\'',
                        'ym:u:firstSearchPhrase=@\'qaz\'',
                        'ym:u:firstSearchPhrase=~\'wsx\'',
                        'ym:u:firstSearchPhrase!@\'edc\'',
                        'ym:u:firstSearchPhrase!~\'rfv\''
                    ].join(' or ') + '))');
                });
                it('should work with dates', function () {
                    expect(serialize([{
                        id: 'ym:s:searchPhrase-usercentric',
                        userCentric: true,
                        date1: '2011-10-11',
                        date2: '2011-12-11',
                        items: [
                            'qwerty',
                            '!asdf',
                            '@qaz',
                            '~wsx',
                            '!@edc',
                            '!~rfv'
                        ]
                    }])).to.be.equal(
                        '(EXISTS ym:s:specialUser WITH ((' + [
                            'ym:s:searchPhrase=*\'qwerty\'',
                            'ym:s:searchPhrase!*\'asdf\'',
                            'ym:s:searchPhrase=@\'qaz\'',
                            'ym:s:searchPhrase=~\'wsx\'',
                            'ym:s:searchPhrase!@\'edc\'',
                            'ym:s:searchPhrase!~\'rfv\''
                        ].join(' or ') +
                        ') and ym:s:specialDefaultDate>=\'2011-10-11\' and ym:s:specialDefaultDate<=\'2011-12-11\'))');
                });
            });
            describe('conjunction mode', function () {
                it('should work without dates', function () {
                    expect(serialize([{
                        id: 'ym:u:firstSearchPhrase-usercentric',
                        userCentric: true,
                        conjunction: true,
                        items: [
                            'qwerty',
                            '!asdf',
                            '@qaz',
                            '~wsx',
                            '!@edc',
                            '!~rfv'
                        ]
                    }])).to.be.equal('(EXISTS ym:u:userID WITH (' + [
                        'ym:u:firstSearchPhrase=*\'qwerty\'',
                        'ym:u:firstSearchPhrase!*\'asdf\'',
                        'ym:u:firstSearchPhrase=@\'qaz\'',
                        'ym:u:firstSearchPhrase=~\'wsx\'',
                        'ym:u:firstSearchPhrase!@\'edc\'',
                        'ym:u:firstSearchPhrase!~\'rfv\''
                    ].join(' and ') + '))');
                });
                it('should work with dates', function () {
                    expect(serialize([{
                        id: 'ym:s:searchPhrase-usercentric',
                        userCentric: true,
                        date1: '2011-10-11',
                        date2: '2011-12-11',
                        conjunction: true,
                        items: [
                            'qwerty',
                            '!asdf',
                            '@qaz',
                            '~wsx',
                            '!@edc',
                            '!~rfv'
                        ]
                    }])).to.be.equal(
                        '(EXISTS ym:s:specialUser WITH ((' + [
                            'ym:s:searchPhrase=*\'qwerty\'',
                            'ym:s:searchPhrase!*\'asdf\'',
                            'ym:s:searchPhrase=@\'qaz\'',
                            'ym:s:searchPhrase=~\'wsx\'',
                            'ym:s:searchPhrase!@\'edc\'',
                            'ym:s:searchPhrase!~\'rfv\''
                        ].join(' and ') +
                        ') and ym:s:specialDefaultDate>=\'2011-10-11\' and ym:s:specialDefaultDate<=\'2011-12-11\'))');
                });

            });
        });
    });
    describe('url segment', function () {
        it('should use host dimension for host mode', function () {
            expect(serialize([{id: 'ym:s:referer', items: ['zzz'], urlMode: 'host_dim'}]))
                .to.be.equal('(ym:s:refererDomain=*\'zzz\')');
        });
        it('should use path dimension for path mode', function () {
            expect(serialize([{id: 'ym:s:referer', items: ['zzz'], urlMode: 'path_dim'}]))
                .to.be.equal('(ym:s:refererPathFull=*\'zzz\')');
        });
        it('should use full url dimension for full url mode', function () {
            expect(serialize([{id: 'ym:s:referer', items: ['zzz'], urlMode: 'dim'}]))
                .to.be.equal('(ym:s:referer=*\'zzz\')');
            expect(serialize([{id: 'ym:s:referer', items: ['zzz']}]))
                .to.be.equal('(ym:s:referer=*\'zzz\')');
        });
        //url segments are almost the same as multiline,
        //so do not test user-centric, disjuntion/conjuntiion modes
    });
    describe('params segment', function () {
        describe('suggest mode', function () {
            it('should work without paramName', function () {
                expect(serialize([{
                    id: 'ym:s:paramsLevel1',
                    tail: 'zzzz',
                    noQuantifier: true
                }]))
                    .to.be.equal('(ym:s:paramsLevel1=@\'zzzz\')');
            });
            it('should work with paramName', function () {
                expect(serialize([{
                    id: 'ym:s:paramsLevel1',
                    tail: 'zzzz',
                    noQuantifier: true,
                    paramName: 'l1'
                }]))
                    .to.be.equal('(ym:s:paramsLevel1==\'l1\' and ym:s:paramsLevel2=@\'zzzz\')');
                expect(serialize([{
                    id: 'ym:s:paramsLevel1',
                    tail: 'zzzz',
                    noQuantifier: true,
                    paramName: 'l1.l2'
                }]))
                .to.be.equal(
                    '(ym:s:paramsLevel1==\'l1\' and ym:s:paramsLevel2==\'l2\' and ym:s:paramsLevel3=@\'zzzz\')'
                );
            });
        });
        describe('common filter mode', function () {
            describe('paramName present', function () {
                it('should work with string value', function () {
                    expect(serialize([{
                        id: 'ym:s:paramsLevel1',
                        paramVal: 'zzzz',
                        paramName: 'l1',
                        paramType: 'ym:s:paramsLevel2',
                        op: '=='
                    }]))
                    .to.be.equal('(EXISTS(ym:s:paramsLevel1==\'l1\' and ym:s:paramsLevel2==\'zzzz\'))');
                    expect(serialize([{
                        id: 'ym:s:paramsLevel1',
                        paramVal: 'zzzz',
                        paramName: 'l1.l2',
                        paramType: 'ym:s:paramsLevel3',
                        op: '=='
                    }]))
                    .to.be.equal(
                        '(EXISTS(ym:s:paramsLevel1==\'l1\' and' +
                            ' ym:s:paramsLevel2==\'l2\' and ym:s:paramsLevel3==\'zzzz\'))'
                    );
                });
                it('should work with numeric value with == operator', function () {
                    expect(serialize([{
                        id: 'ym:s:paramsLevel1',
                        paramVal: 2,
                        paramName: 'l1',
                        paramType: 'ym:s:paramsValueDouble',
                        op: '=='
                    }]))
                    .to.be.equal('(EXISTS(ym:s:paramsLevel1==\'l1\' and ym:s:paramsValueDouble==\'2\'))');
                    expect(serialize([{
                        id: 'ym:s:paramsLevel1',
                        paramVal: 3,
                        paramName: 'l1.l2',
                        paramType: 'ym:s:paramsValueDouble',
                        op: '=='
                    }]))
                    .to.be.equal(
                        '(EXISTS(ym:s:paramsLevel1==\'l1\' and' +
                            ' ym:s:paramsLevel2==\'l2\' and ym:s:paramsValueDouble==\'3\'))'
                    );
                });
                it('should work with numeric value with < operator', function () {
                    expect(serialize([{
                        id: 'ym:s:paramsLevel1',
                        paramVal: 2,
                        paramName: 'l1',
                        paramType: 'ym:s:paramsValueDouble',
                        op: '<'
                    }]))
                    .to.be.equal('(EXISTS(ym:s:paramsLevel1==\'l1\' and ym:s:paramsValueDouble<\'2\'))');
                    expect(serialize([{
                        id: 'ym:s:paramsLevel1',
                        paramVal: 3,
                        paramName: 'l1.l2',
                        paramType: 'ym:s:paramsValueDouble',
                        op: '<'
                    }]))
                    .to.be.equal(
                        '(EXISTS(ym:s:paramsLevel1==\'l1\' and' +
                            ' ym:s:paramsLevel2==\'l2\' and ym:s:paramsValueDouble<\'3\'))'
                    );
                });
                it('should work with numeric value with > operator', function () {
                    expect(serialize([{
                        id: 'ym:s:paramsLevel1',
                        paramVal: 2,
                        paramName: 'l1',
                        paramType: 'ym:s:paramsValueDouble',
                        op: '>'
                    }]))
                    .to.be.equal('(EXISTS(ym:s:paramsLevel1==\'l1\' and ym:s:paramsValueDouble>\'2\'))');
                    expect(serialize([{
                        id: 'ym:s:paramsLevel1',
                        paramVal: 52,
                        paramName: 'l1.l2',
                        paramType: 'ym:s:paramsValueDouble',
                        op: '>'
                    }]))
                    .to.be.equal(
                        '(EXISTS(ym:s:paramsLevel1==\'l1\' and' +
                            ' ym:s:paramsLevel2==\'l2\' and ym:s:paramsValueDouble>\'52\'))'
                    );
                });
            });
            describe('paramName missing', function () {
                it('should work with string value', function () {
                    expect(serialize([{
                        id: 'ym:s:paramsLevel1',
                        paramVal: 'zzzz',
                        paramType: 'ym:s:paramsLevel1',
                        op: '=='
                    }]))
                    .to.be.equal('(EXISTS(ym:s:paramsLevel1==\'zzzz\'))');
                });
                it('should work with numeric value with == operator', function () {
                    expect(serialize([{
                        id: 'ym:s:paramsLevel1',
                        paramVal: 222,
                        paramType: 'ym:s:paramsValueDouble',
                        op: '=='
                    }]))
                    .to.be.equal('(EXISTS(ym:s:paramsValueDouble==\'222\'))');
                });
                it('should work with numeric value with > operator', function () {
                    expect(serialize([{
                        id: 'ym:s:paramsLevel1',
                        paramVal: 101,
                        paramType: 'ym:s:paramsValueDouble',
                        op: '>'
                    }]))
                    .to.be.equal('(EXISTS(ym:s:paramsValueDouble>\'101\'))');
                });
                it('should work with numeric value with < operator', function () {
                    expect(serialize([{
                        id: 'ym:s:paramsLevel1',
                        paramVal: 4321,
                        paramType: 'ym:s:paramsValueDouble',
                        op: '<'
                    }]))
                    .to.be.equal('(EXISTS(ym:s:paramsValueDouble<\'4321\'))');
                });
            });
        });
        describe('user-centric mode', function () {
            it('should work without dates', function () {
                expect(serialize([{
                    id: 'ym:s:paramsLevel1-usercentric',
                    userCentric: true,
                    paramVal: 3,
                    paramName: 'l1.l2',
                    paramType: 'ym:s:paramsValueDouble',
                    op: '=='
                }]))
                .to.be.equal(
                    '(EXISTS ym:s:specialUser WITH (EXISTS(ym:s:paramsLevel1==\'l1\' and' +
                        ' ym:s:paramsLevel2==\'l2\' and ym:s:paramsValueDouble==\'3\')))'
                );
            });
            it('should work with dates', function () {
                expect(serialize([{
                    id: 'ym:s:paramsLevel1-usercentric',
                    userCentric: true,
                    date1: '2016-01-01',
                    date2: '2016-02-02',
                    paramVal: 3,
                    paramName: 'l1.l2',
                    paramType: 'ym:s:paramsValueDouble',
                    op: '=='
                }]))
                .to.be.equal(
                    '(EXISTS ym:s:specialUser WITH ((EXISTS(ym:s:paramsLevel1==\'l1\' and' +
                        ' ym:s:paramsLevel2==\'l2\' and ym:s:paramsValueDouble==\'3\')) and' +
                        ' ym:s:specialDefaultDate>=\'2016-01-01\' and ym:s:specialDefaultDate<=\'2016-02-02\'))'
                );
            });
            it('should not wrap with EXISTS for user-centric dimension', function () {
                expect(serialize([{
                    exclude: false,
                    id: 'ym:up:paramsLevel1-usercentric',
                    noQuantifier: true,
                    op: '=@',
                    paramType: 'ym:up:paramsLevel1',
                    paramVal: 'level1',
                    userCentric: false
                }]))
                    .to.be.equal('(ym:up:paramsLevel1=@\'level1\')');
            });
        });
    });
    describe('list segment', function () {
        describe('include mode', function () {
            it('should work with one value', function () {
                expect(serialize([{
                    id: 'ym:s:trafficSource',
                    items: [{id: 1}]
                }])).to.be.equal('(ym:s:trafficSource==\'1\')');
                expect(serialize([{
                    id: 'ym:s:trafficSource',
                    items: [{id: null}]
                }])).to.be.equal('(ym:s:trafficSource=n)');
            });
            it('should work with many values', function () {
                expect(serialize([{
                    id: 'ym:s:trafficSource',
                    items: [{id: 1}, {id: 'zzz'}, {id: null}]
                }])).to.be.equal(
                    '(ym:s:trafficSource==\'1\' or ym:s:trafficSource==\'zzz\' or ym:s:trafficSource=n)'
                );
            });
        });
        describe('exclude mode', function () {
            it('should work with one value', function () {
                expect(serialize([{
                    id: 'ym:s:trafficSource',
                    items: [{id: 1}],
                    exclude: true
                }])).to.be.equal('(ym:s:trafficSource!=\'1\')');
                expect(serialize([{
                    id: 'ym:s:trafficSource',
                    items: [{id: null}],
                    exclude: true
                }])).to.be.equal('(ym:s:trafficSource!n)');
            });
            it('should work with many values', function () {
                expect(serialize([{
                    id: 'ym:s:trafficSource',
                    items: [{id: 1}, {id: 'zzz'}, {id: null}],
                    exclude: true
                }])).to.be.equal(
                    '(ym:s:trafficSource!=\'1\' and ym:s:trafficSource!=\'zzz\' and ym:s:trafficSource!n)'
                );
            });
        });
        describe('user-centric mode', function () {
            describe('include mode', function () {
                it('should work witout dates', function () {
                    expect(serialize([{
                        id: 'ym:s:regionCitySize-usercentric',
                        userCentric: true,
                        items: [{id: 1}, {id: 'zzz'}, {id: null}]
                    }])).to.be.equal(
                        '(EXISTS ym:s:specialUser WITH (' +
                            'ym:s:regionCitySize==\'1\' or ym:s:regionCitySize==\'zzz\' or ym:s:regionCitySize=n))'
                    );
                });
                it('should work with dates', function () {
                    expect(serialize([{
                        id: 'ym:s:regionCitySize-usercentric',
                        userCentric: true,
                        items: [{id: 1}, {id: 'zzz'}, {id: null}],
                        date1: '2015-05-04',
                        date2: '2016-05-04'
                    }])).to.be.equal(
                        '(EXISTS ym:s:specialUser WITH (' +
                            '(ym:s:regionCitySize==\'1\' or ym:s:regionCitySize==\'zzz\' or ym:s:regionCitySize=n)' +
                            ' and ym:s:specialDefaultDate>=\'2015-05-04\' and ym:s:specialDefaultDate<=\'2016-05-04\'))'
                    );
                });
            });
            describe('exclude mode', function () {
                it('should work witout dates', function () {
                    expect(serialize([{
                        id: 'ym:s:regionCitySize-usercentric',
                        userCentric: true,
                        items: [{id: 1}, {id: 'zzz'}, {id: null}],
                        exclude: true
                    }])).to.be.equal(
                        '(EXISTS ym:s:specialUser WITH (' +
                            'ym:s:regionCitySize!=\'1\' and ym:s:regionCitySize!=\'zzz\' and ym:s:regionCitySize!n))'
                    );
                });
                it('should work with dates', function () {
                    expect(serialize([{
                        id: 'ym:s:regionCitySize-usercentric',
                        userCentric: true,
                        items: [{id: 1}, {id: 'zzz'}, {id: null}],
                        date1: '2015-05-04',
                        date2: '2016-05-04',
                        exclude: true
                    }])).to.be.equal(
                        '(EXISTS ym:s:specialUser WITH (' +
                            '(ym:s:regionCitySize!=\'1\' and ym:s:regionCitySize!=\'zzz\' and ym:s:regionCitySize!n)' +
                            ' and ym:s:specialDefaultDate>=\'2015-05-04\' and ym:s:specialDefaultDate<=\'2016-05-04\'))'
                    );
                });
            });
        });
    });
    describe('tree segment', function () {
        describe('include mode', function () {
            describe('values from one depth level', function () {
                describe('values from first depth level', function () {
                    it('should work with one value', function () {
                        expect(serialize([{
                            id: 'ym:s:browser',
                            items: [[{id: 'chrome'}]]
                        }])).to.be.equal('(ym:s:browser IN(\'chrome\'))');
                    });
                    it('should work with many values', function () {
                        expect(serialize([{
                            id: 'ym:s:browser',
                            items: [[{id: 'chrome'}], [{id: 'firefox'}]]
                        }])).to.be.equal('(ym:s:browser IN(\'chrome\',\'firefox\'))');
                    });
                });
                describe('values from not first depth level', function () {
                    it('should work with one value', function () {
                        var items = [[]];
                        items[0][1] = {id: 'chrome 44'};
                        expect(serialize([{
                            id: 'ym:s:browser',
                            items: items
                        }])).to.be.equal('(ym:s:browserAndVersionMajor IN(\'chrome 44\'))');
                    });
                    it('should work with many values', function () {
                        var items = [[], []];
                        items[0][1] = {id: 'chrome 44'};
                        items[1][1] = {id: 'firefox 37'};
                        expect(serialize([{
                            id: 'ym:s:browser',
                            items: items
                        }])).to.be.equal('(ym:s:browserAndVersionMajor IN(\'chrome 44\',\'firefox 37\'))');
                    });
                });
            });
            describe('values from different depth levels', function () {
                it('should work with one value at first level and one at second', function () {
                    var items = [[], []];
                    items[0][0] = {id: 'chrome'};
                    items[1][1] = {id: 'firefox 37'};
                    expect(serialize([{
                        id: 'ym:s:browser',
                        items: items
                    }])).to.be.equal(
                        '(ym:s:browser IN(\'chrome\') or' +
                        ' ym:s:browserAndVersionMajor IN(\'firefox 37\'))'
                    );
                });

                it('should work with one value at first level and many at second', function () {
                    var items = [[], [], []];
                    items[0][0] = {id: 'chrome'};
                    items[1][1] = {id: 'firefox 37'};
                    items[2][1] = {id: 'opera 22'};
                    expect(serialize([{
                        id: 'ym:s:browser',
                        items: items
                    }])).to.be.equal(
                        '(ym:s:browser IN(\'chrome\') or' +
                        ' ym:s:browserAndVersionMajor IN(\'firefox 37\',\'opera 22\'))'
                    );
                });

                it('should work with many values at first level and one at second', function () {
                    var items = [[], [], []];
                    items[0][0] = {id: 'chrome'};
                    items[1][0] = {id: 'firefox'};
                    items[2][1] = {id: 'opera 22'};
                    expect(serialize([{
                        id: 'ym:s:browser',
                        items: items
                    }])).to.be.equal(
                        '(ym:s:browser IN(\'chrome\',\'firefox\') or' +
                        ' ym:s:browserAndVersionMajor IN(\'opera 22\'))'
                    );
                });
                it('should work with many values at first level and many at second', function () {
                    var items = [[], [], [], []];
                    items[0][0] = {id: 'chrome'};
                    items[1][0] = {id: 'firefox'};
                    items[2][1] = {id: 'opera 22'};
                    items[3][1] = {id: 'IE 11'};
                    expect(serialize([{
                        id: 'ym:s:browser',
                        items: items
                    }])).to.be.equal(
                        '(ym:s:browser IN(\'chrome\',\'firefox\') or' +
                        ' ym:s:browserAndVersionMajor IN(\'opera 22\',\'IE 11\'))'
                    );
                });
            });
        });
        describe('exclude mode', function () {
            describe('values from one depth level', function () {
                describe('values from first depth level', function () {
                    it('should work with one value', function () {
                        expect(serialize([{
                            id: 'ym:s:browser',
                            items: [[{id: 'chrome'}]],
                            exclude: true
                        }])).to.be.equal('(ym:s:browser NOT IN(\'chrome\'))');
                    });
                    it('should work with many values', function () {
                        expect(serialize([{
                            id: 'ym:s:browser',
                            items: [[{id: 'chrome'}], [{id: 'firefox'}]],
                            exclude: true
                        }])).to.be.equal('(ym:s:browser NOT IN(\'chrome\',\'firefox\'))');
                    });
                });
                describe('values from not first depth level', function () {
                    it('should work with one value', function () {
                        var items = [[]];
                        items[0][1] = {id: 'chrome 44'};
                        expect(serialize([{
                            id: 'ym:s:browser',
                            items: items,
                            exclude: true
                        }])).to.be.equal('(ym:s:browserAndVersionMajor NOT IN(\'chrome 44\'))');
                    });
                    it('should work with many values', function () {
                        var items = [[], []];
                        items[0][1] = {id: 'chrome 44'};
                        items[1][1] = {id: 'firefox 37'};
                        expect(serialize([{
                            id: 'ym:s:browser',
                            items: items,
                            exclude: true
                        }])).to.be.equal('(ym:s:browserAndVersionMajor NOT IN(\'chrome 44\',\'firefox 37\'))');
                    });
                });
            });
            describe('values from different depth levels', function () {
                it('should work with one value at first level and one at second', function () {
                    var items = [[], []];
                    items[0][0] = {id: 'chrome'};
                    items[1][1] = {id: 'firefox 37'};
                    expect(serialize([{
                        id: 'ym:s:browser',
                        items: items,
                        exclude: true
                    }])).to.be.equal(
                        '(ym:s:browser NOT IN(\'chrome\') and' +
                        ' ym:s:browserAndVersionMajor NOT IN(\'firefox 37\'))'
                    );
                });

                it('should work with one value at first level and many at second', function () {
                    var items = [[], [], []];
                    items[0][0] = {id: 'chrome'};
                    items[1][1] = {id: 'firefox 37'};
                    items[2][1] = {id: 'opera 22'};
                    expect(serialize([{
                        id: 'ym:s:browser',
                        items: items,
                        exclude: true
                    }])).to.be.equal(
                        '(ym:s:browser NOT IN(\'chrome\') and' +
                        ' ym:s:browserAndVersionMajor NOT IN(\'firefox 37\',\'opera 22\'))'
                    );
                });

                it('should work with many values at first level and one at second', function () {
                    var items = [[], [], []];
                    items[0][0] = {id: 'chrome'};
                    items[1][0] = {id: 'firefox'};
                    items[2][1] = {id: 'opera 22'};
                    expect(serialize([{
                        id: 'ym:s:browser',
                        items: items,
                        exclude: true
                    }])).to.be.equal(
                        '(ym:s:browser NOT IN(\'chrome\',\'firefox\') and' +
                        ' ym:s:browserAndVersionMajor NOT IN(\'opera 22\'))'
                    );
                });
                it('should work with many values at first level and one at second', function () {
                    var items = [[], [], [], []];
                    items[0][0] = {id: 'chrome'};
                    items[1][0] = {id: 'firefox'};
                    items[2][1] = {id: 'opera 22'};
                    items[3][1] = {id: 'IE 11'};
                    expect(serialize([{
                        id: 'ym:s:browser',
                        items: items,
                        exclude: true
                    }])).to.be.equal(
                        '(ym:s:browser NOT IN(\'chrome\',\'firefox\') and' +
                        ' ym:s:browserAndVersionMajor NOT IN(\'opera 22\',\'IE 11\'))'
                    );
                });
            });
        });
        describe('user-centric mode', function () {
            describe('include mode', function () {
                it('should work without dates', function () {
                    var items = [[], [], [], []];
                    items[0][0] = {id: 'linux'};
                    items[1][0] = {id: 'windows'};
                    items[2][1] = {id: 'freebsd 10'};
                    items[3][1] = {id: 'QNX 5'};
                    expect(serialize([{
                        id: 'ym:s:operatingSystemRoot-usercentric',
                        userCentric: true,
                        items: items
                    }])).to.be.equal(
                        '(EXISTS ym:s:specialUser WITH ' +
                            '(ym:s:operatingSystemRoot IN(\'linux\',\'windows\') or' +
                            ' ym:s:operatingSystem IN(\'freebsd 10\',\'QNX 5\')))'
                    );
                });
                it('should work with dates', function () {
                    var items = [[], [], [], []];
                    items[0][0] = {id: 'linux'};
                    items[1][0] = {id: 'windows'};
                    items[2][1] = {id: 'freebsd 10'};
                    items[3][1] = {id: 'QNX 5'};
                    expect(serialize([{
                        id: 'ym:s:operatingSystemRoot-usercentric',
                        userCentric: true,
                        items: items,
                        date1: '2014-09-09',
                        date2: '2014-09-16'
                    }])).to.be.equal(
                        '(EXISTS ym:s:specialUser WITH (' +
                            '(ym:s:operatingSystemRoot IN(\'linux\',\'windows\') or' +
                            ' ym:s:operatingSystem IN(\'freebsd 10\',\'QNX 5\'))' +
                            ' and ym:s:specialDefaultDate>=\'2014-09-09\' and ym:s:specialDefaultDate<=\'2014-09-16\'))'
                    );
                });
            });
            describe('exclude mode', function () {
                it('should work without dates', function () {
                    var items = [[], [], [], []];
                    items[0][0] = {id: 'linux'};
                    items[1][0] = {id: 'windows'};
                    items[2][1] = {id: 'freebsd 10'};
                    items[3][1] = {id: 'QNX 5'};
                    expect(serialize([{
                        id: 'ym:s:operatingSystemRoot-usercentric',
                        userCentric: true,
                        items: items,
                        exclude: true
                    }])).to.be.equal(
                        '(EXISTS ym:s:specialUser WITH ' +
                            '(ym:s:operatingSystemRoot NOT IN(\'linux\',\'windows\') and' +
                            ' ym:s:operatingSystem NOT IN(\'freebsd 10\',\'QNX 5\')))'
                    );
                });
                it('should work with dates', function () {
                    var items = [[], [], [], []];
                    items[0][0] = {id: 'linux'};
                    items[1][0] = {id: 'windows'};
                    items[2][1] = {id: 'freebsd 10'};
                    items[3][1] = {id: 'QNX 5'};
                    expect(serialize([{
                        id: 'ym:s:operatingSystemRoot-usercentric',
                        userCentric: true,
                        items: items,
                        date1: '2014-09-09',
                        date2: '2014-09-16',
                        exclude: true
                    }])).to.be.equal(
                        '(EXISTS ym:s:specialUser WITH (' +
                            '(ym:s:operatingSystemRoot NOT IN(\'linux\',\'windows\') and' +
                            ' ym:s:operatingSystem NOT IN(\'freebsd 10\',\'QNX 5\'))' +
                            ' and ym:s:specialDefaultDate>=\'2014-09-09\' and ym:s:specialDefaultDate<=\'2014-09-16\'))'
                    );
                });
            });
        });
    });
    describe('path segment', function () {
        describe('include mode', function () {
            describe('single dimension expressions', function () {
                it('should work with single value', function () {
                    expect(serialize([{
                        id: 'ym:s:deviceCategory',
                        items: [[{id: 'phone'}]]
                    }])).to.be.equal(
                        '((ym:s:deviceCategory==\'phone\'))'
                    );
                });
                it('should work with many values', function () {
                    expect(serialize([{
                        id: 'ym:s:deviceCategory',
                        items: [[{id: 'tablet'}], [{id: 'phone'}]]
                    }])).to.be.equal(
                        '((ym:s:deviceCategory==\'tablet\') or (ym:s:deviceCategory==\'phone\'))'
                    );
                });
            });
            describe('multiple dimensions expressions', function () {
                it('should work with expression like many-dims', function () {
                    expect(serialize([{
                        id: 'ym:s:deviceCategory',
                        items: [[{id: 'tablet'}, {id: 'ipad'}]]
                    }])).to.be.equal(
                        '((ym:s:deviceCategory==\'tablet\' and ym:s:mobilePhone==\'ipad\'))'
                    );
                });
                it('should work with expression like one-dim many-dims', function () {
                    expect(serialize([{
                        id: 'ym:s:deviceCategory',
                        items: [
                            [{id: 'phone'}],
                            [{id: 'tablet'}, {id: 'ipad'}]
                        ]
                    }])).to.be.equal(
                        '((ym:s:deviceCategory==\'phone\') or' +
                        ' (ym:s:deviceCategory==\'tablet\' and ym:s:mobilePhone==\'ipad\'))'
                    );
                });
                it('should work with expression like many-dims one-dim', function () {
                    expect(serialize([{
                        id: 'ym:s:deviceCategory',
                        items: [
                            [{id: 'tablet'}, {id: 'ipad'}],
                            [{id: 'phone'}]
                        ]
                    }])).to.be.equal(
                        '((ym:s:deviceCategory==\'tablet\' and ym:s:mobilePhone==\'ipad\') or' +
                        ' (ym:s:deviceCategory==\'phone\'))'
                    );
                });
                it('should work with expression like many-dim many-dims', function () {
                    expect(serialize([{
                        id: 'ym:s:deviceCategory',
                        items: [
                            [{id: 'tablet'}, {id: 'ipad'}],
                            [{id: 'phone'}, {id: 'iphone'}]
                        ]
                    }])).to.be.equal(
                        '((ym:s:deviceCategory==\'tablet\' and ym:s:mobilePhone==\'ipad\') or' +
                        ' (ym:s:deviceCategory==\'phone\' and ym:s:mobilePhone==\'iphone\'))'
                    );
                });
            });
        });
        describe('exclude mode', function () {
            describe('single dimension expressions', function () {
                it('should work with single value', function () {
                    expect(serialize([{
                        id: 'ym:s:deviceCategory',
                        items: [[{id: 'phone'}]],
                        exclude: true
                    }])).to.be.equal(
                        '((ym:s:deviceCategory!=\'phone\'))'
                    );
                });
                it('should work with many values', function () {
                    expect(serialize([{
                        id: 'ym:s:deviceCategory',
                        items: [[{id: 'tablet'}], [{id: 'phone'}]],
                        exclude: true
                    }])).to.be.equal(
                        '((ym:s:deviceCategory!=\'tablet\') and (ym:s:deviceCategory!=\'phone\'))'
                    );
                });
            });
            describe('multiple dimensions expressions', function () {
                it('should work with expression like many-dims', function () {
                    expect(serialize([{
                        id: 'ym:s:deviceCategory',
                        items: [[{id: 'tablet'}, {id: 'ipad'}]],
                        exclude: true
                    }])).to.be.equal(
                        '((ym:s:deviceCategory!=\'tablet\' or ym:s:mobilePhone!=\'ipad\'))'
                    );
                });
                it('should work with expression like one-dim many-dims', function () {
                    expect(serialize([{
                        id: 'ym:s:deviceCategory',
                        items: [
                            [{id: 'phone'}],
                            [{id: 'tablet'}, {id: 'ipad'}]
                        ],
                        exclude: true
                    }])).to.be.equal(
                        '((ym:s:deviceCategory!=\'phone\') and' +
                        ' (ym:s:deviceCategory!=\'tablet\' or ym:s:mobilePhone!=\'ipad\'))'
                    );
                });
                it('should work with expression like many-dims one-dim', function () {
                    expect(serialize([{
                        id: 'ym:s:deviceCategory',
                        items: [
                            [{id: 'tablet'}, {id: 'ipad'}],
                            [{id: 'phone'}]
                        ],
                        exclude: true
                    }])).to.be.equal(
                        '((ym:s:deviceCategory!=\'tablet\' or ym:s:mobilePhone!=\'ipad\') and' +
                        ' (ym:s:deviceCategory!=\'phone\'))'
                    );
                });
                it('should work with expression like many-dim many-dims', function () {
                    expect(serialize([{
                        id: 'ym:s:deviceCategory',
                        items: [
                            [{id: 'tablet'}, {id: 'ipad'}],
                            [{id: 'phone'}, {id: 'iphone'}]
                        ],
                        exclude: true
                    }])).to.be.equal(
                        '((ym:s:deviceCategory!=\'tablet\' or ym:s:mobilePhone!=\'ipad\') and' +
                        ' (ym:s:deviceCategory!=\'phone\' or ym:s:mobilePhone!=\'iphone\'))'
                    );
                });
            });
        });
        describe('user centric', function () {
            describe('include mode', function () {
                it('should work without dates', function () {
                    expect(serialize([{
                        id: 'ym:s:regionCountry-usercentric',
                        userCentric: true,
                        items: [
                            [{id: 'country1'}, {id: 'area1'}],
                            [{id: 'country2'}, {id: 'area2'}]
                        ]
                    }])).to.be.equal(
                        '(EXISTS ym:s:specialUser WITH (' +
                        '(ym:s:regionCountry==\'country1\' and ym:s:regionArea==\'area1\') or' +
                        ' (ym:s:regionCountry==\'country2\' and ym:s:regionArea==\'area2\')' +
                        '))'
                    );
                });
                it('should work with dates', function () {
                    expect(serialize([{
                        id: 'ym:s:regionCountry-usercentric',
                        userCentric: true,
                        items: [
                            [{id: 'country1'}, {id: 'area1'}],
                            [{id: 'country2'}, {id: 'area2'}]
                        ],
                        date1: '2015-12-12',
                        date2: '2016-03-01'
                    }])).to.be.equal(
                        '(EXISTS ym:s:specialUser WITH (' +
                        '((ym:s:regionCountry==\'country1\' and ym:s:regionArea==\'area1\') or' +
                        ' (ym:s:regionCountry==\'country2\' and ym:s:regionArea==\'area2\')) and' +
                        ' ym:s:specialDefaultDate>=\'2015-12-12\' and ym:s:specialDefaultDate<=\'2016-03-01\'))'
                    );
                });
            });
            describe('exclude mode', function () {
                it('should work without dates', function () {
                    expect(serialize([{
                        id: 'ym:s:regionCountry-usercentric',
                        userCentric: true,
                        items: [
                            [{id: 'country1'}, {id: 'area1'}],
                            [{id: 'country2'}, {id: 'area2'}]
                        ],
                        exclude: true
                    }])).to.be.equal(
                        '(EXISTS ym:s:specialUser WITH (' +
                        '(ym:s:regionCountry!=\'country1\' or ym:s:regionArea!=\'area1\') and' +
                        ' (ym:s:regionCountry!=\'country2\' or ym:s:regionArea!=\'area2\')' +
                        '))'
                    );
                });
                it('should work with dates', function () {
                    expect(serialize([{
                        id: 'ym:s:regionCountry-usercentric',
                        userCentric: true,
                        items: [
                            [{id: 'country1'}, {id: 'area1'}],
                            [{id: 'country2'}, {id: 'area2'}]
                        ],
                        date1: '2015-12-12',
                        date2: '2016-03-01',
                        exclude: true
                    }])).to.be.equal(
                        '(EXISTS ym:s:specialUser WITH (' +
                        '((ym:s:regionCountry!=\'country1\' or ym:s:regionArea!=\'area1\') and' +
                        ' (ym:s:regionCountry!=\'country2\' or ym:s:regionArea!=\'area2\')) and' +
                        ' ym:s:specialDefaultDate>=\'2015-12-12\' and ym:s:specialDefaultDate<=\'2016-03-01\'))'
                    );

                });
            });
        });
    });
});
