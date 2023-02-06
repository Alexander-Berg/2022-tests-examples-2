#include <gtest/gtest.h>

#include "enum_converter.hpp"

namespace {

enum class SequentialEnum {
  kOne,
  kTwo,
  kThree,
  kFour,
  // keep it last
  kSize
};

enum EnumWithGaps {
  kApple = -10,
  kOrange = 2,
  kPineapple,
  kStrawberry = 19,
  kTomato = -20,
  kOnion,
  kPomidor = kTomato,
};

}  // namespace

TEST(EnumConverterTest, ConversionTest) {
  const auto converter =
      utils::StartEnumConverter<EnumWithGaps, SequentialEnum,
                                SequentialEnum::kSize>()
          .Add(EnumWithGaps::kApple, SequentialEnum::kOne)
          .Add(EnumWithGaps::kStrawberry, SequentialEnum::kTwo)
          .Add(EnumWithGaps::kTomato, SequentialEnum::kThree)
          .Add(EnumWithGaps::kPineapple, SequentialEnum::kFour)
          .Done();

  EXPECT_EQ(converter(EnumWithGaps::kApple), SequentialEnum::kOne);
  EXPECT_EQ(converter(EnumWithGaps::kStrawberry), SequentialEnum::kTwo);
  EXPECT_EQ(converter(EnumWithGaps::kTomato), SequentialEnum::kThree);
  EXPECT_EQ(converter(EnumWithGaps::kPineapple), SequentialEnum::kFour);

  EXPECT_EQ(converter(SequentialEnum::kOne), EnumWithGaps::kApple);
  EXPECT_EQ(converter(SequentialEnum::kTwo), EnumWithGaps::kStrawberry);
  EXPECT_EQ(converter(SequentialEnum::kThree), EnumWithGaps::kTomato);
  EXPECT_EQ(converter(SequentialEnum::kFour), EnumWithGaps::kPineapple);

  EXPECT_THROW(converter(EnumWithGaps::kOnion), std::logic_error);
  EXPECT_THROW(converter(SequentialEnum::kSize), std::logic_error);
}

TEST(EnumConverterTest, NoAliasesTest) {
#ifndef NDEBUG
  EXPECT_DEBUG_DEATH(
      (utils::StartEnumConverter<EnumWithGaps, SequentialEnum, 2>()
           .Add(EnumWithGaps::kTomato, SequentialEnum::kOne)
           .Add(EnumWithGaps::kPomidor, SequentialEnum::kTwo)
           .Done()),
      "");
#else
  EXPECT_THROW((utils::StartEnumConverter<EnumWithGaps, SequentialEnum, 2>()
                    .Add(EnumWithGaps::kTomato, SequentialEnum::kOne)
                    .Add(EnumWithGaps::kPomidor, SequentialEnum::kTwo)
                    .Done()),
               std::logic_error);
#endif
}
