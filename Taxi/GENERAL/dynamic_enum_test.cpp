#include <dynamic_enum/dynamic_enum.hpp>

#include <gtest/gtest.h>
#include <boost/regex.hpp>

#include <array>

#include <userver/utest/utest.hpp>

namespace {

namespace models {
namespace detail {
bool ValidateExam(const std::string& name) {
  static const boost::regex kFormat("[a-zA-Z0-9_-]+");
  return boost::regex_match(name, kFormat);
}
}  // namespace detail

enum class Exam : uint16_t {};
using ExamMapper = ::dynamic_enum::Mapper<Exam, 64, 128, detail::ValidateExam>;
using Exams = ::dynamic_enum::Mask<ExamMapper>;
}  // namespace models

struct ExamMeta {
  std::string name;
  models::Exam value;

  ExamMeta(const std::string& name)
      : name(name), value(models::ExamMapper::Parse(name)) {}
};

std::vector<ExamMeta> GetExamMetaList() {
  std::vector<ExamMeta> list;
  list.emplace_back("express");
  list.emplace_back("econom");
  list.emplace_back("business");
  list.emplace_back("comfortplus");
  list.emplace_back("vip");
  list.emplace_back("minivan");
  return list;
}

}  // namespace

UTEST(DynamicEnum, Parse_Invalid) {
  EXPECT_EQ(models::ExamMapper::kUnknown, models::ExamMapper::Parse(""));
}

UTEST(DynamicEnum, Validate_Valid) {
  for (const auto& item : GetExamMetaList()) {
    EXPECT_EQ(item.value, models::ExamMapper::Validate(item.value));
  }
}

UTEST(DynamicEnum, Validate_Invalid) {
  EXPECT_EQ(models::ExamMapper::kUnknown,
            models::ExamMapper::Validate(models::ExamMapper::kUnknown));
  EXPECT_EQ(models::ExamMapper::kUnknown,
            models::ExamMapper::Validate(static_cast<models::Exam>(-1)));
  EXPECT_EQ(models::ExamMapper::kUnknown,
            models::ExamMapper::Validate(
                static_cast<models::Exam>(models::ExamMapper::kMaxCount + 1)));
}

UTEST(DynamicEnum, Add_Str) {
  const auto& list = GetExamMetaList();

  models::Exams exams;

  // prepare
  for (const auto& c : list) {
    exams.Add(c.name);
  }

  // check
  EXPECT_FALSE(exams.empty());
  for (const auto& c : list) {
    EXPECT_TRUE(exams.Provides(c.value));
  }
}

UTEST(DynamicEnum, Add_Value) {
  const auto& list = GetExamMetaList();

  models::Exams exams;

  // prepare
  for (const auto& c : list) {
    exams.Add(c.value);
  }

  // check
  EXPECT_FALSE(exams.empty());
  for (const auto& c : list) {
    EXPECT_TRUE(exams.Provides(c.value));
  }
}

UTEST(DynamicEnum, Add_Mask) {
  const auto& list = GetExamMetaList();

  models::Exams exams0;
  models::Exams exams1;

  // prepare
  int i = 0;
  for (const auto& c : list) {
    (i++ % 2 ? exams0 : exams1).Add(c.value);
  }
  exams0.Add(exams1);

  // check
  EXPECT_FALSE(exams0.empty());
  for (const auto& c : list) {
    EXPECT_TRUE(exams0.Provides(c.value));
  }
}

UTEST(DynamicEnum, Remove_Str) {
  const auto& list = GetExamMetaList();

  models::Exams exams;

  // prepare
  for (const auto& c : list) {
    exams.Add(c.value);
  }

  int i = 0;
  for (const auto& c : list) {
    if (i++ % 2) exams.Remove(c.name);
  }

  // check
  EXPECT_FALSE(exams.empty());
  i = 0;
  for (const auto& c : list) {
    EXPECT_NE(static_cast<bool>(i++ % 2), exams.Provides(c.value));
  }
}

UTEST(DynamicEnum, Remove_Value) {
  const auto& list = GetExamMetaList();

  models::Exams exams;

  // prepare
  for (const auto& c : list) {
    exams.Add(c.value);
  }

  int i = 0;
  for (const auto& c : list) {
    if (i++ % 2) exams.Remove(c.value);
  }

  // check
  EXPECT_FALSE(exams.empty());
  i = 0;
  for (const auto& c : list) {
    EXPECT_NE(static_cast<bool>(i++ % 2), exams.Provides(c.value));
  }
}

UTEST(DynamicEnum, Remove_Mask) {
  const auto& list = GetExamMetaList();

  models::Exams exams0;
  models::Exams exams1;

  // prepare
  int i = 0;
  for (const auto& c : list) {
    exams0.Add(c.value);
    if (i++ % 2) exams1.Add(c.value);
  }
  exams0.Remove(exams1);

  // check
  EXPECT_FALSE(exams0.empty());
  i = 0;
  for (const auto& c : list) {
    EXPECT_NE(static_cast<bool>(i++ % 2), exams0.Provides(c.value));
  }
}

UTEST(DynamicEnum, AndMask) {
  const auto& list = GetExamMetaList();

  models::Exams exams0;
  models::Exams exams1;

  // prepare
  int i = 0;
  for (const auto& c : list) {
    exams0.Add(c.value);
    if (i++ % 2) exams1.Add(c.value);
  }
  exams0.AndMask(exams1);

  // check
  EXPECT_FALSE(exams0.empty());
  i = 0;
  for (const auto& c : list) {
    EXPECT_EQ(static_cast<bool>(i % 2), exams0.Provides(c.value));
    ++i;
  }
}

UTEST(DynamicEnum, Provides_Value) {
  const auto& list = GetExamMetaList();

  models::Exams exams;

  // prepare
  int i = 0;
  for (const auto& c : list) {
    if (i++ % 2) exams.Add(c.value);
  }

  // check
  i = 0;
  for (const auto& c : list) {
    EXPECT_EQ(static_cast<bool>(i % 2), exams.Provides(c.value));
    ++i;
  }
}

UTEST(DynamicEnum, Provides_Mask) {
  const auto& list = GetExamMetaList();

  models::Exams exams0;
  models::Exams exams1;

  // prepare 0
  int i = 0;
  for (const auto& c : list) {
    exams0.Add(c.value);
    if (i++ % 2) exams1.Add(c.value);
  }

  // check 0
  EXPECT_TRUE(exams0.Provides(exams0));
  EXPECT_TRUE(exams0.Provides(exams1));
  EXPECT_TRUE(exams1.Provides(exams0));
  EXPECT_TRUE(exams1.Provides(exams1));

  // prepare 1
  exams0.Remove(exams1);

  // check 1
  EXPECT_TRUE(exams0.Provides(exams0));
  EXPECT_FALSE(exams0.Provides(exams1));
  EXPECT_FALSE(exams1.Provides(exams0));
  EXPECT_TRUE(exams1.Provides(exams1));
}

UTEST(DynamicEnum, Empty) {
  models::Exams exams;

  // check 0
  EXPECT_TRUE(exams.empty());

  // prepare 1
  exams.Add(models::ExamMapper::kUnknown);

  // check 1
  EXPECT_TRUE(exams.empty());

  // prepare 2
  exams.Add("econom");

  // check 2
  EXPECT_FALSE(exams.empty());
}

UTEST(DynamicEnum, IterateNonEmpty) {
  const auto& list = GetExamMetaList();

  models::Exams exams;

  exams.Add(list[2].value);
  exams.Add(list[4].value);
  exams.Add(list[5].value);

  std::array<models::Exam, 3> expected_types{{
      list[2].value,
      list[4].value,
      list[5].value,
  }};

  uint8_t i = 0;
  for (const auto t : exams) {
    EXPECT_EQ(t, expected_types[i++]);
  }
  EXPECT_EQ(3, i);
  i = 0;
  for (const auto t : exams) {
    EXPECT_EQ(t, expected_types[i++]);
  }
  EXPECT_EQ(3, i);
}

UTEST(DynamicEnum, IterateEmpty) {
  models::Exams exams;
  EXPECT_EQ(exams.begin(), exams.end());
}

UTEST(DynamicEnum, ValidateOk) {
  const auto backend_cpp_exams = {
      "express",
      "econom",
      "business",
      "comfortplus",
      "vip",
      "minivan",
      "pool",
      "business2",
      "kids",
      "uberx",
      "uberselect",
      "uberblack"
      "uberkids",
      "uberstart",
      "start",
      "standart",
      "child_tariff",
      "poputka",
      "ultimate",
      "mkk",
      "selfdriving",
      "ubervan",
      "uberlux",
      "uberselectplus",
      "maybach",
      "demostand",
      "promo",
      "premium_van",
      "premium_suv",
      "suv",
      "personal_driver",
      "cargo",
      "mkk_antifraud",
      "ubernight",
      "universal",
      "night",
      "multiclass",
      "vezetstart",
      "vezeteconom",
      "vezetbusiness",
      "rutaxistart",
      "rutaxieconom",
      "rutaxibusiness",
  };

  for (const auto& name : backend_cpp_exams) {
    EXPECT_NE(models::ExamMapper::kUnknown, models::ExamMapper::Parse(name));
  }
}

UTEST(DynamicEnum, ValidateFailed) {
  const auto failed_exams = {
      "<input type=text value=a onfocus=alert(1337) AUTOFOCUS>",
      "Ситимобайл",
      "HelloWorld!",
      "@econom",
      "Vasya'); DROP TABLE Students;--",
  };

  for (const auto& name : failed_exams) {
    EXPECT_EQ(models::ExamMapper::kUnknown, models::ExamMapper::Parse(name));
  }
}

UTEST(DynamicEnum, ValidateTooLong) {
  const auto too_long_exams =
      "economeconomeconomeconomeconomeconomeconomeconomeconomeconomeconom"
      "economeconomeconomeconomeconomeconomeconomeconomeconomeconomeconom"
      "economeconomeconomeconomeconomeconomeconomeconomeconomeconomeconom"
      "economeconomeconomeconomeconomeconomeconomeconomeconomeconomeconom"
      "economeconomeconomeconomeconomeconomeconomeconomeconomeconomeconom";

  EXPECT_EQ(models::ExamMapper::kUnknown,
            models::ExamMapper::Parse(too_long_exams));
}

UTEST(DynamicEnum, Logic) {
  const models::Exams one({
      "express",
      "econom",
      "business",
      "comfortplus",
      "vip",
  });
  const models::Exams two({
      "express",
      "business",
      "vip",
  });
  const models::Exams three({
      "comfortplus",
      "vip",
  });

  EXPECT_EQ(models::Exams({"comfortplus", "vip"}), (one | ~two) & three);
  EXPECT_EQ(models::Exams({"express", "business", "vip"}),
            (one | ~three) & two);
  EXPECT_EQ(models::Exams({"vip"}), (two | ~one) & three);
  EXPECT_EQ(models::Exams({"express", "econom", "business", "vip"}),
            (two | ~three) & one);
  EXPECT_EQ(models::Exams({"vip"}), (three | ~one) & two);
  EXPECT_EQ(models::Exams({"econom", "comfortplus", "vip"}),
            (three | ~two) & one);
}
