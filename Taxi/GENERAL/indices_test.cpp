#include <gtest/gtest.h>

#include "indices.hpp"

std::string ToString(const utils::OptionalIndexList& list) {
  if (!list) {
    return "none";
  }

  std::ostringstream oss;
  oss << "{";
  for (const auto& index : *list) {
    oss << index << ",";
  }
  auto result = oss.str();
  if (result.back() == ',') {
    result.back() = '}';
  }
  return result;
};

void AssertEq(const utils::OptionalIndexList& expected,
              const utils::OptionalIndexList& actual,
              const char* testcase = nullptr) {
  ASSERT_TRUE(expected == actual)
      << "Test case: "
      << (testcase != nullptr ? std::string{testcase} : ToString(expected));
}

void AssertEq(const utils::IndexList& expected,
              const utils::OptionalIndexList& actual,
              const char* testcase = nullptr) {
  AssertEq(utils::OptionalIndexList{expected}, actual, testcase);
}

TEST(TestIndices, GetStringIndexList) {
  const utils::StringToIndexMap map{
      //
      {"abc", utils::Index{3u}},  //
      {"def", utils::Index{1u}},  //
      {"ghi", utils::Index{4u}},  //
  };

  AssertEq(boost::none, utils::GetStringIndexList({}, map));
  AssertEq(utils::IndexList{}, utils::GetStringIndexList({"xxx"}, map));
  AssertEq({1u}, utils::GetStringIndexList({"def"}, map));
  AssertEq({1u, 3u}, utils::GetStringIndexList({"def", "abc"}, map));
  AssertEq({1u, 3u}, utils::GetStringIndexList({"abc", "def"}, map));
  AssertEq({1u, 3u, 4u}, utils::GetStringIndexList({"abc", "def", "ghi"}, map));
}

TEST(TestIndices, IntersectOptionalIndexListWith) {
  const utils::IndexList any{1u, 2u, 3u};

  utils::OptionalIndexList list;

  utils::IntersectOptionalIndexListWith(list, utils::Indices{});
  AssertEq(utils::IndexList{}, list, "none * empty -> empty");

  utils::IntersectOptionalIndexListWith(list, utils::IndexList{});
  AssertEq(utils::IndexList{}, list, "empty * empty -> empty");

  utils::IntersectOptionalIndexListWith(list, any);
  AssertEq(utils::IndexList{}, list, "empty * any -> empty");

  list = boost::none;
  utils::IntersectOptionalIndexListWith(list, any);
  AssertEq(any, list, "none * any -> any");

  utils::IntersectOptionalIndexListWith(list, any);
  AssertEq(any, list, "any * any -> any");

  utils::IntersectOptionalIndexListWith(list, utils::Indices{2u, 3u, 4u});
  AssertEq({2u, 3u}, list, "any * any2");

  utils::IntersectOptionalIndexListWith(list, utils::IndexList{});
  AssertEq(utils::IndexList{}, list, "any * empty -> empty");
}

TEST(TestIndices, IntersectOptionalIndexListWithUnion) {
  const utils::IndicesMap<int> map{{1, {1u, 2u}}, {2, {2u, 3u}}};

  utils::OptionalIndexList list;

  utils::IntersectOptionalIndexListWithUnion<int>(list, {3, 4}, map);
  AssertEq(utils::IndexList{}, list, "none * empty -> empty");

  utils::IntersectOptionalIndexListWithUnion<int>(list, {1, 2}, map);
  AssertEq(utils::IndexList{}, list, "empty * any -> empty");

  list = boost::none;
  utils::IntersectOptionalIndexListWithUnion<int>(list, {1, 2}, map);
  AssertEq({1u, 2u, 3u}, list, "none * any -> any");

  utils::IntersectOptionalIndexListWithUnion<int>(list, {2}, map);
  AssertEq({2u, 3u}, list, "any * subset any -> subset any");

  utils::IntersectOptionalIndexListWithUnion<int>(list, {1}, map);
  AssertEq({2u}, list, "a * b");
}

TEST(TestIndices, IntersectOptionalIndexListWithIntersection) {
  const utils::IndicesMap<int> map{{1, {1u, 2u}}, {2, {2u, 3u}}};

  utils::OptionalIndexList list;

  utils::IntersectOptionalIndexListWithIntersection(
      list, std::vector<int>{3, 4}, map);
  AssertEq(utils::IndexList{}, list, "none * empty -> empty");

  utils::IntersectOptionalIndexListWithIntersection(
      list, std::vector<int>{1, 2}, map);
  AssertEq(utils::IndexList{}, list, "empty * any -> empty");

  list = boost::none;
  utils::IntersectOptionalIndexListWithIntersection(
      list, std::vector<int>{1, 2}, map);
  AssertEq({2u}, list, "none * any -> any");

  utils::IntersectOptionalIndexListWithIntersection(list, std::vector<int>{2},
                                                    map);
  AssertEq({2u}, list, "subset any * any -> subset any");

  utils::IntersectOptionalIndexListWithIntersection(list, std::vector<int>{1},
                                                    map);
  AssertEq({2u}, list, "subset any * any -> subset any");
}
