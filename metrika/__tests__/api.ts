import { State } from 'client/store/state';

import { createIdToName, serialzeSegmentToApiFormat } from '../api';
import { getParser } from '../parser';
import { Segment } from '../segments/typings';
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

const idToName = createIdToName(state as State);

const serialize = (filter: Segment[]) => {
    return serialzeSegmentToApiFormat(filter, idToName);
};

it('should handle empty strings', function () {
    expect(parse('')).toEqual([]);
});

describe('boolean segment', function () {
    it('should handle Yes', function () {
        const segmentString = "ym:s:isNewUser=='Yes'";
        expect(serialize(parse(segmentString))).toMatch(segmentString);
    });
    it('should handle No', function () {
        const segmentString = "ym:s:isNewUser=='No'";
        expect(serialize(parse(segmentString))).toMatch(segmentString);
    });
    describe('user-centric mode', function () {
        it('should work without dates', function () {
            const segmentString =
                "EXISTS ym:s:specialUser WITH (ym:s:hasGCLID=='Yes')";
            expect(serialize(parse(segmentString))).toMatch(segmentString);
            const segmentString2 =
                "EXISTS ym:s:specialUser WITH (ym:s:hasGCLID=='No')";
            expect(serialize(parse(segmentString2))).toMatch(segmentString2);
        });
        it('should work with one date', function () {
            const segmentString =
                "EXISTS ym:s:specialUser WITH (ym:s:hasGCLID=='Yes' and" +
                " ym:s:specialDefaultDate=='2015-12-15')";
            expect(serialize(parse(segmentString))).toMatch(segmentString);
        });
        it('should work with two dates', function () {
            const segmentString =
                "EXISTS ym:s:specialUser WITH (ym:s:hasGCLID=='No' and" +
                " ym:s:specialDefaultDate>='2015-12-12' and ym:s:specialDefaultDate<='2016-12-12')";
            expect(serialize(parse(segmentString))).toMatch(segmentString);
        });
    });
});

describe('uid segment', function () {
    it('should parse uid segments', function () {
        const segmentString = 'ym:s:userIDHash==123456';
        expect(serialize(parse(segmentString))).toMatch(segmentString);
    });
    // there are no user-centric segments for uid -- no tests
});

describe('goal segment', function () {
    describe('single expression', function () {
        it('should parse goal reached segment', function () {
            const segmentString = "ym:s:goal123456IsReached=='Yes'";
            expect(serialize(parse(segmentString))).toMatch(segmentString);
        });
        it('should parse goal not reached segment', function () {
            const segmentString = "ym:s:goal123456IsReached=='No'";
            expect(serialize(parse(segmentString))).toMatch(segmentString);
        });
    });
    describe('complex expression', function () {
        it('should parse goal reached segment', function () {
            const segmentString =
                "ym:s:goal123456IsReached=='No' and ym:s:goal98765IsReached=='No'";
            expect(serialize(parse(segmentString))).toMatch(segmentString);
        });
    });
});

describe('number segment', function () {
    it('should parse == expression', function () {
        const segmentString = 'ym:s:pageViews==5';
        expect(serialize(parse(segmentString))).toMatch(segmentString);
    });
    it('should parse > expression', function () {
        const segmentString = 'ym:s:pageViews>5';
        expect(serialize(parse(segmentString))).toMatch(segmentString);
    });
    it('should parse < expression', function () {
        const segmentString = 'ym:s:pageViews<5';
        expect(serialize(parse(segmentString))).toMatch(segmentString);
    });
    it('should parse between', function () {
        const segmentString = 'ym:s:pageViews>=5 and ym:s:pageViews<=10';
        expect(serialize(parse(segmentString))).toMatch(segmentString);
    });
    it('should parse with currency', function () {
        const segmentString = 'ym:u:userCNYRevenue==2';
        expect(serialize(parse(segmentString))).toMatch(segmentString);
    });
    describe('user-centric mode', function () {
        it('should work without dates', function () {
            const segmentString =
                'EXISTS ym:u:userID WITH (ym:u:daysSinceFirstVisitOneBased>5)';
            expect(serialize(parse(segmentString))).toMatch(segmentString);

            const segmentString2 = "ym:s:goal123456IsReached=='Yes'";
            expect(serialize(parse(segmentString2))).toMatch(segmentString2);

            const segmentString3 =
                'EXISTS ym:u:userID WITH' +
                ' (ym:u:daysSinceFirstVisitOneBased>=5 and ym:u:daysSinceFirstVisitOneBased<=7)';
            expect(serialize(parse(segmentString3))).toMatch(segmentString3);
        });
        it('should work with one date', function () {
            const segmentString =
                'EXISTS ym:u:userID WITH (ym:u:daysSinceFirstVisitOneBased==5 and' +
                " ym:u:specialDefaultDate=='2012-3-5')";
            expect(serialize(parse(segmentString))).toMatch(segmentString);

            const segmentString2 =
                'EXISTS ym:u:userID WITH' +
                ' (ym:u:daysSinceFirstVisitOneBased>=5 and ym:u:daysSinceFirstVisitOneBased<=10 and' +
                " ym:u:specialDefaultDate=='2012-3-5')";
            expect(serialize(parse(segmentString2))).toMatch(segmentString2);
        });
        it('should work with two dates', function () {
            const segmentString =
                'EXISTS ym:u:userID WITH (ym:u:daysSinceFirstVisitOneBased==5 and' +
                " ym:u:specialDefaultDate>='2012-3-5' and ym:u:specialDefaultDate<='2015-01-05')";
            expect(serialize(parse(segmentString))).toMatch(segmentString);

            const segmentString2 =
                'EXISTS ym:u:userID WITH' +
                ' (ym:u:daysSinceFirstVisitOneBased>=5 and ym:u:daysSinceFirstVisitOneBased<=10 and' +
                " ym:u:specialDefaultDate>='2012-3-5' and ym:u:specialDefaultDate<='2015-01-05')";
            expect(serialize(parse(segmentString2))).toMatch(segmentString2);
        });
    });
});

describe('date segment', function () {
    it('should parse == expression', function () {
        const segmentString = "ym:s:previousVisitDate>'2016-02-02'";
        expect(serialize(parse(segmentString))).toMatch(segmentString);
    });
    it('should parse > expression', function () {
        const segmentString = "ym:s:goal123456IsReached=='Yes'";
        expect(serialize(parse(segmentString))).toMatch(segmentString);
    });
    it('should parse < expression', function () {
        const segmentString = "ym:s:previousVisitDate<'2016-03-04'";
        expect(serialize(parse(segmentString))).toMatch(segmentString);
    });
    it('should parse between', function () {
        const segmentString =
            "ym:s:previousVisitDate>='2015-12-01' and ym:s:previousVisitDate<='2016-03-05'";
        expect(serialize(parse(segmentString))).toMatch(segmentString);
    });
});

describe('multiline segment', function () {
    describe('one line', function () {
        it('should parse == expression', function () {
            const segmentString = "ym:s:searchPhrase=*'phrase1'";
            expect(serialize(parse(segmentString))).toMatch(segmentString);
        });
        it('should parse @ expression', function () {
            const segmentString = "ym:s:searchPhrase=@'phrase1'";
            expect(serialize(parse(segmentString))).toMatch(segmentString);
        });
        it('should parse !@ expression', function () {
            const segmentString = "ym:s:searchPhrase!@'phrase1'";
            expect(serialize(parse(segmentString))).toMatch(segmentString);
        });
        it('should parse ~ expression', function () {
            const segmentString = "ym:s:searchPhrase=~'phrase1'";
            expect(serialize(parse(segmentString))).toMatch(segmentString);
        });
        it('should parse !~ expression', function () {
            const segmentString = "ym:s:searchPhrase!~'phrase1'";
            expect(serialize(parse(segmentString))).toMatch(segmentString);
        });
    });
    describe('multiple lines', function () {
        describe('with conjunction', function () {
            it('should work with two subexpressions', function () {
                const segmentString =
                    "ym:s:searchPhrase=*'phrase1' and ym:s:searchPhrase=*'phrase2'";
                expect(serialize(parse(segmentString))).toMatch(segmentString);
            });
            it('should work with three subexpressions', function () {
                const segmentString =
                    "ym:s:searchPhrase=*'phrase1' and ym:s:searchPhrase=@'phrase2' and" +
                    " ym:s:searchPhrase=~'phrase3'";
                expect(serialize(parse(segmentString))).toMatch(segmentString);
            });
        });
        describe('with disjunction', function () {
            it('should work with two subexpressions', function () {
                const segmentString =
                    "ym:s:searchPhrase=*'phrase1' or ym:s:searchPhrase=*'phrase2'";
                expect(serialize(parse(segmentString))).toMatch(segmentString);
            });
            it('should work with three subexpressions', function () {
                const segmentString =
                    "ym:s:searchPhrase=*'phrase1' or ym:s:searchPhrase=@'phrase2' or" +
                    " ym:s:searchPhrase=~'phrase3'";
                expect(serialize(parse(segmentString))).toMatch(segmentString);
            });
        });
    });
    describe('user-centric mode', function () {
        describe('one line expression', function () {
            it('should work without dates', function () {
                const segmentString =
                    "EXISTS ym:u:userID WITH (ym:u:firstSearchPhrase=*'qwerty')";
                expect(serialize(parse(segmentString))).toMatch(segmentString);
            });
            it('should work with one date', function () {
                const segmentString =
                    "EXISTS ym:u:userID WITH (ym:u:firstSearchPhrase=*'qwerty' and" +
                    " ym:u:specialDefaultDate=='2016-12-11')";
                expect(serialize(parse(segmentString))).toMatch(segmentString);
            });
            it('should work with two dates', function () {
                const segmentString =
                    "EXISTS ym:u:userID WITH (ym:u:firstSearchPhrase=*'qwerty' and" +
                    " ym:u:specialDefaultDate>='2016-03-05' and ym:u:specialDefaultDate<='2016-03-11')";
                expect(serialize(parse(segmentString))).toMatch(segmentString);
            });
        });
        describe('many lines expression', function () {
            describe('conjunction mode', function () {
                it('should work without dates', function () {
                    const segmentString =
                        'EXISTS ym:u:userID WITH (' +
                        [
                            "ym:u:firstSearchPhrase=*'qwerty'",
                            "ym:u:firstSearchPhrase!*'asdf'",
                            "ym:u:firstSearchPhrase=@'qaz'",
                            "ym:u:firstSearchPhrase=~'wsx'",
                            "ym:u:firstSearchPhrase!@'edc'",
                            "ym:u:firstSearchPhrase!~'rfv'",
                        ].join(' and ') +
                        ')';
                    expect(serialize(parse(segmentString))).toMatch(
                        segmentString,
                    );
                });
                it('should work with one date', function () {
                    const segmentString =
                        'EXISTS ym:u:userID WITH (' +
                        [
                            "ym:u:firstSearchPhrase=*'qwerty'",
                            "ym:u:firstSearchPhrase!*'asdf'",
                            "ym:u:firstSearchPhrase=@'qaz'",
                            "ym:u:firstSearchPhrase=~'wsx'",
                            "ym:u:firstSearchPhrase!@'edc'",
                            "ym:u:firstSearchPhrase!~'rfv'",
                        ].join(' and ') +
                        " and ym:u:specialDefaultDate=='2011-08-08')";
                    expect(serialize(parse(segmentString))).toMatch(
                        segmentString,
                    );
                });
                it('should work with two dates', function () {
                    const segmentString =
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
                        " ym:u:specialDefaultDate<='2012-11-11')";
                    expect(serialize(parse(segmentString))).toMatch(
                        segmentString,
                    );
                });
            });
            describe('disjunction mode', function () {
                it('should work without dates', function () {
                    const segmentString =
                        'EXISTS ym:u:userID WITH ((' +
                        [
                            "ym:u:firstSearchPhrase=*'qwerty'",
                            "ym:u:firstSearchPhrase!*'asdf'",
                            "ym:u:firstSearchPhrase=@'qaz'",
                            "ym:u:firstSearchPhrase=~'wsx'",
                            "ym:u:firstSearchPhrase!@'edc'",
                            "ym:u:firstSearchPhrase!~'rfv'",
                        ].join(' or ') +
                        '))';
                    expect(serialize(parse(segmentString))).toMatch(
                        segmentString,
                    );
                });
                it('should work with one date', function () {
                    const segmentString =
                        'EXISTS ym:u:userID WITH ((' +
                        [
                            "ym:u:firstSearchPhrase=*'qwerty'",
                            "ym:u:firstSearchPhrase!*'asdf'",
                            "ym:u:firstSearchPhrase=@'qaz'",
                            "ym:u:firstSearchPhrase=~'wsx'",
                            "ym:u:firstSearchPhrase!@'edc'",
                            "ym:u:firstSearchPhrase!~'rfv'",
                        ].join(' or ') +
                        ") and ym:u:specialDefaultDate=='2011-08-08')";
                    expect(serialize(parse(segmentString))).toMatch(
                        segmentString,
                    );
                });
                it('should work with two dates', function () {
                    const segmentString =
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
                        " ym:u:specialDefaultDate<='2012-11-11')";
                    expect(serialize(parse(segmentString))).toMatch(
                        segmentString,
                    );
                });
            });
        });
    });
});

describe('url segment', function () {
    it('should correctly handle urlMode', function () {
        const segmentString = "ym:pv:URL=*'phrase1'";
        expect(serialize(parse(segmentString))).toMatch(segmentString);
        const segmentString2 = "ym:pv:URLDomain=*'phrase1'";
        expect(serialize(parse(segmentString2))).toMatch(segmentString2);
        const segmentString3 = "ym:pv:URLPathFull=*'phrase1'";
        expect(serialize(parse(segmentString3))).toMatch(segmentString3);
    });
    it('should correctly handle user centric', function () {
        const segmentString =
            '(EXISTS ym:pv:specialUser WITH (' +
            [
                "ym:pv:URLPathFull=*'/owner/*'",
                "ym:pv:URLPathFull=*'2016-01-01'",
                "ym:pv:URLPathFull=*'2020-07-25'",
            ].join(' and ') +
            '))';
        expect(serialize(parse(segmentString))).toMatch(segmentString);
    });
});

describe('params segment', function () {
    describe('without quantifier', function () {
        it('should correctly handle noQuantifier flag for simple expression', function () {
            const segmentString = "ym:s:paramsLevel1=='level1'";
            expect(serialize(parse(segmentString))).toMatch(segmentString);
        });
        it('should correctly handle noQuantifier flag for complex expression', function () {
            const segmentString =
                "ym:s:paramsLevel1=='level1' and ym:s:paramsLevel2=='level2' and ym:s:paramsLevel3=='level3'";
            expect(serialize(parse(segmentString))).toMatch(segmentString);
        });
    });
    describe('with quantifier', function () {
        it('should correctly handle noQuantifier flag for simple expression', function () {
            const segmentString = "EXISTS(ym:s:paramsLevel1=='level1')";
            expect(serialize(parse(segmentString))).toMatch(segmentString);
        });
        it('should correctly handle noQuantifier flag for complex expression', function () {
            const segmentString =
                "EXISTS(ym:s:paramsLevel1=='level1' and ym:s:paramsLevel2=='level2')";
            expect(serialize(parse(segmentString))).toMatch(segmentString);
        });
    });
    it('should correctly parse simple expression', function () {
        const segmentString = "ym:s:paramsLevel1=='level1'";
        expect(serialize(parse(segmentString))).toMatch(segmentString);
    });
    it('should correctly parse complex expression', function () {
        const segmentString =
            "ym:s:paramsLevel1=='level1' and ym:s:paramsLevel2=='level2'";
        expect(serialize(parse(segmentString))).toMatch(segmentString);
    });
    it('should correctly parse long complex expression', function () {
        const segmentString =
            "ym:s:paramsLevel1=='level1' and ym:s:paramsLevel2=='level2' and ym:s:paramsLevel3=='level3'";
        expect(serialize(parse(segmentString))).toMatch(segmentString);
    });
    it('should correctly parse complex expression with double value', function () {
        const segmentString =
            "ym:s:paramsLevel1=='level1' and ym:s:paramsValueDouble==5";
        expect(serialize(parse(segmentString))).toMatch(segmentString);
    });
    it('should correctly parse value comparison operators', function () {
        const segmentString =
            "ym:s:paramsLevel1=='level1' and ym:s:paramsValueDouble==5";
        expect(serialize(parse(segmentString))).toMatch(segmentString);

        const segmentString2 =
            "ym:s:paramsLevel1=='level1' and ym:s:paramsValueDouble>5";
        expect(serialize(parse(segmentString2))).toMatch(segmentString2);

        const segmentString3 =
            "ym:s:paramsLevel1=='level1' and ym:s:paramsValueDouble<5";
        expect(serialize(parse(segmentString3))).toMatch(segmentString3);
    });
    describe('user-centric mode', function () {
        describe('without internal quantifier', function () {
            describe('without user-centric dates', function () {
                it('should correctly handle noQuantifier flag for simple expression', function () {
                    const segmentString =
                        "EXISTS ym:s:specialUser WITH (ym:s:paramsLevel1=='level1')";
                    expect(serialize(parse(segmentString))).toMatch(
                        segmentString,
                    );
                });
                it('should correctly handle noQuantifier flag for complex expression', function () {
                    const segmentString =
                        "EXISTS ym:s:specialUser WITH (ym:s:paramsLevel1=='level1' and" +
                        " ym:s:paramsLevel2=='level2')";
                    expect(serialize(parse(segmentString))).toMatch(
                        segmentString,
                    );
                });
            });
            describe('with one user-centric date', function () {
                it('should correctly handle noQuantifier flag for simple expression', function () {
                    const segmentString =
                        "EXISTS ym:s:specialUser WITH (ym:s:paramsLevel1=='level1' and" +
                        " ym:s:specialDefaultDate=='2016-03-15')";
                    expect(serialize(parse(segmentString))).toMatch(
                        segmentString,
                    );
                });
                it('should correctly handle noQuantifier flag for complex expression', function () {
                    const segmentString =
                        "EXISTS ym:s:specialUser WITH (ym:s:paramsLevel1=='level1' and" +
                        " ym:s:paramsLevel2=='level2' and" +
                        " ym:s:specialDefaultDate=='2016-03-15')";
                    expect(serialize(parse(segmentString))).toMatch(
                        segmentString,
                    );
                });
            });
            describe('with two user-centric dates', function () {
                it('should correctly handle noQuantifier flag for simple expression', function () {
                    const segmentString =
                        "EXISTS ym:s:specialUser WITH (ym:s:paramsLevel1=='level1' and" +
                        " ym:s:specialDefaultDate>='2016-03-15' and ym:s:specialDefaultDate<='2016-03-17')";
                    expect(serialize(parse(segmentString))).toMatch(
                        segmentString,
                    );
                });
                it('should correctly handle noQuantifier flag for complex expression', function () {
                    const segmentString =
                        "EXISTS ym:s:specialUser WITH (ym:s:paramsLevel1=='level1' and" +
                        " ym:s:paramsLevel2=='level2' and" +
                        " ym:s:specialDefaultDate>='2016-03-15' and ym:s:specialDefaultDate<='2016-03-17')";
                    expect(serialize(parse(segmentString))).toMatch(
                        segmentString,
                    );
                });
            });
        });
        describe('with internal quantifier', function () {
            describe('without user-centric dates', function () {
                it('should correctly handle noQuantifier flag for simple expression', function () {
                    const segmentString =
                        "EXISTS ym:s:specialUser WITH (EXISTS(ym:s:paramsLevel1=='level1'))";
                    expect(serialize(parse(segmentString))).toMatch(
                        segmentString,
                    );
                });
                it('should correctly handle noQuantifier flag for complex expression', function () {
                    const segmentString =
                        "EXISTS ym:s:specialUser WITH (EXISTS(ym:s:paramsLevel1=='level1' and" +
                        " ym:s:paramsLevel2=='level2'))";
                    expect(serialize(parse(segmentString))).toMatch(
                        segmentString,
                    );
                });
            });
            describe('with one user-centric date', function () {
                it('should correctly handle noQuantifier flag for simple expression', function () {
                    const segmentString =
                        "EXISTS ym:s:specialUser WITH (EXISTS(ym:s:paramsLevel1=='level1') and" +
                        " ym:s:specialDefaultDate=='2016-03-15')";
                    expect(serialize(parse(segmentString))).toMatch(
                        segmentString,
                    );
                });
                it('should correctly handle noQuantifier flag for complex expression', function () {
                    const segmentString =
                        "EXISTS ym:s:specialUser WITH (EXISTS(ym:s:paramsLevel1=='level1' and" +
                        " ym:s:paramsLevel2=='level2') and" +
                        " ym:s:specialDefaultDate=='2016-03-15')";
                    expect(serialize(parse(segmentString))).toMatch(
                        segmentString,
                    );
                });
            });
            describe('with two user-centric dates', function () {
                it('should correctly handle noQuantifier flag for simple expression', function () {
                    const segmentString =
                        "EXISTS ym:s:specialUser WITH (EXISTS(ym:s:paramsLevel1=='level1') and" +
                        " ym:s:specialDefaultDate>='2016-03-15' and ym:s:specialDefaultDate<='2016-03-17')";
                    expect(serialize(parse(segmentString))).toMatch(
                        segmentString,
                    );
                });
                it('should correctly handle noQuantifier flag for complex expression', function () {
                    const segmentString =
                        "EXISTS ym:s:specialUser WITH (EXISTS(ym:s:paramsLevel1=='level1' and" +
                        " ym:s:paramsLevel2=='level2') and" +
                        " ym:s:specialDefaultDate>='2016-03-15' and ym:s:specialDefaultDate<='2016-03-17')";
                    expect(serialize(parse(segmentString))).toMatch(
                        segmentString,
                    );
                });
            });
        });
        describe('for suggest', function () {
            // в моб. метрике нету саджестов
            // eslint-disable-next-line jest/no-disabled-tests
            it.skip('should handle user-centric dimension without EXISTS wrapper', function () {
                const segmentString = "(ym:up:paramsLevel1=@'level1')";
                expect(serialize(parse(segmentString))).toMatch(segmentString);
            });
        });
    });
});

describe('list segment', function () {
    describe('simple expression', function () {
        it('should parse include expression with regular value', function () {
            const segmentString = "ym:s:browserCountry=='ru'";
            expect(serialize(parse(segmentString))).toMatch(segmentString);
        });
        it('should parse include expression with null value', function () {
            const segmentString = 'ym:s:browserCountry=n';
            expect(serialize(parse(segmentString))).toMatch(segmentString);
        });
        it('should parse exclude expression with regular value', function () {
            const segmentString = "ym:s:browserCountry!='ru'";
            expect(serialize(parse(segmentString))).toMatch(segmentString);
        });
        it('should parse exclude with null value', function () {
            const segmentString = 'ym:s:browserCountry!n';
            expect(serialize(parse(segmentString))).toMatch(segmentString);
        });
    });
    describe('complex expression', function () {
        it('should parse include expression', function () {
            const segmentString =
                "(ym:s:browserCountry=='ru' or ym:s:browserCountry=='us' or ym:s:browserCountry=n)";
            expect(serialize(parse(segmentString))).toMatch(segmentString);
        });
        it('should parse exclude expression', function () {
            const segmentString =
                "ym:s:browserCountry!='ru' and ym:s:browserCountry!='us' and ym:s:browserCountry!n";
            expect(serialize(parse(segmentString))).toMatch(segmentString);
        });
    });
    describe('user-centric mode', function () {
        describe('include mode', function () {
            describe('without dates', function () {
                it('should work with simple expression', function () {
                    const segmentString =
                        'EXISTS ym:s:specialUser WITH (ym:s:regionCitySize==1)';
                    expect(serialize(parse(segmentString))).toMatch(
                        segmentString,
                    );
                });
                it('should work with complex expression', function () {
                    const segmentString =
                        'EXISTS ym:s:specialUser WITH ((ym:s:regionCitySize==1 or ym:s:regionCitySize==2))';
                    expect(serialize(parse(segmentString))).toMatch(
                        segmentString,
                    );
                });
            });
            describe('with one date', function () {
                it('should work with simple expression', function () {
                    const segmentString =
                        'EXISTS ym:s:specialUser WITH (ym:s:regionCitySize==1 and' +
                        " ym:s:specialDefaultDate=='2012-06-05')";
                    expect(serialize(parse(segmentString))).toMatch(
                        segmentString,
                    );
                });
                it('should work with complex expression', function () {
                    const segmentString =
                        'EXISTS ym:s:specialUser WITH ((ym:s:regionCitySize==1 or ym:s:regionCitySize==5) and' +
                        " ym:s:specialDefaultDate=='2012-06-05')";
                    expect(serialize(parse(segmentString))).toMatch(
                        segmentString,
                    );
                });
            });
            describe('with two dates', function () {
                it('should work with simple expression', function () {
                    const segmentString =
                        'EXISTS ym:s:specialUser WITH (ym:s:regionCitySize==1 and' +
                        " ym:s:specialDefaultDate>='2012-06-05' and ym:s:specialDefaultDate<='2012-06-07')";
                    expect(serialize(parse(segmentString))).toMatch(
                        segmentString,
                    );
                });
                it('should work with complex expression', function () {
                    const segmentString =
                        'EXISTS ym:s:specialUser WITH ((ym:s:regionCitySize==1 or ym:s:regionCitySize==5) and' +
                        " ym:s:specialDefaultDate>='2012-06-05' and" +
                        " ym:s:specialDefaultDate<='2012-06-07')";
                    expect(serialize(parse(segmentString))).toMatch(
                        segmentString,
                    );
                });
            });
        });
        describe('exclude mode', function () {
            describe('without dates', function () {
                it('should work with simple expression', function () {
                    const segmentString =
                        'EXISTS ym:s:specialUser WITH (ym:s:regionCitySize!=1)';
                    expect(serialize(parse(segmentString))).toMatch(
                        segmentString,
                    );
                });
                it('should work with complex expression', function () {
                    const segmentString =
                        'EXISTS ym:s:specialUser WITH (ym:s:regionCitySize!=1 and ym:s:regionCitySize!=2)';
                    expect(serialize(parse(segmentString))).toMatch(
                        segmentString,
                    );
                });
            });
            describe('with one date', function () {
                it('should work with simple expression', function () {
                    const segmentString =
                        'EXISTS ym:s:specialUser WITH (ym:s:regionCitySize!=1 and' +
                        " ym:s:specialDefaultDate=='2012-06-05')";
                    expect(serialize(parse(segmentString))).toMatch(
                        segmentString,
                    );
                });
                it('should work with complex expression', function () {
                    const segmentString =
                        'EXISTS ym:s:specialUser WITH (ym:s:regionCitySize!=1 and ym:s:regionCitySize!=5 and' +
                        " ym:s:specialDefaultDate=='2012-06-05')";
                    expect(serialize(parse(segmentString))).toMatch(
                        segmentString,
                    );
                });
            });
            describe('with two dates', function () {
                it('should work with simple expression', function () {
                    const segmentString =
                        'EXISTS ym:s:specialUser WITH (ym:s:regionCitySize!=1 and' +
                        " ym:s:specialDefaultDate>='2012-06-05' and ym:s:specialDefaultDate<='2012-06-07')";
                    expect(serialize(parse(segmentString))).toMatch(
                        segmentString,
                    );
                });
                it('should work with complex expression', function () {
                    const segmentString =
                        'EXISTS ym:s:specialUser WITH (ym:s:regionCitySize!=1 and ym:s:regionCitySize!=5 and' +
                        " ym:s:specialDefaultDate>='2012-06-05' and" +
                        " ym:s:specialDefaultDate<='2012-06-07')";
                    expect(serialize(parse(segmentString))).toMatch(
                        segmentString,
                    );
                });
            });
        });
    });
});

describe('tree segment', function () {
    describe('one level', function () {
        describe('first dimension', function () {
            it('should parse in include mode with one value', function () {
                const segmentString = "ym:s:operatingSystemRoot IN('windows')";
                expect(serialize(parse(segmentString))).toMatch(segmentString);
            });
            it('should parse in include mode with many values', function () {
                const segmentString =
                    "ym:s:operatingSystemRoot IN('windows', 'linux')";
                expect(serialize(parse(segmentString))).toMatch(segmentString);
            });
            it('should parse in exclude mode with one value', function () {
                const segmentString =
                    "ym:s:operatingSystemRoot NOT IN('windows')";
                expect(serialize(parse(segmentString))).toMatch(segmentString);
            });
            it('should parse in exclude mode with many values', function () {
                const segmentString =
                    "ym:s:operatingSystemRoot NOT IN('windows', 'linux')";
                expect(serialize(parse(segmentString))).toMatch(segmentString);
            });
        });
        describe('not first dimension', function () {
            it('should parse in include mode with one value', function () {
                const segmentString = "ym:s:operatingSystem IN('windows xp')";
                expect(serialize(parse(segmentString))).toMatch(segmentString);
            });
            it('should parse in include mode with many values', function () {
                const segmentString =
                    "ym:s:operatingSystem IN('windows xp', 'linux debian')";
                expect(serialize(parse(segmentString))).toMatch(segmentString);
            });
            it('should parse in exclude mode with one value', function () {
                const segmentString =
                    "ym:s:operatingSystem NOT IN('windows xp')";
                expect(serialize(parse(segmentString))).toMatch(segmentString);
            });
            it('should parse in exclude mode with many values', function () {
                const segmentString =
                    "ym:s:operatingSystem NOT IN('windows xp', 'linux debian')";
                expect(serialize(parse(segmentString))).toMatch(segmentString);
            });
        });
    });
    describe('multi level', function () {
        it('one value and one value in include mode', function () {
            const segmentString =
                "ym:s:operatingSystemRoot IN('windows') or ym:s:operatingSystem IN('windows xp')";
            expect(serialize(parse(segmentString))).toMatch(segmentString);
        });
        it('one value and many values in include mode', function () {
            const segmentString =
                "ym:s:operatingSystemRoot IN('windows') or" +
                " ym:s:operatingSystem IN('windows xp', 'linux debian')";
            expect(serialize(parse(segmentString))).toMatch(segmentString);
        });
        it('many values and many values in include mode', function () {
            const segmentString =
                "ym:s:operatingSystemRoot IN('windows', 'linux') or" +
                " ym:s:operatingSystem IN('windows xp', 'linux debian')";
            expect(serialize(parse(segmentString))).toMatch(segmentString);
        });
        it('many values and one value in include mode', function () {
            const segmentString =
                "ym:s:operatingSystemRoot IN('windows', 'linux') or ym:s:operatingSystem IN('windows xp')";
            expect(serialize(parse(segmentString))).toMatch(segmentString);
        });
        it('one value and one value in exclude mode', function () {
            const segmentString =
                "ym:s:operatingSystemRoot NOT IN('windows') and ym:s:operatingSystem NOT IN('windows xp')";
            expect(serialize(parse(segmentString))).toMatch(segmentString);
        });
        it('one value and many values in exclude mode', function () {
            const segmentString =
                "ym:s:operatingSystemRoot NOT IN('windows') and" +
                " ym:s:operatingSystem NOT IN('windows xp', 'linux debian')";
            expect(serialize(parse(segmentString))).toMatch(segmentString);
        });
        it('many values and many values in exclude mode', function () {
            const segmentString =
                "ym:s:operatingSystemRoot NOT IN('windows', 'linux') and" +
                " ym:s:operatingSystem NOT IN('windows xp', 'linux debian')";
            expect(serialize(parse(segmentString))).toMatch(segmentString);
        });
        it('many values and one value in exclude mode', function () {
            const segmentString =
                "ym:s:operatingSystemRoot NOT IN('windows', 'linux') and" +
                " ym:s:operatingSystem NOT IN('windows xp')";
            expect(serialize(parse(segmentString))).toMatch(segmentString);
        });
    });
    describe('user-centric', function () {
        describe('one level', function () {
            describe('include mode', function () {
                it('should work without user-centric dates', function () {
                    const segmentString =
                        'EXISTS ym:s:specialUser WITH (' +
                        "ym:s:operatingSystemRoot IN('windows', 'linux')" +
                        ')';
                    expect(serialize(parse(segmentString))).toMatch(
                        segmentString,
                    );
                });
                it('should work with user-centric dates', function () {
                    const segmentString =
                        'EXISTS ym:s:specialUser WITH (' +
                        "ym:s:operatingSystemRoot IN('windows', 'linux') and" +
                        " ym:s:specialDefaultDate>='2015-04-05' and ym:s:specialDefaultDate<='2015-05-07'" +
                        ')';
                    expect(serialize(parse(segmentString))).toMatch(
                        segmentString,
                    );
                });
            });
            describe('exclude mode', function () {
                it('should work without user-centric dates', function () {
                    const segmentString =
                        'EXISTS ym:s:specialUser WITH (' +
                        "ym:s:operatingSystemRoot NOT IN('windows', 'linux')" +
                        ')';
                    expect(serialize(parse(segmentString))).toMatch(
                        segmentString,
                    );
                });
                it('should work with user-centric dates', function () {
                    const segmentString =
                        'EXISTS ym:s:specialUser WITH (' +
                        "ym:s:operatingSystemRoot NOT IN('windows', 'linux') and" +
                        " ym:s:specialDefaultDate>='2015-04-05' and ym:s:specialDefaultDate<='2015-05-07'" +
                        ')';
                    expect(serialize(parse(segmentString))).toMatch(
                        segmentString,
                    );
                });
            });
        });
        describe('multi level', function () {
            describe('include mode', function () {
                it('should work without user-centric dates', function () {
                    const segmentString =
                        'EXISTS ym:s:specialUser WITH ((' +
                        "ym:s:operatingSystemRoot IN('windows', 'linux') or" +
                        " ym:s:operatingSystem IN('windows xp', 'linux debian')" +
                        '))';
                    expect(serialize(parse(segmentString))).toMatch(
                        segmentString,
                    );
                });
                it('should work with user-centric dates', function () {
                    const segmentString =
                        'EXISTS ym:s:specialUser WITH (' +
                        "(ym:s:operatingSystemRoot IN('windows', 'linux') or" +
                        " ym:s:operatingSystem IN('windows xp', 'linux debian')) and" +
                        " ym:s:specialDefaultDate>='2015-04-05' and ym:s:specialDefaultDate<='2015-05-07'" +
                        ')';
                    expect(serialize(parse(segmentString))).toMatch(
                        segmentString,
                    );
                });
            });
            describe('exclude mode', function () {
                it('should work without user-centric dates', function () {
                    const segmentString =
                        'EXISTS ym:s:specialUser WITH (' +
                        "ym:s:operatingSystemRoot NOT IN('windows', 'linux') and" +
                        " ym:s:operatingSystem NOT IN('windows xp', 'linux debian')" +
                        ')';
                    expect(serialize(parse(segmentString))).toMatch(
                        segmentString,
                    );
                });
                it('should work with user-centric dates', function () {
                    const segmentString =
                        'EXISTS ym:s:specialUser WITH (' +
                        "ym:s:operatingSystemRoot NOT IN('windows', 'linux') and" +
                        " ym:s:operatingSystem NOT IN('windows xp', 'linux debian') and" +
                        " ym:s:specialDefaultDate>='2015-04-05' and ym:s:specialDefaultDate<='2015-05-07'" +
                        ')';
                    expect(serialize(parse(segmentString))).toMatch(
                        segmentString,
                    );
                });
            });
        });
    });
});

describe('path segment', function () {
    describe('include mode', function () {
        describe('one dimension expression', function () {
            it('shold work with regular value', function () {
                const segmentString = 'ym:s:deviceCategory==1';
                expect(serialize(parse(segmentString))).toMatch(segmentString);
            });
            it('shold work with null value', function () {
                const segmentString = 'ym:s:deviceCategory=n';
                expect(serialize(parse(segmentString))).toMatch(segmentString);
            });
            it('should work with two and more values', function () {
                const segmentString =
                    '(ym:s:deviceCategory==1 or ym:s:deviceCategory=n)';
                expect(serialize(parse(segmentString))).toMatch(segmentString);
            });
        });
        describe('multi dimension expression', function () {
            it('should work with one multidimension expression', function () {
                const segmentString =
                    'ym:s:deviceCategory==2 and ym:s:mobilePhone==5';
                expect(serialize(parse(segmentString))).toMatch(segmentString);
            });
            it('should work with one or many', function () {
                const segmentString =
                    'ym:s:deviceCategory==1 or ym:s:deviceCategory==2 and ym:s:mobilePhone==5';
                expect(serialize(parse(segmentString))).toMatch(segmentString);
            });
            it('should work with many or one', function () {
                const segmentString =
                    'ym:s:deviceCategory==1 and ym:s:mobilePhone==7 or ym:s:deviceCategory==2';
                expect(serialize(parse(segmentString))).toMatch(segmentString);
            });
            it('should work with many or many', function () {
                const segmentString =
                    '(ym:s:deviceCategory==1 and ym:s:mobilePhone==7 or ym:s:deviceCategory==2 and ym:s:mobilePhone==5)';
                expect(serialize(parse(segmentString))).toMatch(segmentString);
            });
        });
    });
    describe('exclude mode', function () {
        describe('one dimension expression', function () {
            it('shold work with regular value', function () {
                const segmentString = 'ym:s:deviceCategory!=1';
                expect(serialize(parse(segmentString))).toMatch(segmentString);
            });
            it('shold work with null value', function () {
                const segmentString = 'ym:s:deviceCategory!n';
                expect(serialize(parse(segmentString))).toMatch(segmentString);
            });
            it('should work with two and more values', function () {
                const segmentString =
                    'ym:s:deviceCategory!=1 and ym:s:deviceCategory!n';
                expect(serialize(parse(segmentString))).toMatch(segmentString);
            });
        });
        describe('multi dimension expression', function () {
            it('should work with one multidimension expression', function () {
                const segmentString =
                    'ym:s:deviceCategory!=2 or ym:s:mobilePhone!=5';
                expect(serialize(parse(segmentString))).toMatch(segmentString);
            });
            it('should work with one or many', function () {
                const segmentString =
                    '(ym:s:deviceCategory!=1 and (ym:s:deviceCategory!=2 or ym:s:mobilePhone!=5))';
                expect(serialize(parse(segmentString))).toMatch(segmentString);
            });
            it('should work with many or one', function () {
                const segmentString =
                    '((ym:s:deviceCategory!=1 or ym:s:mobilePhone!=7) and ym:s:deviceCategory!=2)';
                expect(serialize(parse(segmentString))).toMatch(segmentString);
            });
            it('should work with many or many', function () {
                const segmentString =
                    '((ym:s:deviceCategory!=1 or ym:s:mobilePhone!=7) and' +
                    ' (ym:s:deviceCategory!=2 or ym:s:mobilePhone!=5))';
                expect(serialize(parse(segmentString))).toMatch(segmentString);
            });
        });
    });
    describe('user-centric mode', function () {
        describe('include mode', function () {
            describe('one dimension expression', function () {
                it('should work without user-centric dates', function () {
                    const segmentString =
                        'EXISTS ym:s:specialUser WITH ((ym:s:deviceCategory==1 or ym:s:deviceCategory=n))';
                    expect(serialize(parse(segmentString))).toMatch(
                        segmentString,
                    );
                });
                it('should work with user-centric dates', function () {
                    const segmentString =
                        'EXISTS ym:s:specialUser WITH ((ym:s:deviceCategory==1 or ym:s:deviceCategory=n) and' +
                        " ym:s:specialDefaultDate>='2014-12-14' and" +
                        " ym:s:specialDefaultDate<='2016-01-01')";
                    expect(serialize(parse(segmentString))).toMatch(
                        segmentString,
                    );
                });
            });
            describe('multi dimension expression', function () {
                describe('without dates', function () {
                    it('should work with one multidimension expression', function () {
                        const segmentString =
                            'EXISTS ym:s:specialUser WITH (ym:s:deviceCategory==2 and ym:s:mobilePhone==5)';
                        expect(serialize(parse(segmentString))).toMatch(
                            segmentString,
                        );
                    });
                    it('should work with one or many', function () {
                        const segmentString =
                            'EXISTS ym:s:specialUser WITH ((' +
                            'ym:s:deviceCategory==1 or ym:s:deviceCategory==2 and ym:s:mobilePhone==5' +
                            '))';
                        expect(serialize(parse(segmentString))).toMatch(
                            segmentString,
                        );
                    });
                    it('should work with many or one', function () {
                        const segmentString =
                            'EXISTS ym:s:specialUser WITH ((' +
                            'ym:s:deviceCategory==1 and ym:s:mobilePhone==7 or ym:s:deviceCategory==2' +
                            '))';
                        expect(serialize(parse(segmentString))).toMatch(
                            segmentString,
                        );
                    });
                    it('should work with many or many', function () {
                        const segmentString =
                            'EXISTS ym:s:specialUser WITH ((' +
                            'ym:s:deviceCategory==1 and ym:s:mobilePhone==7 or ' +
                            'ym:s:deviceCategory==2 and ym:s:mobilePhone==5' +
                            '))';
                        expect(serialize(parse(segmentString))).toMatch(
                            segmentString,
                        );
                    });
                });
                describe('with dates', function () {
                    it('should work with one multidimension expression', function () {
                        const segmentString =
                            'EXISTS ym:s:specialUser WITH (' +
                            'ym:s:deviceCategory==2 and ym:s:mobilePhone==5 and' +
                            " ym:s:specialDefaultDate>='2012-12-12' and" +
                            " ym:s:specialDefaultDate<='2012-12-15'" +
                            ')';
                        expect(serialize(parse(segmentString))).toMatch(
                            segmentString,
                        );
                    });
                    it('should work with one or many', function () {
                        const segmentString =
                            'EXISTS ym:s:specialUser WITH (' +
                            '(ym:s:deviceCategory==1 or ym:s:deviceCategory==2 and ym:s:mobilePhone==5) and' +
                            " ym:s:specialDefaultDate>='2012-12-12' and" +
                            " ym:s:specialDefaultDate<='2012-12-15'" +
                            ')';
                        expect(serialize(parse(segmentString))).toMatch(
                            segmentString,
                        );
                    });
                    it('should work with many or one', function () {
                        const segmentString =
                            'EXISTS ym:s:specialUser WITH (' +
                            '(ym:s:deviceCategory==1 and ym:s:mobilePhone==7 or ym:s:deviceCategory==2) and' +
                            " ym:s:specialDefaultDate>='2012-12-12' and" +
                            " ym:s:specialDefaultDate<='2012-12-15'" +
                            ')';
                        expect(serialize(parse(segmentString))).toMatch(
                            segmentString,
                        );
                    });
                    it('should work with many or many', function () {
                        const segmentString =
                            'EXISTS ym:s:specialUser WITH (' +
                            '(ym:s:deviceCategory==1 and ym:s:mobilePhone==7 or' +
                            ' ym:s:deviceCategory==2 and ym:s:mobilePhone==5) and' +
                            " ym:s:specialDefaultDate>='2012-12-12' and" +
                            " ym:s:specialDefaultDate<='2012-12-15'" +
                            ')';
                        expect(serialize(parse(segmentString))).toMatch(
                            segmentString,
                        );
                    });
                });
            });
        });
        describe('exclude mode', function () {
            describe('one dimension expression', function () {
                it('should work without user-centric dates', function () {
                    const segmentString =
                        'EXISTS ym:s:specialUser WITH (ym:s:deviceCategory!=1 and ym:s:deviceCategory!n)';
                    expect(serialize(parse(segmentString))).toMatch(
                        segmentString,
                    );
                });
                it('should work with user-centric dates', function () {
                    const segmentString =
                        'EXISTS ym:s:specialUser WITH (ym:s:deviceCategory!=1 and ym:s:deviceCategory!n and' +
                        " ym:s:specialDefaultDate>='2014-12-14' and" +
                        " ym:s:specialDefaultDate<='2016-01-01')";
                    expect(serialize(parse(segmentString))).toMatch(
                        segmentString,
                    );
                });
            });
            describe('multi dimension expression', function () {
                describe('without dates', function () {
                    it('should work with one multidimension expression', function () {
                        const segmentString =
                            'EXISTS ym:s:specialUser WITH ((ym:s:deviceCategory!=2 or ym:s:mobilePhone!=5))';
                        expect(serialize(parse(segmentString))).toMatch(
                            segmentString,
                        );
                    });
                    it('should work with one or many', function () {
                        const segmentString =
                            'EXISTS ym:s:specialUser WITH (' +
                            'ym:s:deviceCategory!=1 and (ym:s:deviceCategory!=2 or ym:s:mobilePhone!=5)' +
                            ')';
                        expect(serialize(parse(segmentString))).toMatch(
                            segmentString,
                        );
                    });
                    it('should work with many or one', function () {
                        const segmentString =
                            'EXISTS ym:s:specialUser WITH (' +
                            '(ym:s:deviceCategory!=1 or ym:s:mobilePhone!=7) and ym:s:deviceCategory!=2' +
                            ')';
                        expect(serialize(parse(segmentString))).toMatch(
                            segmentString,
                        );
                    });
                    it('should work with many or many', function () {
                        const segmentString =
                            'EXISTS ym:s:specialUser WITH (' +
                            '(ym:s:deviceCategory!=1 or ym:s:mobilePhone!=7) and' +
                            ' (ym:s:deviceCategory!=2 or ym:s:mobilePhone!=5)' +
                            ')';
                        expect(serialize(parse(segmentString))).toMatch(
                            segmentString,
                        );
                    });
                });
                describe('with dates', function () {
                    it('should work with one multidimension expression', function () {
                        const segmentString =
                            'EXISTS ym:s:specialUser WITH (' +
                            '(ym:s:deviceCategory!=2 or ym:s:mobilePhone!=5) and' +
                            " ym:s:specialDefaultDate>='2012-12-12' and" +
                            " ym:s:specialDefaultDate<='2012-12-15'" +
                            ')';
                        expect(serialize(parse(segmentString))).toMatch(
                            segmentString,
                        );
                    });
                    it('should work with one or many', function () {
                        const segmentString =
                            'EXISTS ym:s:specialUser WITH (' +
                            'ym:s:deviceCategory!=1 and (ym:s:deviceCategory!=2 or ym:s:mobilePhone!=5) and' +
                            " ym:s:specialDefaultDate>='2012-12-12' and" +
                            " ym:s:specialDefaultDate<='2012-12-15'" +
                            ')';
                        expect(serialize(parse(segmentString))).toMatch(
                            segmentString,
                        );
                    });
                    it('should work with many or one', function () {
                        const segmentString =
                            'EXISTS ym:s:specialUser WITH (' +
                            '(ym:s:deviceCategory!=1 or ym:s:mobilePhone!=7) and ym:s:deviceCategory!=2 and' +
                            " ym:s:specialDefaultDate>='2012-12-12' and" +
                            " ym:s:specialDefaultDate<='2012-12-15'" +
                            ')';
                        expect(serialize(parse(segmentString))).toMatch(
                            segmentString,
                        );
                    });
                    it('should work with many or many', function () {
                        const segmentString =
                            'EXISTS ym:s:specialUser WITH (' +
                            '(ym:s:deviceCategory!=1 or ym:s:mobilePhone!=7) and' +
                            ' (ym:s:deviceCategory!=2 or ym:s:mobilePhone!=5) and' +
                            " ym:s:specialDefaultDate>='2012-12-12' and" +
                            " ym:s:specialDefaultDate<='2012-12-15'" +
                            ')';
                        expect(serialize(parse(segmentString))).toMatch(
                            segmentString,
                        );
                    });
                });
            });
        });
    });
});
