#include <userver/utest/utest.hpp>

#include <userver/formats/bson/inline.hpp>
#include <userver/formats/bson/serialize.hpp>
#include <userver/formats/bson/value_builder.hpp>

#include <taxi-requirements/models/parse/requirements.hpp>

namespace taxi_requirements::models::requirements {

namespace fb = formats::bson;

namespace {

auto Serialize(const Requirements& model) {
  return fb::ValueBuilder(model).ExtractValue();
}

auto Serialize(const ClassesRequirements& model) {
  return fb::ValueBuilder(model).ExtractValue();
}

template <class T>
void CheckSerializer(const T& requirements, const fb::Value& source) {
  const auto serialized_requirements = Serialize(requirements);
  EXPECT_EQ(serialized_requirements, source)
      << '\n'
      << fb::ToRelaxedJsonString(serialized_requirements)
      << " != " << fb::ToRelaxedJsonString(source) << '\n';
}

}  // namespace

TEST(ModelsParse, NotObject) {
  const auto source = fb::MakeArray(true, 42, "abacaba");
  const auto parsed = source.As<Requirements>();
  EXPECT_EQ(parsed.size(), 0);
  // Empty doc instead of invalid source input.
  CheckSerializer(parsed, fb::MakeDoc());
}

TEST(ModelsParse, ParseBool) {
  const auto source = fb::MakeDoc("ski", true,  //
                                  "yellowcarnumber", false);
  const auto parsed = source.As<Requirements>();

  EXPECT_EQ(parsed.size(), 2);

  EXPECT_TRUE(parsed.count("ski"));
  EXPECT_EQ(std::get<Bool>(parsed.at("ski")), true);

  EXPECT_TRUE(parsed.count("yellowcarnumber"));
  EXPECT_EQ(std::get<Bool>(parsed.at("yellowcarnumber")), false);

  CheckSerializer(parsed, source);
}

TEST(ModelsParse, ParseString) {
  const auto source = fb::MakeDoc("coupon", "promocode123");
  const auto parsed = source.As<Requirements>();

  EXPECT_EQ(parsed.size(), 1);

  EXPECT_TRUE(parsed.count("coupon"));
  EXPECT_EQ(std::get<String>(parsed.at("coupon")), "promocode123");

  CheckSerializer(parsed, source);
}

TEST(ModelsParse, ParseNumber) {
  const auto source = fb::MakeDoc("hourly_rental", 2,  //
                                  "capacity", 3.14);
  const auto parsed = source.As<Requirements>();

  EXPECT_EQ(parsed.size(), 2);

  EXPECT_TRUE(parsed.count("hourly_rental"));
  EXPECT_EQ(std::get<Number>(parsed.at("hourly_rental")), 2);

  EXPECT_TRUE(parsed.count("capacity"));
  EXPECT_EQ(std::get<Number>(parsed.at("capacity")), 3);

  // New doc with truncated floats instead of source doc.
  CheckSerializer(parsed, fb::MakeDoc("hourly_rental", Number{2},  //
                                      "capacity", Number{3}));
}

TEST(ModelsParse, ParseSelect) {
  const auto source = fb::MakeDoc("childchair_moscow", fb::MakeArray(3, 7),  //
                                  "cargo_type", fb::MakeArray("van", "lcv_m"));
  const auto parsed = source.As<Requirements>();

  EXPECT_EQ(parsed.size(), 2);

  EXPECT_TRUE(parsed.count("childchair_moscow"));
  EXPECT_EQ(std::get<Array>(parsed.at("childchair_moscow")),
            (Array{Number{3}, Number{7}}));

  EXPECT_TRUE(parsed.count("cargo_type"));
  EXPECT_EQ(std::get<Array>(parsed.at("cargo_type")),
            (Array{String{"van"}, String{"lcv_m"}}));

  // New doc with int32 upgraded to int64 instead of source doc.
  CheckSerializer(
      parsed,
      fb::MakeDoc("childchair_moscow", fb::MakeArray(Number{3}, Number{7}),  //
                  "cargo_type", fb::MakeArray("van", "lcv_m")));
}

TEST(ModelsParse, ClassesRequirementsNotObject) {
  const auto source = fb::MakeArray(true, 42, "abacaba");
  const auto parsed = source.As<ClassesRequirements>();
  EXPECT_EQ(parsed.size(), 0);

  // Empty doc instead of invalid source input.
  CheckSerializer(parsed, fb::MakeDoc());
}

TEST(ModelsParse, ClassesRequirements) {
  const auto source =
      fb::MakeDoc("child_tariff", fb::MakeDoc("childchair_v2", 10),  //
                  "express", fb::MakeDoc("door_to_door", true),      //
                  "business",
                  fb::MakeDoc("coupon", "promocode123",  //
                              "ski", true));
  const auto parsed = source.As<ClassesRequirements>();

  EXPECT_EQ(parsed.size(), 3);

  EXPECT_TRUE(parsed.count("child_tariff"));
  EXPECT_EQ(parsed.at("child_tariff"),
            (Requirements{{"childchair_v2", Number{10}}}));

  EXPECT_TRUE(parsed.count("express"));
  EXPECT_EQ(parsed.at("express"), (Requirements{{"door_to_door", Bool{true}}}));

  EXPECT_TRUE(parsed.count("business"));
  EXPECT_EQ(
      parsed.at("business"),
      (Requirements{{"coupon", String{"promocode123"}}, {"ski", Bool{true}}}));

  // New doc with int32 upgraded to int64 instead of source doc.
  CheckSerializer(
      parsed,
      fb::MakeDoc("child_tariff", fb::MakeDoc("childchair_v2", Number{10}),  //
                  "express", fb::MakeDoc("door_to_door", true),              //
                  "business",
                  fb::MakeDoc("coupon", "promocode123",  //
                              "ski", true)));
}

}  // namespace taxi_requirements::models::requirements
