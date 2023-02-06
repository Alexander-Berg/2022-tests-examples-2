#include <userver/utest/utest.hpp>

#include <string>
#include <vector>

#include <eventus/mappers/string_to_dict_mapper.hpp>
#include <eventus/mappers/test_utils.hpp>

namespace {

using namespace eventus::mappers::test_utils;
using OperationArgsV = std::vector<eventus::common::OperationArgument>;

const OperationArgsV string_to_dict_args{{"dst", "dst_key"},
                                         {"src", "src_key"}};

void AppendArgs(OperationArgsV& to, const OperationArgsV& from) {
  if (!from.empty()) {
    to.insert(to.end(), from.begin(), from.end());
  }
}

void MakeStringToDictTest(std::string&& event_str, std::string&& expected,
                          OperationArgsV add_args = {}) {
  auto args = string_to_dict_args;
  AppendArgs(args, add_args);
  MakeTest<eventus::mappers::StringToDictMapper>(std::move(event_str),
                                                 std::move(expected), args);
}

void MakeStringToDictTestWithExcp(std::string&& event_str,
                                  OperationArgsV add_args = {}) {
  auto args = string_to_dict_args;
  AppendArgs(args, add_args);
  MakeTestWithException<eventus::mappers::StringToDictMapper>(
      std::move(event_str), args);
}

}  // namespace

TEST(StringToDictMapper, Good) {
  std::string event_str = R"(
    {
      "src_key":"app_brand=yataxi,app_ver3=0,device_make=apple,app_name=mobileweb_iphone,platform_ver2=4,app_build=release,app_ver2=17,app_ver1=600,platform_ver1=14"
    }
  )";

  std::string expected = R"(
    {
      "src_key":"app_brand=yataxi,app_ver3=0,device_make=apple,app_name=mobileweb_iphone,platform_ver2=4,app_build=release,app_ver2=17,app_ver1=600,platform_ver1=14",
      "dst_key":{
        "app_brand":"yataxi",
        "app_ver3":"0",
        "device_make":"apple",
        "app_name":"mobileweb_iphone",
        "platform_ver2":"4",
        "app_build":"release",
        "app_ver2":"17",
        "app_ver1":"600",
        "platform_ver1":"14"
      }
    }
  )";
  MakeStringToDictTest(std::move(event_str), std::move(expected));
}

TEST(StringToDictMapper, GoodWithoutTrim) {
  OperationArgsV add_args{{"pairs_delimiter", ";"},
                          {"key_value_delimiter", ":"}};

  std::string event_str = R"(
    {
      "src_key":"app_brand: yataxi;app_ver3: 0;device_make: apple;app_name: mobileweb_iphone;platform_ver2: 4;app_build: release;app_ver2: 17;app_ver1: 600;platform_ver1: 14"
    }
  )";

  std::string expected = R"(
    {
      "src_key":"app_brand: yataxi;app_ver3: 0;device_make: apple;app_name: mobileweb_iphone;platform_ver2: 4;app_build: release;app_ver2: 17;app_ver1: 600;platform_ver1: 14",
      "dst_key":{
        "app_brand":" yataxi",
        "app_ver3":" 0",
        "device_make":" apple",
        "app_name":" mobileweb_iphone",
        "platform_ver2":" 4",
        "app_build":" release",
        "app_ver2":" 17",
        "app_ver1":" 600",
        "platform_ver1":" 14"
      }
    }
  )";
  MakeStringToDictTest(std::move(event_str), std::move(expected), add_args);
}

TEST(StringToDictMapper, GoodWithTrim) {
  OperationArgsV add_args{
      {"pairs_delimiter", ";"}, {"key_value_delimiter", ":"}, {"trim", "true"}};

  std::string event_str = R"(
    {
      "src_key":"app_brand: yataxi; app_ver3: 0; device_make: apple; app_name: mobileweb_iphone; platform_ver2: 4; app_build: release; app_ver2: 17; app_ver1: 600; platform_ver1: 14"
    }
  )";

  std::string expected = R"(
    {
      "src_key":"app_brand: yataxi; app_ver3: 0; device_make: apple; app_name: mobileweb_iphone; platform_ver2: 4; app_build: release; app_ver2: 17; app_ver1: 600; platform_ver1: 14",
      "dst_key":{
        "app_brand":"yataxi",
        "app_ver3":"0",
        "device_make":"apple",
        "app_name":"mobileweb_iphone",
        "platform_ver2":"4",
        "app_build":"release",
        "app_ver2":"17",
        "app_ver1":"600",
        "platform_ver1":"14"
      }
    }
  )";
  MakeStringToDictTest(std::move(event_str), std::move(expected), add_args);
}

TEST(StringToDictMapper, EmptyKey) {
  std::string event_str = R"(
    {
      "src_key":"=yataxi,app_ver3,device_make=apple"
    }
  )";
  MakeStringToDictTestWithExcp(std::move(event_str));
}

TEST(StringToDictMapper, KeyValue3Elems) {
  std::string event_str = R"(
    {
      "src_key":"a=yataxi=a,app_ver3,device_make=apple"
    }
  )";
  MakeStringToDictTestWithExcp(std::move(event_str));
}

TEST(StringToDictMapper, FailedToSplit) {
  std::string event_str = R"(
    {
      "src_key":"app_brand=yataxi,app_ver3,device_make=apple"
    }
  )";
  MakeStringToDictTestWithExcp(std::move(event_str));
}

TEST(StringToDictMapper, WrongArgs1) {
  const OperationArgsV add_args{{"key_value_delimiter", ";"},
                                {"pairs_delimiter", ""}};
  auto args = string_to_dict_args;
  AppendArgs(args, add_args);
  EXPECT_THROW(auto m = eventus::mappers::StringToDictMapper(args),
               std::exception);
}

TEST(StringToDictMapper, WrongArgs2) {
  const OperationArgsV add_args{{"key_value_delimiter", ";"},
                                {"pairs_delimiter", "asd"}};
  auto args = string_to_dict_args;
  AppendArgs(args, add_args);
  EXPECT_THROW(auto m = eventus::mappers::StringToDictMapper(args),
               std::exception);
}

TEST(StringToDictMapper, WrongArgs3) {
  const OperationArgsV add_args{{"key_value_delimiter", ";"},
                                {"pairs_delimiter", ";"}};
  auto args = string_to_dict_args;
  AppendArgs(args, add_args);
  EXPECT_THROW(auto m = eventus::mappers::StringToDictMapper(args),
               std::exception);
}

TEST(StringToDictMapper, WrongArgs4) {
  const OperationArgsV add_args{
      {"key_value_delimiter", ","}, {"pairs_delimiter", ";"}, {"trim", "asd"}};
  auto args = string_to_dict_args;
  AppendArgs(args, add_args);
  EXPECT_THROW(auto m = eventus::mappers::StringToDictMapper(args),
               std::exception);
}
