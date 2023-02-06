#include "expression.hpp"

#include <gtest/gtest.h>

namespace eats_catalog::expression {

using PredicateSource = handlers::libraries::eats_catalog_predicate::Predicate;
using ValueTypeSource = handlers::libraries::eats_catalog_predicate::ValueType;
using handlers::libraries::eats_catalog_predicate::Argument;
using handlers::libraries::eats_catalog_predicate::PredicateInit;
using handlers::libraries::eats_catalog_predicate::PredicateType;

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

auto Set(const Argument name, ValueType&& value) {
  return [name, value = std::move(value)](Arguments& args) {
    args[::utils::UnderlyingValue(name)] = std::move(value);
  };
}

template <typename... Args>
Arguments Args(Args... args) {
  Arguments result;
  (args(result), ...);
  return result;
}

}  // namespace

TEST(Eval, NEQ) {
  std::unordered_set<std::variant<std::string, double>> set_one;
  {
    set_one.insert(2);
    set_one.insert("2");
    set_one.insert(3);
    set_one.insert(" 3");
    set_one.insert("abc");
  }

  std::unordered_set<std::variant<std::string, double>> set_two;
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
                  Argument::kPlaceId,        // arg_name
                  ValueTypeSource::kInt,     // arg_type
                  1,                         // value
              }                              // init
          },                                 // predicate
          Args(Set(Argument::kPlaceId, 2)),  // args
          true,                              // expected
      },
      TestCase{
          "1 != 1",  // name
          PredicateSource{
              PredicateType::kNeq,  // type
              PredicateInit{
                  Argument::kPlaceId,        // arg_name
                  ValueTypeSource::kInt,     // arg_type
                  1,                         // value
              }                              // init
          },                                 // predicate
          Args(Set(Argument::kPlaceId, 1)),  // args
          false,                             // expected
      },
      TestCase{
          "'1' != '1'",  // name
          PredicateSource{
              PredicateType::kNeq,  // type
              PredicateInit{
                  Argument::kPlaceId,          // arg_name
                  ValueTypeSource::kString,    // arg_type
                  "1",                         // value
              }                                // init
          },                                   // predicate
          Args(Set(Argument::kPlaceId, "1")),  // args
          false,                               // expected
      },
      TestCase{
          "100 != '100' (type missmatch always true)",  // name
          PredicateSource{
              PredicateType::kNeq,  // type
              PredicateInit{
                  Argument::kPlaceId,            // arg_name
                  ValueTypeSource::kInt,         // arg_type
                  "100",                         // value
              }                                  // init
          },                                     // predicate
          Args(Set(Argument::kPlaceId, "100")),  // args
          true,                                  // expected
      },
      TestCase{
          "[2, '3', 3, ' 3', 'abc'] != [2, 3]",  // name
          PredicateSource{
              PredicateType::kNeq,  // type
              PredicateInit{
                  Argument::kPlaceId,                       // arg_name
                  std::nullopt,                             // arg_type
                  std::nullopt,                             // value
                  ValueTypeSource::kInt,                    // set_elem_type
                  set_one,                                  // set
              }                                             // init
          },                                                // predicate
          Args(Set(Argument::kPlaceId, SetIntType{2, 3})),  // args
          false,                                            // expected
      },
      TestCase{
          "[2, '1', 3] != [2, 3]",  // name
          PredicateSource{
              PredicateType::kNeq,  // type
              PredicateInit{
                  Argument::kPlaceId,                       // arg_name
                  std::nullopt,                             // arg_type
                  std::nullopt,                             // value
                  ValueTypeSource::kInt,                    // set_elem_type
                  set_two,                                  // set
              }                                             // init
          },                                                // predicate
          Args(Set(Argument::kPlaceId, SetIntType{2, 3})),  // args
          true,                                             // expected
      },
  };

  for (const auto& test_case : cases) {
    bool actual = Eval(test_case.predicate, test_case.args);
    EXPECT_EQ(test_case.expected, actual) << test_case.name;
  }
}

TEST(Eval, EQ) {
  std::unordered_set<std::variant<std::string, double>> set_one;
  {
    set_one.insert(2);
    set_one.insert("2");
    set_one.insert(3);
    set_one.insert(" 3");
    set_one.insert("abc");
  }

  std::unordered_set<std::variant<std::string, double>> set_two;
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
                  Argument::kPlaceId,        // arg_name
                  ValueTypeSource::kInt,     // arg_type
                  1,                         // value
              }                              // init
          },                                 // predicate
          Args(Set(Argument::kPlaceId, 2)),  // args
          false,                             // expected
      },
      TestCase{
          "1 == 1",  // name
          PredicateSource{
              PredicateType::kEq,  // type
              PredicateInit{
                  Argument::kPlaceId,        // arg_name
                  ValueTypeSource::kInt,     // arg_type
                  1,                         // value
              }                              // init
          },                                 // predicate
          Args(Set(Argument::kPlaceId, 1)),  // args
          true,                              // expected
      },
      TestCase{
          "'1' == '1'",  // name
          PredicateSource{
              PredicateType::kEq,  // type
              PredicateInit{
                  Argument::kPlaceId,          // arg_name
                  ValueTypeSource::kString,    // arg_type
                  "1",                         // value
              }                                // init
          },                                   // predicate
          Args(Set(Argument::kPlaceId, "1")),  // args
          true,                                // expected
      },
      TestCase{
          "100 != '100' (type missmatch always false)",  // name
          PredicateSource{
              PredicateType::kEq,  // type
              PredicateInit{
                  Argument::kPlaceId,            // arg_name
                  ValueTypeSource::kInt,         // arg_type
                  "100",                         // value
              }                                  // init
          },                                     // predicate
          Args(Set(Argument::kPlaceId, "100")),  // args
          false,                                 // expected
      },
      TestCase{
          "[2, '3', 3, ' 3', 'abc']  == [2, 3]",  // name
          PredicateSource{
              PredicateType::kEq,  // type
              PredicateInit{
                  Argument::kPlaceId,                       // arg_name
                  std::nullopt,                             // arg_type
                  std::nullopt,                             // value
                  ValueTypeSource::kInt,                    // set_elem_type
                  set_one,                                  // set
              }                                             // init
          },                                                // predicate
          Args(Set(Argument::kPlaceId, SetIntType{2, 3})),  // args
          true,                                             // expected
      },
      TestCase{
          "[2, '1', 3] != [2, 3]",  // name
          PredicateSource{
              PredicateType::kEq,  // type
              PredicateInit{
                  Argument::kPlaceId,                       // arg_name
                  std::nullopt,                             // arg_type
                  std::nullopt,                             // value
                  ValueTypeSource::kInt,                    // set_elem_type
                  set_two,                                  // set
              }                                             // init
          },                                                // predicate
          Args(Set(Argument::kPlaceId, SetIntType{2, 3})),  // args
          false,                                            // expected
      },
  };

  for (const auto& test_case : cases) {
    bool actual = Eval(test_case.predicate, test_case.args);
    EXPECT_EQ(test_case.expected, actual) << test_case.name;
  }
}

TEST(Eval, NotInSet) {
  std::unordered_set<std::variant<std::string, double>> set;
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

  bool actual = Eval(predicate, Args(Set(Argument::kPlaceId, 2)));
  ASSERT_EQ(false, actual);
}

TEST(Eval, InSetSimple) {
  std::unordered_set<std::variant<std::string, double>> set;
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

  const Arguments args{{}};

  bool actual = Eval(predicate, Args(Set(Argument::kPlaceId, 2)));
  ASSERT_EQ(true, actual);
}

TEST(Eval, InSetSimpleString) {
  std::unordered_set<std::variant<std::string, double>> set;
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

  const Arguments args{{}};

  bool actual = Eval(predicate, Args(Set(Argument::kPlaceId, "abc")));
  ASSERT_EQ(true, actual);
}

TEST(Eval, AllOf) {
  std::vector<PredicateSource> predicates;

  {
    std::unordered_set<std::variant<std::string, double>> set;
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
            Argument::kBrandId,        // arg_name
            ValueTypeSource::kString,  // arg_type
            "hello",                   // value
        }                              // init
    });
  }

  PredicateSource main;
  main.type = PredicateType::kAllOf;
  main.predicates = predicates;

  bool actual = Eval(main, Args(Set(Argument::kPlaceId, " 3"),
                                Set(Argument::kBrandId, "hello")));
  ASSERT_EQ(true, actual);
}

TEST(Eval, NotAllOf) {
  std::vector<PredicateSource> predicates;

  {
    std::unordered_set<std::variant<std::string, double>> set;
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
            Argument::kBrandId,        // arg_name
            ValueTypeSource::kString,  // arg_type
            "world",                   // value
        }                              // init
    });
  }

  PredicateSource main;
  main.type = PredicateType::kAllOf;
  main.predicates = predicates;

  bool actual = Eval(main, Args(Set(Argument::kPlaceId, " 3"),
                                Set(Argument::kBrandId, "hello")));
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
            Argument::kBrandId,        // arg_name
            ValueTypeSource::kString,  // arg_type
            "hello",                   // value
        }                              // init
    });
  }
  PredicateSource main;
  main.type = PredicateType::kAnyOf;
  main.predicates = predicates;

  bool actual = Eval(main, Args(Set(Argument::kPlaceId, " 3"),
                                Set(Argument::kBrandId, "hello")));
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
            Argument::kBrandId,        // arg_name
            ValueTypeSource::kString,  // arg_type
            "world",                   // value
        }                              // init
    });
  }
  PredicateSource main;
  main.type = PredicateType::kAnyOf;
  main.predicates = predicates;

  bool actual = Eval(main, Args(Set(Argument::kPlaceId, " 3"),
                                Set(Argument::kBrandId, "hello")));
  ASSERT_EQ(false, actual);
}

TEST(Eval, CourierTypeInSet) {
  const std::unordered_set<std::variant<std::string, double>> set{
      "yandex_rover", "pedestrian"};
  const PredicateSource predicate{
      PredicateType::kInSet,  // type
      PredicateInit{
          Argument::kCourierType,    // arg_name
          std::nullopt,              // arg_type
          std::nullopt,              // value
          ValueTypeSource::kString,  // set_elem_type
          set,                       // set
      },                             // init
  };

  const bool actual =
      Eval(predicate, Args(Set(Argument::kCourierType, "yandex_rover")));
  ASSERT_TRUE(actual);
}

TEST(Eval, PromoTypeInSet) {
  const std::unordered_set<std::variant<std::string, double>> set{1, 2};
  const PredicateSource predicate{
      PredicateType::kInSet,  // type
      PredicateInit{
          Argument::kPromoType,   // arg_name
          std::nullopt,           // arg_type
          std::nullopt,           // value
          ValueTypeSource::kInt,  // set_elem_type
          set,                    // set
      },                          // init
  };

  const bool actual = Eval(predicate, Args(Set(Argument::kPromoType, 1)));
  ASSERT_TRUE(actual);
}

TEST(Eval, PromoTypesIntersects) {
  const std::unordered_set<std::variant<std::string, double>> set{1, 2, 3, 4,
                                                                  5};
  const PredicateSource predicate{
      PredicateType::kIntersects,  // type
      PredicateInit{
          Argument::kPromoType,   // arg_name
          std::nullopt,           // arg_type
          std::nullopt,           // value
          ValueTypeSource::kInt,  // set_elem_type
          set,                    // set
      },                          // init
  };

  const bool actual =
      Eval(predicate,
           Args(Set(Argument::kPromoType, std::unordered_set<int>{1, 3, 5})));
  ASSERT_TRUE(actual);
}

TEST(Eval, PromoTypesNotIntersects) {
  const std::unordered_set<std::variant<std::string, double>> set{2, 4};
  const PredicateSource predicate{
      PredicateType::kIntersects,  // type
      PredicateInit{
          Argument::kPromoType,   // arg_name
          std::nullopt,           // arg_type
          std::nullopt,           // value
          ValueTypeSource::kInt,  // set_elem_type
          set,                    // set
      },                          // init
  };

  const bool actual =
      Eval(predicate,
           Args(Set(Argument::kPromoType, std::unordered_set<int>{1, 3, 5})));
  ASSERT_FALSE(actual);
}

TEST(Eval, Lt) {
  std::unordered_set<std::variant<std::string, double>> predicate_set{1, 2};
  SetIntType arg_set{1, 2};

  std::vector<TestCase> cases = {
      TestCase{
          "1 < 2",  // name
          PredicateSource{
              PredicateType::kLt,  // type
              PredicateInit{
                  Argument::kDeliveryTimeMax,        // arg_name
                  ValueTypeSource::kInt,             // arg_type
                  2,                                 // value
              }                                      // init
          },                                         // predicate
          Args(Set(Argument::kDeliveryTimeMax, 1)),  // args
          true,                                      // expected
      },
      TestCase{
          "2 < 1",  // name
          PredicateSource{
              PredicateType::kLt,  // type
              PredicateInit{
                  Argument::kDeliveryTimeMax,        // arg_name
                  ValueTypeSource::kInt,             // arg_type
                  1,                                 // value
              }                                      // init
          },                                         // predicate
          Args(Set(Argument::kDeliveryTimeMax, 2)),  // args
          false,                                     // expected
      },
      TestCase{
          "'a' < 'b'",  // name
          PredicateSource{
              PredicateType::kLt,  // type
              PredicateInit{
                  Argument::kDeliveryTimeMax,          // arg_name
                  ValueTypeSource::kString,            // arg_type
                  "b",                                 // value
              }                                        // init
          },                                           // predicate
          Args(Set(Argument::kDeliveryTimeMax, "a")),  // args
          true,                                        // expected
      },
      TestCase{
          "'b' < 'a'",  // name
          PredicateSource{
              PredicateType::kLt,  // type
              PredicateInit{
                  Argument::kDeliveryTimeMax,          // arg_name
                  ValueTypeSource::kString,            // arg_type
                  "a",                                 // value
              }                                        // init
          },                                           // predicate
          Args(Set(Argument::kDeliveryTimeMax, "b")),  // args
          false,                                       // expected
      },
      TestCase{
          "[1, 2] < [1, 2]",  // name
          PredicateSource{
              PredicateType::kLt,  // type
              PredicateInit{
                  Argument::kPlaceId,                      // arg_name
                  std::nullopt,                            // arg_type
                  std::nullopt,                            // value
                  ValueTypeSource::kInt,                   // set_elem_type
                  predicate_set,                           // set
              }                                            // init
          },                                               // predicate
          Args(Set(Argument::kDeliveryTimeMax, arg_set)),  // args
          false,                                           // expected
      },
  };

  for (const auto& test_case : cases) {
    bool actual = Eval(test_case.predicate, test_case.args);
    EXPECT_EQ(test_case.expected, actual) << test_case.name;
  }
}

TEST(Eval, Lte) {
  std::unordered_set<std::variant<std::string, double>> predicate_set{1, 2};
  SetIntType arg_set{1, 2};

  std::vector<TestCase> cases = {
      TestCase{
          "1 <= 2",  // name
          PredicateSource{
              PredicateType::kLte,  // type
              PredicateInit{
                  Argument::kDeliveryTimeMax,        // arg_name
                  ValueTypeSource::kInt,             // arg_type
                  2,                                 // value
              }                                      // init
          },                                         // predicate
          Args(Set(Argument::kDeliveryTimeMax, 1)),  // args
          true,                                      // expected
      },
      TestCase{
          "2 <= 1",  // name
          PredicateSource{
              PredicateType::kLte,  // type
              PredicateInit{
                  Argument::kDeliveryTimeMax,        // arg_name
                  ValueTypeSource::kInt,             // arg_type
                  1,                                 // value
              }                                      // init
          },                                         // predicate
          Args(Set(Argument::kDeliveryTimeMax, 2)),  // args
          false,                                     // expected
      },
      TestCase{
          "3 <= 3",  // name
          PredicateSource{
              PredicateType::kLte,  // type
              PredicateInit{
                  Argument::kDeliveryTimeMax,        // arg_name
                  ValueTypeSource::kInt,             // arg_type
                  3,                                 // value
              }                                      // init
          },                                         // predicate
          Args(Set(Argument::kDeliveryTimeMax, 3)),  // args
          true,                                      // expected
      },
      TestCase{
          "'a' <= 'b'",  // name
          PredicateSource{
              PredicateType::kLte,  // type
              PredicateInit{
                  Argument::kDeliveryTimeMax,          // arg_name
                  ValueTypeSource::kString,            // arg_type
                  "b",                                 // value
              }                                        // init
          },                                           // predicate
          Args(Set(Argument::kDeliveryTimeMax, "a")),  // args
          true,                                        // expected
      },
      TestCase{
          "'b' <= 'a'",  // name
          PredicateSource{
              PredicateType::kLte,  // type
              PredicateInit{
                  Argument::kDeliveryTimeMax,          // arg_name
                  ValueTypeSource::kString,            // arg_type
                  "a",                                 // value
              }                                        // init
          },                                           // predicate
          Args(Set(Argument::kDeliveryTimeMax, "b")),  // args
          false,                                       // expected
      },
      TestCase{
          "'c' <= 'c'",  // name
          PredicateSource{
              PredicateType::kLte,  // type
              PredicateInit{
                  Argument::kDeliveryTimeMax,          // arg_name
                  ValueTypeSource::kString,            // arg_type
                  "c",                                 // value
              }                                        // init
          },                                           // predicate
          Args(Set(Argument::kDeliveryTimeMax, "c")),  // args
          true,                                        // expected
      },
      TestCase{
          "[1, 2] <= [1, 2]",  // name
          PredicateSource{
              PredicateType::kLte,  // type
              PredicateInit{
                  Argument::kPlaceId,                      // arg_name
                  std::nullopt,                            // arg_type
                  std::nullopt,                            // value
                  ValueTypeSource::kInt,                   // set_elem_type
                  predicate_set,                           // set
              }                                            // init
          },                                               // predicate
          Args(Set(Argument::kDeliveryTimeMax, arg_set)),  // args
          false,                                           // expected
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
          Args(Set(Argument::kPlaceId, 2)),  // args
          true,                              // expected
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
          Args(Set(Argument::kPlaceId, 2)),  // args
          false,                             // expected
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
                            std::unordered_set<
                                std::variant<std::string, double>>
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
          Args(Set(Argument::kPlaceId, 4)),  // args
          true,                              // expected
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
                            std::unordered_set<
                                std::variant<std::string, double>>
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
          Args(Set(Argument::kPlaceId, 1)),  // args
          false,                             // expected
      },
      {
          "contains category 1",  // name
          PredicateSource{
              PredicateType::kContains,  // type
              PredicateInit{
                  Argument::kCategoryId,  // arg_name
                  ValueTypeSource::kInt,  // arg_type
                  1,                      // value
              },                          // init
          },                              // predicate
          Args(Set(Argument::kCategoryId,
                   std::unordered_set<int>{1, 2, 3})),  // args
          true,                                         // expected

      },
      {
          "not contains category 1",  // name
          PredicateSource{
              PredicateType::kContains,  // type
              PredicateInit{
                  Argument::kCategoryId,  // arg_name
                  ValueTypeSource::kInt,  // arg_type
                  1,                      // value
              },                          // init
          },                              // predicate
          Args(Set(Argument::kCategoryId,
                   std::unordered_set<int>{2, 3})),  // args
          false,                                     // expected

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
                  std::unordered_set<
                      std::variant<std::string, double>>{},  // set
              }                                              // init
          },                                                 // predicate
          Args(Set(Argument::kPlaceId, 1)),                  // args
          false,                                             // expected
      },
      {
          "slug bb_1 == slug bb_1",  // name
          PredicateSource{
              PredicateType::kEq,  // type
              PredicateInit{
                  Argument::kPlaceSlug,      // arg_name
                  ValueTypeSource::kString,  // arg_type,
                  "bb_1",                    // value
              },                             // init
          },                                 // predicate
          Args(Set(Argument::kPlaceSlug, "bb_1")),
          true,  // expected
      },
      {
          "is_null(slug) == false",  // name
          PredicateSource{
              PredicateType::kIsNull,  // type
              PredicateInit{
                  Argument::kPlaceSlug,  // arg_name
              },                         // init
          },                             // predicate
          Args(Set(Argument::kPlaceSlug, "bb_1")),
          false,  // expected
      },
      {
          "is_null(slug) == true",  // name
          PredicateSource{
              PredicateType::kIsNull,  // type
              PredicateInit{
                  Argument::kPlaceSlug,  // arg_name
              },                         // init
          },                             // predicate
          Arguments{},
          true,  // expected
      },
      {
          "bool() == false",  // name
          PredicateSource{
              PredicateType::kBool,  // type
              PredicateInit{
                  Argument::kIsUltima,  // arg_name
              },                        // init
          },                            // predicate
          Arguments{},
          false,  // expected
      },
      {
          "bool(false) == false",  // name
          PredicateSource{
              PredicateType::kBool,  // type
              PredicateInit{
                  Argument::kIsUltima,  // arg_name
              },                        // init
          },                            // predicate
          Args(Set(Argument::kIsUltima, BoolType{false})),
          false,  // expected
      },
      {
          "bool(true) == true",  // name
          PredicateSource{
              PredicateType::kBool,  // type
              PredicateInit{
                  Argument::kIsUltima,  // arg_name
              },                        // init
          },                            // predicate
          Args(Set(Argument::kIsUltima, BoolType{true})),
          true,  // expected
      },
  };
}

}  // namespace eats_catalog::expression
