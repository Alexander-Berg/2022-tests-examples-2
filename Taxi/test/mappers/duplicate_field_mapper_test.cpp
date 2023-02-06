#include <userver/utest/utest.hpp>

#include <eventus/mappers/atlas/duplicate_field_mapper.hpp>
#include <eventus/mappers/test_utils.hpp>
#include <string>
#include <vector>

namespace {

using namespace eventus::mappers::test_utils;
using OperationArgsV = std::vector<eventus::common::OperationArgument>;

const OperationArgsV duplicate_field_args{
    {"dst", "dst_key"}, {"src", "src_key"}, {"length", "length_key"}};

void MakeDuplicateFieldTest(std::string&& event_str, std::string&& expected) {
  MakeTest<eventus::mappers::atlas::DuplicateFieldMapper>(
      std::move(event_str), std::move(expected), duplicate_field_args);
}

void MakeDuplicateFieldTestWithExcp(std::string&& event_str) {
  MakeTestWithException<eventus::mappers::atlas::DuplicateFieldMapper>(
      std::move(event_str), duplicate_field_args);
}

}  // namespace

TEST(DuplicateFieldMapper, Good_1) {
  std::string event_str = R"(
    {
      "src_key":"test",
      "length_key":[1,1,1]
    }
  )";

  std::string expected = R"(
    {
      "src_key":"test",
      "length_key":[1,1,1],
      "dst_key":["test","test","test"]
    }
  )";
  MakeDuplicateFieldTest(std::move(event_str), std::move(expected));
}

TEST(DuplicateFieldMapper, Good_2) {
  std::string event_str = R"(
    {
      "src_key":"test",
      "length_key":[1,1,1],
      "test_data":
      {
        "test": "test",
        "test_2": "test"
      }
    }
  )";
  std::string expected = R"(
    {
      "src_key":"test",
      "length_key":[1,1,1],
      "test_data":
      {
        "test": "test",
        "test_2": "test"
      },
      "dst_key":["test","test","test"]
    }
  )";
  MakeDuplicateFieldTest(std::move(event_str), std::move(expected));
}

TEST(DuplicateFieldMapper, Good_3) {
  std::string event_str = R"(
    {
      "src_key":{"obj":"obj","obj1":"obj1"},
      "length_key":[1,1,1]
    }
  )";
  std::string expected = R"(
    {
      "src_key":{"obj":"obj", "obj1":"obj1"},
      "length_key":[1,1,1],
      "dst_key":[{"obj":"obj","obj1":"obj1"},{"obj":"obj","obj1":"obj1"},{"obj":"obj","obj1":"obj1"}]
    }
  )";
  MakeDuplicateFieldTest(std::move(event_str), std::move(expected));
}

TEST(DuplicateFieldMapper, Good_4) {
  std::string event_str = R"(
    {
      "src_key":"test",
      "length_key":[1,1,1],
      "dst_key": "something"
    }
  )";
  std::string expected = R"(
    {
      "src_key":"test",
      "length_key":[1,1,1],
      "dst_key":["test","test","test"]
    }
  )";
  MakeDuplicateFieldTest(std::move(event_str), std::move(expected));
}

TEST(DuplicateFieldMapper, EmptyLength) {
  std::string event_str = R"(
    {
      "src_key":"test",
      "length_key":[]
    }
  )";
  std::string expected = R"(
    {
      "src_key":"test",
      "length_key":[],
      "dst_key":[]
    }
  )";
  MakeDuplicateFieldTest(std::move(event_str), std::move(expected));
}

TEST(DuplicateFieldMapper, WithNull) {
  std::string event_str = R"(
    {
      "src_key":null,
      "length_key":[1,1,1]
    }
  )";
  std::string expected = R"(
    {
      "src_key":null,
      "length_key":[1,1,1],
      "dst_key":[null,null,null]
    }
  )";
  MakeDuplicateFieldTest(std::move(event_str), std::move(expected));
}

TEST(DuplicateFieldMapper, NoFrom) {
  std::string event_str = R"(
    {
      "length_key":[1,1,1]
    }
  )";
  MakeDuplicateFieldTestWithExcp(std::move(event_str));
}

TEST(DuplicateFieldMapper, NoLength) {
  std::string event_str = R"(
    {
      "key_from":""
    }
  )";
  MakeDuplicateFieldTestWithExcp(std::move(event_str));
}

TEST(DuplicateFieldMapper, LengthIsNotArray) {
  std::string event_str = R"(
    {
      "src_key":"test",
      "length_key":"1"
    }
  )";
  MakeDuplicateFieldTestWithExcp(std::move(event_str));
}
