#include <gtest/gtest.h>

#include <userver/formats/json.hpp>

#include <utils/json_field_check.hpp>
#include <utils/time.hpp>

namespace hejmdal::utils::detail {

using ParamCheck = utils::JsonFieldCheck<except::InvalidBlockSerialization>;

namespace {

class MockClass {
 public:
  MockClass(int) : data_("int"){};
  MockClass(double) : data_("double"){};
  MockClass(bool) : data_("bool"){};

  bool operator==(const MockClass& other) const { return data_ == other.data_; }

 private:
  std::string data_;
};

}  // namespace

TEST(TestJsonFieldCheck, MainTest) {
  formats::json::ValueBuilder builder(formats::json::Type::kObject);
  builder["int"] = 5;
  builder["double"] = 3.3;
  builder["string"] = "data";
  builder["bool"] = false;
  builder["array"] = formats::json::MakeArray(1, 2, 3);
  const auto serialisation = builder.ExtractValue();

  // 1. General check
  ASSERT_EQ(ParamCheck("Test", serialisation, "int").Int().Get(), 5);
  ASSERT_EQ(ParamCheck("Test", serialisation, "double").Double().Get(), 3.3);
  ASSERT_EQ(ParamCheck("Test", serialisation, "string").String().Get(), "data");
  ASSERT_EQ(ParamCheck("Test", serialisation, "bool").Bool().Get(), false);
  ASSERT_EQ(ParamCheck("Test", serialisation, "array").ArrayOf<int>().Get(),
            std::vector<int>({1, 2, 3}));

  // 2. GetOpt and GetOr
  ASSERT_EQ(ParamCheck("Test", serialisation, "not exist").Int().GetOpt(),
            std::nullopt);
  ASSERT_EQ(ParamCheck("Test", serialisation, "not exist").Int().GetOr(3), 3);

  // 3. GetAsOptOf
  ASSERT_EQ(ParamCheck("Test", serialisation, "int")
                .Int()
                .GetAsOptOf<time::Seconds>(),
            time::Seconds{5});
  ASSERT_EQ(ParamCheck("Test", serialisation, "not exist")
                .Int()
                .GetAsOptOf<time::Seconds>(),
            std::nullopt);
  ASSERT_EQ(ParamCheck("Test", serialisation, "int")
                .Int()
                .GetAsOptOf<MockClass>()
                .value(),
            MockClass(1));
  ASSERT_EQ(ParamCheck("Test", serialisation, "double")
                .Double()
                .GetAsOptOf<MockClass>()
                .value(),
            MockClass(3.3));
  ASSERT_EQ(ParamCheck("Test", serialisation, "bool")
                .Bool()
                .GetAsOptOf<MockClass>()
                .value(),
            MockClass(false));

  // 4. Fails
  ASSERT_THROW(ParamCheck("Test", serialisation, "bool").Int().Get(),
               except::InvalidBlockSerialization);
  ASSERT_THROW(ParamCheck("Test", serialisation, "string").Double().Get(),
               except::InvalidBlockSerialization);
  ASSERT_THROW(ParamCheck("Test", serialisation, "not exist").Required(),
               except::InvalidBlockSerialization);
}

}  // namespace hejmdal::utils::detail
