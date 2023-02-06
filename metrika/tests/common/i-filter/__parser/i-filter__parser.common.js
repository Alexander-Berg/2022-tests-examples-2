describe('i-filter__parser', function () {
    var tree,
        parse = function (filter) {
            return BN('i-filter').parseApiFilter(filter, tree);
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

    it('should handle empty strings', function () {
        expect(parse('')).to.deep.equal([]);
    });

    describe('boolean segment', function () {
        it('should handle Yes', function () {
            expect(parse('ym:s:isNewUser==\'Yes\'')).to.deep.equal([{
                value: 'Yes',
                id: 'ym:s:isNewUser',
                userCentric: false,
                exclude: false
            }]);
        });
        it('should handle No', function () {
            expect(parse('ym:s:isNewUser==\'No\'')).to.deep.equal([{
                value: 'No',
                id: 'ym:s:isNewUser',
                userCentric: false,
                exclude: false
            }]);
        });
        describe('user-centric mode', function () {
            it('should work without dates', function () {
                expect(parse('EXISTS ym:s:specialUser WITH (ym:s:hasGCLID==\'Yes\')')).to.deep.equal([{
                    id: 'ym:s:hasGCLID-usercentric',
                    userCentric: true,
                    value: 'Yes',
                    exclude: false
                }]);
                expect(parse('EXISTS ym:s:specialUser WITH (ym:s:hasGCLID==\'No\')')).to.deep.equal([{
                    id: 'ym:s:hasGCLID-usercentric',
                    userCentric: true,
                    value: 'No',
                    exclude: false
                }]);
            });
            it('should work with one date', function () {
                expect(parse(
                    'EXISTS ym:s:specialUser WITH (ym:s:hasGCLID==\'Yes\' and' +
                        ' ym:s:specialDefaultDate==\'2015-12-15\')'
                )).to.deep.equal([{
                    id: 'ym:s:hasGCLID-usercentric',
                    userCentric: true,
                    value: 'Yes',
                    exclude: false,
                    date1: '2015-12-15'
                }]);
                expect(parse(
                    'EXISTS ym:s:specialUser WITH ((ym:s:hasGCLID==\'Yes\') and' +
                        ' ym:s:specialDefaultDate==\'2015-11-12\')'
                )).to.deep.equal([{
                    id: 'ym:s:hasGCLID-usercentric',
                    userCentric: true,
                    value: 'Yes',
                    exclude: false,
                    date1: '2015-11-12'
                }]);
                expect(parse(
                    'EXISTS ym:s:specialUser WITH ((ym:s:hasGCLID==\'Yes\') and' +
                        ' (ym:s:specialDefaultDate==\'2015-10-12\'))'
                )).to.deep.equal([{
                    id: 'ym:s:hasGCLID-usercentric',
                    userCentric: true,
                    value: 'Yes',
                    exclude: false,
                    date1: '2015-10-12'
                }]);
                expect(parse(
                    'EXISTS ym:s:specialUser WITH (ym:s:hasGCLID==\'Yes\' and' +
                        ' (ym:s:specialDefaultDate==\'2015-9-12\'))'
                )).to.deep.equal([{
                    id: 'ym:s:hasGCLID-usercentric',
                    userCentric: true,
                    value: 'Yes',
                    exclude: false,
                    date1: '2015-9-12'
                }]);
            });
            it('should work with two dates', function () {
                expect(parse(
                    'EXISTS ym:s:specialUser WITH (ym:s:hasGCLID==\'No\' and' +
                        ' ym:s:specialDefaultDate>=\'2015-12-12\' and ym:s:specialDefaultDate<=\'2016-12-12\')'
                )).to.deep.equal([{
                    id: 'ym:s:hasGCLID-usercentric',
                    userCentric: true,
                    value: 'No',
                    exclude: false,
                    date1: '2015-12-12',
                    date2: '2016-12-12'
                }]);
                expect(parse(
                    'EXISTS ym:s:specialUser WITH ((ym:s:hasGCLID==\'No\') and' +
                        ' ym:s:specialDefaultDate>=\'2015-12-12\' and ym:s:specialDefaultDate<=\'2016-12-12\')'
                )).to.deep.equal([{
                    id: 'ym:s:hasGCLID-usercentric',
                    userCentric: true,
                    value: 'No',
                    exclude: false,
                    date1: '2015-12-12',
                    date2: '2016-12-12'
                }]);
                expect(parse(
                    'EXISTS ym:s:specialUser WITH ((ym:s:hasGCLID==\'No\') and' +
                        ' (ym:s:specialDefaultDate>=\'2015-12-12\' and ym:s:specialDefaultDate<=\'2016-12-12\'))'
                )).to.deep.equal([{
                    id: 'ym:s:hasGCLID-usercentric',
                    userCentric: true,
                    value: 'No',
                    exclude: false,
                    date1: '2015-12-12',
                    date2: '2016-12-12'
                }]);
                expect(parse(
                    'EXISTS ym:s:specialUser WITH (ym:s:hasGCLID==\'No\' and' +
                        ' (ym:s:specialDefaultDate>=\'2015-12-12\' and ym:s:specialDefaultDate<=\'2016-12-12\'))'
                )).to.deep.equal([{
                    id: 'ym:s:hasGCLID-usercentric',
                    userCentric: true,
                    value: 'No',
                    exclude: false,
                    date1: '2015-12-12',
                    date2: '2016-12-12'
                }]);
            });
        });
    });

    describe('uid segment', function () {
        it('should parse uid segments', function () {
            expect(parse('ym:s:userIDHash==123456')).to.deep.equal([{
                value: 123456,
                id: 'ym:s:userIDHash',
                userCentric: false,
                exclude: false
            }]);
        });
        //there are no user-centric segments for uid -- no tests
    });

    describe('goal segment', function () {
        describe('single expression', function () {
            it('should parse goal reached segment', function () {
                expect(parse('ym:s:goal123456IsReached==\'Yes\'')).to.deep.equal([{
                    items: [{id: '123456'}],
                    id: 'ym:s:goal',
                    userCentric: false,
                    exclude: false
                }]);
            });
            it('should parse goal not reached segment', function () {
                expect(parse('ym:s:goal123456IsReached==\'No\'')).to.deep.equal([{
                    items: [{id: '123456'}],
                    id: 'ym:s:goal',
                    userCentric: false,
                    exclude: true
                }]);
            });
        });
        describe('complex expression', function () {
            it('should parse goal reached segment', function () {
                expect(parse('ym:s:goal123456IsReached==\'No\' and ym:s:goal98765IsReached==\'No\'')).to.deep.equal([{
                    items: [{id: '123456'}, {id: '98765'}],
                    id: 'ym:s:goal',
                    userCentric: false,
                    exclude: true
                }]);
            });
        });
        //there are no user-centric segments for uid -- no tests
    });

    describe('number segment', function () {
        it('should parse == expression', function () {
            expect(parse('ym:s:pageViews==5')).to.deep.equal([{
                value: 5,
                op: '==',
                id: 'ym:s:pageViews',
                userCentric: false,
                exclude: false
            }]);
        });
        it('should parse > expression', function () {
            expect(parse('ym:s:pageViews>5')).to.deep.equal([{
                value: 5,
                op: '>',
                id: 'ym:s:pageViews',
                userCentric: false,
                exclude: false
            }]);
        });
        it('should parse < expression', function () {
            expect(parse('ym:s:pageViews<5')).to.deep.equal([{
                value: 5,
                op: '<',
                id: 'ym:s:pageViews',
                userCentric: false,
                exclude: false
            }]);
        });
        it('should parse between', function () {
            expect(parse('ym:s:pageViews>=5 and ym:s:pageViews<=10')).to.deep.equal([{
                value: [5, 10],
                op: '<>',
                id: 'ym:s:pageViews',
                userCentric: false,
                exclude: false
            }]);
            expect(parse('ym:s:pageViews<=7 and ym:s:pageViews>=3')).to.deep.equal([{
                value: [3, 7],
                op: '<>',
                id: 'ym:s:pageViews',
                userCentric: false,
                exclude: false
            }]);
        });
        describe('user-centric mode', function () {
            it('should work without dates', function () {
                expect(parse(
                    'EXISTS ym:u:specialUser WITH (ym:u:daysSinceFirstVisitOneBased==5)'
                )).to.deep.equal([{
                    value: 5,
                    op: '==',
                    id: 'ym:u:daysSinceFirstVisitOneBased-usercentric',
                    userCentric: true,
                    exclude: false
                }]);
                expect(parse(
                    'EXISTS ym:u:specialUser WITH ((ym:u:daysSinceFirstVisitOneBased>5))'
                )).to.deep.equal([{
                    value: 5,
                    op: '>',
                    id: 'ym:u:daysSinceFirstVisitOneBased-usercentric',
                    userCentric: true,
                    exclude: false
                }]);
                expect(parse(
                    'EXISTS ym:u:specialUser WITH' +
                        ' ((ym:u:daysSinceFirstVisitOneBased>=5 and ym:u:daysSinceFirstVisitOneBased<=7))'
                )).to.deep.equal([{
                    value: [5, 7],
                    op: '<>',
                    id: 'ym:u:daysSinceFirstVisitOneBased-usercentric',
                    userCentric: true,
                    exclude: false
                }]);
            });
            it('should work with one date', function () {
                expect(parse(
                    'EXISTS ym:u:specialUser WITH (ym:u:daysSinceFirstVisitOneBased==5 and' +
                        ' ym:u:specialDefaultDate==\'2012-3-5\')'
                )).to.deep.equal([{
                    value: 5,
                    op: '==',
                    id: 'ym:u:daysSinceFirstVisitOneBased-usercentric',
                    userCentric: true,
                    exclude: false,
                    date1: '2012-3-5'
                }]);
                expect(parse(
                    'EXISTS ym:u:specialUser WITH' +
                        ' (ym:u:daysSinceFirstVisitOneBased>=5 and ym:u:daysSinceFirstVisitOneBased<=10 and' +
                        ' ym:u:specialDefaultDate==\'2012-3-5\')'
                )).to.deep.equal([{
                    value: [5, 10],
                    op: '<>',
                    id: 'ym:u:daysSinceFirstVisitOneBased-usercentric',
                    userCentric: true,
                    exclude: false,
                    date1: '2012-3-5'
                }]);
                expect(parse(
                    'EXISTS ym:u:specialUser WITH' +
                        ' ((ym:u:daysSinceFirstVisitOneBased>=5 and ym:u:daysSinceFirstVisitOneBased<=10) and' +
                        ' ym:u:specialDefaultDate==\'2012-3-5\')'
                )).to.deep.equal([{
                    value: [5, 10],
                    op: '<>',
                    id: 'ym:u:daysSinceFirstVisitOneBased-usercentric',
                    userCentric: true,
                    exclude: false,
                    date1: '2012-3-5'
                }]);
                expect(parse(
                    'EXISTS ym:u:specialUser WITH' +
                        ' ((ym:u:daysSinceFirstVisitOneBased>=5 and ym:u:daysSinceFirstVisitOneBased<=10) and' +
                        ' (ym:u:specialDefaultDate==\'2012-3-5\'))'
                )).to.deep.equal([{
                    value: [5, 10],
                    op: '<>',
                    id: 'ym:u:daysSinceFirstVisitOneBased-usercentric',
                    userCentric: true,
                    exclude: false,
                    date1: '2012-3-5'
                }]);
                expect(parse(
                    'EXISTS ym:u:specialUser WITH' +
                        ' (ym:u:daysSinceFirstVisitOneBased>=5 and ym:u:daysSinceFirstVisitOneBased<=10 and' +
                        ' (ym:u:specialDefaultDate==\'2012-3-5\'))'
                )).to.deep.equal([{
                    value: [5, 10],
                    op: '<>',
                    id: 'ym:u:daysSinceFirstVisitOneBased-usercentric',
                    userCentric: true,
                    exclude: false,
                    date1: '2012-3-5'
                }]);
            });
            it('should work with two dates', function () {
                expect(parse(
                    'EXISTS ym:u:specialUser WITH (ym:u:daysSinceFirstVisitOneBased==5 and' +
                        ' ym:u:specialDefaultDate>=\'2012-3-5\' and ym:u:specialDefaultDate<=\'2015-01-05\')'
                )).to.deep.equal([{
                    value: 5,
                    op: '==',
                    id: 'ym:u:daysSinceFirstVisitOneBased-usercentric',
                    userCentric: true,
                    exclude: false,
                    date1: '2012-3-5',
                    date2: '2015-01-05'
                }]);
                expect(parse(
                    'EXISTS ym:u:specialUser WITH' +
                        ' (ym:u:daysSinceFirstVisitOneBased>=5 and ym:u:daysSinceFirstVisitOneBased<=10 and' +
                        ' ym:u:specialDefaultDate>=\'2012-3-5\' and ym:u:specialDefaultDate<=\'2015-01-05\')'
                )).to.deep.equal([{
                    value: [5, 10],
                    op: '<>',
                    id: 'ym:u:daysSinceFirstVisitOneBased-usercentric',
                    userCentric: true,
                    exclude: false,
                    date1: '2012-3-5',
                    date2: '2015-01-05'
                }]);
                expect(parse(
                    'EXISTS ym:u:specialUser WITH' +
                        ' ((ym:u:daysSinceFirstVisitOneBased>=5 and ym:u:daysSinceFirstVisitOneBased<=10) and' +
                        ' ym:u:specialDefaultDate>=\'2012-3-5\' and ym:u:specialDefaultDate<=\'2015-01-05\')'
                )).to.deep.equal([{
                    value: [5, 10],
                    op: '<>',
                    id: 'ym:u:daysSinceFirstVisitOneBased-usercentric',
                    userCentric: true,
                    exclude: false,
                    date1: '2012-3-5',
                    date2: '2015-01-05'
                }]);
                expect(parse(
                    'EXISTS ym:u:specialUser WITH' +
                        ' ((ym:u:daysSinceFirstVisitOneBased>=5 and ym:u:daysSinceFirstVisitOneBased<=10) and' +
                        ' (ym:u:specialDefaultDate>=\'2012-3-5\' and ym:u:specialDefaultDate<=\'2015-01-05\'))'
                )).to.deep.equal([{
                    value: [5, 10],
                    op: '<>',
                    id: 'ym:u:daysSinceFirstVisitOneBased-usercentric',
                    userCentric: true,
                    exclude: false,
                    date1: '2012-3-5',
                    date2: '2015-01-05'
                }]);
                expect(parse(
                    'EXISTS ym:u:specialUser WITH' +
                        ' (ym:u:daysSinceFirstVisitOneBased>=5 and ym:u:daysSinceFirstVisitOneBased<=10 and' +
                        ' (ym:u:specialDefaultDate>=\'2012-3-5\' and ym:u:specialDefaultDate<=\'2015-01-05\'))'
                )).to.deep.equal([{
                    value: [5, 10],
                    op: '<>',
                    id: 'ym:u:daysSinceFirstVisitOneBased-usercentric',
                    userCentric: true,
                    exclude: false,
                    date1: '2012-3-5',
                    date2: '2015-01-05'
                }]);
            });
        });
    });

    describe('date segment', function () {
        it('should parse == expression', function () {
            expect(parse('ym:s:previousVisitDate==\'2016-01-01\'')).to.deep.equal([{
                from: '2016-01-01',
                to: '2016-01-01',
                op: '==',
                id: 'ym:s:previousVisitDate',
                userCentric: false,
                exclude: false
            }]);
        });
        it('should parse > expression', function () {
            expect(parse('ym:s:previousVisitDate>\'2016-02-02\'')).to.deep.equal([{
                from: '2016-02-02',
                to: '2016-02-02',
                op: '>',
                id: 'ym:s:previousVisitDate',
                userCentric: false,
                exclude: false
            }]);
        });
        it('should parse < expression', function () {
            expect(parse('ym:s:previousVisitDate<\'2016-03-04\'')).to.deep.equal([{
                from: '2016-03-04',
                to: '2016-03-04',
                op: '<',
                id: 'ym:s:previousVisitDate',
                userCentric: false,
                exclude: false
            }]);
        });
        it('should parse between', function () {
            expect(parse(
                'ym:s:previousVisitDate>=\'2015-12-01\' and ym:s:previousVisitDate<=\'2016-03-05\''
            )).to.deep.equal([{
                from: '2015-12-01',
                to: '2016-03-05',
                op: '<>',
                id: 'ym:s:previousVisitDate',
                userCentric: false,
                exclude: false
            }]);
            expect(parse(
                'ym:s:previousVisitDate<=\'2014-05-06\' and ym:s:previousVisitDate>=\'2013-12-12\''
            )).to.deep.equal([{
                from: '2013-12-12',
                to: '2014-05-06',
                op: '<>',
                id: 'ym:s:previousVisitDate',
                userCentric: false,
                exclude: false
            }]);
        });
        //date segment is almost the same as number segment -- no tests for user-centric
    });

    describe('multiline segment', function () {
        describe('one line', function () {
            it('should parse == expression', function () {
                expect(parse('ym:s:searchPhrase==\'phrase1\'')).to.deep.equal([{
                    items: ['phrase1'],
                    id: 'ym:s:searchPhrase',
                    exclude: false,
                    userCentric: false,
                    conjunction: false
                }]);
            });
            it('should parse @ expression', function () {
                expect(parse('ym:s:searchPhrase=@\'phrase1\'')).to.deep.equal([{
                    items: ['@phrase1'],
                    id: 'ym:s:searchPhrase',
                    exclude: false,
                    userCentric: false,
                    conjunction: false
                }]);
            });
            it('should parse !@ expression', function () {
                expect(parse('ym:s:searchPhrase!@\'phrase1\'')).to.deep.equal([{
                    items: ['!@phrase1'],
                    id: 'ym:s:searchPhrase',
                    exclude: false,
                    userCentric: false,
                    conjunction: false
                }]);
            });
            it('should parse ~ expression', function () {
                expect(parse('ym:s:searchPhrase=~\'phrase1\'')).to.deep.equal([{
                    items: ['~phrase1'],
                    id: 'ym:s:searchPhrase',
                    exclude: false,
                    userCentric: false,
                    conjunction: false
                }]);
            });
            it('should parse !~ expression', function () {
                expect(parse('ym:s:searchPhrase!~\'phrase1\'')).to.deep.equal([{
                    items: ['!~phrase1'],
                    id: 'ym:s:searchPhrase',
                    exclude: false,
                    userCentric: false,
                    conjunction: false
                }]);
            });
        });
        describe('multiple lines', function () {
            describe('with conjunction', function () {
                it('should work with two subexpressions', function () {
                    expect(parse('ym:s:searchPhrase==\'phrase1\' and ym:s:searchPhrase==\'phrase2\'')).to.deep.equal([{
                        items: ['phrase1', 'phrase2'],
                        id: 'ym:s:searchPhrase',
                        userCentric: false,
                        exclude: false,
                        conjunction: true
                    }]);
                });
                it('should work with three subexpressions', function () {
                    expect(parse(
                        'ym:s:searchPhrase==\'phrase1\' and ym:s:searchPhrase=@\'phrase2\' and' +
                            ' ym:s:searchPhrase=~\'phrase3\''
                    )).to.deep.equal([{
                        items: ['phrase1', '@phrase2', '~phrase3'],
                        id: 'ym:s:searchPhrase',
                        userCentric: false,
                        exclude: false,
                        conjunction: true
                    }]);
                });
            });
            describe('with disjunction', function () {
                it('should work with two subexpressions', function () {
                    expect(parse('ym:s:searchPhrase==\'phrase1\' or ym:s:searchPhrase==\'phrase2\'')).to.deep.equal([{
                        items: ['phrase1', 'phrase2'],
                        id: 'ym:s:searchPhrase',
                        userCentric: false,
                        exclude: false,
                        conjunction: false
                    }]);
                });
                it('should work with three subexpressions', function () {
                    expect(parse(
                        'ym:s:searchPhrase==\'phrase1\' or ym:s:searchPhrase=@\'phrase2\' or' +
                            ' ym:s:searchPhrase=~\'phrase3\''
                    )).to.deep.equal([{
                        items: ['phrase1', '@phrase2', '~phrase3'],
                        id: 'ym:s:searchPhrase',
                        userCentric: false,
                        exclude: false,
                        conjunction: false
                    }]);
                });
            });
        });
        describe('user-centric mode', function () {
            describe('one line expression', function () {
                it('should work without dates', function () {
                    expect(parse(
                        'EXISTS ym:u:userID WITH (ym:u:firstSearchPhrase==\'qwerty\')'
                    )).to.deep.equal([{
                        id: 'ym:u:firstSearchPhrase-usercentric',
                        userCentric: true,
                        items: ['qwerty'],
                        exclude: false,
                        conjunction: false
                    }]);
                });
                it('should work with one date', function () {
                    expect(parse(
                        'EXISTS ym:u:userID WITH (ym:u:firstSearchPhrase==\'qwerty\' and' +
                            ' ym:u:specialDefaultDate==\'2016-12-11\')'
                    )).to.deep.equal([{
                        id: 'ym:u:firstSearchPhrase-usercentric',
                        conjunction: false,
                        exclude: false,
                        userCentric: true,
                        items: ['qwerty'],
                        date1: '2016-12-11'
                    }]);
                });
                it('should work with two dates', function () {
                    expect(parse(
                        'EXISTS ym:u:userID WITH (ym:u:firstSearchPhrase==\'qwerty\' and' +
                            ' ym:u:specialDefaultDate>=\'2016-03-05\' and ym:u:specialDefaultDate<=\'2016-03-11\')'
                    )).to.deep.equal([{
                        id: 'ym:u:firstSearchPhrase-usercentric',
                        conjunction: false,
                        exclude: false,
                        userCentric: true,
                        items: ['qwerty'],
                        date1: '2016-03-05',
                        date2: '2016-03-11'
                    }]);
                });
            });
            describe('many lines expression', function () {
                describe('conjunction mode', function () {
                    it('should work without dates', function () {
                        expect(parse(
                            'EXISTS ym:u:userID WITH (' + [
                                'ym:u:firstSearchPhrase=*\'qwerty\'',
                                'ym:u:firstSearchPhrase!*\'asdf\'',
                                'ym:u:firstSearchPhrase=@\'qaz\'',
                                'ym:u:firstSearchPhrase=~\'wsx\'',
                                'ym:u:firstSearchPhrase!@\'edc\'',
                                'ym:u:firstSearchPhrase!~\'rfv\''
                                ].join(' and ') + ')'
                        )).to.deep.equal([{
                            id: 'ym:u:firstSearchPhrase-usercentric',
                            userCentric: true,
                            items: [
                                'qwerty',
                                '!asdf',
                                '@qaz',
                                '~wsx',
                                '!@edc',
                                '!~rfv'
                            ],
                            exclude: false,
                            conjunction: true
                        }]);
                    });
                    it('should work with one date', function () {
                        expect(parse(
                            'EXISTS ym:u:userID WITH (' + [
                                'ym:u:firstSearchPhrase=*\'qwerty\'',
                                'ym:u:firstSearchPhrase!*\'asdf\'',
                                'ym:u:firstSearchPhrase=@\'qaz\'',
                                'ym:u:firstSearchPhrase=~\'wsx\'',
                                'ym:u:firstSearchPhrase!@\'edc\'',
                                'ym:u:firstSearchPhrase!~\'rfv\''
                                ].join(' and ') +
                                ' and ym:u:specialDefaultDate==\'2011-08-08\')'
                        )).to.deep.equal([{
                            id: 'ym:u:firstSearchPhrase-usercentric',
                            userCentric: true,
                            date1: '2011-08-08',
                            items: [
                                'qwerty',
                                '!asdf',
                                '@qaz',
                                '~wsx',
                                '!@edc',
                                '!~rfv'
                            ],
                            exclude: false,
                            conjunction: true
                        }]);
                        expect(parse(
                            'EXISTS ym:u:userID WITH ((' + [
                                'ym:u:firstSearchPhrase=*\'qwerty\'',
                                'ym:u:firstSearchPhrase!*\'asdf\'',
                                'ym:u:firstSearchPhrase=@\'qaz\'',
                                'ym:u:firstSearchPhrase=~\'wsx\'',
                                'ym:u:firstSearchPhrase!@\'edc\'',
                                'ym:u:firstSearchPhrase!~\'rfv\''
                                ].join(' and ') +
                                ') and ym:u:specialDefaultDate==\'2011-08-08\')'
                        )).to.deep.equal([{
                            id: 'ym:u:firstSearchPhrase-usercentric',
                            userCentric: true,
                            date1: '2011-08-08',
                            items: [
                                'qwerty',
                                '!asdf',
                                '@qaz',
                                '~wsx',
                                '!@edc',
                                '!~rfv'
                            ],
                            exclude: false,
                            conjunction: true
                        }]);
                        expect(parse(
                            'EXISTS ym:u:userID WITH ((' + [
                                'ym:u:firstSearchPhrase=*\'qwerty\'',
                                'ym:u:firstSearchPhrase!*\'asdf\'',
                                'ym:u:firstSearchPhrase=@\'qaz\'',
                                'ym:u:firstSearchPhrase=~\'wsx\'',
                                'ym:u:firstSearchPhrase!@\'edc\'',
                                'ym:u:firstSearchPhrase!~\'rfv\''
                                ].join(' and ') +
                                ') and (ym:u:specialDefaultDate==\'2011-08-08\'))'
                        )).to.deep.equal([{
                            id: 'ym:u:firstSearchPhrase-usercentric',
                            userCentric: true,
                            date1: '2011-08-08',
                            items: [
                                'qwerty',
                                '!asdf',
                                '@qaz',
                                '~wsx',
                                '!@edc',
                                '!~rfv'
                            ],
                            exclude: false,
                            conjunction: true
                        }]);
                        expect(parse(
                            'EXISTS ym:u:userID WITH (' + [
                                'ym:u:firstSearchPhrase=*\'qwerty\'',
                                'ym:u:firstSearchPhrase!*\'asdf\'',
                                'ym:u:firstSearchPhrase=@\'qaz\'',
                                'ym:u:firstSearchPhrase=~\'wsx\'',
                                'ym:u:firstSearchPhrase!@\'edc\'',
                                'ym:u:firstSearchPhrase!~\'rfv\''
                                ].join(' and ') +
                                ' and (ym:u:specialDefaultDate==\'2011-08-08\'))'
                        )).to.deep.equal([{
                            id: 'ym:u:firstSearchPhrase-usercentric',
                            userCentric: true,
                            date1: '2011-08-08',
                            items: [
                                'qwerty',
                                '!asdf',
                                '@qaz',
                                '~wsx',
                                '!@edc',
                                '!~rfv'
                            ],
                            exclude: false,
                            conjunction: true
                        }]);
                    });
                    it('should work with two dates', function () {
                        expect(parse(
                            'EXISTS ym:u:userID WITH (' + [
                                'ym:u:firstSearchPhrase=*\'qwerty\'',
                                'ym:u:firstSearchPhrase!*\'asdf\'',
                                'ym:u:firstSearchPhrase=@\'qaz\'',
                                'ym:u:firstSearchPhrase=~\'wsx\'',
                                'ym:u:firstSearchPhrase!@\'edc\'',
                                'ym:u:firstSearchPhrase!~\'rfv\''
                                ].join(' and ') +
                                ' and ym:u:specialDefaultDate>=\'2011-08-08\' and' +
                                ' ym:u:specialDefaultDate<=\'2012-11-11\')'
                        )).to.deep.equal([{
                            id: 'ym:u:firstSearchPhrase-usercentric',
                            userCentric: true,
                            date1: '2011-08-08',
                            date2: '2012-11-11',
                            items: [
                                'qwerty',
                                '!asdf',
                                '@qaz',
                                '~wsx',
                                '!@edc',
                                '!~rfv'
                            ],
                            exclude: false,
                            conjunction: true
                        }]);
                        expect(parse(
                            'EXISTS ym:u:userID WITH ((' + [
                                'ym:u:firstSearchPhrase=*\'qwerty\'',
                                'ym:u:firstSearchPhrase!*\'asdf\'',
                                'ym:u:firstSearchPhrase=@\'qaz\'',
                                'ym:u:firstSearchPhrase=~\'wsx\'',
                                'ym:u:firstSearchPhrase!@\'edc\'',
                                'ym:u:firstSearchPhrase!~\'rfv\''
                                ].join(' and ') +
                                ') and ym:u:specialDefaultDate>=\'2011-08-08\' and' +
                                ' ym:u:specialDefaultDate<=\'2012-11-11\')'
                        )).to.deep.equal([{
                            id: 'ym:u:firstSearchPhrase-usercentric',
                            userCentric: true,
                            date1: '2011-08-08',
                            date2: '2012-11-11',
                            items: [
                                'qwerty',
                                '!asdf',
                                '@qaz',
                                '~wsx',
                                '!@edc',
                                '!~rfv'
                            ],
                            exclude: false,
                            conjunction: true
                        }]);
                        expect(parse(
                            'EXISTS ym:u:userID WITH ((' + [
                                'ym:u:firstSearchPhrase=*\'qwerty\'',
                                'ym:u:firstSearchPhrase!*\'asdf\'',
                                'ym:u:firstSearchPhrase=@\'qaz\'',
                                'ym:u:firstSearchPhrase=~\'wsx\'',
                                'ym:u:firstSearchPhrase!@\'edc\'',
                                'ym:u:firstSearchPhrase!~\'rfv\''
                                ].join(' and ') +
                                ') and (ym:u:specialDefaultDate>=\'2011-08-08\' and' +
                                ' ym:u:specialDefaultDate<=\'2012-11-11\'))'
                        )).to.deep.equal([{
                            id: 'ym:u:firstSearchPhrase-usercentric',
                            userCentric: true,
                            date1: '2011-08-08',
                            date2: '2012-11-11',
                            items: [
                                'qwerty',
                                '!asdf',
                                '@qaz',
                                '~wsx',
                                '!@edc',
                                '!~rfv'
                            ],
                            exclude: false,
                            conjunction: true
                        }]);
                        expect(parse(
                            'EXISTS ym:u:userID WITH (' + [
                                'ym:u:firstSearchPhrase=*\'qwerty\'',
                                'ym:u:firstSearchPhrase!*\'asdf\'',
                                'ym:u:firstSearchPhrase=@\'qaz\'',
                                'ym:u:firstSearchPhrase=~\'wsx\'',
                                'ym:u:firstSearchPhrase!@\'edc\'',
                                'ym:u:firstSearchPhrase!~\'rfv\''
                                ].join(' and ') +
                                ' and (ym:u:specialDefaultDate>=\'2011-08-08\' and' +
                                ' ym:u:specialDefaultDate<=\'2012-11-11\'))'
                        )).to.deep.equal([{
                            id: 'ym:u:firstSearchPhrase-usercentric',
                            userCentric: true,
                            date1: '2011-08-08',
                            date2: '2012-11-11',
                            items: [
                                'qwerty',
                                '!asdf',
                                '@qaz',
                                '~wsx',
                                '!@edc',
                                '!~rfv'
                            ],
                            exclude: false,
                            conjunction: true
                        }]);
                    });
                });
                describe('disjunction mode', function () {
                    it('should work without dates', function () {
                        expect(parse(
                            'EXISTS ym:u:userID WITH (' + [
                                'ym:u:firstSearchPhrase=*\'qwerty\'',
                                'ym:u:firstSearchPhrase!*\'asdf\'',
                                'ym:u:firstSearchPhrase=@\'qaz\'',
                                'ym:u:firstSearchPhrase=~\'wsx\'',
                                'ym:u:firstSearchPhrase!@\'edc\'',
                                'ym:u:firstSearchPhrase!~\'rfv\''
                                ].join(' or ') + ')'
                        )).to.deep.equal([{
                            id: 'ym:u:firstSearchPhrase-usercentric',
                            userCentric: true,
                            items: [
                                'qwerty',
                                '!asdf',
                                '@qaz',
                                '~wsx',
                                '!@edc',
                                '!~rfv'
                            ],
                            exclude: false,
                            conjunction: false
                        }]);
                    });
                    it('should work with one date', function () {
                        expect(parse(
                            'EXISTS ym:u:userID WITH ((' + [
                                'ym:u:firstSearchPhrase=*\'qwerty\'',
                                'ym:u:firstSearchPhrase!*\'asdf\'',
                                'ym:u:firstSearchPhrase=@\'qaz\'',
                                'ym:u:firstSearchPhrase=~\'wsx\'',
                                'ym:u:firstSearchPhrase!@\'edc\'',
                                'ym:u:firstSearchPhrase!~\'rfv\''
                                ].join(' or') +
                                ') and ym:u:specialDefaultDate==\'2011-08-08\')'
                        )).to.deep.equal([{
                            id: 'ym:u:firstSearchPhrase-usercentric',
                            userCentric: true,
                            date1: '2011-08-08',
                            items: [
                                'qwerty',
                                '!asdf',
                                '@qaz',
                                '~wsx',
                                '!@edc',
                                '!~rfv'
                            ],
                            exclude: false,
                            conjunction: false
                        }]);
                        expect(parse(
                            'EXISTS ym:u:userID WITH ((' + [
                                'ym:u:firstSearchPhrase=*\'qwerty\'',
                                'ym:u:firstSearchPhrase!*\'asdf\'',
                                'ym:u:firstSearchPhrase=@\'qaz\'',
                                'ym:u:firstSearchPhrase=~\'wsx\'',
                                'ym:u:firstSearchPhrase!@\'edc\'',
                                'ym:u:firstSearchPhrase!~\'rfv\''
                                ].join(' or ') +
                                ') and (ym:u:specialDefaultDate==\'2011-08-08\'))'
                        )).to.deep.equal([{
                            id: 'ym:u:firstSearchPhrase-usercentric',
                            userCentric: true,
                            date1: '2011-08-08',
                            items: [
                                'qwerty',
                                '!asdf',
                                '@qaz',
                                '~wsx',
                                '!@edc',
                                '!~rfv'
                            ],
                            exclude: false,
                            conjunction: false
                        }]);
                    });
                    it('should work with two dates', function () {
                        expect(parse(
                            'EXISTS ym:u:userID WITH ((' + [
                                'ym:u:firstSearchPhrase=*\'qwerty\'',
                                'ym:u:firstSearchPhrase!*\'asdf\'',
                                'ym:u:firstSearchPhrase=@\'qaz\'',
                                'ym:u:firstSearchPhrase=~\'wsx\'',
                                'ym:u:firstSearchPhrase!@\'edc\'',
                                'ym:u:firstSearchPhrase!~\'rfv\''
                                ].join(' or ') +
                                ') and ym:u:specialDefaultDate>=\'2011-08-08\' and' +
                                ' ym:u:specialDefaultDate<=\'2012-11-11\')'
                        )).to.deep.equal([{
                            id: 'ym:u:firstSearchPhrase-usercentric',
                            userCentric: true,
                            date1: '2011-08-08',
                            date2: '2012-11-11',
                            items: [
                                'qwerty',
                                '!asdf',
                                '@qaz',
                                '~wsx',
                                '!@edc',
                                '!~rfv'
                            ],
                            exclude: false,
                            conjunction: false
                        }]);
                        expect(parse(
                            'EXISTS ym:u:userID WITH ((' + [
                                'ym:u:firstSearchPhrase=*\'qwerty\'',
                                'ym:u:firstSearchPhrase!*\'asdf\'',
                                'ym:u:firstSearchPhrase=@\'qaz\'',
                                'ym:u:firstSearchPhrase=~\'wsx\'',
                                'ym:u:firstSearchPhrase!@\'edc\'',
                                'ym:u:firstSearchPhrase!~\'rfv\''
                                ].join(' or ') +
                                ') and (ym:u:specialDefaultDate>=\'2011-08-08\' and' +
                                ' ym:u:specialDefaultDate<=\'2012-11-11\'))'
                        )).to.deep.equal([{
                            id: 'ym:u:firstSearchPhrase-usercentric',
                            userCentric: true,
                            date1: '2011-08-08',
                            date2: '2012-11-11',
                            items: [
                                'qwerty',
                                '!asdf',
                                '@qaz',
                                '~wsx',
                                '!@edc',
                                '!~rfv'
                            ],
                            exclude: false,
                            conjunction: false
                        }]);
                    });
                });
            });
        });
    });

    describe('url segment', function () {
        it('should correctly handle urlMode', function () {
            expect(parse('ym:pv:URL==\'phrase1\'')).to.deep.equal([{
                items: ['phrase1'],
                id: 'ym:pv:URL',
                conjunction: false,
                urlMode: 'dim',
                exclude: false,
                userCentric: false
            }]);
            expect(parse('ym:pv:URLDomain==\'phrase1\'')).to.deep.equal([{
                items: ['phrase1'],
                id: 'ym:pv:URL',
                conjunction: false,
                urlMode: 'host_dim',
                exclude: false,
                userCentric: false
            }]);
            expect(parse('ym:pv:URLPathFull==\'phrase1\'')).to.deep.equal([{
                items: ['phrase1'],
                id: 'ym:pv:URL',
                conjunction: false,
                urlMode: 'path_dim',
                exclude: false,
                userCentric: false
            }]);
        });
        //url segment is almost the same as multiline segment -- no tests for user-centric
    });

    describe('params segment', function () {
        describe('without quantifier', function () {
            it('should correctly handle noQuantifier flag for simple expression', function () {
                expect(parse('ym:s:paramsLevel1==\'level1\'')).to.deep.equal([{
                    id: 'ym:s:paramsLevel1',
                    exclude: false,
                    noQuantifier: true,
                    userCentric: false,
                    op: '==',
                    paramVal: 'level1',
                    paramType: 'ym:s:paramsLevel1'
                }]);
            });
            it('should correctly handle noQuantifier flag for complex expression', function () {
                expect(parse('ym:s:paramsLevel1==\'level1\' and ym:s:paramsLevel2==\'level2\'')).to.deep.equal([{
                    id: 'ym:s:paramsLevel1',
                    exclude: false,
                    noQuantifier: true,
                    userCentric: false,
                    paramName: 'level1',
                    op: '==',
                    paramVal: 'level2',
                    paramType: 'ym:s:paramsLevel2'
                }]);
            });
        });
        describe('with quantifier', function () {
            it('should correctly handle noQuantifier flag for simple expression', function () {
                expect(parse('EXISTS(ym:s:paramsLevel1==\'level1\')')).to.deep.equal([{
                    id: 'ym:s:paramsLevel1',
                    exclude: false,
                    noQuantifier: false,
                    userCentric: false,
                    op: '==',
                    paramVal: 'level1',
                    paramType: 'ym:s:paramsLevel1'
                }]);
            });
            it('should correctly handle noQuantifier flag for complex expression', function () {
                expect(parse(
                    'EXISTS(ym:s:paramsLevel1==\'level1\' and ym:s:paramsLevel2==\'level2\')'
                )).to.deep.equal([{
                    id: 'ym:s:paramsLevel1',
                    exclude: false,
                    noQuantifier: false,
                    userCentric: false,
                    paramName: 'level1',
                    op: '==',
                    paramVal: 'level2',
                    paramType: 'ym:s:paramsLevel2'
                }]);
            });
        });
        it('should correctly parse simple expression', function () {
            expect(parse('ym:s:paramsLevel1==\'level1\'')).to.deep.equal([{
                id: 'ym:s:paramsLevel1',
                exclude: false,
                noQuantifier: true,
                userCentric: false,
                op: '==',
                paramVal: 'level1',
                paramType: 'ym:s:paramsLevel1'
            }]);
        });
        it('should correctly parse complex expression', function () {
            expect(parse('ym:s:paramsLevel1==\'level1\' and ym:s:paramsLevel2==\'level2\'')).to.deep.equal([{
                id: 'ym:s:paramsLevel1',
                exclude: false,
                noQuantifier: true,
                userCentric: false,
                paramName: 'level1',
                op: '==',
                paramVal: 'level2',
                paramType: 'ym:s:paramsLevel2'
            }]);
        });
        it('should correctly parse long complex expression', function () {
            expect(parse(
                'ym:s:paramsLevel1==\'level1\' and ym:s:paramsLevel2==\'level2\' and ym:s:paramsLevel3==\'level3\''
            )).to.deep.equal([{
                id: 'ym:s:paramsLevel1',
                exclude: false,
                noQuantifier: true,
                userCentric: false,
                paramName: 'level1.level2',
                op: '==',
                paramVal: 'level3',
                paramType: 'ym:s:paramsLevel3'
            }]);
        });
        it('should correctly parse complex expression with double value', function () {
            expect(parse('ym:s:paramsLevel1==\'level1\' and ym:s:paramsValueDouble==5')).to.deep.equal([{
                id: 'ym:s:paramsLevel1',
                exclude: false,
                noQuantifier: true,
                userCentric: false,
                paramName: 'level1',
                op: '==',
                paramVal: 5,
                paramType: 'ym:s:paramsValueDouble'
            }]);
        });
        it('should correctly parse value comparison operators', function () {
            expect(parse('ym:s:paramsLevel1==\'level1\' and ym:s:paramsValueDouble==5')).to.deep.equal([{
                id: 'ym:s:paramsLevel1',
                exclude: false,
                noQuantifier: true,
                userCentric: false,
                paramName: 'level1',
                op: '==',
                paramVal: 5,
                paramType: 'ym:s:paramsValueDouble'
            }]);
            expect(parse('ym:s:paramsLevel1==\'level1\' and ym:s:paramsValueDouble>5')).to.deep.equal([{
                id: 'ym:s:paramsLevel1',
                exclude: false,
                noQuantifier: true,
                userCentric: false,
                paramName: 'level1',
                op: '>',
                paramVal: 5,
                paramType: 'ym:s:paramsValueDouble'
            }]);
            expect(parse('ym:s:paramsLevel1==\'level1\' and ym:s:paramsValueDouble<5')).to.deep.equal([{
                id: 'ym:s:paramsLevel1',
                exclude: false,
                noQuantifier: true,
                userCentric: false,
                paramName: 'level1',
                op: '<',
                paramVal: 5,
                paramType: 'ym:s:paramsValueDouble'
            }]);
        });
        describe('user-centric mode', function () {
            describe('without internal quantifier', function () {
                describe('without user-centric dates', function () {
                    it('should correctly handle noQuantifier flag for simple expression', function () {
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(ym:s:paramsLevel1==\'level1\')'
                        )).to.deep.equal([{
                            id: 'ym:s:paramsLevel1-usercentric',
                            userCentric: true,
                            exclude: false,
                            noQuantifier: true,
                            op: '==',
                            paramVal: 'level1',
                            paramType: 'ym:s:paramsLevel1'
                        }]);
                    });
                    it('should correctly handle noQuantifier flag for complex expression', function () {
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH (ym:s:paramsLevel1==\'level1\' and' +
                                ' ym:s:paramsLevel2==\'level2\')'
                        )).to.deep.equal([{
                            id: 'ym:s:paramsLevel1-usercentric',
                            userCentric: true,
                            exclude: false,
                            noQuantifier: true,
                            paramName: 'level1',
                            op: '==',
                            paramVal: 'level2',
                            paramType: 'ym:s:paramsLevel2'
                        }]);
                    });
                });
                describe('with one user-centric date', function () {
                    it('should correctly handle noQuantifier flag for simple expression', function () {
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(ym:s:paramsLevel1==\'level1\' and' +
                                ' ym:s:specialDefaultDate==\'2016-03-15\')'
                        )).to.deep.equal([{
                            id: 'ym:s:paramsLevel1-usercentric',
                            userCentric: true,
                            exclude: false,
                            noQuantifier: true,
                            op: '==',
                            paramVal: 'level1',
                            paramType: 'ym:s:paramsLevel1',
                            date1: '2016-03-15'
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH((ym:s:paramsLevel1==\'level1\') and' +
                                ' ym:s:specialDefaultDate==\'2016-03-15\')'
                        )).to.deep.equal([{
                            id: 'ym:s:paramsLevel1-usercentric',
                            userCentric: true,
                            exclude: false,
                            noQuantifier: true,
                            op: '==',
                            paramVal: 'level1',
                            paramType: 'ym:s:paramsLevel1',
                            date1: '2016-03-15'
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH((ym:s:paramsLevel1==\'level1\') and' +
                                ' (ym:s:specialDefaultDate==\'2016-03-15\'))'
                        )).to.deep.equal([{
                            id: 'ym:s:paramsLevel1-usercentric',
                            userCentric: true,
                            exclude: false,
                            noQuantifier: true,
                            op: '==',
                            paramVal: 'level1',
                            paramType: 'ym:s:paramsLevel1',
                            date1: '2016-03-15'
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(ym:s:paramsLevel1==\'level1\' and' +
                                ' (ym:s:specialDefaultDate==\'2016-03-15\'))'
                        )).to.deep.equal([{
                            id: 'ym:s:paramsLevel1-usercentric',
                            userCentric: true,
                            exclude: false,
                            noQuantifier: true,
                            op: '==',
                            paramVal: 'level1',
                            paramType: 'ym:s:paramsLevel1',
                            date1: '2016-03-15'
                        }]);
                    });
                    it('should correctly handle noQuantifier flag for complex expression', function () {
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH (ym:s:paramsLevel1==\'level1\' and' +
                                ' ym:s:paramsLevel2==\'level2\' and ' +
                                ' ym:s:specialDefaultDate==\'2016-03-15\')'
                        )).to.deep.equal([{
                            id: 'ym:s:paramsLevel1-usercentric',
                            userCentric: true,
                            exclude: false,
                            noQuantifier: true,
                            paramName: 'level1',
                            op: '==',
                            paramVal: 'level2',
                            paramType: 'ym:s:paramsLevel2',
                            date1: '2016-03-15'
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH ((ym:s:paramsLevel1==\'level1\' and' +
                                ' ym:s:paramsLevel2==\'level2\') and ' +
                                ' ym:s:specialDefaultDate==\'2016-03-15\')'
                        )).to.deep.equal([{
                            id: 'ym:s:paramsLevel1-usercentric',
                            userCentric: true,
                            exclude: false,
                            noQuantifier: true,
                            paramName: 'level1',
                            op: '==',
                            paramVal: 'level2',
                            paramType: 'ym:s:paramsLevel2',
                            date1: '2016-03-15'
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH (ym:s:paramsLevel1==\'level1\' and' +
                                ' ym:s:paramsLevel2==\'level2\' and ' +
                                ' (ym:s:specialDefaultDate==\'2016-03-15\'))'
                        )).to.deep.equal([{
                            id: 'ym:s:paramsLevel1-usercentric',
                            userCentric: true,
                            exclude: false,
                            noQuantifier: true,
                            paramName: 'level1',
                            op: '==',
                            paramVal: 'level2',
                            paramType: 'ym:s:paramsLevel2',
                            date1: '2016-03-15'
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH ((ym:s:paramsLevel1==\'level1\' and' +
                                ' ym:s:paramsLevel2==\'level2\') and ' +
                                ' (ym:s:specialDefaultDate==\'2016-03-15\'))'
                        )).to.deep.equal([{
                            id: 'ym:s:paramsLevel1-usercentric',
                            userCentric: true,
                            exclude: false,
                            noQuantifier: true,
                            paramName: 'level1',
                            op: '==',
                            paramVal: 'level2',
                            paramType: 'ym:s:paramsLevel2',
                            date1: '2016-03-15'
                        }]);
                    });
                });
                describe('with two user-centric dates', function () {
                    it('should correctly handle noQuantifier flag for simple expression', function () {
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(ym:s:paramsLevel1==\'level1\' and' +
                                ' ym:s:specialDefaultDate>=\'2016-03-15\' and ym:s:specialDefaultDate<=\'2016-03-17\')'
                        )).to.deep.equal([{
                            id: 'ym:s:paramsLevel1-usercentric',
                            userCentric: true,
                            exclude: false,
                            noQuantifier: true,
                            op: '==',
                            paramVal: 'level1',
                            paramType: 'ym:s:paramsLevel1',
                            date1: '2016-03-15',
                            date2: '2016-03-17'
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH((ym:s:paramsLevel1==\'level1\') and' +
                                ' ym:s:specialDefaultDate>=\'2016-03-15\' and ym:s:specialDefaultDate<=\'2016-03-17\')'
                        )).to.deep.equal([{
                            id: 'ym:s:paramsLevel1-usercentric',
                            userCentric: true,
                            exclude: false,
                            noQuantifier: true,
                            op: '==',
                            paramVal: 'level1',
                            paramType: 'ym:s:paramsLevel1',
                            date1: '2016-03-15',
                            date2: '2016-03-17'
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH((ym:s:paramsLevel1==\'level1\') and' +
                                ' (ym:s:specialDefaultDate>=\'2016-03-15\' and' +
                                ' ym:s:specialDefaultDate<=\'2016-03-17\'))'
                        )).to.deep.equal([{
                            id: 'ym:s:paramsLevel1-usercentric',
                            userCentric: true,
                            exclude: false,
                            noQuantifier: true,
                            op: '==',
                            paramVal: 'level1',
                            paramType: 'ym:s:paramsLevel1',
                            date1: '2016-03-15',
                            date2: '2016-03-17'
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(ym:s:paramsLevel1==\'level1\' and' +
                                ' (ym:s:specialDefaultDate>=\'2016-03-15\' and' +
                                ' ym:s:specialDefaultDate<=\'2016-03-17\'))'
                        )).to.deep.equal([{
                            id: 'ym:s:paramsLevel1-usercentric',
                            userCentric: true,
                            exclude: false,
                            noQuantifier: true,
                            op: '==',
                            paramVal: 'level1',
                            paramType: 'ym:s:paramsLevel1',
                            date1: '2016-03-15',
                            date2: '2016-03-17'
                        }]);
                    });
                    it('should correctly handle noQuantifier flag for complex expression', function () {
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH (ym:s:paramsLevel1==\'level1\' and' +
                                ' ym:s:paramsLevel2==\'level2\' and ' +
                                ' ym:s:specialDefaultDate>=\'2016-03-15\' and ym:s:specialDefaultDate<=\'2016-03-17\')'
                        )).to.deep.equal([{
                            id: 'ym:s:paramsLevel1-usercentric',
                            userCentric: true,
                            exclude: false,
                            noQuantifier: true,
                            paramName: 'level1',
                            op: '==',
                            paramVal: 'level2',
                            paramType: 'ym:s:paramsLevel2',
                            date1: '2016-03-15',
                            date2: '2016-03-17'
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH ((ym:s:paramsLevel1==\'level1\' and' +
                                ' ym:s:paramsLevel2==\'level2\') and ' +
                                ' ym:s:specialDefaultDate>=\'2016-03-15\' and ym:s:specialDefaultDate<=\'2016-03-17\')'
                        )).to.deep.equal([{
                            id: 'ym:s:paramsLevel1-usercentric',
                            userCentric: true,
                            exclude: false,
                            noQuantifier: true,
                            paramName: 'level1',
                            op: '==',
                            paramVal: 'level2',
                            paramType: 'ym:s:paramsLevel2',
                            date1: '2016-03-15',
                            date2: '2016-03-17'
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH (ym:s:paramsLevel1==\'level1\' and' +
                                ' ym:s:paramsLevel2==\'level2\' and ' +
                                ' (ym:s:specialDefaultDate>=\'2016-03-15\' and' +
                                ' ym:s:specialDefaultDate<=\'2016-03-17\'))'
                        )).to.deep.equal([{
                            id: 'ym:s:paramsLevel1-usercentric',
                            userCentric: true,
                            exclude: false,
                            noQuantifier: true,
                            paramName: 'level1',
                            op: '==',
                            paramVal: 'level2',
                            paramType: 'ym:s:paramsLevel2',
                            date1: '2016-03-15',
                            date2: '2016-03-17'
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH ((ym:s:paramsLevel1==\'level1\' and' +
                                ' ym:s:paramsLevel2==\'level2\') and ' +
                                ' (ym:s:specialDefaultDate>=\'2016-03-15\' and' +
                                ' ym:s:specialDefaultDate<=\'2016-03-17\'))'
                        )).to.deep.equal([{
                            id: 'ym:s:paramsLevel1-usercentric',
                            userCentric: true,
                            exclude: false,
                            noQuantifier: true,
                            paramName: 'level1',
                            op: '==',
                            paramVal: 'level2',
                            paramType: 'ym:s:paramsLevel2',
                            date1: '2016-03-15',
                            date2: '2016-03-17'
                        }]);
                    });
                });
            });
            describe('with internal quantifier', function () {
                describe('without user-centric dates', function () {
                    it('should correctly handle noQuantifier flag for simple expression', function () {
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(EXISTS(ym:s:paramsLevel1==\'level1\'))'
                        )).to.deep.equal([{
                            id: 'ym:s:paramsLevel1-usercentric',
                            userCentric: true,
                            exclude: false,
                            noQuantifier: false,
                            op: '==',
                            paramVal: 'level1',
                            paramType: 'ym:s:paramsLevel1'
                        }]);
                    });
                    it('should correctly handle noQuantifier flag for complex expression', function () {
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH (EXISTS(ym:s:paramsLevel1==\'level1\' and' +
                                ' ym:s:paramsLevel2==\'level2\'))'
                        )).to.deep.equal([{
                            id: 'ym:s:paramsLevel1-usercentric',
                            userCentric: true,
                            exclude: false,
                            noQuantifier: false,
                            paramName: 'level1',
                            op: '==',
                            paramVal: 'level2',
                            paramType: 'ym:s:paramsLevel2'
                        }]);
                    });
                });
                describe('with one user-centric date', function () {
                    it('should correctly handle noQuantifier flag for simple expression', function () {
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(EXISTS(ym:s:paramsLevel1==\'level1\') and' +
                                ' ym:s:specialDefaultDate==\'2016-03-15\')'
                        )).to.deep.equal([{
                            id: 'ym:s:paramsLevel1-usercentric',
                            userCentric: true,
                            exclude: false,
                            noQuantifier: false,
                            op: '==',
                            paramVal: 'level1',
                            paramType: 'ym:s:paramsLevel1',
                            date1: '2016-03-15'
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH((EXISTS(ym:s:paramsLevel1==\'level1\')) and' +
                                ' ym:s:specialDefaultDate==\'2016-03-15\')'
                        )).to.deep.equal([{
                            id: 'ym:s:paramsLevel1-usercentric',
                            userCentric: true,
                            exclude: false,
                            noQuantifier: false,
                            op: '==',
                            paramVal: 'level1',
                            paramType: 'ym:s:paramsLevel1',
                            date1: '2016-03-15'
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH((EXISTS(ym:s:paramsLevel1==\'level1\')) and' +
                                ' (ym:s:specialDefaultDate==\'2016-03-15\'))'
                        )).to.deep.equal([{
                            id: 'ym:s:paramsLevel1-usercentric',
                            userCentric: true,
                            exclude: false,
                            noQuantifier: false,
                            op: '==',
                            paramVal: 'level1',
                            paramType: 'ym:s:paramsLevel1',
                            date1: '2016-03-15'
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(EXISTS(ym:s:paramsLevel1==\'level1\') and' +
                                ' (ym:s:specialDefaultDate==\'2016-03-15\'))'
                        )).to.deep.equal([{
                            id: 'ym:s:paramsLevel1-usercentric',
                            userCentric: true,
                            exclude: false,
                            noQuantifier: false,
                            op: '==',
                            paramVal: 'level1',
                            paramType: 'ym:s:paramsLevel1',
                            date1: '2016-03-15'
                        }]);
                    });
                    it('should correctly handle noQuantifier flag for complex expression', function () {
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH (EXISTS(ym:s:paramsLevel1==\'level1\' and' +
                                ' ym:s:paramsLevel2==\'level2\') and ' +
                                ' ym:s:specialDefaultDate==\'2016-03-15\')'
                        )).to.deep.equal([{
                            id: 'ym:s:paramsLevel1-usercentric',
                            userCentric: true,
                            exclude: false,
                            noQuantifier: false,
                            paramName: 'level1',
                            op: '==',
                            paramVal: 'level2',
                            paramType: 'ym:s:paramsLevel2',
                            date1: '2016-03-15'
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH ((EXISTS(ym:s:paramsLevel1==\'level1\' and' +
                                ' ym:s:paramsLevel2==\'level2\')) and ' +
                                ' ym:s:specialDefaultDate==\'2016-03-15\')'
                        )).to.deep.equal([{
                            id: 'ym:s:paramsLevel1-usercentric',
                            userCentric: true,
                            exclude: false,
                            noQuantifier: false,
                            paramName: 'level1',
                            op: '==',
                            paramVal: 'level2',
                            paramType: 'ym:s:paramsLevel2',
                            date1: '2016-03-15'
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH (EXISTS(ym:s:paramsLevel1==\'level1\' and' +
                                ' ym:s:paramsLevel2==\'level2\') and ' +
                                ' (ym:s:specialDefaultDate==\'2016-03-15\'))'
                        )).to.deep.equal([{
                            id: 'ym:s:paramsLevel1-usercentric',
                            userCentric: true,
                            exclude: false,
                            noQuantifier: false,
                            paramName: 'level1',
                            op: '==',
                            paramVal: 'level2',
                            paramType: 'ym:s:paramsLevel2',
                            date1: '2016-03-15'
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH ((EXISTS(ym:s:paramsLevel1==\'level1\' and' +
                                ' ym:s:paramsLevel2==\'level2\')) and ' +
                                ' (ym:s:specialDefaultDate==\'2016-03-15\'))'
                        )).to.deep.equal([{
                            id: 'ym:s:paramsLevel1-usercentric',
                            userCentric: true,
                            exclude: false,
                            noQuantifier: false,
                            paramName: 'level1',
                            op: '==',
                            paramVal: 'level2',
                            paramType: 'ym:s:paramsLevel2',
                            date1: '2016-03-15'
                        }]);
                    });
                });
                describe('with two user-centric dates', function () {
                    it('should correctly handle noQuantifier flag for simple expression', function () {
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(EXISTS(ym:s:paramsLevel1==\'level1\') and' +
                                ' ym:s:specialDefaultDate>=\'2016-03-15\' and ym:s:specialDefaultDate<=\'2016-03-17\')'
                        )).to.deep.equal([{
                            id: 'ym:s:paramsLevel1-usercentric',
                            userCentric: true,
                            exclude: false,
                            noQuantifier: false,
                            op: '==',
                            paramVal: 'level1',
                            paramType: 'ym:s:paramsLevel1',
                            date1: '2016-03-15',
                            date2: '2016-03-17'
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(EXISTS((ym:s:paramsLevel1==\'level1\')) and' +
                                ' ym:s:specialDefaultDate>=\'2016-03-15\' and ym:s:specialDefaultDate<=\'2016-03-17\')'
                        )).to.deep.equal([{
                            id: 'ym:s:paramsLevel1-usercentric',
                            userCentric: true,
                            exclude: false,
                            noQuantifier: false,
                            op: '==',
                            paramVal: 'level1',
                            paramType: 'ym:s:paramsLevel1',
                            date1: '2016-03-15',
                            date2: '2016-03-17'
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH((EXISTS(ym:s:paramsLevel1==\'level1\')) and' +
                                ' (ym:s:specialDefaultDate>=\'2016-03-15\' and' +
                                ' ym:s:specialDefaultDate<=\'2016-03-17\'))'
                        )).to.deep.equal([{
                            id: 'ym:s:paramsLevel1-usercentric',
                            userCentric: true,
                            exclude: false,
                            noQuantifier: false,
                            op: '==',
                            paramVal: 'level1',
                            paramType: 'ym:s:paramsLevel1',
                            date1: '2016-03-15',
                            date2: '2016-03-17'
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(EXISTS(ym:s:paramsLevel1==\'level1\') and' +
                                ' (ym:s:specialDefaultDate>=\'2016-03-15\' and' +
                                ' ym:s:specialDefaultDate<=\'2016-03-17\'))'
                        )).to.deep.equal([{
                            id: 'ym:s:paramsLevel1-usercentric',
                            userCentric: true,
                            exclude: false,
                            noQuantifier: false,
                            op: '==',
                            paramVal: 'level1',
                            paramType: 'ym:s:paramsLevel1',
                            date1: '2016-03-15',
                            date2: '2016-03-17'
                        }]);
                    });
                    it('should correctly handle noQuantifier flag for complex expression', function () {
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH (EXISTS(ym:s:paramsLevel1==\'level1\' and' +
                                ' ym:s:paramsLevel2==\'level2\') and ' +
                                ' ym:s:specialDefaultDate>=\'2016-03-15\' and ym:s:specialDefaultDate<=\'2016-03-17\')'
                        )).to.deep.equal([{
                            id: 'ym:s:paramsLevel1-usercentric',
                            userCentric: true,
                            exclude: false,
                            noQuantifier: false,
                            paramName: 'level1',
                            op: '==',
                            paramVal: 'level2',
                            paramType: 'ym:s:paramsLevel2',
                            date1: '2016-03-15',
                            date2: '2016-03-17'
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH ((EXISTS(ym:s:paramsLevel1==\'level1\' and' +
                                ' ym:s:paramsLevel2==\'level2\')) and ' +
                                ' ym:s:specialDefaultDate>=\'2016-03-15\' and ym:s:specialDefaultDate<=\'2016-03-17\')'
                        )).to.deep.equal([{
                            id: 'ym:s:paramsLevel1-usercentric',
                            userCentric: true,
                            exclude: false,
                            noQuantifier: false,
                            paramName: 'level1',
                            op: '==',
                            paramVal: 'level2',
                            paramType: 'ym:s:paramsLevel2',
                            date1: '2016-03-15',
                            date2: '2016-03-17'
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH (EXISTS(ym:s:paramsLevel1==\'level1\' and' +
                                ' ym:s:paramsLevel2==\'level2\') and ' +
                                ' (ym:s:specialDefaultDate>=\'2016-03-15\' and' +
                                ' ym:s:specialDefaultDate<=\'2016-03-17\'))'
                        )).to.deep.equal([{
                            id: 'ym:s:paramsLevel1-usercentric',
                            userCentric: true,
                            exclude: false,
                            noQuantifier: false,
                            paramName: 'level1',
                            op: '==',
                            paramVal: 'level2',
                            paramType: 'ym:s:paramsLevel2',
                            date1: '2016-03-15',
                            date2: '2016-03-17'
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH ((EXISTS(ym:s:paramsLevel1==\'level1\' and' +
                                ' ym:s:paramsLevel2==\'level2\')) and ' +
                                ' (ym:s:specialDefaultDate>=\'2016-03-15\' and' +
                                ' ym:s:specialDefaultDate<=\'2016-03-17\'))'
                        )).to.deep.equal([{
                            id: 'ym:s:paramsLevel1-usercentric',
                            userCentric: true,
                            exclude: false,
                            noQuantifier: false,
                            paramName: 'level1',
                            op: '==',
                            paramVal: 'level2',
                            paramType: 'ym:s:paramsLevel2',
                            date1: '2016-03-15',
                            date2: '2016-03-17'
                        }]);
                    });
                });
            });
            describe('for suggest', function () {
                it('should handle user-centric dimension without EXISTS wrapper', function () {
                    expect(parse(
                        '(ym:up:paramsLevel1=@\'level1\')'
                    )).to.deep.equal([{
                        exclude: false,
                        id: 'ym:up:paramsLevel1-usercentric',
                        noQuantifier: true,
                        op: '=@',
                        paramType: 'ym:up:paramsLevel1',
                        paramVal: 'level1',
                        userCentric: false
                    }]);
                });
            });
        });
    });

    describe('list segment', function () {
        describe('simple expression', function () {
            it('should parse include expression with regular value', function () {
                expect(parse('ym:s:browserCountry==\'ru\'')).to.deep.equal([{
                    id: 'ym:s:browserCountry',
                    exclude: false,
                    userCentric: false,
                    items: [{id: 'ru'}]
                }]);
            });
            it('should parse include expression with null value', function () {
                expect(parse('ym:s:browserCountry=n')).to.deep.equal([{
                    id: 'ym:s:browserCountry',
                    exclude: false,
                    userCentric: false,
                    items: [{id: null}]
                }]);
            });
            it('should parse exclude expression with regular value', function () {
                expect(parse('ym:s:browserCountry!=\'ru\'')).to.deep.equal([{
                    id: 'ym:s:browserCountry',
                    exclude: true,
                    userCentric: false,
                    items: [{id: 'ru'}]
                }]);
            });
            it('should parse exclude with null value', function () {
                expect(parse('ym:s:browserCountry!n')).to.deep.equal([{
                    id: 'ym:s:browserCountry',
                    exclude: true,
                    userCentric: false,
                    items: [{id: null}]
                }]);
            });
        });
        describe('complex expression', function () {
            it('should parse include expression', function () {
                expect(
                    parse('ym:s:browserCountry==\'ru\' or ym:s:browserCountry==\'us\' or ym:s:browserCountry=n')
                ).to.deep.equal([{
                    id: 'ym:s:browserCountry',
                    exclude: false,
                    userCentric: false,
                    items: [{id: 'ru'}, {id: 'us'}, {id: null}]
                }]);
            });
            it('should parse exclude expression', function () {
                expect(
                    parse('ym:s:browserCountry!=\'ru\' and ym:s:browserCountry!=\'us\' and ym:s:browserCountry!n')
                ).to.deep.equal([{
                    id: 'ym:s:browserCountry',
                    exclude: true,
                    userCentric: false,
                    items: [{id: 'ru'}, {id: 'us'}, {id: null}]
                }]);
            });
        });
        describe('user-centric mode', function () {
            describe('include mode', function () {
                describe('without dates', function () {
                    it('should work with simple expression', function () {
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(ym:s:regionCitySize==1)'
                        )).to.deep.equal([{
                            id: 'ym:s:regionCitySize-usercentric',
                            userCentric: true,
                            exclude: false,
                            items: [{id: 1}]
                        }]);
                    });
                    it('should work with complex expression', function () {
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(ym:s:regionCitySize==1 or ym:s:regionCitySize==2)'
                        )).to.deep.equal([{
                            id: 'ym:s:regionCitySize-usercentric',
                            userCentric: true,
                            exclude: false,
                            items: [{id: 1}, {id: 2}]
                        }]);
                    });
                });
                describe('with one date', function () {
                    it('should work with simple expression', function () {
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(ym:s:regionCitySize==1 and' +
                                ' ym:s:specialDefaultDate==\'2012-06-05\')'
                        )).to.deep.equal([{
                            id: 'ym:s:regionCitySize-usercentric',
                            userCentric: true,
                            exclude: false,
                            items: [{id: 1}],
                            date1: '2012-06-05'
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH((ym:s:regionCitySize==1) and' +
                                ' ym:s:specialDefaultDate==\'2012-06-05\')'
                        )).to.deep.equal([{
                            id: 'ym:s:regionCitySize-usercentric',
                            userCentric: true,
                            exclude: false,
                            items: [{id: 1}],
                            date1: '2012-06-05'
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH((ym:s:regionCitySize==1) and' +
                                ' (ym:s:specialDefaultDate==\'2012-06-05\'))'
                        )).to.deep.equal([{
                            id: 'ym:s:regionCitySize-usercentric',
                            userCentric: true,
                            exclude: false,
                            items: [{id: 1}],
                            date1: '2012-06-05'
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(ym:s:regionCitySize==1 and' +
                                ' (ym:s:specialDefaultDate==\'2012-06-05\'))'
                        )).to.deep.equal([{
                            id: 'ym:s:regionCitySize-usercentric',
                            userCentric: true,
                            exclude: false,
                            items: [{id: 1}],
                            date1: '2012-06-05'
                        }]);
                    });
                    it('should work with complex expression', function () {
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH((ym:s:regionCitySize==1 or ym:s:regionCitySize==5) and' +
                                ' ym:s:specialDefaultDate==\'2012-06-05\')'
                        )).to.deep.equal([{
                            id: 'ym:s:regionCitySize-usercentric',
                            userCentric: true,
                            exclude: false,
                            items: [{id: 1}, {id: 5}],
                            date1: '2012-06-05'
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH((ym:s:regionCitySize==1 or ym:s:regionCitySize==5) and' +
                                ' (ym:s:specialDefaultDate==\'2012-06-05\'))'
                        )).to.deep.equal([{
                            id: 'ym:s:regionCitySize-usercentric',
                            userCentric: true,
                            exclude: false,
                            items: [{id: 1}, {id: 5}],
                            date1: '2012-06-05'
                        }]);
                    });
                });
                describe('with two dates', function () {
                    it('should work with simple expression', function () {
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(ym:s:regionCitySize==1 and' +
                                ' ym:s:specialDefaultDate>=\'2012-06-05\' and ym:s:specialDefaultDate<=\'2012-06-07\')'
                        )).to.deep.equal([{
                            id: 'ym:s:regionCitySize-usercentric',
                            userCentric: true,
                            exclude: false,
                            items: [{id: 1}],
                            date1: '2012-06-05',
                            date2: '2012-06-07'
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH((ym:s:regionCitySize==1) and' +
                                ' ym:s:specialDefaultDate>=\'2012-06-05\' and ym:s:specialDefaultDate<=\'2012-06-07\')'
                        )).to.deep.equal([{
                            id: 'ym:s:regionCitySize-usercentric',
                            userCentric: true,
                            exclude: false,
                            items: [{id: 1}],
                            date1: '2012-06-05',
                            date2: '2012-06-07'
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH((ym:s:regionCitySize==1) and' +
                                ' (ym:s:specialDefaultDate>=\'2012-06-05\' and' +
                                ' ym:s:specialDefaultDate<=\'2012-06-07\'))'
                        )).to.deep.equal([{
                            id: 'ym:s:regionCitySize-usercentric',
                            userCentric: true,
                            exclude: false,
                            items: [{id: 1}],
                            date1: '2012-06-05',
                            date2: '2012-06-07'
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(ym:s:regionCitySize==1 and' +
                                ' (ym:s:specialDefaultDate>=\'2012-06-05\' and' +
                                ' ym:s:specialDefaultDate<=\'2012-06-07\'))'
                        )).to.deep.equal([{
                            id: 'ym:s:regionCitySize-usercentric',
                            userCentric: true,
                            exclude: false,
                            items: [{id: 1}],
                            date1: '2012-06-05',
                            date2: '2012-06-07'
                        }]);
                    });
                    it('should work with complex expression', function () {
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH((ym:s:regionCitySize==1 or ym:s:regionCitySize==5) and' +
                                ' ym:s:specialDefaultDate>=\'2012-06-05\' and' +
                                ' ym:s:specialDefaultDate<=\'2012-06-07\')'
                        )).to.deep.equal([{
                            id: 'ym:s:regionCitySize-usercentric',
                            userCentric: true,
                            exclude: false,
                            items: [{id: 1}, {id: 5}],
                            date1: '2012-06-05',
                            date2: '2012-06-07'
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH((ym:s:regionCitySize==1 or ym:s:regionCitySize==5) and' +
                                ' (ym:s:specialDefaultDate>=\'2012-06-05\' and' +
                                ' ym:s:specialDefaultDate<=\'2012-06-07\'))'
                        )).to.deep.equal([{
                            id: 'ym:s:regionCitySize-usercentric',
                            userCentric: true,
                            exclude: false,
                            items: [{id: 1}, {id: 5}],
                            date1: '2012-06-05',
                            date2: '2012-06-07'
                        }]);
                    });

                });
            });
            describe('exclude mode', function () {
                describe('without dates', function () {
                    it('should work with simple expression', function () {
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(ym:s:regionCitySize!=1)'
                        )).to.deep.equal([{
                            id: 'ym:s:regionCitySize-usercentric',
                            userCentric: true,
                            exclude: true,
                            items: [{id: 1}]
                        }]);
                    });
                    it('should work with complex expression', function () {
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(ym:s:regionCitySize!=1 and ym:s:regionCitySize!=2)'
                        )).to.deep.equal([{
                            id: 'ym:s:regionCitySize-usercentric',
                            userCentric: true,
                            exclude: true,
                            items: [{id: 1}, {id: 2}]
                        }]);
                    });
                });
                describe('with one date', function () {
                    it('should work with simple expression', function () {
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(ym:s:regionCitySize!=1 and' +
                                ' ym:s:specialDefaultDate==\'2012-06-05\')'
                        )).to.deep.equal([{
                            id: 'ym:s:regionCitySize-usercentric',
                            userCentric: true,
                            exclude: true,
                            items: [{id: 1}],
                            date1: '2012-06-05'
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH((ym:s:regionCitySize!=1) and' +
                                ' ym:s:specialDefaultDate==\'2012-06-05\')'
                        )).to.deep.equal([{
                            id: 'ym:s:regionCitySize-usercentric',
                            userCentric: true,
                            exclude: true,
                            items: [{id: 1}],
                            date1: '2012-06-05'
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH((ym:s:regionCitySize!=1) and' +
                                ' (ym:s:specialDefaultDate==\'2012-06-05\'))'
                        )).to.deep.equal([{
                            id: 'ym:s:regionCitySize-usercentric',
                            userCentric: true,
                            exclude: true,
                            items: [{id: 1}],
                            date1: '2012-06-05'
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(ym:s:regionCitySize!=1 and' +
                                ' (ym:s:specialDefaultDate==\'2012-06-05\'))'
                        )).to.deep.equal([{
                            id: 'ym:s:regionCitySize-usercentric',
                            userCentric: true,
                            exclude: true,
                            items: [{id: 1}],
                            date1: '2012-06-05'
                        }]);
                    });
                    it('should work with complex expression', function () {
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH((ym:s:regionCitySize!=1 and ym:s:regionCitySize!=5) and' +
                                ' ym:s:specialDefaultDate==\'2012-06-05\')'
                        )).to.deep.equal([{
                            id: 'ym:s:regionCitySize-usercentric',
                            userCentric: true,
                            exclude: true,
                            items: [{id: 1}, {id: 5}],
                            date1: '2012-06-05'
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH((ym:s:regionCitySize!=1 and ym:s:regionCitySize!=5) and' +
                                ' (ym:s:specialDefaultDate==\'2012-06-05\'))'
                        )).to.deep.equal([{
                            id: 'ym:s:regionCitySize-usercentric',
                            userCentric: true,
                            exclude: true,
                            items: [{id: 1}, {id: 5}],
                            date1: '2012-06-05'
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(ym:s:regionCitySize!=1 and ym:s:regionCitySize!=5 and' +
                                ' ym:s:specialDefaultDate==\'2012-06-05\')'
                        )).to.deep.equal([{
                            id: 'ym:s:regionCitySize-usercentric',
                            userCentric: true,
                            exclude: true,
                            items: [{id: 1}, {id: 5}],
                            date1: '2012-06-05'
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(ym:s:regionCitySize!=1 and ym:s:regionCitySize!=5 and' +
                                ' (ym:s:specialDefaultDate==\'2012-06-05\'))'
                        )).to.deep.equal([{
                            id: 'ym:s:regionCitySize-usercentric',
                            userCentric: true,
                            exclude: true,
                            items: [{id: 1}, {id: 5}],
                            date1: '2012-06-05'
                        }]);

                    });
                });
                describe('with two dates', function () {
                    it('should work with simple expression', function () {
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(ym:s:regionCitySize!=1 and' +
                                ' ym:s:specialDefaultDate>=\'2012-06-05\' and ym:s:specialDefaultDate<=\'2012-06-07\')'
                        )).to.deep.equal([{
                            id: 'ym:s:regionCitySize-usercentric',
                            userCentric: true,
                            exclude: true,
                            items: [{id: 1}],
                            date1: '2012-06-05',
                            date2: '2012-06-07'
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH((ym:s:regionCitySize!=1) and' +
                                ' ym:s:specialDefaultDate>=\'2012-06-05\' and ym:s:specialDefaultDate<=\'2012-06-07\')'
                        )).to.deep.equal([{
                            id: 'ym:s:regionCitySize-usercentric',
                            userCentric: true,
                            exclude: true,
                            items: [{id: 1}],
                            date1: '2012-06-05',
                            date2: '2012-06-07'
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH((ym:s:regionCitySize!=1) and' +
                                ' (ym:s:specialDefaultDate>=\'2012-06-05\' and' +
                                ' ym:s:specialDefaultDate<=\'2012-06-07\'))'
                        )).to.deep.equal([{
                            id: 'ym:s:regionCitySize-usercentric',
                            userCentric: true,
                            exclude: true,
                            items: [{id: 1}],
                            date1: '2012-06-05',
                            date2: '2012-06-07'
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(ym:s:regionCitySize!=1 and' +
                                ' (ym:s:specialDefaultDate>=\'2012-06-05\' and' +
                                ' ym:s:specialDefaultDate<=\'2012-06-07\'))'
                        )).to.deep.equal([{
                            id: 'ym:s:regionCitySize-usercentric',
                            userCentric: true,
                            exclude: true,
                            items: [{id: 1}],
                            date1: '2012-06-05',
                            date2: '2012-06-07'
                        }]);
                    });
                    it('should work with complex expression', function () {
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH((ym:s:regionCitySize!=1 and ym:s:regionCitySize!=5) and' +
                                ' ym:s:specialDefaultDate>=\'2012-06-05\' and' +
                                ' ym:s:specialDefaultDate<=\'2012-06-07\')'
                        )).to.deep.equal([{
                            id: 'ym:s:regionCitySize-usercentric',
                            userCentric: true,
                            exclude: true,
                            items: [{id: 1}, {id: 5}],
                            date1: '2012-06-05',
                            date2: '2012-06-07'
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH((ym:s:regionCitySize!=1 and ym:s:regionCitySize!=5) and' +
                                ' (ym:s:specialDefaultDate>=\'2012-06-05\' and' +
                                ' ym:s:specialDefaultDate<=\'2012-06-07\'))'
                        )).to.deep.equal([{
                            id: 'ym:s:regionCitySize-usercentric',
                            userCentric: true,
                            exclude: true,
                            items: [{id: 1}, {id: 5}],
                            date1: '2012-06-05',
                            date2: '2012-06-07'
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(ym:s:regionCitySize!=1 and ym:s:regionCitySize!=5 and' +
                                ' ym:s:specialDefaultDate>=\'2012-06-05\' and' +
                                ' ym:s:specialDefaultDate<=\'2012-06-07\')'
                        )).to.deep.equal([{
                            id: 'ym:s:regionCitySize-usercentric',
                            userCentric: true,
                            exclude: true,
                            items: [{id: 1}, {id: 5}],
                            date1: '2012-06-05',
                            date2: '2012-06-07'
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(ym:s:regionCitySize!=1 and ym:s:regionCitySize!=5 and' +
                                ' (ym:s:specialDefaultDate>=\'2012-06-05\' and' +
                                ' ym:s:specialDefaultDate<=\'2012-06-07\'))'
                        )).to.deep.equal([{
                            id: 'ym:s:regionCitySize-usercentric',
                            userCentric: true,
                            exclude: true,
                            items: [{id: 1}, {id: 5}],
                            date1: '2012-06-05',
                            date2: '2012-06-07'
                        }]);
                    });
                });
            });
        });
    });

    describe('tree segment', function () {
        describe('one level', function () {
            describe('first dimension', function () {
                it('should parse in include mode with one value', function () {
                    expect(parse('ym:s:operatingSystemRoot IN(\'windows\')')).to.deep.equal([{
                        id: 'ym:s:operatingSystemRoot',
                        exclude: false,
                        userCentric: false,
                        items: [[{id: 'windows'}]]
                    }]);
                    expect(parse('ym:s:operatingSystemRoot =.(\'windows\')')).to.deep.equal([{
                        id: 'ym:s:operatingSystemRoot',
                        exclude: false,
                        userCentric: false,
                        items: [[{id: 'windows'}]]
                    }]);
                });
                it('should parse in include mode with many values', function () {
                    expect(parse('ym:s:operatingSystemRoot IN(\'windows\', \'linux\')')).to.deep.equal([{
                        id: 'ym:s:operatingSystemRoot',
                        exclude: false,
                        userCentric: false,
                        items: [[{id: 'windows'}], [{id: 'linux'}]]
                    }]);
                    expect(parse('ym:s:operatingSystemRoot =.(\'windows\', \'linux\')')).to.deep.equal([{
                        id: 'ym:s:operatingSystemRoot',
                        exclude: false,
                        userCentric: false,
                        items: [[{id: 'windows'}], [{id: 'linux'}]]
                    }]);
                });
                it('should parse in exclude mode with one value', function () {
                    expect(parse('ym:s:operatingSystemRoot NOT IN(\'windows\')')).to.deep.equal([{
                        id: 'ym:s:operatingSystemRoot',
                        exclude: true,
                        userCentric: false,
                        items: [[{id: 'windows'}]]
                    }]);
                    expect(parse('ym:s:operatingSystemRoot !.(\'windows\')')).to.deep.equal([{
                        id: 'ym:s:operatingSystemRoot',
                        exclude: true,
                        userCentric: false,
                        items: [[{id: 'windows'}]]
                    }]);
                });
                it('should parse in exclude mode with many values', function () {
                    expect(parse('ym:s:operatingSystemRoot NOT IN(\'windows\', \'linux\')')).to.deep.equal([{
                        id: 'ym:s:operatingSystemRoot',
                        exclude: true,
                        userCentric: false,
                        items: [[{id: 'windows'}], [{id: 'linux'}]]
                    }]);
                    expect(parse('ym:s:operatingSystemRoot !.(\'windows\', \'linux\')')).to.deep.equal([{
                        id: 'ym:s:operatingSystemRoot',
                        exclude: true,
                        userCentric: false,
                        items: [[{id: 'windows'}], [{id: 'linux'}]]
                    }]);
                });
            });
            describe('not first dimension', function () {
                it('should parse in include mode with one value', function () {
                    var items = [[]];
                    items[0][1] = {id: 'windows xp'};

                    expect(parse('ym:s:operatingSystem IN(\'windows xp\')')).to.deep.equal([{
                        id: 'ym:s:operatingSystemRoot',
                        exclude: false,
                        userCentric: false,
                        items: items
                    }]);
                    expect(parse('ym:s:operatingSystem =.(\'windows xp\')')).to.deep.equal([{
                        id: 'ym:s:operatingSystemRoot',
                        exclude: false,
                        userCentric: false,
                        items: items
                    }]);
                });
                it('should parse in include mode with many values', function () {
                    var items = [[], []];
                    items[0][1] = {id: 'windows xp'};
                    items[1][1] = {id: 'linux debian'};

                    expect(parse('ym:s:operatingSystem IN(\'windows xp\', \'linux debian\')')).to.deep.equal([{
                        id: 'ym:s:operatingSystemRoot',
                        exclude: false,
                        userCentric: false,
                        items: items
                    }]);
                    expect(parse('ym:s:operatingSystem =.(\'windows xp\', \'linux debian\')')).to.deep.equal([{
                        id: 'ym:s:operatingSystemRoot',
                        exclude: false,
                        userCentric: false,
                        items: items
                    }]);
                });
                it('should parse in exclude mode with one value', function () {
                    var items = [[]];
                    items[0][1] = {id: 'windows xp'};

                    expect(parse('ym:s:operatingSystem NOT IN(\'windows xp\')')).to.deep.equal([{
                        id: 'ym:s:operatingSystemRoot',
                        exclude: true,
                        userCentric: false,
                        items: items
                    }]);
                    expect(parse('ym:s:operatingSystem !.(\'windows xp\')')).to.deep.equal([{
                        id: 'ym:s:operatingSystemRoot',
                        exclude: true,
                        userCentric: false,
                        items: items
                    }]);
                });
                it('should parse in exclude mode with many values', function () {
                    var items = [[], []];
                    items[0][1] = {id: 'windows xp'};
                    items[1][1] = {id: 'linux debian'};
                    expect(parse('ym:s:operatingSystem NOT IN(\'windows xp\', \'linux debian\')')).to.deep.equal([{
                        id: 'ym:s:operatingSystemRoot',
                        exclude: true,
                        userCentric: false,
                        items: items
                    }]);
                    expect(parse('ym:s:operatingSystem !.(\'windows xp\', \'linux debian\')')).to.deep.equal([{
                        id: 'ym:s:operatingSystemRoot',
                        exclude: true,
                        userCentric: false,
                        items: items
                    }]);
                });
            });
        });
        describe('multi level', function () {
            it('one value and one value in include mode', function () {
                var items = [[], []];
                items[0][0] = {id: 'windows'};
                items[1][1] = {id: 'windows xp'};

                expect(parse(
                    'ym:s:operatingSystemRoot IN(\'windows\') or ym:s:operatingSystem IN(\'windows xp\')'
                )).to.deep.equal([{
                    id: 'ym:s:operatingSystemRoot',
                    exclude: false,
                    userCentric: false,
                    items: items
                }]);
                expect(parse(
                    'ym:s:operatingSystemRoot =.(\'windows\') or ym:s:operatingSystem =.(\'windows xp\')'
                )).to.deep.equal([{
                    id: 'ym:s:operatingSystemRoot',
                    exclude: false,
                    userCentric: false,
                    items: items
                }]);
            });
            it('one value and many values in include mode', function () {
                var items = [[], [], []];
                items[0][0] = {id: 'windows'};
                items[1][1] = {id: 'windows xp'};
                items[2][1] = {id: 'linux debian'};

                expect(parse(
                    'ym:s:operatingSystemRoot IN(\'windows\') or' +
                        ' ym:s:operatingSystem IN(\'windows xp\', \'linux debian\')'
                )).to.deep.equal([{
                    id: 'ym:s:operatingSystemRoot',
                    exclude: false,
                    userCentric: false,
                    items: items
                }]);
                expect(parse(
                    'ym:s:operatingSystemRoot =.(\'windows\') or' +
                        ' ym:s:operatingSystem =.(\'windows xp\', \'linux debian\')'
                )).to.deep.equal([{
                    id: 'ym:s:operatingSystemRoot',
                    exclude: false,
                    userCentric: false,
                    items: items
                }]);
            });
            it('many values and many values in include mode', function () {
                var items = [[], [], [], []];
                items[0][0] = {id: 'windows'};
                items[1][0] = {id: 'linux'};
                items[2][1] = {id: 'windows xp'};
                items[3][1] = {id: 'linux debian'};

                expect(parse(
                    'ym:s:operatingSystemRoot IN(\'windows\', \'linux\') or' +
                        ' ym:s:operatingSystem IN(\'windows xp\', \'linux debian\')'
                )).to.deep.equal([{
                    id: 'ym:s:operatingSystemRoot',
                    exclude: false,
                    userCentric: false,
                    items: items
                }]);
                expect(parse(
                    'ym:s:operatingSystemRoot =.(\'windows\', \'linux\') or' +
                        ' ym:s:operatingSystem =.(\'windows xp\', \'linux debian\')'
                )).to.deep.equal([{
                    id: 'ym:s:operatingSystemRoot',
                    exclude: false,
                    userCentric: false,
                    items: items
                }]);
            });
            it('many values and one value in include mode', function () {
                var items = [[], [], []];
                items[0][0] = {id: 'windows'};
                items[1][0] = {id: 'linux'};
                items[2][1] = {id: 'windows xp'};

                expect(parse(
                    'ym:s:operatingSystemRoot IN(\'windows\', \'linux\') or ym:s:operatingSystem IN(\'windows xp\')'
                )).to.deep.equal([{
                    id: 'ym:s:operatingSystemRoot',
                    exclude: false,
                    userCentric: false,
                    items: items
                }]);
                expect(parse(
                    'ym:s:operatingSystemRoot =.(\'windows\', \'linux\') or ym:s:operatingSystem =.(\'windows xp\')'
                )).to.deep.equal([{
                    id: 'ym:s:operatingSystemRoot',
                    exclude: false,
                    userCentric: false,
                    items: items
                }]);
            });
            it('one value and one value in exclude mode', function () {
                var items = [[], []];
                items[0][0] = {id: 'windows'};
                items[1][1] = {id: 'windows xp'};

                expect(parse(
                    'ym:s:operatingSystemRoot NOT IN(\'windows\') and ym:s:operatingSystem NOT IN(\'windows xp\')'
                )).to.deep.equal([{
                    id: 'ym:s:operatingSystemRoot',
                    exclude: true,
                    userCentric: false,
                    items: items
                }]);
                expect(parse(
                    'ym:s:operatingSystemRoot !.(\'windows\') and ym:s:operatingSystem !.(\'windows xp\')'
                )).to.deep.equal([{
                    id: 'ym:s:operatingSystemRoot',
                    exclude: true,
                    userCentric: false,
                    items: items
                }]);

            });
            it('one value and many values in exclude mode', function () {
                var items = [[], [], []];
                items[0][0] = {id: 'windows'};
                items[1][1] = {id: 'windows xp'};
                items[2][1] = {id: 'linux debian'};

                expect(parse(
                    'ym:s:operatingSystemRoot NOT IN(\'windows\') and' +
                        ' ym:s:operatingSystem NOT IN(\'windows xp\', \'linux debian\')'
                )).to.deep.equal([{
                    id: 'ym:s:operatingSystemRoot',
                    exclude: true,
                    userCentric: false,
                    items: items
                }]);
                expect(parse(
                    'ym:s:operatingSystemRoot !.(\'windows\') and' +
                        ' ym:s:operatingSystem !.(\'windows xp\', \'linux debian\')'
                )).to.deep.equal([{
                    id: 'ym:s:operatingSystemRoot',
                    exclude: true,
                    userCentric: false,
                    items: items
                }]);

            });
            it('many values and many values in exclude mode', function () {
                var items = [[], [], [], []];
                items[0][0] = {id: 'windows'};
                items[1][0] = {id: 'linux'};
                items[2][1] = {id: 'windows xp'};
                items[3][1] = {id: 'linux debian'};

                expect(parse(
                    'ym:s:operatingSystemRoot NOT IN(\'windows\', \'linux\') and' +
                        ' ym:s:operatingSystem NOT IN(\'windows xp\', \'linux debian\')'
                )).to.deep.equal([{
                    id: 'ym:s:operatingSystemRoot',
                    exclude: true,
                    userCentric: false,
                    items: items
                }]);
                expect(parse(
                    'ym:s:operatingSystemRoot !.(\'windows\', \'linux\') and' +
                        ' ym:s:operatingSystem !.(\'windows xp\', \'linux debian\')'
                )).to.deep.equal([{
                    id: 'ym:s:operatingSystemRoot',
                    exclude: true,
                    userCentric: false,
                    items: items
                }]);

            });
            it('many values and one value in exclude mode', function () {
                var items = [[], [], []];
                items[0][0] = {id: 'windows'};
                items[1][0] = {id: 'linux'};
                items[2][1] = {id: 'windows xp'};

                expect(parse(
                    'ym:s:operatingSystemRoot NOT IN(\'windows\', \'linux\') and' +
                        ' ym:s:operatingSystem NOT IN(\'windows xp\')'
                )).to.deep.equal([{
                    id: 'ym:s:operatingSystemRoot',
                    exclude: true,
                    userCentric: false,
                    items: items
                }]);
                expect(parse(
                    'ym:s:operatingSystemRoot !.(\'windows\', \'linux\') and' +
                        ' ym:s:operatingSystem !.(\'windows xp\')'
                )).to.deep.equal([{
                    id: 'ym:s:operatingSystemRoot',
                    exclude: true,
                    userCentric: false,
                    items: items
                }]);
            });
        });
        describe('should fallback to path format parser for legacy filter format', function () {
            describe('include mode', function () {
                describe('same depth level mode', function () {
                    it('should handle single expression', function () {
                        expect(parse('ym:s:operatingSystemRoot==\'windows\'')).to.deep.equal([{
                            id: 'ym:s:operatingSystemRoot',
                            exclude: false,
                            userCentric: false,
                            items: [[{id: 'windows'}]]
                        }]);
                    });
                    it('should handle multivalue expression of first level', function () {
                        expect(parse(
                            'ym:s:operatingSystemRoot==\'windows\' or ym:s:operatingSystemRoot==\'linux\''
                        )).to.deep.equal([{
                            id: 'ym:s:operatingSystemRoot',
                            exclude: false,
                            userCentric: false,
                            items: [[{id: 'windows'}], [{id: 'linux'}]]
                        }]);
                    });
                    it('should handle single path-like expression', function () {
                        var items;
                        items = [[]];
                        items[0][1] = {id: 'windows xp'};
                        expect(parse(
                            'ym:s:operatingSystemRoot==\'windows\' and ym:s:operatingSystem==\'windows xp\''
                        )).to.deep.equal([{
                            id: 'ym:s:operatingSystemRoot',
                            exclude: false,
                            userCentric: false,
                            items: items
                        }]);
                    });
                    it('should handle multivalue path-like expression', function () {
                        var items;
                        items = [[], []];
                        items[0][1] = {id: 'windows xp'};
                        items[1][1] = {id: 'linux debian'};
                        expect(parse(
                            'ym:s:operatingSystemRoot==\'windows\' and ym:s:operatingSystem==\'windows xp\' or' +
                            ' ym:s:operatingSystemRoot==\'linux\' and ym:s:operatingSystem==\'linux debian\''
                        )).to.deep.equal([{
                            id: 'ym:s:operatingSystemRoot',
                            exclude: false,
                            userCentric: false,
                            items: items
                        }]);
                    });
                });
                describe('mixed depth mode', function () {
                    it('should handle first simple and second is complex', function () {
                        var items;
                        items = [[], []];
                        items[0] = [{id: 'windows'}];
                        items[1][1] = {id: 'linux debian'};
                        expect(parse(
                            'ym:s:operatingSystemRoot==\'windows\' or' +
                            ' ym:s:operatingSystemRoot==\'linux\' and ym:s:operatingSystem==\'linux debian\''
                        )).to.deep.equal([{
                            id: 'ym:s:operatingSystemRoot',
                            exclude: false,
                            userCentric: false,
                            items: items
                        }]);
                    });
                    it('should handle first complex and second is simple', function () {
                        var items;
                        items = [[], []];
                        items[0][1] = {id: 'windows xp'};
                        items[1][0] = {id: 'linux'};
                        expect(parse(
                            'ym:s:operatingSystemRoot==\'windows\' and ym:s:operatingSystem==\'windows xp\' or' +
                            ' ym:s:operatingSystemRoot==\'linux\''
                        )).to.deep.equal([{
                            id: 'ym:s:operatingSystemRoot',
                            exclude: false,
                            userCentric: false,
                            items: items
                        }]);
                    });
                });
            });
            describe('exclude mode', function () {
                describe('same depth level mode', function () {
                    it('should handle single expression', function () {
                        expect(parse('ym:s:operatingSystemRoot!=\'windows\'')).to.deep.equal([{
                            id: 'ym:s:operatingSystemRoot',
                            exclude: true,
                            userCentric: false,
                            items: [[{id: 'windows'}]]
                        }]);
                    });
                    it('should handle multivalue expression of first level', function () {
                        expect(parse(
                            'ym:s:operatingSystemRoot!=\'windows\' and ym:s:operatingSystemRoot!=\'linux\''
                        )).to.deep.equal([{
                            id: 'ym:s:operatingSystemRoot',
                            exclude: true,
                            userCentric: false,
                            items: [[{id: 'windows'}], [{id: 'linux'}]]
                        }]);
                    });
                    it('should handle single path-like expression', function () {
                        var items;
                        items = [[]];
                        items[0][1] = {id: 'windows xp'};
                        expect(parse(
                            'ym:s:operatingSystemRoot!=\'windows\' or ym:s:operatingSystem!=\'windows xp\''
                        )).to.deep.equal([{
                            id: 'ym:s:operatingSystemRoot',
                            exclude: true,
                            userCentric: false,
                            items: items
                        }]);
                    });
                    it('should handle multivalue path-like expression', function () {
                        var items = [[], []];
                        items[0][1] = {id: 'windows xp'};
                        items[1][1] = {id: 'linux debian'};
                        expect(parse(
                            '((ym:s:operatingSystemRoot!=\'windows\' or ym:s:operatingSystem!=\'windows xp\') and' +
                            ' (ym:s:operatingSystemRoot!=\'linux\' or ym:s:operatingSystem!=\'linux debian\'))'
                        )).to.deep.equal([{
                            id: 'ym:s:operatingSystemRoot',
                            exclude: true,
                            userCentric: false,
                            items: items
                        }]);
                    });
                });
                describe('mixed depth mode', function () {
                    it('should handle first simple and second is complex', function () {
                        var items;
                        items = [[], []];
                        items[0] = [{id: 'windows'}];
                        items[1][1] = {id: 'linux debian'};
                        expect(parse(
                            '(ym:s:operatingSystemRoot!=\'windows\' and ' +
                            ' (ym:s:operatingSystemRoot!=\'linux\' or ym:s:operatingSystem!=\'linux debian\'))'
                        )).to.deep.equal([{
                            id: 'ym:s:operatingSystemRoot',
                            exclude: true,
                            userCentric: false,
                            items: items
                        }]);
                    });
                    it('should handle first complex and second is simple', function () {
                        var items;
                        items = [[], []];
                        items[0][1] = {id: 'windows xp'};
                        items[1][0] = {id: 'linux'};
                        expect(parse(
                            '((ym:s:operatingSystemRoot!=\'windows\' or ym:s:operatingSystem!=\'windows xp\') and' +
                            ' ym:s:operatingSystemRoot!=\'linux\')'
                        )).to.deep.equal([{
                            id: 'ym:s:operatingSystemRoot',
                            exclude: true,
                            userCentric: false,
                            items: items
                        }]);
                    });
                });
            });
        });
        describe('user-centric', function () {
            describe('one level', function () {
                describe('include mode', function () {
                    it('should work without user-centric dates', function () {
                        var items;
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(' +
                                'ym:s:operatingSystemRoot IN(\'windows\', \'linux\')' +
                                ')'
                        )).to.deep.equal([{
                            id: 'ym:s:operatingSystemRoot-usercentric',
                            userCentric: true,
                            exclude: false,
                            items: [[{id: 'windows'}], [{id: 'linux'}]]
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(' +
                                'ym:s:operatingSystemRoot =.(\'windows\', \'linux\')' +
                                ')'
                        )).to.deep.equal([{
                            id: 'ym:s:operatingSystemRoot-usercentric',
                            userCentric: true,
                            exclude: false,
                            items: [[{id: 'windows'}], [{id: 'linux'}]]
                        }]);

                        items = [[], []];
                        items[0][1] = {id: 'windows xp'};
                        items[1][1] = {id: 'linux debian'};
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(' +
                                'ym:s:operatingSystem IN(\'windows xp\', \'linux debian\')' +
                                ')'
                        )).to.deep.equal([{
                            id: 'ym:s:operatingSystemRoot-usercentric',
                            userCentric: true,
                            exclude: false,
                            items: items
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(' +
                                'ym:s:operatingSystem =.(\'windows xp\', \'linux debian\')' +
                                ')'
                        )).to.deep.equal([{
                            id: 'ym:s:operatingSystemRoot-usercentric',
                            userCentric: true,
                            exclude: false,
                            items: items
                        }]);
                    });
                    it('should work with user-centric dates', function () {
                        var items;
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(' +
                                'ym:s:operatingSystemRoot IN(\'windows\', \'linux\') and' +
                                ' ym:s:specialDefaultDate>=\'2015-04-05\' and ym:s:specialDefaultDate<=\'2015-05-07\'' +
                                ')'
                        )).to.deep.equal([{
                            id: 'ym:s:operatingSystemRoot-usercentric',
                            userCentric: true,
                            exclude: false,
                            items: [[{id: 'windows'}], [{id: 'linux'}]],
                            date1: '2015-04-05',
                            date2: '2015-05-07'
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(' +
                                'ym:s:operatingSystemRoot =.(\'windows\', \'linux\') and' +
                                ' ym:s:specialDefaultDate>=\'2015-04-05\' and ym:s:specialDefaultDate<=\'2015-05-07\'' +
                                ')'
                        )).to.deep.equal([{
                            id: 'ym:s:operatingSystemRoot-usercentric',
                            userCentric: true,
                            exclude: false,
                            items: [[{id: 'windows'}], [{id: 'linux'}]],
                            date1: '2015-04-05',
                            date2: '2015-05-07'
                        }]);

                        items = [[], []];
                        items[0][1] = {id: 'windows xp'};
                        items[1][1] = {id: 'linux debian'};
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(' +
                                'ym:s:operatingSystem IN(\'windows xp\', \'linux debian\') and' +
                                ' ym:s:specialDefaultDate>=\'2015-04-05\' and ym:s:specialDefaultDate<=\'2015-05-07\'' +
                                ')'
                        )).to.deep.equal([{
                            id: 'ym:s:operatingSystemRoot-usercentric',
                            userCentric: true,
                            exclude: false,
                            items: items,
                            date1: '2015-04-05',
                            date2: '2015-05-07'
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(' +
                                'ym:s:operatingSystem =.(\'windows xp\', \'linux debian\') and' +
                                ' ym:s:specialDefaultDate>=\'2015-04-05\' and ym:s:specialDefaultDate<=\'2015-05-07\'' +
                                ')'
                        )).to.deep.equal([{
                            id: 'ym:s:operatingSystemRoot-usercentric',
                            userCentric: true,
                            exclude: false,
                            items: items,
                            date1: '2015-04-05',
                            date2: '2015-05-07'
                        }]);
                    });
                });
                describe('exclude mode', function () {
                    it('should work without user-centric dates', function () {
                        var items;
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(' +
                                'ym:s:operatingSystemRoot NOT IN(\'windows\', \'linux\')' +
                                ')'
                        )).to.deep.equal([{
                            id: 'ym:s:operatingSystemRoot-usercentric',
                            userCentric: true,
                            exclude: true,
                            items: [[{id: 'windows'}], [{id: 'linux'}]]
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(' +
                                'ym:s:operatingSystemRoot !.(\'windows\', \'linux\')' +
                                ')'
                        )).to.deep.equal([{
                            id: 'ym:s:operatingSystemRoot-usercentric',
                            userCentric: true,
                            exclude: true,
                            items: [[{id: 'windows'}], [{id: 'linux'}]]
                        }]);
                        items = [[], []];
                        items[0][1] = {id: 'windows xp'};
                        items[1][1] = {id: 'linux debian'};
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(' +
                                'ym:s:operatingSystem NOT IN(\'windows xp\', \'linux debian\')' +
                                ')'
                        )).to.deep.equal([{
                            id: 'ym:s:operatingSystemRoot-usercentric',
                            userCentric: true,
                            exclude: true,
                            items: items
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(' +
                                'ym:s:operatingSystem !.(\'windows xp\', \'linux debian\')' +
                                ')'
                        )).to.deep.equal([{
                            id: 'ym:s:operatingSystemRoot-usercentric',
                            userCentric: true,
                            exclude: true,
                            items: items
                        }]);
                    });
                    it('should work with user-centric dates', function () {
                        var items;
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(' +
                                'ym:s:operatingSystemRoot NOT IN(\'windows\', \'linux\') and' +
                                ' ym:s:specialDefaultDate>=\'2015-04-05\' and ym:s:specialDefaultDate<=\'2015-05-07\'' +
                                ')'
                        )).to.deep.equal([{
                            id: 'ym:s:operatingSystemRoot-usercentric',
                            userCentric: true,
                            exclude: true,
                            items: [[{id: 'windows'}], [{id: 'linux'}]],
                            date1: '2015-04-05',
                            date2: '2015-05-07'
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(' +
                                'ym:s:operatingSystemRoot !.(\'windows\', \'linux\') and' +
                                ' ym:s:specialDefaultDate>=\'2015-04-05\' and ym:s:specialDefaultDate<=\'2015-05-07\'' +
                                ')'
                        )).to.deep.equal([{
                            id: 'ym:s:operatingSystemRoot-usercentric',
                            userCentric: true,
                            exclude: true,
                            items: [[{id: 'windows'}], [{id: 'linux'}]],
                            date1: '2015-04-05',
                            date2: '2015-05-07'
                        }]);
                        items = [[], []];
                        items[0][1] = {id: 'windows xp'};
                        items[1][1] = {id: 'linux debian'};
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(' +
                                'ym:s:operatingSystem NOT IN(\'windows xp\', \'linux debian\') and' +
                                ' ym:s:specialDefaultDate>=\'2015-04-05\' and ym:s:specialDefaultDate<=\'2015-05-07\'' +
                                ')'
                        )).to.deep.equal([{
                            id: 'ym:s:operatingSystemRoot-usercentric',
                            userCentric: true,
                            exclude: true,
                            items: items,
                            date1: '2015-04-05',
                            date2: '2015-05-07'
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(' +
                                'ym:s:operatingSystem !.(\'windows xp\', \'linux debian\') and' +
                                ' ym:s:specialDefaultDate>=\'2015-04-05\' and ym:s:specialDefaultDate<=\'2015-05-07\'' +
                                ')'
                        )).to.deep.equal([{
                            id: 'ym:s:operatingSystemRoot-usercentric',
                            userCentric: true,
                            exclude: true,
                            items: items,
                            date1: '2015-04-05',
                            date2: '2015-05-07'
                        }]);

                    });
                });
            });
            describe('multi level', function () {
                describe('include mode', function () {
                    it('should work without user-centric dates', function () {
                        var items = [[], [], [], []];
                        items[0][0] = {id: 'windows'};
                        items[1][0] = {id: 'linux'};
                        items[2][1] = {id: 'windows xp'};
                        items[3][1] = {id: 'linux debian'};

                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(' +
                                'ym:s:operatingSystemRoot IN(\'windows\', \'linux\') or' +
                                ' ym:s:operatingSystem IN(\'windows xp\', \'linux debian\')' +
                                ')'
                        )).to.deep.equal([{
                            id: 'ym:s:operatingSystemRoot-usercentric',
                            exclude: false,
                            userCentric: true,
                            items: items
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(' +
                                'ym:s:operatingSystemRoot =.(\'windows\', \'linux\') or' +
                                ' ym:s:operatingSystem =.(\'windows xp\', \'linux debian\')' +
                                ')'
                        )).to.deep.equal([{
                            id: 'ym:s:operatingSystemRoot-usercentric',
                            exclude: false,
                            userCentric: true,
                            items: items
                        }]);

                    });
                    it('should work with user-centric dates', function () {
                        var items = [[], [], [], []];
                        items[0][0] = {id: 'windows'};
                        items[1][0] = {id: 'linux'};
                        items[2][1] = {id: 'windows xp'};
                        items[3][1] = {id: 'linux debian'};

                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(' +
                                '(ym:s:operatingSystemRoot IN(\'windows\', \'linux\') or' +
                                ' ym:s:operatingSystem IN(\'windows xp\', \'linux debian\')) and' +
                                ' ym:s:specialDefaultDate>=\'2015-04-05\' and ym:s:specialDefaultDate<=\'2015-05-07\'' +
                                ')'
                        )).to.deep.equal([{
                            id: 'ym:s:operatingSystemRoot-usercentric',
                            exclude: false,
                            userCentric: true,
                            items: items,
                            date1: '2015-04-05',
                            date2: '2015-05-07'
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(' +
                                '(ym:s:operatingSystemRoot =.(\'windows\', \'linux\') or' +
                                ' ym:s:operatingSystem =.(\'windows xp\', \'linux debian\')) and' +
                                ' ym:s:specialDefaultDate>=\'2015-04-05\' and ym:s:specialDefaultDate<=\'2015-05-07\'' +
                                ')'
                        )).to.deep.equal([{
                            id: 'ym:s:operatingSystemRoot-usercentric',
                            exclude: false,
                            userCentric: true,
                            items: items,
                            date1: '2015-04-05',
                            date2: '2015-05-07'
                        }]);

                    });
                });
                describe('exclude mode', function () {
                    it('should work without user-centric dates', function () {
                        var items = [[], [], [], []];
                        items[0][0] = {id: 'windows'};
                        items[1][0] = {id: 'linux'};
                        items[2][1] = {id: 'windows xp'};
                        items[3][1] = {id: 'linux debian'};

                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(' +
                                'ym:s:operatingSystemRoot NOT IN(\'windows\', \'linux\') and' +
                                ' ym:s:operatingSystem NOT IN(\'windows xp\', \'linux debian\')' +
                                ')'
                        )).to.deep.equal([{
                            id: 'ym:s:operatingSystemRoot-usercentric',
                            exclude: true,
                            userCentric: true,
                            items: items
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(' +
                                'ym:s:operatingSystemRoot !.(\'windows\', \'linux\') and' +
                                ' ym:s:operatingSystem !.(\'windows xp\', \'linux debian\')' +
                                ')'
                        )).to.deep.equal([{
                            id: 'ym:s:operatingSystemRoot-usercentric',
                            exclude: true,
                            userCentric: true,
                            items: items
                        }]);
                    });
                    it('should work with user-centric dates', function () {
                        var items = [[], [], [], []];
                        items[0][0] = {id: 'windows'};
                        items[1][0] = {id: 'linux'};
                        items[2][1] = {id: 'windows xp'};
                        items[3][1] = {id: 'linux debian'};

                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(' +
                                '(ym:s:operatingSystemRoot NOT IN(\'windows\', \'linux\') and ' +
                                ' ym:s:operatingSystem NOT IN(\'windows xp\', \'linux debian\')) and' +
                                ' ym:s:specialDefaultDate>=\'2015-04-05\' and ym:s:specialDefaultDate<=\'2015-05-07\'' +
                                ')'
                        )).to.deep.equal([{
                            id: 'ym:s:operatingSystemRoot-usercentric',
                            exclude: true,
                            userCentric: true,
                            items: items,
                            date1: '2015-04-05',
                            date2: '2015-05-07'
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(' +
                                '(ym:s:operatingSystemRoot !.(\'windows\', \'linux\') and ' +
                                ' ym:s:operatingSystem !.(\'windows xp\', \'linux debian\')) and' +
                                ' ym:s:specialDefaultDate>=\'2015-04-05\' and ym:s:specialDefaultDate<=\'2015-05-07\'' +
                                ')'
                        )).to.deep.equal([{
                            id: 'ym:s:operatingSystemRoot-usercentric',
                            exclude: true,
                            userCentric: true,
                            items: items,
                            date1: '2015-04-05',
                            date2: '2015-05-07'
                        }]);

                    });
                });
            });
        });
    });

    describe('path segment', function () {
        describe('include mode', function () {
            describe('one dimension expression', function () {
                it('shold work with regular value', function () {
                    expect(parse('ym:s:regionCountry==1')).to.deep.equal([{
                        id: 'ym:s:regionCountry',
                        exclude: false,
                        userCentric: false,
                        items: [[{id: 1}]]
                    }]);
                });
                it('shold work with null value', function () {
                    expect(parse('ym:s:regionCountry=n')).to.deep.equal([{
                        id: 'ym:s:regionCountry',
                        exclude: false,
                        userCentric: false,
                        items: [[{id: null}]]
                    }]);
                });
                it('should work with two and more values', function () {
                    expect(parse('ym:s:regionCountry==1 or ym:s:regionCountry=n')).to.deep.equal([{
                        id: 'ym:s:regionCountry',
                        exclude: false,
                        userCentric: false,
                        items: [[{id: 1}], [{id: null}]]
                    }]);
                });
            });
            describe('multi dimension expression', function () {
                it('should work with one multidimension expression', function () {
                    expect(parse(
                        'ym:s:regionCountry==2 and ym:s:regionArea==5'
                    )).to.deep.equal([{
                        id: 'ym:s:regionCountry',
                        exclude: false,
                        userCentric: false,
                        items: [[{id: 2}, {id: 5}]]
                    }]);
                });
                it('should work with one or many', function () {
                    expect(parse(
                        'ym:s:regionCountry==1 or ym:s:regionCountry==2 and ym:s:regionArea==5'
                    )).to.deep.equal([{
                        id: 'ym:s:regionCountry',
                        exclude: false,
                        userCentric: false,
                        items: [[{id: 1}], [{id: 2}, {id: 5}]]
                    }]);
                });
                it('should work with many or one', function () {
                    expect(parse(
                        'ym:s:regionCountry==1 and ym:s:regionArea==7 or ym:s:regionCountry==2'
                    )).to.deep.equal([{
                        id: 'ym:s:regionCountry',
                        exclude: false,
                        userCentric: false,
                        items: [[{id: 1}, {id: 7}], [{id: 2}]]
                    }]);
                });
                it('should work with many or many', function () {
                    expect(parse(
                        'ym:s:regionCountry==1 and ym:s:regionArea==7 or ym:s:regionCountry==2 and ym:s:regionArea==5 '
                    )).to.deep.equal([{
                        id: 'ym:s:regionCountry',
                        exclude: false,
                        userCentric: false,
                        items: [[{id: 1}, {id: 7}], [{id: 2}, {id: 5}]]
                    }]);
                });
            });
        });
        describe('exclude mode', function () {
            describe('one dimension expression', function () {
                it('shold work with regular value', function () {
                    expect(parse('ym:s:regionCountry!=1')).to.deep.equal([{
                        id: 'ym:s:regionCountry',
                        exclude: true,
                        userCentric: false,
                        items: [[{id: 1}]]
                    }]);
                });
                it('shold work with null value', function () {
                    expect(parse('ym:s:regionCountry!n')).to.deep.equal([{
                        id: 'ym:s:regionCountry',
                        exclude: true,
                        userCentric: false,
                        items: [[{id: null}]]
                    }]);
                });
                it('should work with two and more values', function () {
                    expect(parse('ym:s:regionCountry!=1 and ym:s:regionCountry!n')).to.deep.equal([{
                        id: 'ym:s:regionCountry',
                        exclude: true,
                        userCentric: false,
                        items: [[{id: 1}], [{id: null}]]
                    }]);
                });
            });
            describe('multi dimension expression', function () {
                it('should work with one multidimension expression', function () {
                    expect(parse(
                        'ym:s:regionCountry!=2 or ym:s:regionArea!=5'
                    )).to.deep.equal([{
                        id: 'ym:s:regionCountry',
                        exclude: true,
                        userCentric: false,
                        items: [[{id: 2}, {id: 5}]]
                    }]);
                });
                it('should work with one or many', function () {
                    expect(parse(
                        '(ym:s:regionCountry!=1 and (ym:s:regionCountry!=2 or ym:s:regionArea!=5))'
                    )).to.deep.equal([{
                        id: 'ym:s:regionCountry',
                        exclude: true,
                        userCentric: false,
                        items: [[{id: 1}], [{id: 2}, {id: 5}]]
                    }]);
                });
                it('should work with many or one', function () {
                    expect(parse(
                        '((ym:s:regionCountry!=1 or ym:s:regionArea!=7) and (ym:s:regionCountry!=2))'
                    )).to.deep.equal([{
                        id: 'ym:s:regionCountry',
                        exclude: true,
                        userCentric: false,
                        items: [[{id: 1}, {id: 7}], [{id: 2}]]
                    }]);
                });
                it('should work with many or many', function () {
                    expect(parse(
                        '((ym:s:regionCountry!=1 or ym:s:regionArea!=7) and' +
                            ' (ym:s:regionCountry!=2 or ym:s:regionArea!=5))'
                    )).to.deep.equal([{
                        id: 'ym:s:regionCountry',
                        exclude: true,
                        userCentric: false,
                        items: [[{id: 1}, {id: 7}], [{id: 2}, {id: 5}]]
                    }]);
                });
            });
        });
        describe('user-centric mode', function () {
            describe('include mode', function () {
                describe('one dimension expression', function () {
                    it('should work without user-centric dates', function () {
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(ym:s:regionCountry==1 or ym:s:regionCountry=n)'
                        )).to.deep.equal([{
                            id: 'ym:s:regionCountry-usercentric',
                            userCentric: true,
                            exclude: false,
                            items: [[{id: 1}], [{id: null}]]
                        }]);
                    });
                    it('should work with user-centric dates', function () {
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH((ym:s:regionCountry==1 or ym:s:regionCountry=n) and' +
                                ' ym:s:specialDefaultDate>=\'2014-12-14\' and' +
                                ' ym:s:specialDefaultDate <= \'2016-01-01\')'
                        )).to.deep.equal([{
                            id: 'ym:s:regionCountry-usercentric',
                            userCentric: true,
                            exclude: false,
                            items: [[{id: 1}], [{id: null}]],
                            date1: '2014-12-14',
                            date2: '2016-01-01'
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH((ym:s:regionCountry==1 or ym:s:regionCountry=n) and' +
                                ' (ym:s:specialDefaultDate>=\'2014-12-14\' and' +
                                ' ym:s:specialDefaultDate <= \'2016-01-01\'))'
                        )).to.deep.equal([{
                            id: 'ym:s:regionCountry-usercentric',
                            userCentric: true,
                            exclude: false,
                            items: [[{id: 1}], [{id: null}]],
                            date1: '2014-12-14',
                            date2: '2016-01-01'
                        }]);
                    });
                });
                describe('multi dimension expression', function () {
                    describe('without dates', function () {
                        it('should work with one multidimension expression', function () {
                            expect(parse(
                                'EXISTS ym:s:specialUser WITH(ym:s:regionCountry==2 and ym:s:regionArea==5)'
                            )).to.deep.equal([{
                                id: 'ym:s:regionCountry-usercentric',
                                userCentric: true,
                                exclude: false,
                                items: [[{id: 2}, {id: 5}]]
                            }]);
                        });
                        it('should work with one or many', function () {
                            expect(parse(
                                'EXISTS ym:s:specialUser WITH(' +
                                    'ym:s:regionCountry==1 or ym:s:regionCountry==2 and ym:s:regionArea==5' +
                                    ')'
                            )).to.deep.equal([{
                                id: 'ym:s:regionCountry-usercentric',
                                exclude: false,
                                userCentric: true,
                                items: [[{id: 1}], [{id: 2}, {id: 5}]]
                            }]);
                        });
                        it('should work with many or one', function () {
                            expect(parse(
                                'EXISTS ym:s:specialUser WITH(' +
                                    'ym:s:regionCountry==1 and ym:s:regionArea==7 or ym:s:regionCountry==2' +
                                    ')'
                            )).to.deep.equal([{
                                id: 'ym:s:regionCountry-usercentric',
                                exclude: false,
                                userCentric: true,
                                items: [[{id: 1}, {id: 7}], [{id: 2}]]
                            }]);
                        });
                        it('should work with many or many', function () {
                            expect(parse(
                                'EXISTS ym:s:specialUser WITH(' +
                                    'ym:s:regionCountry==1 and ym:s:regionArea==7 or' +
                                    'ym:s:regionCountry==2 and ym:s:regionArea==5 ' +
                                    ')'
                            )).to.deep.equal([{
                                id: 'ym:s:regionCountry-usercentric',
                                exclude: false,
                                userCentric: true,
                                items: [[{id: 1}, {id: 7}], [{id: 2}, {id: 5}]]
                            }]);
                        });
                    });
                    describe('with dates', function () {
                        it('should work with one multidimension expression', function () {
                            expect(parse(
                                'EXISTS ym:s:specialUser WITH(' +
                                    'ym:s:regionCountry==2 and ym:s:regionArea==5 and' +
                                    ' ym:s:specialDefaultDate >= \'2012-12-12\' and' +
                                    ' ym:s:specialDefaultDate <= \'2012-12-15\'' +
                                    ')'
                            )).to.deep.equal([{
                                id: 'ym:s:regionCountry-usercentric',
                                userCentric: true,
                                exclude: false,
                                items: [[{id: 2}, {id: 5}]],
                                date1: '2012-12-12',
                                date2: '2012-12-15'
                            }]);
                        });
                        it('should work with one or many', function () {
                            expect(parse(
                                'EXISTS ym:s:specialUser WITH(' +
                                    '(ym:s:regionCountry==1 or ym:s:regionCountry==2 and ym:s:regionArea==5) and' +
                                    ' ym:s:specialDefaultDate >= \'2012-12-12\' and' +
                                    ' ym:s:specialDefaultDate <= \'2012-12-15\'' +
                                    ')'
                            )).to.deep.equal([{
                                id: 'ym:s:regionCountry-usercentric',
                                exclude: false,
                                userCentric: true,
                                items: [[{id: 1}], [{id: 2}, {id: 5}]],
                                date1: '2012-12-12',
                                date2: '2012-12-15'
                            }]);
                        });
                        it('should work with many or one', function () {
                            expect(parse(
                                'EXISTS ym:s:specialUser WITH(' +
                                    '(ym:s:regionCountry==1 and ym:s:regionArea==7 or ym:s:regionCountry==2) and' +
                                    ' ym:s:specialDefaultDate >= \'2012-12-12\' and' +
                                    ' ym:s:specialDefaultDate <= \'2012-12-15\'' +
                                    ')'
                            )).to.deep.equal([{
                                id: 'ym:s:regionCountry-usercentric',
                                exclude: false,
                                userCentric: true,
                                items: [[{id: 1}, {id: 7}], [{id: 2}]],
                                date1: '2012-12-12',
                                date2: '2012-12-15'
                            }]);
                        });
                        it('should work with many or many', function () {
                            expect(parse(
                                'EXISTS ym:s:specialUser WITH(' +
                                    '(ym:s:regionCountry==1 and ym:s:regionArea==7 or' +
                                    ' ym:s:regionCountry==2 and ym:s:regionArea==5) and ' +
                                    ' ym:s:specialDefaultDate >= \'2012-12-12\' and' +
                                    ' ym:s:specialDefaultDate <= \'2012-12-15\'' +
                                    ')'
                            )).to.deep.equal([{
                                id: 'ym:s:regionCountry-usercentric',
                                exclude: false,
                                userCentric: true,
                                items: [[{id: 1}, {id: 7}], [{id: 2}, {id: 5}]],
                                date1: '2012-12-12',
                                date2: '2012-12-15'
                            }]);
                        });
                    });
                });
            });
            describe('exclude mode', function () {
                describe('one dimension expression', function () {
                    it('should work without user-centric dates', function () {
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(ym:s:regionCountry!=1 and ym:s:regionCountry!n)'
                        )).to.deep.equal([{
                            id: 'ym:s:regionCountry-usercentric',
                            userCentric: true,
                            exclude: true,
                            items: [[{id: 1}], [{id: null}]]
                        }]);
                    });
                    it('should work with user-centric dates', function () {
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH((ym:s:regionCountry!=1 and ym:s:regionCountry!n) and' +
                                ' ym:s:specialDefaultDate>=\'2014-12-14\' and' +
                                ' ym:s:specialDefaultDate <= \'2016-01-01\')'
                        )).to.deep.equal([{
                            id: 'ym:s:regionCountry-usercentric',
                            userCentric: true,
                            exclude: true,
                            items: [[{id: 1}], [{id: null}]],
                            date1: '2014-12-14',
                            date2: '2016-01-01'
                        }]);
                        expect(parse(
                            'EXISTS ym:s:specialUser WITH(ym:s:regionCountry!=1 and ym:s:regionCountry!n and' +
                                ' ym:s:specialDefaultDate>=\'2014-12-14\' and' +
                                ' ym:s:specialDefaultDate <= \'2016-01-01\')'
                        )).to.deep.equal([{
                            id: 'ym:s:regionCountry-usercentric',
                            userCentric: true,
                            exclude: true,
                            items: [[{id: 1}], [{id: null}]],
                            date1: '2014-12-14',
                            date2: '2016-01-01'
                        }]);
                    });
                });
                describe('multi dimension expression', function () {
                    describe('without dates', function () {
                        it('should work with one multidimension expression', function () {
                            expect(parse(
                                'EXISTS ym:s:specialUser WITH(ym:s:regionCountry!=2 or ym:s:regionArea!=5)'
                            )).to.deep.equal([{
                                id: 'ym:s:regionCountry-usercentric',
                                userCentric: true,
                                exclude: true,
                                items: [[{id: 2}, {id: 5}]]
                            }]);
                        });
                        it('should work with one or many', function () {
                            expect(parse(
                                'EXISTS ym:s:specialUser WITH(' +
                                    'ym:s:regionCountry!=1 and (ym:s:regionCountry!=2 or ym:s:regionArea!=5)' +
                                    ')'
                            )).to.deep.equal([{
                                id: 'ym:s:regionCountry-usercentric',
                                exclude: true,
                                userCentric: true,
                                items: [[{id: 1}], [{id: 2}, {id: 5}]]
                            }]);
                        });
                        it('should work with many or one', function () {
                            expect(parse(
                                'EXISTS ym:s:specialUser WITH(' +
                                    '(ym:s:regionCountry!=1 or ym:s:regionArea!=7) and ym:s:regionCountry!=2' +
                                    ')'
                            )).to.deep.equal([{
                                id: 'ym:s:regionCountry-usercentric',
                                exclude: true,
                                userCentric: true,
                                items: [[{id: 1}, {id: 7}], [{id: 2}]]
                            }]);
                        });
                        it('should work with many or many', function () {
                            expect(parse(
                                'EXISTS ym:s:specialUser WITH(' +
                                    '(ym:s:regionCountry!=1 or ym:s:regionArea!=7) and' +
                                    ' (ym:s:regionCountry!=2 or ym:s:regionArea!=5)' +
                                    ')'
                            )).to.deep.equal([{
                                id: 'ym:s:regionCountry-usercentric',
                                exclude: true,
                                userCentric: true,
                                items: [[{id: 1}, {id: 7}], [{id: 2}, {id: 5}]]
                            }]);
                        });
                    });
                    describe('with dates', function () {
                        it('should work with one multidimension expression', function () {
                            expect(parse(
                                'EXISTS ym:s:specialUser WITH(' +
                                    '(ym:s:regionCountry!=2 or ym:s:regionArea!=5) and' +
                                    ' ym:s:specialDefaultDate >= \'2012-12-12\' and' +
                                    ' ym:s:specialDefaultDate <= \'2012-12-15\'' +
                                    ')'
                            )).to.deep.equal([{
                                id: 'ym:s:regionCountry-usercentric',
                                userCentric: true,
                                exclude: true,
                                items: [[{id: 2}, {id: 5}]],
                                date1: '2012-12-12',
                                date2: '2012-12-15'
                            }]);
                        });
                        it('should work with one or many', function () {
                            expect(parse(
                                'EXISTS ym:s:specialUser WITH(' +
                                    '((ym:s:regionCountry!=1) and (ym:s:regionCountry!=2 or ym:s:regionArea!=5)) and' +
                                    ' ym:s:specialDefaultDate >= \'2012-12-12\' and' +
                                    ' ym:s:specialDefaultDate <= \'2012-12-15\'' +
                                    ')'
                            )).to.deep.equal([{
                                id: 'ym:s:regionCountry-usercentric',
                                exclude: true,
                                userCentric: true,
                                items: [[{id: 1}], [{id: 2}, {id: 5}]],
                                date1: '2012-12-12',
                                date2: '2012-12-15'
                            }]);
                        });
                        it('should work with many or one', function () {
                            expect(parse(
                                'EXISTS ym:s:specialUser WITH(' +
                                    '((ym:s:regionCountry!=1 or ym:s:regionArea!=7) and (ym:s:regionCountry!=2)) and' +
                                    ' ym:s:specialDefaultDate >= \'2012-12-12\' and' +
                                    ' ym:s:specialDefaultDate <= \'2012-12-15\'' +
                                    ')'
                            )).to.deep.equal([{
                                id: 'ym:s:regionCountry-usercentric',
                                exclude: true,
                                userCentric: true,
                                items: [[{id: 1}, {id: 7}], [{id: 2}]],
                                date1: '2012-12-12',
                                date2: '2012-12-15'
                            }]);
                        });
                        it('should work with many or many', function () {
                            expect(parse(
                                'EXISTS ym:s:specialUser WITH(' +
                                    '((ym:s:regionCountry!=1 or ym:s:regionArea!=7) and ' +
                                    ' (ym:s:regionCountry!=2 or ym:s:regionArea!=5)) and ' +
                                    ' ym:s:specialDefaultDate >= \'2012-12-12\' and' +
                                    ' ym:s:specialDefaultDate <= \'2012-12-15\'' +
                                    ')'
                            )).to.deep.equal([{
                                id: 'ym:s:regionCountry-usercentric',
                                exclude: true,
                                userCentric: true,
                                items: [[{id: 1}, {id: 7}], [{id: 2}, {id: 5}]],
                                date1: '2012-12-12',
                                date2: '2012-12-15'
                            }]);
                        });
                    });
                });
            });
        });
    });
});
