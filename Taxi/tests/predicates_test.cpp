#include <gtest/gtest.h>

#include <experiments3_common/models/errors.hpp>
#include <experiments3_common/models/kwargs.hpp>
#include <experiments3_common/models/predicates.hpp>
#include <models/configs.hpp>
#include <utils/application.hpp>
#include <utils/hash.hpp>
#include <utils/known_apps.hpp>

#include <iostream>

TEST(ExperimentsPredicates, BoolPredicateWithoutArgumentInKwargs) {
  LogExtra log_extra;
  experiments3::models::Bool bool1 = experiments3::models::Bool("non_existing");
  ASSERT_FALSE(bool1({}, log_extra));
}

TEST(ExperimentsPredicates, Int64Predicate) {
  LogExtra log_extra;
  experiments3::models::Bool intv1 = experiments3::models::Bool("int_val_zero");
  experiments3::models::Bool intv2 = experiments3::models::Bool("int_val_one");
  ASSERT_FALSE(
      intv1({{"int_val_zero", static_cast<std::int64_t>(0)}}, log_extra));
  ASSERT_TRUE(
      intv2({{"int_val_one", static_cast<std::int64_t>(1)}}, log_extra));
}

TEST(ExperimentsPredicates, ApplicationVersionPredicate) {
  LogExtra log_extra;
  experiments3::models::Bool app_version_predicate =
      experiments3::models::Bool("version");
  ASSERT_TRUE(app_version_predicate(
      {{"version", models::ApplicationVersion("1.2.3")}}, log_extra));
}

TEST(ExperimentsPredicates, ApplicationPredicate) {
  LogExtra log_extra;
  experiments3::models::Bool app_predicate =
      experiments3::models::Bool("application");
  ASSERT_TRUE(app_predicate({{"application", models::applications::Iphone}},
                            log_extra));
}

TEST(ExperimentsPredicates, LikePositive) {
  LogExtra log_extra;
  experiments3::models::Like like("arg", std::string("capybara"));
  ASSERT_TRUE(like({{"arg", std::string("bar")}}, log_extra));
}

TEST(ExperimentsPredicates, LikeNegative) {
  LogExtra log_extra;
  experiments3::models::Like like("arg", std::string("capybara"));
  ASSERT_FALSE(like({{"arg", "BAR"}}, log_extra));
}

TEST(ExperimentsPredicates, NotPredicate) {
  LogExtra log_extra;
  experiments3::models::Not notPredicate(
      std::make_shared<experiments3::models::False>());
  ASSERT_TRUE(notPredicate({}, log_extra));
}

TEST(ExperimentsPredicates, IsNullPredicate) {
  LogExtra log_extra;
  experiments3::models::IsNull predicate("foo");
  experiments3::models::Kwargs kwargs_true = {
      {"bar", static_cast<std::int64_t>(1)}};
  ASSERT_TRUE(predicate(kwargs_true, log_extra));
  experiments3::models::Kwargs kwargs_false = {
      {"foo", static_cast<std::int64_t>(2)}};
  ASSERT_FALSE(predicate(kwargs_false, log_extra));
}

TEST(ExperimentsPredicates, NotNullPredicate) {
  LogExtra log_extra;
  experiments3::models::NotNull predicate("foo");
  experiments3::models::Kwargs kwargs_true = {
      {"foo", static_cast<std::int64_t>(1)}};
  ASSERT_TRUE(predicate(kwargs_true, log_extra));
  experiments3::models::Kwargs kwargs_false = {
      {"bar", static_cast<std::int64_t>(2)}};
  ASSERT_FALSE(predicate(kwargs_false, log_extra));
}

TEST(ExperimentsPredicates, AddVectorMethod) {
  LogExtra log_extra;
  experiments3::models::Like like("words[1]", std::string("capybara"));
  experiments3::models::Kwargs kwargs;
  const std::vector<std::string> words = {"foo", "bar"};
  experiments3::models::AddVector<std::string>(kwargs, std::string("words"),
                                               words);
  ASSERT_TRUE(like(kwargs, log_extra));
}

TEST(ExperimentsPredicates, FallsInsideLinearRingPredicate) {
  LogExtra log_extra;
  std::vector<::utils::geometry::Point> linear_ring = {
      {0, 0}, {0, 1}, {1, 1}, {1, 0}};
  experiments3::models::FallsInsideLinearRing falls_inside("point",
                                                           linear_ring);

  experiments3::models::Kwargs kwargs_true = {
      {"point", ::utils::geometry::Point{0.5, 0.5}}};
  ASSERT_TRUE(falls_inside(kwargs_true, log_extra));

  experiments3::models::Kwargs kwargs_edge = {
      {"point", ::utils::geometry::Point{0, 0}}};
  ASSERT_TRUE(falls_inside(kwargs_edge, log_extra));

  experiments3::models::Kwargs kwargs_false = {
      {"point", ::utils::geometry::Point{-1, 0}}};
  ASSERT_FALSE(falls_inside(kwargs_false, log_extra));
}

TEST(ExperimentsPredicates, ModSha1WithSaltPredicate) {
  auto test = [](const auto& hash_calculator) {
    using Segmentation = experiments3::models::Segmentation<
        std::decay_t<decltype(hash_calculator)>>;
    Segmentation predicate1({{"time1", 10}}, 0, 50, 100, "salt");
    Segmentation predicate2({{"time2", 10}}, 50, 100, 100, "salt");

    using experiments3::models::Kwargs;
    Kwargs kwargs = {
        {"time1", static_cast<std::int64_t>(10000)},
        {"time2", static_cast<std::int64_t>(80000)},
    };

    ASSERT_FALSE(predicate1(Kwargs{}));
    ASSERT_FALSE(predicate2(Kwargs{}));

    bool res1 = predicate1(Kwargs(kwargs));
    bool res2 = predicate2(Kwargs(kwargs));

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

    using experiments3::models::Kwargs;
    Kwargs kwargs;

    constexpr size_t ITERS_COUNT = 10000;
    for (size_t i = 0; i < ITERS_COUNT; ++i) {
      kwargs["int_kwarg_ru"] =
          static_cast<experiments3::models::KwargTypeInt>(i);
      kwargs["int_kwarg"] = static_cast<experiments3::models::KwargTypeInt>(i);
      kwargs["str_kwarg"] = std::to_string(i);
      kwargs["time_point_kwarg"] = std::chrono::system_clock::now();
      kwargs["app_version_kwarg"] =
          experiments3::models::KwargTypeAppVersion(i, i + 1, i + 2);

      auto kwargs_map = Kwargs(kwargs);
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

TEST(ExperimentsPredicates, StableModShaWithSalt) {
  auto test = [](const auto& hash_calculator, bool need1, bool need2,
                 bool need3) {
    using Segmentation = experiments3::models::Segmentation<
        std::decay_t<decltype(hash_calculator)>>;
    Segmentation predicate1({{"arg1", {}}}, 0, 50, 100, "salt");
    Segmentation predicate2({{"arg2", {}}}, 0, 50, 100, "salt");
    Segmentation predicate3({{"arg3", {}}}, 0, 50, 100, "salt");

    using experiments3::models::Kwargs;
    Kwargs kwargs{
        {"arg1", experiments3::models::KwargTypeString{"abacaba1"}},
        {"arg2", experiments3::models::KwargTypeString{"abacaba2"}},
        {"arg3", experiments3::models::KwargTypeString{"abacaba3"}},
    };

    bool res1 = predicate1(Kwargs(kwargs));
    bool res2 = predicate2(Kwargs(kwargs));
    bool res3 = predicate3(Kwargs(kwargs));

    ASSERT_EQ(res1, need1);
    ASSERT_EQ(res2, need2);
    ASSERT_EQ(res3, need3);
  };
  test(experiments3::models::ModSha1WithSalt::HashCalculator(""), true, true,
       false);
  test(experiments3::models::StableSegmentation::HashCalculator(""), true,
       false, false);
}
