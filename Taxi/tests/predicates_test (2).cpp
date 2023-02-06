#include <gtest/gtest.h>

#include <cstdlib>
#include <iostream>
#include <list>
#include <random>
#include <string>
#include <type_traits>

#include <userver/logging/log.hpp>

#include <experiments3/models/errors.hpp>
#include <experiments3_common/models/kwargs.hpp>
#include <experiments3_common/models/predicates.hpp>
#include <ua_parser/application.hpp>

using AppVersion = ua_parser::ApplicationVersion;
using KwargsMap = experiments3::models::KwargsMap;

TEST(ExperimentsPredicates, BoolPredicateWithoutArgumentInKwargs) {
  experiments3::models::Bool bool1 = experiments3::models::Bool("non_existing");
  KwargsMap::Map kwargs = {};
  ASSERT_FALSE(bool1(KwargsMap(kwargs)));
}

TEST(ExperimentsPredicates, Int64Predicate) {
  experiments3::models::Bool intv1 = experiments3::models::Bool("int_val_zero");
  experiments3::models::Bool intv2 = experiments3::models::Bool("int_val_one");
  KwargsMap::Map kwargs = {{"int_val_zero", static_cast<std::int64_t>(0)}};
  ASSERT_FALSE(intv1(KwargsMap(kwargs)));
  kwargs = {{"int_val_one", static_cast<std::int64_t>(1)}};
  ASSERT_TRUE(intv2(KwargsMap(kwargs)));
}

TEST(ExperimentsPredicates, ApplicationVersionPredicate) {
  experiments3::models::Bool app_version_predicate =
      experiments3::models::Bool("version");
  KwargsMap::Map kwargs = {{"version", AppVersion("1.2.3")}};
  ASSERT_TRUE(app_version_predicate(KwargsMap(kwargs)));
}

TEST(ExperimentsPredicates, ApplicationPredicate) {
  experiments3::models::Bool app_predicate =
      experiments3::models::Bool("application");
  KwargsMap::Map kwargs = {{"application", "iphone"}};
  ASSERT_TRUE(app_predicate(KwargsMap(kwargs)));
}

TEST(ExperimentsPredicates, LikePositive) {
  experiments3::models::Like like("arg", std::string("capybara"));
  KwargsMap::Map kwargs = {{"arg", std::string("bar")}};
  ASSERT_TRUE(like(KwargsMap(kwargs)));
}

TEST(ExperimentsPredicates, LikeNegative) {
  experiments3::models::Like like("arg", std::string("capybara"));
  KwargsMap::Map kwargs = {{"arg", "BAR"}};
  ASSERT_FALSE(like(KwargsMap(kwargs)));
}

TEST(ExperimentsPredicates, NotPredicate) {
  experiments3::models::Not notPredicate(
      std::make_shared<experiments3::models::False>());
  KwargsMap::Map kwargs = {};
  ASSERT_TRUE(notPredicate(KwargsMap(kwargs)));
}

TEST(ExperimentsPredicates, IsNullPredicate) {
  experiments3::models::IsNull predicate("foo");
  KwargsMap::Map kwargs_true = {{"bar", static_cast<std::int64_t>(1)}};
  ASSERT_TRUE(predicate(KwargsMap(kwargs_true)));
  KwargsMap::Map kwargs_false = {{"foo", static_cast<std::int64_t>(2)}};
  ASSERT_FALSE(predicate(KwargsMap(kwargs_false)));
}

TEST(ExperimentsPredicates, NotNullPredicate) {
  experiments3::models::NotNull predicate("foo");
  KwargsMap::Map kwargs_true = {{"foo", static_cast<std::int64_t>(1)}};
  ASSERT_TRUE(predicate(KwargsMap(kwargs_true)));
  KwargsMap::Map kwargs_false = {{"bar", static_cast<std::int64_t>(2)}};
  ASSERT_FALSE(predicate(KwargsMap(kwargs_false)));
}

TEST(ExperimentsPredicates, FallsInsideLinearRingPredicate) {
  std::vector<::utils::geometry::Point> linear_ring = {
      {0, 0}, {0, 1}, {1, 1}, {1, 0}};
  experiments3::models::FallsInsideLinearRing falls_inside("point",
                                                           linear_ring);

  KwargsMap::Map kwargs_true = {{"point", ::utils::geometry::Point{0.5, 0.5}}};
  ASSERT_TRUE(falls_inside(KwargsMap(kwargs_true)));

  KwargsMap::Map kwargs_edge = {{"point", ::utils::geometry::Point{0, 0}}};
  ASSERT_TRUE(falls_inside(KwargsMap(kwargs_edge)));

  KwargsMap::Map kwargs_false = {{"point", ::utils::geometry::Point{-1, 0}}};
  ASSERT_FALSE(falls_inside(KwargsMap(kwargs_false)));
}

TEST(ExperimentsPredicates, ModSha1WithSaltPredicate) {
  auto test = [](const auto& hash_calculator) {
    using Segmentation = experiments3::models::Segmentation<
        std::decay_t<decltype(hash_calculator)>>;
    Segmentation predicate1({{"time1", 10}}, 0, 50, 100, "salt");
    Segmentation predicate2({{"time2", 10}}, 50, 100, 100, "salt");

    KwargsMap::Map kwargs = {
        {"time1", static_cast<std::int64_t>(10000)},
        {"time2", static_cast<std::int64_t>(80000)},
    };

    ASSERT_FALSE(predicate1(KwargsMap{}));
    ASSERT_FALSE(predicate2(KwargsMap{}));

    bool res1 = predicate1(KwargsMap(kwargs));
    bool res2 = predicate2(KwargsMap(kwargs));

    ASSERT_TRUE((res1 && !res2) || (res2 && !res1));
  };
  test(experiments3::models::ModSha1WithSalt::HashCalculator(""));
  test(experiments3::models::StableSegmentation::HashCalculator(""));
}

TEST(ExperimentsPredicates, ModSha1WithSaltEfficiency) {
  auto test = [](const auto& hash_calculator) {
    using Segmentation = experiments3::models::Segmentation<
        std::decay_t<decltype(hash_calculator)>>;
    std::list<Segmentation> predicates;
    using IKI = experiments3::models::impl::InputKwargInfo;

    predicates.emplace_back(std::vector<IKI>{{"int_kwarg_ru", 3}}, 0, 50, 100,
                            "salt");
    for (const auto& kwarg_name :
         {"int_kwarg", "str_kwarg", "time_point_kwarg", "app_version_kwarg"}) {
      predicates.emplace_back(std::vector<IKI>{{kwarg_name, {}}}, 0, 50, 100,
                              "salt");
    }
    std::vector<size_t> hits(predicates.size());

    KwargsMap::Map kwargs;

    constexpr size_t ITERS_COUNT = 10000;
    for (size_t i = 0; i < ITERS_COUNT; ++i) {
      kwargs["int_kwarg_ru"] =
          static_cast<experiments3::models::KwargTypeInt>(i);
      kwargs["int_kwarg"] = static_cast<experiments3::models::KwargTypeInt>(i);
      kwargs["str_kwarg"] = std::to_string(i);
      kwargs["time_point_kwarg"] = std::chrono::system_clock::now();
      kwargs["app_version_kwarg"] =
          experiments3::models::KwargTypeAppVersion(i, i + 1, i + 2);

      auto kwargs_map = KwargsMap(kwargs);
      size_t j = 0;
      for (const auto& predicate : predicates) {
        hits[j++] += predicate(kwargs_map);
      }
    }

    for (auto hits_count : hits) {
      ASSERT_TRUE(0.4 * ITERS_COUNT <= hits_count &&
                  hits_count <= 0.6 * ITERS_COUNT);
    }
  };
  test(experiments3::models::ModSha1WithSalt::HashCalculator(""));
  test(experiments3::models::StableSegmentation::HashCalculator(""));
}

TEST(ExperimentsPredicates, ModSha1WithSaltDifferentSalt) {
  auto test = [](const auto& hash_calculator) {
    using Segmentation = experiments3::models::Segmentation<
        std::decay_t<decltype(hash_calculator)>>;
    Segmentation predicate1({{"str", {}}}, 0, 50, 100, "salt1");
    Segmentation predicate2({{"str", {}}}, 0, 50, 100, "salt2");

    KwargsMap::Map kwargs{
        {"str", experiments3::models::KwargTypeString{""}},
    };

    std::mt19937 gen;
    const auto append_char_visitor = [&gen](auto&& str) {
      if constexpr (std::is_same_v<experiments3::models::KwargTypeString,
                                   std::decay_t<decltype(str)>>) {
        str += char('a' + gen() % 26);
      } else {
        throw 42;
      }
    };

    constexpr size_t ITERS_COUNT = 1000;

    size_t diffs_count = 0;
    for (size_t i = 0; i < ITERS_COUNT; ++i) {
      std::visit(append_char_visitor, kwargs["str"]);
      diffs_count +=
          (predicate1(KwargsMap(kwargs)) != predicate2(KwargsMap(kwargs)));
    }

    ASSERT_TRUE(0.4 * ITERS_COUNT <= diffs_count);
  };
  test(experiments3::models::ModSha1WithSalt::HashCalculator(""));
  test(experiments3::models::StableSegmentation::HashCalculator(""));
}

TEST(ExperimentsPredicates, ModSha1WithSaltCompositeHash) {
  auto test = [](const auto& hash_calculator) {
    using Segmentation = experiments3::models::Segmentation<
        std::decay_t<decltype(hash_calculator)>>;
    Segmentation predicate1({{"t1", 1}, {"t2", 1}}, 0, 50, 100, "salt");
    Segmentation predicate2({{"t2", 1}, {"t1", 1}}, 0, 50, 100, "salt");
    Segmentation predicate3({{"t1", 1}, {"t2", 1}, {"str", {}}}, 0, 50, 100,
                            "salt");

    ASSERT_FALSE(predicate1(KwargsMap{}));
    ASSERT_FALSE(predicate2(KwargsMap{}));
    ASSERT_FALSE(predicate3(KwargsMap{}));

    KwargsMap::Map kwargs{
        {"str", experiments3::models::KwargTypeString{"abacaba"}},
    };

    constexpr size_t ITERS_COUNT = 100;

    size_t diffs12 = 0;
    size_t diffs13 = 0;

    for (size_t i = 0; i < ITERS_COUNT; ++i) {
      for (size_t j = 0; j < ITERS_COUNT; ++j) {
        kwargs["t1"] = static_cast<experiments3::models::KwargTypeInt>(i);
        kwargs["t2"] = static_cast<experiments3::models::KwargTypeInt>(j);
        bool res1 = predicate1(KwargsMap(kwargs));
        bool res2 = predicate2(KwargsMap(kwargs));
        bool res3 = predicate3(KwargsMap(kwargs));
        diffs12 += (res1 != res2);
        diffs13 += (res1 != res3);
      }
    }

    ASSERT_EQ(diffs12, 0);
    ASSERT_TRUE(0.4 * ITERS_COUNT <= diffs13);
  };
  test(experiments3::models::ModSha1WithSalt::HashCalculator(""));
  test(experiments3::models::StableSegmentation::HashCalculator(""));
}

TEST(ExperimentsPredicates, StableModShaWithSalt) {
  auto test = [](const auto& hash_calculator, bool need1, bool need2,
                 bool need3) {
    using Segmentation = experiments3::models::Segmentation<
        std::decay_t<decltype(hash_calculator)>>;
    Segmentation predicate1({{"arg1", {}}}, 0, 50, 100, "salt");
    Segmentation predicate2({{"arg2", {}}}, 0, 50, 100, "salt");
    Segmentation predicate3({{"arg3", {}}}, 0, 50, 100, "salt");

    KwargsMap::Map kwargs{
        {"arg1", experiments3::models::KwargTypeString{"abacaba1"}},
        {"arg2", experiments3::models::KwargTypeString{"abacaba2"}},
        {"arg3", experiments3::models::KwargTypeString{"abacaba3"}},
    };

    bool res1 = predicate1(KwargsMap(kwargs));
    bool res2 = predicate2(KwargsMap(kwargs));
    bool res3 = predicate3(KwargsMap(kwargs));

    ASSERT_EQ(res1, need1);
    ASSERT_EQ(res2, need2);
    ASSERT_EQ(res3, need3);
  };
  test(experiments3::models::ModSha1WithSalt::HashCalculator(""), true, true,
       false);
  test(experiments3::models::StableSegmentation::HashCalculator(""), true,
       false, false);
}
