import { State } from 'client/store/state';

import { getParser } from '../parser';
import { transform } from '../transformer';
import { transformTree } from '../tree/transformer';

import { counter } from './fixtures/counter';
import { tree } from './fixtures/segments';

const parser = getParser();
const state: Partial<State> = {
    counter: counter as any,
    segmentationTree: [],
};

state.segmentationTree = transformTree(state as State, tree);

const parse = (s: string) => {
    const ast = parser.parse(s);

    return transform(ast, state as State);
};

it('should handle empty strings', function () {
    expect(parse('')).toEqual([]);
});

describe('boolean segment', function () {
    it('should handle Yes', function () {
        expect(parse("ym:s:isNewUser=='Yes'")).toMatchSnapshot();
    });
    it('should handle No', function () {
        expect(parse("ym:s:isNewUser=='No'")).toMatchSnapshot();
    });
    describe('user-centric mode', function () {
        it('should work without dates', function () {
            expect(
                parse("EXISTS ym:s:specialUser WITH (ym:s:hasGCLID=='Yes')"),
            ).toMatchSnapshot();
            expect(
                parse("EXISTS ym:s:specialUser WITH (ym:s:hasGCLID=='No')"),
            ).toMatchSnapshot();
        });
        it('should work with one date', function () {
            expect(
                parse(
                    "EXISTS ym:s:specialUser WITH (ym:s:hasGCLID=='Yes' and" +
                        " ym:s:specialDefaultDate=='2015-12-15')",
                ),
            ).toMatchSnapshot();
        });
        it('should work with two dates', function () {
            expect(
                parse(
                    "EXISTS ym:s:specialUser WITH (ym:s:hasGCLID=='No' and" +
                        " ym:s:specialDefaultDate>='2015-12-12' and ym:s:specialDefaultDate<='2016-12-12')",
                ),
            ).toMatchSnapshot();
        });
    });
});

describe('uid segment', function () {
    it('should parse uid segments', function () {
        expect(parse('ym:s:userIDHash==123456')).toMatchSnapshot();
    });
    // there are no user-centric segments for uid -- no tests
});

describe('goal segment', function () {
    describe('single expression', function () {
        it('should parse goal reached segment', function () {
            expect(parse("ym:s:goal123456IsReached=='Yes'")).toMatchSnapshot();
        });
        it('should parse goal not reached segment', function () {
            expect(parse("ym:s:goal123456IsReached=='No'")).toMatchSnapshot();
        });
    });
    describe('complex expression', function () {
        it('should parse goal reached segment', function () {
            expect(
                parse(
                    "ym:s:goal123456IsReached=='No' and ym:s:goal98765IsReached=='No'",
                ),
            ).toMatchSnapshot();
        });
    });
    // there are no user-centric segments for uid -- no tests
});

describe('number segment', function () {
    it('should parse == expression', function () {
        expect(parse('ym:s:pageViews==5')).toMatchSnapshot();
    });
    it('should parse > expression', function () {
        expect(parse('ym:s:pageViews>5')).toMatchSnapshot();
    });
    it('should parse < expression', function () {
        expect(parse('ym:s:pageViews<5')).toMatchSnapshot();
    });
    it('should parse between', function () {
        expect(
            parse('ym:s:pageViews>=5 and ym:s:pageViews<=10'),
        ).toMatchSnapshot();
        expect(
            parse('ym:s:pageViews<=7 and ym:s:pageViews>=3'),
        ).toMatchSnapshot();
    });
    it('should parse with currency', function () {
        const segmentString = 'ym:u:userCNYRevenue==2';
        expect(parse(segmentString)).toMatchSnapshot();
    });
    describe('user-centric mode', function () {
        it('should work without dates', function () {
            expect(
                parse(
                    'EXISTS ym:u:specialUser WITH (ym:u:daysSinceFirstVisitOneBased==5)',
                ),
            ).toMatchSnapshot();
            expect(
                parse(
                    'EXISTS ym:u:specialUser WITH ((ym:u:daysSinceFirstVisitOneBased>5))',
                ),
            ).toMatchSnapshot();
            expect(
                parse(
                    'EXISTS ym:u:specialUser WITH' +
                        ' ((ym:u:daysSinceFirstVisitOneBased>=5 and ym:u:daysSinceFirstVisitOneBased<=7))',
                ),
            ).toMatchSnapshot();
        });
        it('should work with one date', function () {
            expect(
                parse(
                    'EXISTS ym:u:specialUser WITH (ym:u:daysSinceFirstVisitOneBased==5 and' +
                        " ym:u:specialDefaultDate=='2012-3-5')",
                ),
            ).toMatchSnapshot();
            expect(
                parse(
                    'EXISTS ym:u:specialUser WITH' +
                        ' (ym:u:daysSinceFirstVisitOneBased>=5 and ym:u:daysSinceFirstVisitOneBased<=10 and' +
                        " ym:u:specialDefaultDate=='2012-3-5')",
                ),
            ).toMatchSnapshot();
        });
        it('should work with two dates', function () {
            expect(
                parse(
                    'EXISTS ym:u:specialUser WITH (ym:u:daysSinceFirstVisitOneBased==5 and' +
                        " ym:u:specialDefaultDate>='2012-3-5' and ym:u:specialDefaultDate<='2015-01-05')",
                ),
            ).toMatchSnapshot();
            expect(
                parse(
                    'EXISTS ym:u:specialUser WITH' +
                        ' (ym:u:daysSinceFirstVisitOneBased>=5 and ym:u:daysSinceFirstVisitOneBased<=10 and' +
                        " ym:u:specialDefaultDate>='2012-3-5' and ym:u:specialDefaultDate<='2015-01-05')",
                ),
            ).toMatchSnapshot();
        });
    });
});

describe('date segment', function () {
    it('should parse == expression', function () {
        expect(parse("ym:s:previousVisitDate=='2016-01-01'")).toMatchSnapshot();
    });
    it('should parse > expression', function () {
        expect(parse("ym:s:previousVisitDate>'2016-02-02'")).toMatchSnapshot();
    });
    it('should parse < expression', function () {
        expect(parse("ym:s:previousVisitDate<'2016-03-04'")).toMatchSnapshot();
    });
    it('should parse between', function () {
        expect(
            parse(
                "ym:s:previousVisitDate>='2015-12-01' and ym:s:previousVisitDate<='2016-03-05'",
            ),
        ).toMatchSnapshot();
        expect(
            parse(
                "ym:s:previousVisitDate<='2014-05-06' and ym:s:previousVisitDate>='2013-12-12'",
            ),
        ).toMatchSnapshot();
    });
    // date segment is almost the same as number segment -- no tests for user-centric
});

describe('multiline segment', function () {
    describe('one line', function () {
        it('should parse == expression', function () {
            expect(parse("ym:s:searchPhrase=='phrase1'")).toMatchSnapshot();
        });
        it('should parse @ expression', function () {
            expect(parse("ym:s:searchPhrase=@'phrase1'")).toMatchSnapshot();
        });
        it('should parse !@ expression', function () {
            expect(parse("ym:s:searchPhrase!@'phrase1'")).toMatchSnapshot();
        });
        it('should parse ~ expression', function () {
            expect(parse("ym:s:searchPhrase=~'phrase1'")).toMatchSnapshot();
        });
        it('should parse !~ expression', function () {
            expect(parse("ym:s:searchPhrase!~'phrase1'")).toMatchSnapshot();
        });
    });
    describe('multiple lines', function () {
        describe('with conjunction', function () {
            it('should work with two subexpressions', function () {
                expect(
                    parse(
                        "ym:s:searchPhrase=='phrase1' and ym:s:searchPhrase=='phrase2'",
                    ),
                ).toMatchSnapshot();
            });
            it('should work with three subexpressions', function () {
                expect(
                    parse(
                        "ym:s:searchPhrase=='phrase1' and ym:s:searchPhrase=@'phrase2' and" +
                            " ym:s:searchPhrase=~'phrase3'",
                    ),
                ).toMatchSnapshot();
            });
        });
        describe('with disjunction', function () {
            it('should work with two subexpressions', function () {
                expect(
                    parse(
                        "ym:s:searchPhrase=='phrase1' or ym:s:searchPhrase=='phrase2'",
                    ),
                ).toMatchSnapshot();
            });
            it('should work with three subexpressions', function () {
                expect(
                    parse(
                        "ym:s:searchPhrase=='phrase1' or ym:s:searchPhrase=@'phrase2' or" +
                            " ym:s:searchPhrase=~'phrase3'",
                    ),
                ).toMatchSnapshot();
            });
        });
    });
    describe('user-centric mode', function () {
        describe('one line expression', function () {
            it('should work without dates', function () {
                expect(
                    parse(
                        "EXISTS ym:u:userID WITH (ym:u:firstSearchPhrase=='qwerty')",
                    ),
                ).toMatchSnapshot();
            });
            it('should work with one date', function () {
                expect(
                    parse(
                        "EXISTS ym:u:userID WITH (ym:u:firstSearchPhrase=='qwerty' and" +
                            " ym:u:specialDefaultDate=='2016-12-11')",
                    ),
                ).toMatchSnapshot();
            });
            it('should work with two dates', function () {
                expect(
                    parse(
                        "EXISTS ym:u:userID WITH (ym:u:firstSearchPhrase=='qwerty' and" +
                            " ym:u:specialDefaultDate>='2016-03-05' and ym:u:specialDefaultDate<='2016-03-11')",
                    ),
                ).toMatchSnapshot();
            });
        });
        describe('many lines expression', function () {
            describe('conjunction mode', function () {
                it('should work without dates', function () {
                    expect(
                        parse(
                            'EXISTS ym:u:userID WITH (' +
                                [
                                    "ym:u:firstSearchPhrase=*'qwerty'",
                                    "ym:u:firstSearchPhrase!*'asdf'",
                                    "ym:u:firstSearchPhrase=@'qaz'",
                                    "ym:u:firstSearchPhrase=~'wsx'",
                                    "ym:u:firstSearchPhrase!@'edc'",
                                    "ym:u:firstSearchPhrase!~'rfv'",
                                ].join(' and ') +
                                ')',
                        ),
                    ).toMatchSnapshot();
                });
                it('should work with one date', function () {
                    expect(
                        parse(
                            'EXISTS ym:u:userID WITH (' +
                                [
                                    "ym:u:firstSearchPhrase=*'qwerty'",
                                    "ym:u:firstSearchPhrase!*'asdf'",
                                    "ym:u:firstSearchPhrase=@'qaz'",
                                    "ym:u:firstSearchPhrase=~'wsx'",
                                    "ym:u:firstSearchPhrase!@'edc'",
                                    "ym:u:firstSearchPhrase!~'rfv'",
                                ].join(' and ') +
                                " and ym:u:specialDefaultDate=='2011-08-08')",
                        ),
                    ).toMatchSnapshot();
                });
                it('should work with two dates', function () {
                    expect(
                        parse(
                            'EXISTS ym:u:userID WITH (' +
                                [
                                    "ym:u:firstSearchPhrase=*'qwerty'",
                                    "ym:u:firstSearchPhrase!*'asdf'",
                                    "ym:u:firstSearchPhrase=@'qaz'",
                                    "ym:u:firstSearchPhrase=~'wsx'",
                                    "ym:u:firstSearchPhrase!@'edc'",
                                    "ym:u:firstSearchPhrase!~'rfv'",
                                ].join(' and ') +
                                " and ym:u:specialDefaultDate>='2011-08-08' and" +
                                " ym:u:specialDefaultDate<='2012-11-11')",
                        ),
                    ).toMatchSnapshot();
                });
            });
            describe('disjunction mode', function () {
                it('should work without dates', function () {
                    expect(
                        parse(
                            'EXISTS ym:u:userID WITH (' +
                                [
                                    "ym:u:firstSearchPhrase=*'qwerty'",
                                    "ym:u:firstSearchPhrase!*'asdf'",
                                    "ym:u:firstSearchPhrase=@'qaz'",
                                    "ym:u:firstSearchPhrase=~'wsx'",
                                    "ym:u:firstSearchPhrase!@'edc'",
                                    "ym:u:firstSearchPhrase!~'rfv'",
                                ].join(' or ') +
                                ')',
                        ),
                    ).toMatchSnapshot();
                });
                it('should work with one date', function () {
                    expect(
                        parse(
                            'EXISTS ym:u:userID WITH ((' +
                                [
                                    "ym:u:firstSearchPhrase=*'qwerty'",
                                    "ym:u:firstSearchPhrase!*'asdf'",
                                    "ym:u:firstSearchPhrase=@'qaz'",
                                    "ym:u:firstSearchPhrase=~'wsx'",
                                    "ym:u:firstSearchPhrase!@'edc'",
                                    "ym:u:firstSearchPhrase!~'rfv'",
                                ].join(' or') +
                                ") and ym:u:specialDefaultDate=='2011-08-08')",
                        ),
                    ).toMatchSnapshot();
                });
                it('should work with two dates', function () {
                    expect(
                        parse(
                            'EXISTS ym:u:userID WITH ((' +
                                [
                                    "ym:u:firstSearchPhrase=*'qwerty'",
                                    "ym:u:firstSearchPhrase!*'asdf'",
                                    "ym:u:firstSearchPhrase=@'qaz'",
                                    "ym:u:firstSearchPhrase=~'wsx'",
                                    "ym:u:firstSearchPhrase!@'edc'",
                                    "ym:u:firstSearchPhrase!~'rfv'",
                                ].join(' or ') +
                                ") and ym:u:specialDefaultDate>='2011-08-08' and" +
                                " ym:u:specialDefaultDate<='2012-11-11')",
                        ),
                    ).toMatchSnapshot();
                });
            });
        });
    });
});

describe('url segment', function () {
    it('should correctly handle urlMode', function () {
        expect(parse("ym:pv:URL=='phrase1'")).toMatchSnapshot();
        expect(parse("ym:pv:URLDomain=='phrase1'")).toMatchSnapshot();
        expect(parse("ym:pv:URLPathFull=='phrase1'")).toMatchSnapshot();
    });
    // url segment is almost the same as multiline segment -- no tests for user-centric
});

describe('params segment', function () {
    describe('without quantifier', function () {
        it('should correctly handle noQuantifier flag for simple expression', function () {
            expect(parse("ym:s:paramsLevel1=='level1'")).toMatchSnapshot();
        });
        it('should correctly handle noQuantifier flag for complex expression', function () {
            expect(
                parse(
                    "ym:s:paramsLevel1=='level1' and ym:s:paramsLevel2=='level2'",
                ),
            ).toMatchSnapshot();
        });
    });
    describe('with quantifier', function () {
        it('should correctly handle noQuantifier flag for simple expression', function () {
            expect(
                parse("EXISTS(ym:s:paramsLevel1=='level1')"),
            ).toMatchSnapshot();
        });
        it('should correctly handle noQuantifier flag for complex expression', function () {
            expect(
                parse(
                    "EXISTS(ym:s:paramsLevel1=='level1' and ym:s:paramsLevel2=='level2')",
                ),
            ).toMatchSnapshot();
        });
    });
    it('should correctly parse simple expression', function () {
        expect(parse("ym:s:paramsLevel1=='level1'")).toMatchSnapshot();
    });
    it('should correctly parse complex expression', function () {
        expect(
            parse(
                "ym:s:paramsLevel1=='level1' and ym:s:paramsLevel2=='level2'",
            ),
        ).toMatchSnapshot();
    });
    it('should correctly parse long complex expression', function () {
        expect(
            parse(
                "ym:s:paramsLevel1=='level1' and ym:s:paramsLevel2=='level2' and ym:s:paramsLevel3=='level3'",
            ),
        ).toMatchSnapshot();
    });
    it('should correctly parse complex expression with double value', function () {
        expect(
            parse("ym:s:paramsLevel1=='level1' and ym:s:paramsValueDouble==5"),
        ).toMatchSnapshot();
    });
    it('should correctly parse value comparison operators', function () {
        expect(
            parse("ym:s:paramsLevel1=='level1' and ym:s:paramsValueDouble==5"),
        ).toMatchSnapshot();
        expect(
            parse("ym:s:paramsLevel1=='level1' and ym:s:paramsValueDouble>5"),
        ).toMatchSnapshot();
        expect(
            parse("ym:s:paramsLevel1=='level1' and ym:s:paramsValueDouble<5"),
        ).toMatchSnapshot();
    });
    describe('user-centric mode', function () {
        describe('without internal quantifier', function () {
            describe('without user-centric dates', function () {
                it('should correctly handle noQuantifier flag for simple expression', function () {
                    expect(
                        parse(
                            "EXISTS ym:s:specialUser WITH(ym:s:paramsLevel1=='level1')",
                        ),
                    ).toMatchSnapshot();
                });
                it('should correctly handle noQuantifier flag for complex expression', function () {
                    expect(
                        parse(
                            "EXISTS ym:s:specialUser WITH (ym:s:paramsLevel1=='level1' and" +
                                " ym:s:paramsLevel2=='level2')",
                        ),
                    ).toMatchSnapshot();
                });
            });
            describe('with one user-centric date', function () {
                it('should correctly handle noQuantifier flag for simple expression', function () {
                    expect(
                        parse(
                            "EXISTS ym:s:specialUser WITH(ym:s:paramsLevel1=='level1' and" +
                                " ym:s:specialDefaultDate=='2016-03-15')",
                        ),
                    ).toMatchSnapshot();
                });
                it('should correctly handle noQuantifier flag for complex expression', function () {
                    expect(
                        parse(
                            "EXISTS ym:s:specialUser WITH (ym:s:paramsLevel1=='level1' and" +
                                " ym:s:paramsLevel2=='level2' and " +
                                " ym:s:specialDefaultDate=='2016-03-15')",
                        ),
                    ).toMatchSnapshot();
                    expect(
                        parse(
                            "EXISTS ym:s:specialUser WITH ((ym:s:paramsLevel1=='level1' and" +
                                " ym:s:paramsLevel2=='level2') and " +
                                " ym:s:specialDefaultDate=='2016-03-15')",
                        ),
                    ).toMatchSnapshot();
                });
            });
            describe('with two user-centric dates', function () {
                it('should correctly handle noQuantifier flag for simple expression', function () {
                    expect(
                        parse(
                            "EXISTS ym:s:specialUser WITH(ym:s:paramsLevel1=='level1' and" +
                                " ym:s:specialDefaultDate>='2016-03-15' and ym:s:specialDefaultDate<='2016-03-17')",
                        ),
                    ).toMatchSnapshot();
                });
                it('should correctly handle noQuantifier flag for complex expression', function () {
                    expect(
                        parse(
                            "EXISTS ym:s:specialUser WITH (ym:s:paramsLevel1=='level1' and" +
                                " ym:s:paramsLevel2=='level2' and " +
                                " ym:s:specialDefaultDate>='2016-03-15' and ym:s:specialDefaultDate<='2016-03-17')",
                        ),
                    ).toMatchSnapshot();
                    expect(
                        parse(
                            "EXISTS ym:s:specialUser WITH ((ym:s:paramsLevel1=='level1' and" +
                                " ym:s:paramsLevel2=='level2') and " +
                                " ym:s:specialDefaultDate>='2016-03-15' and ym:s:specialDefaultDate<='2016-03-17')",
                        ),
                    ).toMatchSnapshot();
                });
            });
        });
        describe('with internal quantifier', function () {
            describe('without user-centric dates', function () {
                it('should correctly handle noQuantifier flag for simple expression', function () {
                    expect(
                        parse(
                            "EXISTS ym:s:specialUser WITH(EXISTS(ym:s:paramsLevel1=='level1'))",
                        ),
                    ).toMatchSnapshot();
                });
                it('should correctly handle noQuantifier flag for complex expression', function () {
                    expect(
                        parse(
                            "EXISTS ym:s:specialUser WITH (EXISTS(ym:s:paramsLevel1=='level1' and" +
                                " ym:s:paramsLevel2=='level2'))",
                        ),
                    ).toMatchSnapshot();
                });
            });
            describe('with one user-centric date', function () {
                it('should correctly handle noQuantifier flag for simple expression', function () {
                    expect(
                        parse(
                            "EXISTS ym:s:specialUser WITH(EXISTS(ym:s:paramsLevel1=='level1') and" +
                                " ym:s:specialDefaultDate=='2016-03-15')",
                        ),
                    ).toMatchSnapshot();
                });
                it('should correctly handle noQuantifier flag for complex expression', function () {
                    expect(
                        parse(
                            "EXISTS ym:s:specialUser WITH (EXISTS(ym:s:paramsLevel1=='level1' and" +
                                " ym:s:paramsLevel2=='level2') and " +
                                " ym:s:specialDefaultDate=='2016-03-15')",
                        ),
                    ).toMatchSnapshot();
                    expect(
                        parse(
                            "EXISTS ym:s:specialUser WITH ((EXISTS(ym:s:paramsLevel1=='level1' and" +
                                " ym:s:paramsLevel2=='level2')) and " +
                                " ym:s:specialDefaultDate=='2016-03-15')",
                        ),
                    ).toMatchSnapshot();
                });
            });
            describe('with two user-centric dates', function () {
                it('should correctly handle noQuantifier flag for simple expression', function () {
                    expect(
                        parse(
                            "EXISTS ym:s:specialUser WITH(EXISTS(ym:s:paramsLevel1=='level1') and" +
                                " ym:s:specialDefaultDate>='2016-03-15' and ym:s:specialDefaultDate<='2016-03-17')",
                        ),
                    ).toMatchSnapshot();
                });
                it('should correctly handle noQuantifier flag for complex expression', function () {
                    expect(
                        parse(
                            "EXISTS ym:s:specialUser WITH (EXISTS(ym:s:paramsLevel1=='level1' and" +
                                " ym:s:paramsLevel2=='level2') and " +
                                " ym:s:specialDefaultDate>='2016-03-15' and ym:s:specialDefaultDate<='2016-03-17')",
                        ),
                    ).toMatchSnapshot();
                    expect(
                        parse(
                            "EXISTS ym:s:specialUser WITH ((EXISTS(ym:s:paramsLevel1=='level1' and" +
                                " ym:s:paramsLevel2=='level2')) and " +
                                " ym:s:specialDefaultDate>='2016-03-15' and ym:s:specialDefaultDate<='2016-03-17')",
                        ),
                    ).toMatchSnapshot();
                });
            });
        });
        describe('for suggest', function () {
            it.skip('should handle user-centric dimension without EXISTS wrapper', function () {
                expect(
                    parse("(ym:up:paramsLevel1=@'level1')"),
                ).toMatchSnapshot();
            });
        });
    });
});

describe('list segment', function () {
    describe('simple expression', function () {
        it('should parse include expression with regular value', function () {
            expect(parse("ym:s:browserCountry=='ru'")).toMatchSnapshot();
        });
        it('should parse include expression with null value', function () {
            expect(parse('ym:s:browserCountry=n')).toMatchSnapshot();
        });
        it('should parse exclude expression with regular value', function () {
            expect(parse("ym:s:browserCountry!='ru'")).toMatchSnapshot();
        });
        it('should parse exclude with null value', function () {
            expect(parse('ym:s:browserCountry!n')).toMatchSnapshot();
        });
    });
    describe('complex expression', function () {
        it('should parse include expression', function () {
            expect(
                parse(
                    "ym:s:browserCountry=='ru' or ym:s:browserCountry=='us' or ym:s:browserCountry=n",
                ),
            ).toMatchSnapshot();
        });
        it('should parse exclude expression', function () {
            expect(
                parse(
                    "ym:s:browserCountry!='ru' and ym:s:browserCountry!='us' and ym:s:browserCountry!n",
                ),
            ).toMatchSnapshot();
        });
    });
    describe('user-centric mode', function () {
        describe('include mode', function () {
            describe('without dates', function () {
                it('should work with simple expression', function () {
                    expect(
                        parse(
                            'EXISTS ym:s:specialUser WITH(ym:s:regionCitySize==1)',
                        ),
                    ).toMatchSnapshot();
                });
                it('should work with complex expression', function () {
                    expect(
                        parse(
                            'EXISTS ym:s:specialUser WITH(ym:s:regionCitySize==1 or ym:s:regionCitySize==2)',
                        ),
                    ).toMatchSnapshot();
                });
            });
            describe('with one date', function () {
                it('should work with simple expression', function () {
                    expect(
                        parse(
                            'EXISTS ym:s:specialUser WITH(ym:s:regionCitySize==1 and' +
                                " ym:s:specialDefaultDate=='2012-06-05')",
                        ),
                    ).toMatchSnapshot();
                    expect(
                        parse(
                            'EXISTS ym:s:specialUser WITH((ym:s:regionCitySize==1) and' +
                                " ym:s:specialDefaultDate=='2012-06-05')",
                        ),
                    ).toMatchSnapshot();
                });
                it('should work with complex expression', function () {
                    expect(
                        parse(
                            'EXISTS ym:s:specialUser WITH((ym:s:regionCitySize==1 or ym:s:regionCitySize==5) and' +
                                " ym:s:specialDefaultDate=='2012-06-05')",
                        ),
                    ).toMatchSnapshot();
                    expect(
                        parse(
                            'EXISTS ym:s:specialUser WITH((ym:s:regionCitySize==1 or ym:s:regionCitySize==5) and' +
                                " (ym:s:specialDefaultDate=='2012-06-05'))",
                        ),
                    ).toMatchSnapshot();
                });
            });
            describe('with two dates', function () {
                it('should work with simple expression', function () {
                    expect(
                        parse(
                            'EXISTS ym:s:specialUser WITH(ym:s:regionCitySize==1 and' +
                                " ym:s:specialDefaultDate>='2012-06-05' and ym:s:specialDefaultDate<='2012-06-07')",
                        ),
                    ).toMatchSnapshot();
                    expect(
                        parse(
                            'EXISTS ym:s:specialUser WITH((ym:s:regionCitySize==1) and' +
                                " ym:s:specialDefaultDate>='2012-06-05' and ym:s:specialDefaultDate<='2012-06-07')",
                        ),
                    ).toMatchSnapshot();
                });
                it('should work with complex expression', function () {
                    expect(
                        parse(
                            'EXISTS ym:s:specialUser WITH((ym:s:regionCitySize==1 or ym:s:regionCitySize==5) and' +
                                " ym:s:specialDefaultDate>='2012-06-05' and" +
                                " ym:s:specialDefaultDate<='2012-06-07')",
                        ),
                    ).toMatchSnapshot();
                    expect(
                        parse(
                            'EXISTS ym:s:specialUser WITH((ym:s:regionCitySize==1 or ym:s:regionCitySize==5) and' +
                                " (ym:s:specialDefaultDate>='2012-06-05' and" +
                                " ym:s:specialDefaultDate<='2012-06-07'))",
                        ),
                    ).toMatchSnapshot();
                });
            });
        });
        describe('exclude mode', function () {
            describe('without dates', function () {
                it('should work with simple expression', function () {
                    expect(
                        parse(
                            'EXISTS ym:s:specialUser WITH(ym:s:regionCitySize!=1)',
                        ),
                    ).toMatchSnapshot();
                });
                it('should work with complex expression', function () {
                    expect(
                        parse(
                            'EXISTS ym:s:specialUser WITH(ym:s:regionCitySize!=1 and ym:s:regionCitySize!=2)',
                        ),
                    ).toMatchSnapshot();
                });
            });
            describe('with one date', function () {
                it('should work with simple expression', function () {
                    expect(
                        parse(
                            'EXISTS ym:s:specialUser WITH(ym:s:regionCitySize!=1 and' +
                                " ym:s:specialDefaultDate=='2012-06-05')",
                        ),
                    ).toMatchSnapshot();
                    expect(
                        parse(
                            'EXISTS ym:s:specialUser WITH((ym:s:regionCitySize!=1) and' +
                                " ym:s:specialDefaultDate=='2012-06-05')",
                        ),
                    ).toMatchSnapshot();
                });
                it('should work with complex expression', function () {
                    expect(
                        parse(
                            'EXISTS ym:s:specialUser WITH((ym:s:regionCitySize!=1 and ym:s:regionCitySize!=5) and' +
                                " ym:s:specialDefaultDate=='2012-06-05')",
                        ),
                    ).toMatchSnapshot();
                    expect(
                        parse(
                            'EXISTS ym:s:specialUser WITH((ym:s:regionCitySize!=1 and ym:s:regionCitySize!=5) and' +
                                " (ym:s:specialDefaultDate=='2012-06-05'))",
                        ),
                    ).toMatchSnapshot();
                });
            });
            describe('with two dates', function () {
                it('should work with simple expression', function () {
                    expect(
                        parse(
                            'EXISTS ym:s:specialUser WITH(ym:s:regionCitySize!=1 and' +
                                " ym:s:specialDefaultDate>='2012-06-05' and ym:s:specialDefaultDate<='2012-06-07')",
                        ),
                    ).toMatchSnapshot();
                    expect(
                        parse(
                            'EXISTS ym:s:specialUser WITH((ym:s:regionCitySize!=1) and' +
                                " ym:s:specialDefaultDate>='2012-06-05' and ym:s:specialDefaultDate<='2012-06-07')",
                        ),
                    ).toMatchSnapshot();
                });
                it('should work with complex expression', function () {
                    expect(
                        parse(
                            'EXISTS ym:s:specialUser WITH((ym:s:regionCitySize!=1 and ym:s:regionCitySize!=5) and' +
                                " ym:s:specialDefaultDate>='2012-06-05' and" +
                                " ym:s:specialDefaultDate<='2012-06-07')",
                        ),
                    ).toMatchSnapshot();
                    expect(
                        parse(
                            'EXISTS ym:s:specialUser WITH((ym:s:regionCitySize!=1 and ym:s:regionCitySize!=5) and' +
                                " (ym:s:specialDefaultDate>='2012-06-05' and" +
                                " ym:s:specialDefaultDate<='2012-06-07'))",
                        ),
                    ).toMatchSnapshot();
                });
            });
        });
    });
});

describe('tree segment', function () {
    describe('one level', function () {
        describe('first dimension', function () {
            it('should parse in include mode with one value', function () {
                expect(
                    parse("ym:s:operatingSystemRoot IN('windows')"),
                ).toMatchSnapshot();
                expect(
                    parse("ym:s:operatingSystemRoot =.('windows')"),
                ).toMatchSnapshot();
            });
            it('should parse in include mode with many values', function () {
                expect(
                    parse("ym:s:operatingSystemRoot IN('windows', 'linux')"),
                ).toMatchSnapshot();
                expect(
                    parse("ym:s:operatingSystemRoot =.('windows', 'linux')"),
                ).toMatchSnapshot();
            });
            it('should parse in exclude mode with one value', function () {
                expect(
                    parse("ym:s:operatingSystemRoot NOT IN('windows')"),
                ).toMatchSnapshot();
                expect(
                    parse("ym:s:operatingSystemRoot !.('windows')"),
                ).toMatchSnapshot();
            });
            it('should parse in exclude mode with many values', function () {
                expect(
                    parse(
                        "ym:s:operatingSystemRoot NOT IN('windows', 'linux')",
                    ),
                ).toMatchSnapshot();
                expect(
                    parse("ym:s:operatingSystemRoot !.('windows', 'linux')"),
                ).toMatchSnapshot();
            });
        });
        describe('not first dimension', function () {
            it('should parse in include mode with one value', function () {
                expect(
                    parse("ym:s:operatingSystem IN('windows xp')"),
                ).toMatchSnapshot();
                expect(
                    parse("ym:s:operatingSystem =.('windows xp')"),
                ).toMatchSnapshot();
            });
            it('should parse in include mode with many values', function () {
                expect(
                    parse(
                        "ym:s:operatingSystem IN('windows xp', 'linux debian')",
                    ),
                ).toMatchSnapshot();
                expect(
                    parse(
                        "ym:s:operatingSystem =.('windows xp', 'linux debian')",
                    ),
                ).toMatchSnapshot();
            });
            it('should parse in exclude mode with one value', function () {
                expect(
                    parse("ym:s:operatingSystem NOT IN('windows xp')"),
                ).toMatchSnapshot();
                expect(
                    parse("ym:s:operatingSystem !.('windows xp')"),
                ).toMatchSnapshot();
            });
            it('should parse in exclude mode with many values', function () {
                expect(
                    parse(
                        "ym:s:operatingSystem NOT IN('windows xp', 'linux debian')",
                    ),
                ).toMatchSnapshot();
                expect(
                    parse(
                        "ym:s:operatingSystem !.('windows xp', 'linux debian')",
                    ),
                ).toMatchSnapshot();
            });
        });
    });
    describe('multi level', function () {
        it('one value and one value in include mode', function () {
            expect(
                parse(
                    "ym:s:operatingSystemRoot IN('windows') or ym:s:operatingSystem IN('windows xp')",
                ),
            ).toMatchSnapshot();
            expect(
                parse(
                    "ym:s:operatingSystemRoot =.('windows') or ym:s:operatingSystem =.('windows xp')",
                ),
            ).toMatchSnapshot();
        });
        it('one value and many values in include mode', function () {
            expect(
                parse(
                    "ym:s:operatingSystemRoot IN('windows') or" +
                        " ym:s:operatingSystem IN('windows xp', 'linux debian')",
                ),
            ).toMatchSnapshot();
            expect(
                parse(
                    "ym:s:operatingSystemRoot =.('windows') or" +
                        " ym:s:operatingSystem =.('windows xp', 'linux debian')",
                ),
            ).toMatchSnapshot();
        });
        it('many values and many values in include mode', function () {
            expect(
                parse(
                    "ym:s:operatingSystemRoot IN('windows', 'linux') or" +
                        " ym:s:operatingSystem IN('windows xp', 'linux debian')",
                ),
            ).toMatchSnapshot();
            expect(
                parse(
                    "ym:s:operatingSystemRoot =.('windows', 'linux') or" +
                        " ym:s:operatingSystem =.('windows xp', 'linux debian')",
                ),
            ).toMatchSnapshot();
        });
        it('many values and one value in include mode', function () {
            expect(
                parse(
                    "ym:s:operatingSystemRoot IN('windows', 'linux') or ym:s:operatingSystem IN('windows xp')",
                ),
            ).toMatchSnapshot();
            expect(
                parse(
                    "ym:s:operatingSystemRoot =.('windows', 'linux') or ym:s:operatingSystem =.('windows xp')",
                ),
            ).toMatchSnapshot();
        });
        it('one value and one value in exclude mode', function () {
            expect(
                parse(
                    "ym:s:operatingSystemRoot NOT IN('windows') and ym:s:operatingSystem NOT IN('windows xp')",
                ),
            ).toMatchSnapshot();
            expect(
                parse(
                    "ym:s:operatingSystemRoot !.('windows') and ym:s:operatingSystem !.('windows xp')",
                ),
            ).toMatchSnapshot();
        });
        it('one value and many values in exclude mode', function () {
            expect(
                parse(
                    "ym:s:operatingSystemRoot NOT IN('windows') and" +
                        " ym:s:operatingSystem NOT IN('windows xp', 'linux debian')",
                ),
            ).toMatchSnapshot();
            expect(
                parse(
                    "ym:s:operatingSystemRoot !.('windows') and" +
                        " ym:s:operatingSystem !.('windows xp', 'linux debian')",
                ),
            ).toMatchSnapshot();
        });
        it('many values and many values in exclude mode', function () {
            expect(
                parse(
                    "ym:s:operatingSystemRoot NOT IN('windows', 'linux') and" +
                        " ym:s:operatingSystem NOT IN('windows xp', 'linux debian')",
                ),
            ).toMatchSnapshot();
            expect(
                parse(
                    "ym:s:operatingSystemRoot !.('windows', 'linux') and" +
                        " ym:s:operatingSystem !.('windows xp', 'linux debian')",
                ),
            ).toMatchSnapshot();
        });
        it('many values and one value in exclude mode', function () {
            expect(
                parse(
                    "ym:s:operatingSystemRoot NOT IN('windows', 'linux') and" +
                        " ym:s:operatingSystem NOT IN('windows xp')",
                ),
            ).toMatchSnapshot();
            expect(
                parse(
                    "ym:s:operatingSystemRoot !.('windows', 'linux') and" +
                        " ym:s:operatingSystem !.('windows xp')",
                ),
            ).toMatchSnapshot();
        });
    });
    describe('should fallback to path format parser for legacy filter format', function () {
        describe('include mode', function () {
            describe('same depth level mode', function () {
                it('should handle single expression', function () {
                    expect(
                        parse("ym:s:operatingSystemRoot=='windows'"),
                    ).toMatchSnapshot();
                });
                it('should handle multivalue expression of first level', function () {
                    expect(
                        parse(
                            "ym:s:operatingSystemRoot=='windows' or ym:s:operatingSystemRoot=='linux'",
                        ),
                    ).toMatchSnapshot();
                });
                it('should handle single path-like expression', function () {
                    expect(
                        parse(
                            "ym:s:operatingSystemRoot=='windows' and ym:s:operatingSystem=='windows xp'",
                        ),
                    ).toMatchSnapshot();
                });
                it('should handle multivalue path-like expression', function () {
                    expect(
                        parse(
                            "ym:s:operatingSystemRoot=='windows' and ym:s:operatingSystem=='windows xp' or" +
                                " ym:s:operatingSystemRoot=='linux' and ym:s:operatingSystem=='linux debian'",
                        ),
                    ).toMatchSnapshot();
                });
            });
            describe('mixed depth mode', function () {
                it('should handle first simple and second is complex', function () {
                    expect(
                        parse(
                            "ym:s:operatingSystemRoot=='windows' or" +
                                " ym:s:operatingSystemRoot=='linux' and ym:s:operatingSystem=='linux debian'",
                        ),
                    ).toMatchSnapshot();
                });
                it('should handle first complex and second is simple', function () {
                    expect(
                        parse(
                            "ym:s:operatingSystemRoot=='windows' and ym:s:operatingSystem=='windows xp' or" +
                                " ym:s:operatingSystemRoot=='linux'",
                        ),
                    ).toMatchSnapshot();
                });
            });
        });
        describe('exclude mode', function () {
            describe('same depth level mode', function () {
                it('should handle single expression', function () {
                    expect(
                        parse("ym:s:operatingSystemRoot!='windows'"),
                    ).toMatchSnapshot();
                });
                it('should handle multivalue expression of first level', function () {
                    expect(
                        parse(
                            "ym:s:operatingSystemRoot!='windows' and ym:s:operatingSystemRoot!='linux'",
                        ),
                    ).toMatchSnapshot();
                });
                it('should handle single path-like expression', function () {
                    expect(
                        parse(
                            "ym:s:operatingSystemRoot!='windows' or ym:s:operatingSystem!='windows xp'",
                        ),
                    ).toMatchSnapshot();
                });
                it('should handle multivalue path-like expression', function () {
                    expect(
                        parse(
                            "((ym:s:operatingSystemRoot!='windows' or ym:s:operatingSystem!='windows xp') and" +
                                " (ym:s:operatingSystemRoot!='linux' or ym:s:operatingSystem!='linux debian'))",
                        ),
                    ).toMatchSnapshot();
                });
            });
            describe('mixed depth mode', function () {
                it('should handle first simple and second is complex', function () {
                    expect(
                        parse(
                            "(ym:s:operatingSystemRoot!='windows' and " +
                                " (ym:s:operatingSystemRoot!='linux' or ym:s:operatingSystem!='linux debian'))",
                        ),
                    ).toMatchSnapshot();
                });
                it('should handle first complex and second is simple', function () {
                    expect(
                        parse(
                            "((ym:s:operatingSystemRoot!='windows' or ym:s:operatingSystem!='windows xp') and" +
                                " ym:s:operatingSystemRoot!='linux')",
                        ),
                    ).toMatchSnapshot();
                });
            });
        });
    });
    describe('user-centric', function () {
        describe('one level', function () {
            describe('include mode', function () {
                it('should work without user-centric dates', function () {
                    expect(
                        parse(
                            'EXISTS ym:s:specialUser WITH(' +
                                "ym:s:operatingSystemRoot IN('windows', 'linux')" +
                                ')',
                        ),
                    ).toMatchSnapshot();
                    expect(
                        parse(
                            'EXISTS ym:s:specialUser WITH(' +
                                "ym:s:operatingSystemRoot =.('windows', 'linux')" +
                                ')',
                        ),
                    ).toMatchSnapshot();

                    expect(
                        parse(
                            'EXISTS ym:s:specialUser WITH(' +
                                "ym:s:operatingSystem IN('windows xp', 'linux debian')" +
                                ')',
                        ),
                    ).toMatchSnapshot();
                    expect(
                        parse(
                            'EXISTS ym:s:specialUser WITH(' +
                                "ym:s:operatingSystem =.('windows xp', 'linux debian')" +
                                ')',
                        ),
                    ).toMatchSnapshot();
                });
                it('should work with user-centric dates', function () {
                    expect(
                        parse(
                            'EXISTS ym:s:specialUser WITH(' +
                                "ym:s:operatingSystemRoot IN('windows', 'linux') and" +
                                " ym:s:specialDefaultDate>='2015-04-05' and ym:s:specialDefaultDate<='2015-05-07'" +
                                ')',
                        ),
                    ).toMatchSnapshot();
                    expect(
                        parse(
                            'EXISTS ym:s:specialUser WITH(' +
                                "ym:s:operatingSystemRoot =.('windows', 'linux') and" +
                                " ym:s:specialDefaultDate>='2015-04-05' and ym:s:specialDefaultDate<='2015-05-07'" +
                                ')',
                        ),
                    ).toMatchSnapshot();

                    expect(
                        parse(
                            'EXISTS ym:s:specialUser WITH(' +
                                "ym:s:operatingSystem IN('windows xp', 'linux debian') and" +
                                " ym:s:specialDefaultDate>='2015-04-05' and ym:s:specialDefaultDate<='2015-05-07'" +
                                ')',
                        ),
                    ).toMatchSnapshot();
                    expect(
                        parse(
                            'EXISTS ym:s:specialUser WITH(' +
                                "ym:s:operatingSystem =.('windows xp', 'linux debian') and" +
                                " ym:s:specialDefaultDate>='2015-04-05' and ym:s:specialDefaultDate<='2015-05-07'" +
                                ')',
                        ),
                    ).toMatchSnapshot();
                });
            });
            describe('exclude mode', function () {
                it('should work without user-centric dates', function () {
                    expect(
                        parse(
                            'EXISTS ym:s:specialUser WITH(' +
                                "ym:s:operatingSystemRoot NOT IN('windows', 'linux')" +
                                ')',
                        ),
                    ).toMatchSnapshot();
                    expect(
                        parse(
                            'EXISTS ym:s:specialUser WITH(' +
                                "ym:s:operatingSystemRoot !.('windows', 'linux')" +
                                ')',
                        ),
                    ).toMatchSnapshot();
                    expect(
                        parse(
                            'EXISTS ym:s:specialUser WITH(' +
                                "ym:s:operatingSystem NOT IN('windows xp', 'linux debian')" +
                                ')',
                        ),
                    ).toMatchSnapshot();
                    expect(
                        parse(
                            'EXISTS ym:s:specialUser WITH(' +
                                "ym:s:operatingSystem !.('windows xp', 'linux debian')" +
                                ')',
                        ),
                    ).toMatchSnapshot();
                });
                it('should work with user-centric dates', function () {
                    expect(
                        parse(
                            'EXISTS ym:s:specialUser WITH(' +
                                "ym:s:operatingSystemRoot NOT IN('windows', 'linux') and" +
                                " ym:s:specialDefaultDate>='2015-04-05' and ym:s:specialDefaultDate<='2015-05-07'" +
                                ')',
                        ),
                    ).toMatchSnapshot();
                    expect(
                        parse(
                            'EXISTS ym:s:specialUser WITH(' +
                                "ym:s:operatingSystemRoot !.('windows', 'linux') and" +
                                " ym:s:specialDefaultDate>='2015-04-05' and ym:s:specialDefaultDate<='2015-05-07'" +
                                ')',
                        ),
                    ).toMatchSnapshot();

                    expect(
                        parse(
                            'EXISTS ym:s:specialUser WITH(' +
                                "ym:s:operatingSystem NOT IN('windows xp', 'linux debian') and" +
                                " ym:s:specialDefaultDate>='2015-04-05' and ym:s:specialDefaultDate<='2015-05-07'" +
                                ')',
                        ),
                    ).toMatchSnapshot();
                    expect(
                        parse(
                            'EXISTS ym:s:specialUser WITH(' +
                                "ym:s:operatingSystem !.('windows xp', 'linux debian') and" +
                                " ym:s:specialDefaultDate>='2015-04-05' and ym:s:specialDefaultDate<='2015-05-07'" +
                                ')',
                        ),
                    ).toMatchSnapshot();
                });
            });
        });
        describe('multi level', function () {
            describe('include mode', function () {
                it('should work without user-centric dates', function () {
                    expect(
                        parse(
                            'EXISTS ym:s:specialUser WITH(' +
                                "ym:s:operatingSystemRoot IN('windows', 'linux') or" +
                                " ym:s:operatingSystem IN('windows xp', 'linux debian')" +
                                ')',
                        ),
                    ).toMatchSnapshot();
                    expect(
                        parse(
                            'EXISTS ym:s:specialUser WITH(' +
                                "ym:s:operatingSystemRoot =.('windows', 'linux') or" +
                                " ym:s:operatingSystem =.('windows xp', 'linux debian')" +
                                ')',
                        ),
                    ).toMatchSnapshot();
                });
                it('should work with user-centric dates', function () {
                    expect(
                        parse(
                            'EXISTS ym:s:specialUser WITH(' +
                                "(ym:s:operatingSystemRoot IN('windows', 'linux') or" +
                                " ym:s:operatingSystem IN('windows xp', 'linux debian')) and" +
                                " ym:s:specialDefaultDate>='2015-04-05' and ym:s:specialDefaultDate<='2015-05-07'" +
                                ')',
                        ),
                    ).toMatchSnapshot();
                    expect(
                        parse(
                            'EXISTS ym:s:specialUser WITH(' +
                                "(ym:s:operatingSystemRoot =.('windows', 'linux') or" +
                                " ym:s:operatingSystem =.('windows xp', 'linux debian')) and" +
                                " ym:s:specialDefaultDate>='2015-04-05' and ym:s:specialDefaultDate<='2015-05-07'" +
                                ')',
                        ),
                    ).toMatchSnapshot();
                });
            });
            describe('exclude mode', function () {
                it('should work without user-centric dates', function () {
                    expect(
                        parse(
                            'EXISTS ym:s:specialUser WITH(' +
                                "ym:s:operatingSystemRoot NOT IN('windows', 'linux') and" +
                                " ym:s:operatingSystem NOT IN('windows xp', 'linux debian')" +
                                ')',
                        ),
                    ).toMatchSnapshot();
                    expect(
                        parse(
                            'EXISTS ym:s:specialUser WITH(' +
                                "ym:s:operatingSystemRoot !.('windows', 'linux') and" +
                                " ym:s:operatingSystem !.('windows xp', 'linux debian')" +
                                ')',
                        ),
                    ).toMatchSnapshot();
                });
                it('should work with user-centric dates', function () {
                    expect(
                        parse(
                            'EXISTS ym:s:specialUser WITH(' +
                                "(ym:s:operatingSystemRoot NOT IN('windows', 'linux') and " +
                                " ym:s:operatingSystem NOT IN('windows xp', 'linux debian')) and" +
                                " ym:s:specialDefaultDate>='2015-04-05' and ym:s:specialDefaultDate<='2015-05-07'" +
                                ')',
                        ),
                    ).toMatchSnapshot();
                    expect(
                        parse(
                            'EXISTS ym:s:specialUser WITH(' +
                                "(ym:s:operatingSystemRoot !.('windows', 'linux') and " +
                                " ym:s:operatingSystem !.('windows xp', 'linux debian')) and" +
                                " ym:s:specialDefaultDate>='2015-04-05' and ym:s:specialDefaultDate<='2015-05-07'" +
                                ')',
                        ),
                    ).toMatchSnapshot();
                });
            });
        });
    });
});

describe('path segment', function () {
    describe('include mode', function () {
        describe('one dimension expression', function () {
            it('shold work with regular value', function () {
                expect(parse('ym:s:regionCountry==1')).toMatchSnapshot();
            });
            it('shold work with null value', function () {
                expect(parse('ym:s:regionCountry=n')).toMatchSnapshot();
            });
            it('should work with two and more values', function () {
                expect(
                    parse('ym:s:regionCountry==1 or ym:s:regionCountry=n'),
                ).toMatchSnapshot();
            });
        });
        describe('multi dimension expression', function () {
            it('should work with one multidimension expression', function () {
                expect(
                    parse('ym:s:regionCountry==2 and ym:s:regionArea==5'),
                ).toMatchSnapshot();
            });
            it('should work with one or many', function () {
                expect(
                    parse(
                        'ym:s:regionCountry==1 or ym:s:regionCountry==2 and ym:s:regionArea==5',
                    ),
                ).toMatchSnapshot();
            });
            it('should work with many or one', function () {
                expect(
                    parse(
                        'ym:s:regionCountry==1 and ym:s:regionArea==7 or ym:s:regionCountry==2',
                    ),
                ).toMatchSnapshot();
            });
            it('should work with many or many', function () {
                expect(
                    parse(
                        'ym:s:regionCountry==1 and ym:s:regionArea==7 or ym:s:regionCountry==2 and ym:s:regionArea==5 ',
                    ),
                ).toMatchSnapshot();
            });
        });
    });
    describe('exclude mode', function () {
        describe('one dimension expression', function () {
            it('shold work with regular value', function () {
                expect(parse('ym:s:regionCountry!=1')).toMatchSnapshot();
            });
            it('shold work with null value', function () {
                expect(parse('ym:s:regionCountry!n')).toMatchSnapshot();
            });
            it('should work with two and more values', function () {
                expect(
                    parse('ym:s:regionCountry!=1 and ym:s:regionCountry!n'),
                ).toMatchSnapshot();
            });
        });
        describe('multi dimension expression', function () {
            it('should work with one multidimension expression', function () {
                expect(
                    parse('ym:s:regionCountry!=2 or ym:s:regionArea!=5'),
                ).toMatchSnapshot();
            });
            it('should work with one or many', function () {
                expect(
                    parse(
                        '(ym:s:regionCountry!=1 and (ym:s:regionCountry!=2 or ym:s:regionArea!=5))',
                    ),
                ).toMatchSnapshot();
            });
            it('should work with many or one', function () {
                expect(
                    parse(
                        '((ym:s:regionCountry!=1 or ym:s:regionArea!=7) and (ym:s:regionCountry!=2))',
                    ),
                ).toMatchSnapshot();
            });
            it('should work with many or many', function () {
                expect(
                    parse(
                        '((ym:s:regionCountry!=1 or ym:s:regionArea!=7) and' +
                            ' (ym:s:regionCountry!=2 or ym:s:regionArea!=5))',
                    ),
                ).toMatchSnapshot();
            });
        });
    });
    describe('user-centric mode', function () {
        describe('include mode', function () {
            describe('one dimension expression', function () {
                it('should work without user-centric dates', function () {
                    expect(
                        parse(
                            'EXISTS ym:s:specialUser WITH(ym:s:regionCountry==1 or ym:s:regionCountry=n)',
                        ),
                    ).toMatchSnapshot();
                });
                it('should work with user-centric dates', function () {
                    expect(
                        parse(
                            'EXISTS ym:s:specialUser WITH((ym:s:regionCountry==1 or ym:s:regionCountry=n) and' +
                                " ym:s:specialDefaultDate>='2014-12-14' and" +
                                " ym:s:specialDefaultDate <= '2016-01-01')",
                        ),
                    ).toMatchSnapshot();
                    expect(
                        parse(
                            'EXISTS ym:s:specialUser WITH((ym:s:regionCountry==1 or ym:s:regionCountry=n) and' +
                                " (ym:s:specialDefaultDate>='2014-12-14' and" +
                                " ym:s:specialDefaultDate <= '2016-01-01'))",
                        ),
                    ).toMatchSnapshot();
                });
            });
            describe('multi dimension expression', function () {
                describe('without dates', function () {
                    it('should work with one multidimension expression', function () {
                        expect(
                            parse(
                                'EXISTS ym:s:specialUser WITH(ym:s:regionCountry==2 and ym:s:regionArea==5)',
                            ),
                        ).toMatchSnapshot();
                    });
                    it('should work with one or many', function () {
                        expect(
                            parse(
                                'EXISTS ym:s:specialUser WITH(' +
                                    'ym:s:regionCountry==1 or ym:s:regionCountry==2 and ym:s:regionArea==5' +
                                    ')',
                            ),
                        ).toMatchSnapshot();
                    });
                    it('should work with many or one', function () {
                        expect(
                            parse(
                                'EXISTS ym:s:specialUser WITH(' +
                                    'ym:s:regionCountry==1 and ym:s:regionArea==7 or ym:s:regionCountry==2' +
                                    ')',
                            ),
                        ).toMatchSnapshot();
                    });
                    it('should work with many or many', function () {
                        expect(
                            parse(
                                'EXISTS ym:s:specialUser WITH(' +
                                    'ym:s:regionCountry==1 and ym:s:regionArea==7 or' +
                                    'ym:s:regionCountry==2 and ym:s:regionArea==5 ' +
                                    ')',
                            ),
                        ).toMatchSnapshot();
                    });
                });
                describe('with dates', function () {
                    it('should work with one multidimension expression', function () {
                        expect(
                            parse(
                                'EXISTS ym:s:specialUser WITH(' +
                                    'ym:s:regionCountry==2 and ym:s:regionArea==5 and' +
                                    " ym:s:specialDefaultDate >= '2012-12-12' and" +
                                    " ym:s:specialDefaultDate <= '2012-12-15'" +
                                    ')',
                            ),
                        ).toMatchSnapshot();
                    });
                    it('should work with one or many', function () {
                        expect(
                            parse(
                                'EXISTS ym:s:specialUser WITH(' +
                                    '(ym:s:regionCountry==1 or ym:s:regionCountry==2 and ym:s:regionArea==5) and' +
                                    " ym:s:specialDefaultDate >= '2012-12-12' and" +
                                    " ym:s:specialDefaultDate <= '2012-12-15'" +
                                    ')',
                            ),
                        ).toMatchSnapshot();
                    });
                    it('should work with many or one', function () {
                        expect(
                            parse(
                                'EXISTS ym:s:specialUser WITH(' +
                                    '(ym:s:regionCountry==1 and ym:s:regionArea==7 or ym:s:regionCountry==2) and' +
                                    " ym:s:specialDefaultDate >= '2012-12-12' and" +
                                    " ym:s:specialDefaultDate <= '2012-12-15'" +
                                    ')',
                            ),
                        ).toMatchSnapshot();
                    });
                    it('should work with many or many', function () {
                        expect(
                            parse(
                                'EXISTS ym:s:specialUser WITH(' +
                                    '(ym:s:regionCountry==1 and ym:s:regionArea==7 or' +
                                    ' ym:s:regionCountry==2 and ym:s:regionArea==5) and ' +
                                    " ym:s:specialDefaultDate >= '2012-12-12' and" +
                                    " ym:s:specialDefaultDate <= '2012-12-15'" +
                                    ')',
                            ),
                        ).toMatchSnapshot();
                    });
                });
            });
        });
        describe('exclude mode', function () {
            describe('one dimension expression', function () {
                it('should work without user-centric dates', function () {
                    expect(
                        parse(
                            'EXISTS ym:s:specialUser WITH(ym:s:regionCountry!=1 and ym:s:regionCountry!n)',
                        ),
                    ).toMatchSnapshot();
                });
                it('should work with user-centric dates', function () {
                    expect(
                        parse(
                            'EXISTS ym:s:specialUser WITH((ym:s:regionCountry!=1 and ym:s:regionCountry!n) and' +
                                " ym:s:specialDefaultDate>='2014-12-14' and" +
                                " ym:s:specialDefaultDate <= '2016-01-01')",
                        ),
                    ).toMatchSnapshot();
                    expect(
                        parse(
                            'EXISTS ym:s:specialUser WITH(ym:s:regionCountry!=1 and ym:s:regionCountry!n and' +
                                " ym:s:specialDefaultDate>='2014-12-14' and" +
                                " ym:s:specialDefaultDate <= '2016-01-01')",
                        ),
                    ).toMatchSnapshot();
                });
            });
            describe('multi dimension expression', function () {
                describe('without dates', function () {
                    it('should work with one multidimension expression', function () {
                        expect(
                            parse(
                                'EXISTS ym:s:specialUser WITH(ym:s:regionCountry!=2 or ym:s:regionArea!=5)',
                            ),
                        ).toMatchSnapshot();
                    });
                    it('should work with one or many', function () {
                        expect(
                            parse(
                                'EXISTS ym:s:specialUser WITH(' +
                                    'ym:s:regionCountry!=1 and (ym:s:regionCountry!=2 or ym:s:regionArea!=5)' +
                                    ')',
                            ),
                        ).toMatchSnapshot();
                    });
                    it('should work with many or one', function () {
                        expect(
                            parse(
                                'EXISTS ym:s:specialUser WITH(' +
                                    '(ym:s:regionCountry!=1 or ym:s:regionArea!=7) and ym:s:regionCountry!=2' +
                                    ')',
                            ),
                        ).toMatchSnapshot();
                    });
                    it('should work with many or many', function () {
                        expect(
                            parse(
                                'EXISTS ym:s:specialUser WITH(' +
                                    '(ym:s:regionCountry!=1 or ym:s:regionArea!=7) and' +
                                    ' (ym:s:regionCountry!=2 or ym:s:regionArea!=5)' +
                                    ')',
                            ),
                        ).toMatchSnapshot();
                    });
                });
                describe('with dates', function () {
                    it('should work with one multidimension expression', function () {
                        expect(
                            parse(
                                'EXISTS ym:s:specialUser WITH(' +
                                    '(ym:s:regionCountry!=2 or ym:s:regionArea!=5) and' +
                                    " ym:s:specialDefaultDate >= '2012-12-12' and" +
                                    " ym:s:specialDefaultDate <= '2012-12-15'" +
                                    ')',
                            ),
                        ).toMatchSnapshot();
                    });
                    it('should work with one or many', function () {
                        expect(
                            parse(
                                'EXISTS ym:s:specialUser WITH(' +
                                    '((ym:s:regionCountry!=1) and (ym:s:regionCountry!=2 or ym:s:regionArea!=5)) and' +
                                    " ym:s:specialDefaultDate >= '2012-12-12' and" +
                                    " ym:s:specialDefaultDate <= '2012-12-15'" +
                                    ')',
                            ),
                        ).toMatchSnapshot();
                    });
                    it('should work with many or one', function () {
                        expect(
                            parse(
                                'EXISTS ym:s:specialUser WITH(' +
                                    '((ym:s:regionCountry!=1 or ym:s:regionArea!=7) and (ym:s:regionCountry!=2)) and' +
                                    " ym:s:specialDefaultDate >= '2012-12-12' and" +
                                    " ym:s:specialDefaultDate <= '2012-12-15'" +
                                    ')',
                            ),
                        ).toMatchSnapshot();
                    });
                    it('should work with many or many', function () {
                        expect(
                            parse(
                                'EXISTS ym:s:specialUser WITH(' +
                                    '((ym:s:regionCountry!=1 or ym:s:regionArea!=7) and ' +
                                    ' (ym:s:regionCountry!=2 or ym:s:regionArea!=5)) and ' +
                                    " ym:s:specialDefaultDate >= '2012-12-12' and" +
                                    " ym:s:specialDefaultDate <= '2012-12-15'" +
                                    ')',
                            ),
                        ).toMatchSnapshot();
                    });
                });
            });
        });
    });
});
