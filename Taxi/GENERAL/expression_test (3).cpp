#include "expression.hpp"

#include <gtest/gtest.h>

namespace eats_menu_categories::expression {

using PredicateSource = handlers::Predicate;
using ValueTypeSource = handlers::ValueType;
using handlers::Argument;
using handlers::PredicateInit;
using handlers::PredicateType;

namespace {
struct TestCase {
  // Название кейса
  const std::string name{};
  // Предикат
  const PredicateSource predicate{};
  // Аргументы
  const Arguments args{};
  // Ожидаемый результат
  const bool expected{};
};

}  // namespace

TEST(Eval, NEQ) {
  std::unordered_set<std::variant<std::string, int>> set_one;
  {
    set_one.insert(2);
    set_one.insert("2");
    set_one.insert(3);
    set_one.insert(" 3");
    set_one.insert("abc");
  }

  std::unordered_set<std::variant<std::string, int>> set_two;
  {
    set_two.insert(2);
    set_two.insert("1");
    set_two.insert(3);
  }

  std::vector<TestCase> cases = {
      TestCase{
          "1 != 2",  // name
          PredicateSource{
              PredicateType::kNeq,  // type
              PredicateInit{
                  Argument::kPlaceId,          // arg_name
                  ValueTypeSource::kInt,       // arg_type
                  1,                           // value
              }                                // init
          },                                   // predicate
          Arguments{{Argument::kPlaceId, 2}},  // args
          true,                                // expected
      },
      TestCase{
          "1 != 1",  // name
          PredicateSource{
              PredicateType::kNeq,  // type
              PredicateInit{
                  Argument::kPlaceId,          // arg_name
                  ValueTypeSource::kInt,       // arg_type
                  1,                           // value
              }                                // init
          },                                   // predicate
          Arguments{{Argument::kPlaceId, 1}},  // args
          false,                               // expected
      },
      TestCase{
          "'1' != '1'",  // name
          PredicateSource{
              PredicateType::kNeq,  // type
              PredicateInit{
                  Argument::kPlaceId,            // arg_name
                  ValueTypeSource::kString,      // arg_type
                  "1",                           // value
              }                                  // init
          },                                     // predicate
          Arguments{{Argument::kPlaceId, "1"}},  // args
          false,                                 // expected
      },
      TestCase{
          "100 != '100' (type missmatch always true)",  // name
          PredicateSource{
              PredicateType::kNeq,  // type
              PredicateInit{
                  Argument::kPlaceId,              // arg_name
                  ValueTypeSource::kInt,           // arg_type
                  "100",                           // value
              }                                    // init
          },                                       // predicate
          Arguments{{Argument::kPlaceId, "100"}},  // args
          true,                                    // expected
      },
      TestCase{
          "[2, '3', 3, ' 3', 'abc'] != [2, 3]",  // name
          PredicateSource{
              PredicateType::kNeq,  // type
              PredicateInit{
                  Argument::kPlaceId,                         // arg_name
                  std::nullopt,                               // arg_type
                  std::nullopt,                               // value
                  ValueTypeSource::kInt,                      // set_elem_type
                  set_one,                                    // set
              }                                               // init
          },                                                  // predicate
          Arguments{{Argument::kPlaceId, SetIntType{2, 3}}},  // args
          false,                                              // expected
      },
      TestCase{
          "[2, '1', 3] != [2, 3]",  // name
          PredicateSource{
              PredicateType::kNeq,  // type
              PredicateInit{
                  Argument::kPlaceId,                         // arg_name
                  std::nullopt,                               // arg_type
                  std::nullopt,                               // value
                  ValueTypeSource::kInt,                      // set_elem_type
                  set_two,                                    // set
              }                                               // init
          },                                                  // predicate
          Arguments{{Argument::kPlaceId, SetIntType{2, 3}}},  // args
          true,                                               // expected
      },
  };

  for (const auto& test_case : cases) {
    bool actual = Eval(test_case.predicate, test_case.args);
    EXPECT_EQ(test_case.expected, actual) << test_case.name;
  }
}

TEST(Eval, EQ) {
  std::unordered_set<std::variant<std::string, int>> set_one;
  {
    set_one.insert(2);
    set_one.insert("2");
    set_one.insert(3);
    set_one.insert(" 3");
    set_one.insert("abc");
  }

  std::unordered_set<std::variant<std::string, int>> set_two;
  {
    set_two.insert(2);
    set_two.insert("1");
    set_two.insert(3);
  }

  std::vector<TestCase> cases = {
      TestCase{
          "1 == 2",  // name
          PredicateSource{
              PredicateType::kEq,  // type
              PredicateInit{
                  Argument::kPlaceId,          // arg_name
                  ValueTypeSource::kInt,       // arg_type
                  1,                           // value
              }                                // init
          },                                   // predicate
          Arguments{{Argument::kPlaceId, 2}},  // args
          false,                               // expected
      },
      TestCase{
          "1 == 1",  // name
          PredicateSource{
              PredicateType::kEq,  // type
              PredicateInit{
                  Argument::kPlaceId,          // arg_name
                  ValueTypeSource::kInt,       // arg_type
                  1,                           // value
              }                                // init
          },                                   // predicate
          Arguments{{Argument::kPlaceId, 1}},  // args
          true,                                // expected
      },
      TestCase{
          "'1' == '1'",  // name
          PredicateSource{
              PredicateType::kEq,  // type
              PredicateInit{
                  Argument::kPlaceId,            // arg_name
                  ValueTypeSource::kString,      // arg_type
                  "1",                           // value
              }                                  // init
          },                                     // predicate
          Arguments{{Argument::kPlaceId, "1"}},  // args
          true,                                  // expected
      },
      TestCase{
          "100 != '100' (type missmatch always false)",  // name
          PredicateSource{
              PredicateType::kEq,  // type
              PredicateInit{
                  Argument::kPlaceId,              // arg_name
                  ValueTypeSource::kInt,           // arg_type
                  "100",                           // value
              }                                    // init
          },                                       // predicate
          Arguments{{Argument::kPlaceId, "100"}},  // args
          false,                                   // expected
      },
      TestCase{
          "[2, '3', 3, ' 3', 'abc']  == [2, 3]",  // name
          PredicateSource{
              PredicateType::kEq,  // type
              PredicateInit{
                  Argument::kPlaceId,                         // arg_name
                  std::nullopt,                               // arg_type
                  std::nullopt,                               // value
                  ValueTypeSource::kInt,                      // set_elem_type
                  set_one,                                    // set
              }                                               // init
          },                                                  // predicate
          Arguments{{Argument::kPlaceId, SetIntType{2, 3}}},  // args
          true,                                               // expected
      },
      TestCase{
          "[2, '1', 3] != [2, 3]",  // name
          PredicateSource{
              PredicateType::kEq,  // type
              PredicateInit{
                  Argument::kPlaceId,                         // arg_name
                  std::nullopt,                               // arg_type
                  std::nullopt,                               // value
                  ValueTypeSource::kInt,                      // set_elem_type
                  set_two,                                    // set
              }                                               // init
          },                                                  // predicate
          Arguments{{Argument::kPlaceId, SetIntType{2, 3}}},  // args
          false,                                              // expected
      },

  };

  for (const auto& test_case : cases) {
    bool actual = Eval(test_case.predicate, test_case.args);
    EXPECT_EQ(test_case.expected, actual) << test_case.name;
  }
}

TEST(Eval, Matches) {
  std::unordered_set<std::variant<std::string, int>> set_one;
  {
    set_one.insert(2);
    set_one.insert("2");
    set_one.insert(3);
    set_one.insert(" 3");
    set_one.insert("abc");
  }

  std::unordered_set<std::variant<std::string, int>> set_two;
  {
    set_two.insert(2);
    set_two.insert("1");
    set_two.insert(3);
  }

  std::vector<TestCase> cases = {
      TestCase{
          "1 == 2",  // name
          PredicateSource{
              PredicateType::kMatches,  // type
              PredicateInit{
                  Argument::kPlaceId,          // arg_name
                  ValueTypeSource::kInt,       // arg_type
                  1,                           // value
              }                                // init
          },                                   // predicate
          Arguments{{Argument::kPlaceId, 2}},  // args
          false,                               // expected
      },
      TestCase{
          "1 == 1",  // name
          PredicateSource{
              PredicateType::kMatches,  // type
              PredicateInit{
                  Argument::kPlaceId,          // arg_name
                  ValueTypeSource::kInt,       // arg_type
                  1,                           // value
              }                                // init
          },                                   // predicate
          Arguments{{Argument::kPlaceId, 1}},  // args
          true,                                // expected
      },
      TestCase{
          "'101*' ~ '1'",  // name
          PredicateSource{
              PredicateType::kMatches,  // type
              PredicateInit{
                  Argument::kPlaceId,                 // arg_name
                  ValueTypeSource::kString,           // arg_type
                  "^101.+",                           // value
              }                                       // init
          },                                          // predicate
          Arguments{{Argument::kPlaceId, "101029"}},  // args
          true,                                       // expected
      },
      TestCase{
          "100 != '100' (type missmatch always false)",  // name
          PredicateSource{
              PredicateType::kMatches,  // type
              PredicateInit{
                  Argument::kPlaceId,              // arg_name
                  ValueTypeSource::kInt,           // arg_type
                  "100",                           // value
              }                                    // init
          },                                       // predicate
          Arguments{{Argument::kPlaceId, "100"}},  // args
          false,                                   // expected
      },
      TestCase{
          "[2, '3', 3, ' 3', 'abc']  == [2, 3]",  // name
          PredicateSource{
              PredicateType::kMatches,  // type
              PredicateInit{
                  Argument::kPlaceId,                         // arg_name
                  std::nullopt,                               // arg_type
                  std::nullopt,                               // value
                  ValueTypeSource::kInt,                      // set_elem_type
                  set_one,                                    // set
              }                                               // init
          },                                                  // predicate
          Arguments{{Argument::kPlaceId, SetIntType{2, 3}}},  // args
          true,                                               // expected

      },
      TestCase{
          "[2, '1', 3] != [2, 3]",  // name
          PredicateSource{
              PredicateType::kMatches,  // type
              PredicateInit{
                  Argument::kPlaceId,                         // arg_name
                  std::nullopt,                               // arg_type
                  std::nullopt,                               // value
                  ValueTypeSource::kInt,                      // set_elem_type
                  set_two,                                    // set
              }                                               // init
          },                                                  // predicate
          Arguments{{Argument::kPlaceId, SetIntType{2, 3}}},  // args
          false,                                              // expected
      },
      TestCase{
          "'..llo.\\w+' ~ 'hello world'",  // name
          PredicateSource{
              PredicateType::kMatches,  // type
              PredicateInit{
                  Argument::kPlaceId,                      // arg_name
                  ValueTypeSource::kString,                // arg_type
                  "..llo.\\w+",                            // value
              }                                            // init
          },                                               // predicate
          Arguments{{Argument::kPlaceId, "hello world"}},  // args
          true,                                            // expected
      },
      TestCase{
          "'..llo.\\w+' !~ 'goodbye world'",  // name
          PredicateSource{
              PredicateType::kMatches,  // type
              PredicateInit{
                  Argument::kPlaceId,                        // arg_name
                  ValueTypeSource::kString,                  // arg_type
                  "..llo.\\w+",                              // value
              }                                              // init
          },                                                 // predicate
          Arguments{{Argument::kPlaceId, "goodbye world"}},  // args
          false,                                             // expected
      },
      TestCase{
          "'.*foo.*' ~ 'bar foo some'",  // name
          PredicateSource{
              PredicateType::kMatches,  // type
              PredicateInit{
                  Argument::kPlaceId,                       // arg_name
                  ValueTypeSource::kString,                 // arg_type
                  ".*foo.*",                                // value
              }                                             // init
          },                                                // predicate
          Arguments{{Argument::kPlaceId, "bar foo some"}},  // args
          true,                                             // expected
      },
      TestCase{
          "'.*foo.*' !~ 'bar bar some'",  // name
          PredicateSource{
              PredicateType::kMatches,  // type
              PredicateInit{
                  Argument::kPlaceId,                       // arg_name
                  ValueTypeSource::kString,                 // arg_type
                  ".*foo.*",                                // value
              }                                             // init
          },                                                // predicate
          Arguments{{Argument::kPlaceId, "bar bar some"}},  // args
          false,                                            // expected
      },
  };

  for (const auto& test_case : cases) {
    bool actual = Eval(test_case.predicate, test_case.args);
    EXPECT_EQ(test_case.expected, actual) << test_case.name;
  }
}

TEST(Eval, NotInSet) {
  std::unordered_set<std::variant<std::string, int>> set;
  set.insert(1);
  set.insert(" 1");
  set.insert(121);

  const PredicateSource predicate{
      PredicateType::kInSet,  // type
      PredicateInit{
          Argument::kPlaceId,     // arg_name
          std::nullopt,           // arg_type
          std::nullopt,           // value
          ValueTypeSource::kInt,  // set_elem_type
          set,
      }  // init
  };

  const Arguments args{{Argument::kPlaceId, 2}};

  bool actual = Eval(predicate, args);
  ASSERT_EQ(false, actual);
}

TEST(Eval, InSetSimple) {
  std::unordered_set<std::variant<std::string, int>> set;
  set.insert(2);
  set.insert("2");
  set.insert(3);
  set.insert(" 3");
  set.insert("abc");

  const PredicateSource predicate{
      PredicateType::kInSet,  // type
      PredicateInit{
          Argument::kPlaceId,     // arg_name
          std::nullopt,           // arg_type
          std::nullopt,           // value
          ValueTypeSource::kInt,  // set_elem_type
          set,
      }  // init
  };

  const Arguments args{{Argument::kPlaceId, 2}};

  bool actual = Eval(predicate, args);
  ASSERT_EQ(true, actual);
}

TEST(Eval, InSetSimpleString) {
  std::unordered_set<std::variant<std::string, int>> set;
  set.insert(2);
  set.insert("2");
  set.insert(3);
  set.insert(" 3");
  set.insert("abc");

  const PredicateSource predicate{
      PredicateType::kInSet,  // type
      PredicateInit{
          Argument::kPlaceId,        // arg_name
          std::nullopt,              // arg_type
          std::nullopt,              // value
          ValueTypeSource::kString,  // set_elem_type
          set,
      }  // init
  };

  const Arguments args{{Argument::kPlaceId, "abc"}};

  bool actual = Eval(predicate, args);
  ASSERT_EQ(true, actual);
}

TEST(Eval, AllOf) {
  std::vector<PredicateSource> predicates;

  {
    std::unordered_set<std::variant<std::string, int>> set;
    set.insert(2);
    set.insert("2");
    set.insert(3);
    set.insert(" 3");
    set.insert("abc");

    predicates.push_back(PredicateSource{
        PredicateType::kInSet,  // type
        PredicateInit{
            Argument::kPlaceId,        // arg_name
            std::nullopt,              // arg_type
            std::nullopt,              // value
            ValueTypeSource::kString,  // set_elem_type
            set,
        }  // init
    });
  }
  {
    predicates.push_back(PredicateSource{
        PredicateType::kEq,  // type
        PredicateInit{
            Argument::kItemId,         // arg_name
            ValueTypeSource::kString,  // arg_type
            "hello",                   // value
        }                              // init
    });
  }

  PredicateSource main;
  main.type = PredicateType::kAllOf;
  main.predicates = predicates;

  bool actual = Eval(main, Arguments{
                               {Argument::kPlaceId, " 3"},
                               {Argument::kItemId, "hello"},
                           });
  ASSERT_EQ(true, actual);
}

TEST(Eval, NotAllOf) {
  std::vector<PredicateSource> predicates;

  {
    std::unordered_set<std::variant<std::string, int>> set;
    set.insert(2);
    set.insert("2");
    set.insert(3);
    set.insert(" 3");
    set.insert("abc");

    predicates.push_back(PredicateSource{
        PredicateType::kInSet,  // type
        PredicateInit{
            Argument::kPlaceId,        // arg_name
            std::nullopt,              // arg_type
            std::nullopt,              // value
            ValueTypeSource::kString,  // set_elem_type
            set,
        }  // init
    });
  }
  {
    predicates.push_back(PredicateSource{
        PredicateType::kEq,  // type
        PredicateInit{
            Argument::kItemId,         // arg_name
            ValueTypeSource::kString,  // arg_type
            "world",                   // value
        }                              // init
    });
  }

  PredicateSource main;
  main.type = PredicateType::kAllOf;
  main.predicates = predicates;

  bool actual = Eval(main, Arguments{
                               {Argument::kPlaceId, " 3"},
                               {Argument::kItemId, "hello"},
                           });
  ASSERT_EQ(false, actual);
}

TEST(Eval, AnyOf) {
  std::vector<PredicateSource> predicates;

  {
    predicates.push_back(PredicateSource{
        PredicateType::kInSet,  // type
        PredicateInit{
            Argument::kPlaceId,     // arg_name
            ValueTypeSource::kInt,  // arg_type
            1,                      // value
        }                           // init
    });
  }
  {
    predicates.push_back(PredicateSource{
        PredicateType::kEq,  // type
        PredicateInit{
            Argument::kItemId,         // arg_name
            ValueTypeSource::kString,  // arg_type
            "hello",                   // value
        }                              // init
    });
  }
  PredicateSource main;
  main.type = PredicateType::kAnyOf;
  main.predicates = predicates;

  bool actual = Eval(main, Arguments{
                               {Argument::kPlaceId, " 3"},
                               {Argument::kItemId, "hello"},
                           });
  ASSERT_EQ(true, actual);
}

TEST(Eval, NoneOf) {
  std::vector<PredicateSource> predicates;

  {
    predicates.push_back(PredicateSource{
        PredicateType::kInSet,  // type
        PredicateInit{
            Argument::kPlaceId,     // arg_name
            ValueTypeSource::kInt,  // arg_type
            1,                      // value
        }                           // init
    });
  }
  {
    predicates.push_back(PredicateSource{
        PredicateType::kEq,  // type
        PredicateInit{
            Argument::kItemId,         // arg_name
            ValueTypeSource::kString,  // arg_type
            "world",                   // value
        }                              // init
    });
  }
  PredicateSource main;
  main.type = PredicateType::kAnyOf;
  main.predicates = predicates;

  bool actual = Eval(main, Arguments{
                               {Argument::kPlaceId, " 3"},
                               {Argument::kItemId, "hello"},
                           });
  ASSERT_EQ(false, actual);
}

TEST(Eval, ItemIdsIntersects) {
  const std::unordered_set<std::variant<std::string, int>> set{1, 2, 3, 4, 5};
  const PredicateSource predicate{
      PredicateType::kIntersects,  // type
      PredicateInit{
          Argument::kItemId,      // arg_name
          std::nullopt,           // arg_type
          std::nullopt,           // value
          ValueTypeSource::kInt,  // set_elem_type
          set,                    // set
      },                          // init
  };

  const Arguments args{{Argument::kItemId, std::unordered_set<int>{1, 3, 5}}};
  const bool actual = Eval(predicate, args);
  ASSERT_TRUE(actual);
}

TEST(Eval, ItemIdsNotIntersects) {
  const std::unordered_set<std::variant<std::string, int>> set{2, 4};
  const PredicateSource predicate{
      PredicateType::kIntersects,  // type
      PredicateInit{
          Argument::kItemId,      // arg_name
          std::nullopt,           // arg_type
          std::nullopt,           // value
          ValueTypeSource::kInt,  // set_elem_type
          set,                    // set
      },                          // init
  };

  const Arguments args{{Argument::kItemId, std::unordered_set<int>{1, 3, 5}}};
  const bool actual = Eval(predicate, args);
  ASSERT_FALSE(actual);
}

TEST(Eval, Lt) {
  std::unordered_set<std::variant<std::string, int>> predicate_set{1, 2};
  SetIntType arg_set{1, 2};

  std::vector<TestCase> cases = {
      TestCase{
          "1 < 2",  // name
          PredicateSource{
              PredicateType::kLt,  // type
              PredicateInit{
                  Argument::kItemId,          // arg_name
                  ValueTypeSource::kInt,      // arg_type
                  2,                          // value
              }                               // init
          },                                  // predicate
          Arguments{{Argument::kItemId, 1}},  // args
          true,                               // expected
      },
      TestCase{
          "2 < 1",  // name
          PredicateSource{
              PredicateType::kLt,  // type
              PredicateInit{
                  Argument::kItemId,          // arg_name
                  ValueTypeSource::kInt,      // arg_type
                  1,                          // value
              }                               // init
          },                                  // predicate
          Arguments{{Argument::kItemId, 2}},  // args
          false,                              // expected
      },
      TestCase{
          "'a' < 'b'",  // name
          PredicateSource{
              PredicateType::kLt,  // type
              PredicateInit{
                  Argument::kItemId,            // arg_name
                  ValueTypeSource::kString,     // arg_type
                  "b",                          // value
              }                                 // init
          },                                    // predicate
          Arguments{{Argument::kItemId, "a"}},  // args
          true,                                 // expected
      },
      TestCase{
          "'b' < 'a'",  // name
          PredicateSource{
              PredicateType::kLt,  // type
              PredicateInit{
                  Argument::kItemId,            // arg_name
                  ValueTypeSource::kString,     // arg_type
                  "a",                          // value
              }                                 // init
          },                                    // predicate
          Arguments{{Argument::kItemId, "b"}},  // args
          false,                                // expected
      },
      TestCase{
          "[1, 2] < [1, 2]",  // name
          PredicateSource{
              PredicateType::kLt,  // type
              PredicateInit{
                  Argument::kPlaceId,               // arg_name
                  std::nullopt,                     // arg_type
                  std::nullopt,                     // value
                  ValueTypeSource::kInt,            // set_elem_type
                  predicate_set,                    // set
              }                                     // init
          },                                        // predicate
          Arguments{{Argument::kItemId, arg_set}},  // args
          false,                                    // expected
      },
  };

  for (const auto& test_case : cases) {
    bool actual = Eval(test_case.predicate, test_case.args);
    EXPECT_EQ(test_case.expected, actual) << test_case.name;
  }
}

TEST(Eval, Lte) {
  std::unordered_set<std::variant<std::string, int>> predicate_set{1, 2};
  SetIntType arg_set{1, 2};

  std::vector<TestCase> cases = {
      TestCase{
          "1 <= 2",  // name
          PredicateSource{
              PredicateType::kLte,  // type
              PredicateInit{
                  Argument::kItemId,          // arg_name
                  ValueTypeSource::kInt,      // arg_type
                  2,                          // value
              }                               // init
          },                                  // predicate
          Arguments{{Argument::kItemId, 1}},  // args
          true,                               // expected
      },
      TestCase{
          "2 <= 1",  // name
          PredicateSource{
              PredicateType::kLte,  // type
              PredicateInit{
                  Argument::kItemId,          // arg_name
                  ValueTypeSource::kInt,      // arg_type
                  1,                          // value
              }                               // init
          },                                  // predicate
          Arguments{{Argument::kItemId, 2}},  // args
          false,                              // expected
      },
      TestCase{
          "3 <= 3",  // name
          PredicateSource{
              PredicateType::kLte,  // type
              PredicateInit{
                  Argument::kItemId,          // arg_name
                  ValueTypeSource::kInt,      // arg_type
                  3,                          // value
              }                               // init
          },                                  // predicate
          Arguments{{Argument::kItemId, 3}},  // args
          true,                               // expected
      },
      TestCase{
          "'a' <= 'b'",  // name
          PredicateSource{
              PredicateType::kLte,  // type
              PredicateInit{
                  Argument::kItemId,            // arg_name
                  ValueTypeSource::kString,     // arg_type
                  "b",                          // value
              }                                 // init
          },                                    // predicate
          Arguments{{Argument::kItemId, "a"}},  // args
          true,                                 // expected
      },
      TestCase{
          "'b' <= 'a'",  // name
          PredicateSource{
              PredicateType::kLte,  // type
              PredicateInit{
                  Argument::kItemId,            // arg_name
                  ValueTypeSource::kString,     // arg_type
                  "a",                          // value
              }                                 // init
          },                                    // predicate
          Arguments{{Argument::kItemId, "b"}},  // args
          false,                                // expected
      },
      TestCase{
          "'c' <= 'c'",  // name
          PredicateSource{
              PredicateType::kLte,  // type
              PredicateInit{
                  Argument::kItemId,            // arg_name
                  ValueTypeSource::kString,     // arg_type
                  "c",                          // value
              }                                 // init
          },                                    // predicate
          Arguments{{Argument::kItemId, "c"}},  // args
          true,                                 // expected
      },
      TestCase{
          "[1, 2] <= [1, 2]",  // name
          PredicateSource{
              PredicateType::kLte,  // type
              PredicateInit{
                  Argument::kPlaceId,               // arg_name
                  std::nullopt,                     // arg_type
                  std::nullopt,                     // value
                  ValueTypeSource::kInt,            // set_elem_type
                  predicate_set,                    // set
              }                                     // init
          },                                        // predicate
          Arguments{{Argument::kItemId, arg_set}},  // args
          false,                                    // expected
      },
  };

  for (const auto& test_case : cases) {
    bool actual = Eval(test_case.predicate, test_case.args);
    EXPECT_EQ(test_case.expected, actual) << test_case.name;
  }
}

std::vector<TestCase> CreateTestCases();

class PredicateTest : public ::testing::TestWithParam<TestCase> {};

TEST_P(PredicateTest, Eval) {
  const auto param = GetParam();

  const auto actual = Eval(param.predicate, param.args);
  ASSERT_EQ(param.expected, actual) << param.name;
}

INSTANTIATE_TEST_SUITE_P(Expression, PredicateTest,
                         ::testing::ValuesIn(CreateTestCases()));

std::vector<TestCase> CreateTestCases() {
  return {
      {
          "not (1 == 2)",  // name
          PredicateSource{
              PredicateType::kNot,  // type
              std::nullopt,         // init
              std::vector<PredicateSource>{
                  {
                      PredicateType::kEq,  // type
                      PredicateInit{
                          Argument::kPlaceId,     // arg_name
                          ValueTypeSource::kInt,  // arg_type
                          1,                      // value
                      },                          // init
                  },
              },  // predicates
          },
          Arguments{{Argument::kPlaceId, 2}},  // args
          true,                                // expected
      },
      {
          "not (1 != 2)",  // name
          PredicateSource{
              PredicateType::kNot,  // type
              std::nullopt,         // init
              std::vector<PredicateSource>{
                  {
                      PredicateType::kNeq,  // type
                      PredicateInit{
                          Argument::kPlaceId,     // arg_name
                          ValueTypeSource::kInt,  // arg_type
                          1,                      // value
                      },                          // init
                  },
              },  // predicates
          },
          Arguments{{Argument::kPlaceId, 2}},  // args
          false,                               // expected
      },
      {
          "not (place_id 4 in set (1, 2, 3))",  // name
          PredicateSource{
              PredicateType::kNot,  // type
              std::nullopt,         // init
              std::vector<PredicateSource>{
                  {
                      PredicateType::kInSet,  // type
                      PredicateInit{
                          Argument::kPlaceId,     // arg_name
                          std::nullopt,           // arg_type
                          std::nullopt,           // value
                          ValueTypeSource::kInt,  // set_elem_type
                          []() {
                            std::unordered_set<std::variant<std::string, int>>
                                result;

                            result.insert(1);
                            result.insert(2);
                            result.insert(3);

                            return result;
                          }(),  // set
                      },        // init
                  },
              },  // predicates
          },
          Arguments{{Argument::kPlaceId, 4}},  // args
          true,                                // expected
      },
      {
          "not (place_id 1 in set (1, 2, 3))",  // name
          PredicateSource{
              PredicateType::kNot,  // type
              std::nullopt,         // init
              std::vector<PredicateSource>{
                  {
                      PredicateType::kInSet,  // type
                      PredicateInit{
                          Argument::kPlaceId,     // arg_name
                          std::nullopt,           // arg_type
                          std::nullopt,           // value
                          ValueTypeSource::kInt,  // set_elem_type
                          []() {
                            std::unordered_set<std::variant<std::string, int>>
                                result;

                            result.insert(1);
                            result.insert(2);
                            result.insert(3);

                            return result;
                          }(),  // set
                      },        // init
                  },
              },  // predicates
          },
          Arguments{{Argument::kPlaceId, 1}},  // args
          false,                               // expected
      },
      {
          "contains category 1",  // name
          PredicateSource{
              PredicateType::kContains,  // type
              PredicateInit{
                  Argument::kItemId,      // arg_name
                  ValueTypeSource::kInt,  // arg_type
                  1,                      // value
              },                          // init
          },                              // predicate
          Arguments{
              {Argument::kItemId, std::unordered_set<int>{1, 2, 3}}},  // args
          true,  // expected

      },
      {
          "not contains category 1",  // name
          PredicateSource{
              PredicateType::kContains,  // type
              PredicateInit{
                  Argument::kItemId,      // arg_name
                  ValueTypeSource::kInt,  // arg_type
                  1,                      // value
              },                          // init
          },                              // predicate
          Arguments{
              {Argument::kItemId, std::unordered_set<int>{2, 3}}},  // args
          false,                                                    // expected

      },
      {
          "place_id not in empty set",  // name
          PredicateSource{
              PredicateType::kInSet,  // type
              PredicateInit{
                  Argument::kPlaceId,        // arg_name
                  std::nullopt,              // arg_type
                  std::nullopt,              // value
                  ValueTypeSource::kString,  // set_elem_type
                  std::unordered_set<std::variant<std::string, int>>{},  // set
              }                                                          // init
          },                                   // predicate
          Arguments{{Argument::kPlaceId, 1}},  // args
          false,                               // expected
      },
      {
          "name bb_1 == name bb_1",  // name
          PredicateSource{
              PredicateType::kEq,  // type
              PredicateInit{
                  Argument::kItemName,       // arg_name
                  ValueTypeSource::kString,  // arg_type,
                  "bb_1",                    // value
              },                             // init
          },                                 // predicate
          Arguments{{Argument::kItemName, "bb_1"}},
          true,  // expected
      },
      {
          "false",  // name
          PredicateSource{
              PredicateType::kFalse,  // type
              PredicateInit{},        // init
          },                          // predicate
          Arguments{},                // args
          false,                      // expected
      },
      {
          "true",  // name
          PredicateSource{
              PredicateType::kTrue,  // type
              PredicateInit{},       // init
          },                         // predicate
          Arguments{},               // args
          true,                      // expected
      },
  };
}

}  // namespace eats_menu_categories::expression
