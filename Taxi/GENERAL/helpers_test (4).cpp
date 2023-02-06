#include "helpers.hpp"

#include <userver/utest/utest.hpp>

namespace {

namespace utils = geobus::utils;

TEST(UtilsHelpers, IsTypeList) {
  static_assert(utils::IsTypeList<utils::TypeList<>>);
  static_assert(utils::IsTypeList<utils::TypeList<int>>);
  static_assert(utils::IsTypeList<utils::TypeList<int, bool>>);

  static_assert(!utils::IsTypeList<int>);
  static_assert(!utils::IsTypeList<bool>);
  static_assert(!utils::IsTypeList<std::tuple<int, bool>>);

  SUCCEED();
}

TEST(UtilsHelpers, Contains) {
  {
    const utils::TypeList<> list0;
    static_assert(!utils::Contains<int>(list0));
  }

  {
    const utils::TypeList<int> list1;
    static_assert(utils::Contains<int>(list1));
    static_assert(!utils::Contains<double>(list1));
  }

  {
    const utils::TypeList<int, bool> list2;
    static_assert(utils::Contains<int>(list2));
    static_assert(utils::Contains<bool>(list2));
    static_assert(!utils::Contains<double>(list2));
  }

  {
    const utils::TypeList<int, bool, double> list3;
    static_assert(utils::Contains<int>(list3));
    static_assert(utils::Contains<bool>(list3));
    static_assert(utils::Contains<double>(list3));
    static_assert(!utils::Contains<float>(list3));
  }

  SUCCEED();
}

TEST(UtilsHelpers, HasDublicates) {
  {
    const utils::TypeList<> list0;
    static_assert(!utils::HasDublicates(list0));
  }

  {
    const utils::TypeList<int> list1;
    static_assert(!utils::HasDublicates(list1));
  }

  {
    const utils::TypeList<int, bool> list2;
    static_assert(!utils::HasDublicates(list2));
  }

  {
    const utils::TypeList<int, int> list2;
    static_assert(utils::HasDublicates(list2));
  }

  {
    const utils::TypeList<int, bool, double> list3;
    static_assert(!utils::HasDublicates(list3));
  }

  {
    const utils::TypeList<int, int, double> list3;
    static_assert(utils::HasDublicates(list3));
  }

  {
    const utils::TypeList<int, double, int> list3;
    static_assert(utils::HasDublicates(list3));
  }

  {
    const utils::TypeList<double, int, int> list3;
    static_assert(utils::HasDublicates(list3));
  }

  SUCCEED();
}

template <typename... Ts>
struct SomeTemplateWithPack {};

TEST(UtilsHelpers, UnpackTypeListTo) {
  {
    using TypeList = utils::TypeList<int, bool>;
    using Result = utils::UnpackTypeListTo<std::tuple, TypeList>;
    static_assert(std::is_same_v<std::tuple<int, bool>, Result>);
  }

  {
    using TypeList = utils::TypeList<bool, double>;
    using Result = utils::UnpackTypeListTo<SomeTemplateWithPack, TypeList>;
    static_assert(std::is_same_v<SomeTemplateWithPack<bool, double>, Result>);
  }

  SUCCEED();
}

}  // namespace
