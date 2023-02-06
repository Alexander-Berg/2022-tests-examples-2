#include <userver/utest/utest.hpp>

#include <eventus/mappers/fetch_keys_from_dict_mapper.hpp>
#include <eventus/mappers/test_utils.hpp>
#include <string>
#include <vector>

namespace {

using namespace eventus::mappers::test_utils;
using OperationArgsV = std::vector<eventus::common::OperationArgument>;

const OperationArgsV fetch_keys_args{{"dst", "dst_key"}, {"dict", "dict_key"}};

void MakeFetchKeysTest(std::string&& event_str, std::string&& expected) {
  MakeTest<eventus::mappers::FetchKeysFromDictMapper>(
      std::move(event_str), std::move(expected), fetch_keys_args);
}

void MakeFetchKeysTestWithExcp(std::string&& event_str) {
  MakeTestWithException<eventus::mappers::FetchKeysFromDictMapper>(
      std::move(event_str), fetch_keys_args);
}

}  // namespace

TEST(FetchKeysMapper, Good_1) {
  std::string event_str = R"(
    {
      "dict_key":{
        "a":"aaa",
        "b":"bbb"
      }
    }
  )";
  std::string expected = R"(
    {
      "dict_key":{
        "a":"aaa",
        "b":"bbb"
      },
      "dst_key":["a", "b"]
    }
  )";
  MakeFetchKeysTest(std::move(event_str), std::move(expected));
}

TEST(FetchKeysMapper, Good_2) {
  std::string event_str = R"(
    {
      "dict_key":{
        "a":"aaa",
        "b":"bbb"
      }
    }
  )";
  std::string expected = R"(
    {
      "dict_key":{
        "a":"aaa",
        "b":"bbb"
      },
      "dst_key":["a", "b"]
    }
  )";
  MakeFetchKeysTest(std::move(event_str), std::move(expected));
}

TEST(FetchKeysMapper, Good_3) {
  std::string event_str = R"(
    {
      "dict_key":{
        "a":{"aaa":"aa"},
        "b":{"bbb":"bb"}
      },
      "dst_key":{"dfg":1}
    }
  )";
  std::string expected = R"(
    {
      "dict_key":{
        "a":{"aaa":"aa"},
        "b":{"bbb":"bb"}
      },
      "dst_key":["a", "b"]
    }
  )";
  MakeFetchKeysTest(std::move(event_str), std::move(expected));
}

TEST(FetchKeysMapper, EmptyDict) {
  std::string event_str = R"(
    {
      "dict_key":{}
    }
  )";
  std::string expected = R"(
    {
      "dict_key":{},
      "dst_key":[]
    }
  )";
  MakeFetchKeysTest(std::move(event_str), std::move(expected));
}

TEST(FetchKeysMapper, NoDictKey) {
  std::string event_str = R"(
    {
    }
  )";
  MakeFetchKeysTestWithExcp(std::move(event_str));
}

TEST(FetchKeysMapper, WrongDictType_1) {
  std::string event_str = R"(
    {
      "dict_key":[1,2]
    }
  )";
  MakeFetchKeysTestWithExcp(std::move(event_str));
}

TEST(FetchKeysMapper, WrongDictType_2) {
  std::string event_str = R"(
    {
      "dict_key": 1
    }
  )";
  MakeFetchKeysTestWithExcp(std::move(event_str));
}
