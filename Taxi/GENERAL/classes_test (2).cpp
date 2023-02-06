#include <models/classes.hpp>

#include <gtest/gtest.h>

#include <array>

#include <userver/utest/utest.hpp>

namespace {

using namespace models;

struct ClassMeta {
  std::string name;
  ClassType id;
};

class ClassesTest : public ::testing::Test {
  void SetUp() {
    AddClass("express");
    AddClass("econom");
    AddClass("business");
    AddClass("comfortplus");
    AddClass("vip");
    AddClass("minivan");
  }

  void AddClass(const std::string& name) {
    auto id = ClassesMapper::Parse(name);
    class_list_.push_back({name, id});
  }

 public:
  std::vector<ClassMeta> class_list_;
};

}  // namespace

UTEST(ClassesMapper, Parse_Invalid) {
  EXPECT_EQ(Classes::kUnknown, ClassesMapper::Parse(""));
}

TEST_F(ClassesTest, Validate_Valid) {
  for (const ClassMeta& c : class_list_) {
    EXPECT_EQ(c.id, ClassesMapper::Validate(c.id));
  }
}

UTEST(Classes, Validate_Invalid) {
  EXPECT_EQ(Classes::kUnknown, ClassesMapper::Validate(Classes::kUnknown));
  EXPECT_EQ(Classes::kUnknown,
            ClassesMapper::Validate(static_cast<ClassType>(-1)));
  EXPECT_EQ(Classes::kUnknown, ClassesMapper::Validate(static_cast<ClassType>(
                                   ClassesMapper::kMaxCount + 1)));
}

TEST_F(ClassesTest, Add_Str) {
  Classes classes;

  // prepare
  for (const ClassMeta& c : class_list_) {
    classes.Add(c.name);
  }

  // check
  EXPECT_FALSE(classes.empty());
  for (const ClassMeta& c : class_list_) {
    EXPECT_TRUE(classes.Provides(c.id));
  }
}

TEST_F(ClassesTest, Add_Id) {
  Classes classes;

  // prepare
  for (const ClassMeta& c : class_list_) {
    classes.Add(c.id);
  }

  // check
  EXPECT_FALSE(classes.empty());
  for (const ClassMeta& c : class_list_) {
    EXPECT_TRUE(classes.Provides(c.id));
  }
}

TEST_F(ClassesTest, Add_Class) {
  Classes classes0;
  Classes classes1;

  // prepare
  int i = 0;
  for (const ClassMeta& c : class_list_) {
    (i++ % 2 ? classes0 : classes1).Add(c.id);
  }
  classes0.Add(classes1);

  // check
  EXPECT_FALSE(classes0.empty());
  for (const ClassMeta& c : class_list_) {
    EXPECT_TRUE(classes0.Provides(c.id));
  }
}

TEST_F(ClassesTest, Remove_Str) {
  Classes classes;

  // prepare
  for (const ClassMeta& c : class_list_) {
    classes.Add(c.id);
  }

  int i = 0;
  for (const ClassMeta& c : class_list_) {
    if (i++ % 2) classes.Remove(c.name);
  }

  // check
  EXPECT_FALSE(classes.empty());
  i = 0;
  for (const ClassMeta& c : class_list_) {
    EXPECT_NE(static_cast<bool>(i++ % 2), classes.Provides(c.id));
  }
}

TEST_F(ClassesTest, Remove_Id) {
  Classes classes;

  // prepare
  for (const ClassMeta& c : class_list_) {
    classes.Add(c.id);
  }

  int i = 0;
  for (const ClassMeta& c : class_list_) {
    if (i++ % 2) classes.Remove(c.id);
  }

  // check
  EXPECT_FALSE(classes.empty());
  i = 0;
  for (const ClassMeta& c : class_list_) {
    EXPECT_NE(static_cast<bool>(i++ % 2), classes.Provides(c.id));
  }
}

TEST_F(ClassesTest, Remove_Classes) {
  Classes classes0;
  Classes classes1;

  // prepare
  int i = 0;
  for (const ClassMeta& c : class_list_) {
    classes0.Add(c.id);
    if (i++ % 2) classes1.Add(c.id);
  }
  classes0.Remove(classes1);

  // check
  EXPECT_FALSE(classes0.empty());
  i = 0;
  for (const ClassMeta& c : class_list_) {
    EXPECT_NE(static_cast<bool>(i++ % 2), classes0.Provides(c.id));
  }
}

TEST_F(ClassesTest, AndMask) {
  Classes classes0;
  Classes classes1;

  // prepare
  int i = 0;
  for (const ClassMeta& c : class_list_) {
    classes0.Add(c.id);
    if (i++ % 2) classes1.Add(c.id);
  }
  classes0.AndMask(classes1);

  // check
  EXPECT_FALSE(classes0.empty());
  i = 0;
  for (const ClassMeta& c : class_list_) {
    EXPECT_EQ(static_cast<bool>(i % 2), classes0.Provides(c.id));
    ++i;
  }
}

TEST_F(ClassesTest, Provides_Id) {
  Classes classes;

  // prepare
  int i = 0;
  for (const ClassMeta& c : class_list_) {
    if (i++ % 2) classes.Add(c.id);
  }

  // check
  i = 0;
  for (const ClassMeta& c : class_list_) {
    EXPECT_EQ(static_cast<bool>(i % 2), classes.Provides(c.id));
    ++i;
  }
}

TEST_F(ClassesTest, Provides_Classes) {
  Classes classes0;
  Classes classes1;

  // prepare 0
  int i = 0;
  for (const ClassMeta& c : class_list_) {
    classes0.Add(c.id);
    if (i++ % 2) classes1.Add(c.id);
  }

  // check 0
  EXPECT_TRUE(classes0.Provides(classes0));
  EXPECT_TRUE(classes0.Provides(classes1));
  EXPECT_TRUE(classes1.Provides(classes0));
  EXPECT_TRUE(classes1.Provides(classes1));

  // prepare 1
  classes0.Remove(classes1);

  // check 1
  EXPECT_TRUE(classes0.Provides(classes0));
  EXPECT_FALSE(classes0.Provides(classes1));
  EXPECT_FALSE(classes1.Provides(classes0));
  EXPECT_TRUE(classes1.Provides(classes1));
}

UTEST(Classes, Empty) {
  Classes classes;

  // check 0
  EXPECT_TRUE(classes.empty());

  // prepare 1
  classes.Add(Classes::kUnknown);

  // check 1
  EXPECT_TRUE(classes.empty());

  // prepare 2
  classes.Add("econom");

  // check 2
  EXPECT_FALSE(classes.empty());
}

TEST_F(ClassesTest, IterateNonEmpty) {
  Classes classes;

  classes.Add(class_list_[2].id);
  classes.Add(class_list_[4].id);
  classes.Add(class_list_[5].id);

  std::array<ClassType, 3> expected_types{{
      class_list_[2].id,
      class_list_[4].id,
      class_list_[5].id,
  }};

  uint8_t i = 0;
  for (const ClassType t : classes) {
    EXPECT_EQ(t, expected_types[i++]);
  }
  EXPECT_EQ(3, i);
  i = 0;
  for (const auto& t : classes) {
    EXPECT_EQ(t, expected_types[i++]);
  }
  EXPECT_EQ(3, i);
}

UTEST(Classes, IterateEmpty) {
  Classes classes;
  EXPECT_EQ(classes.begin(), classes.end());
}

UTEST(ClassesMapper, ValidateOk) {
  const auto backend_cpp_classes = {
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

  for (const auto& name : backend_cpp_classes) {
    EXPECT_NE(Classes::kUnknown, ClassesMapper::Parse(name));
  }
}

UTEST(ClassesMapper, ValidateFailed) {
  const auto failed_classes = {
      "<input type=text value=a onfocus=alert(1337) AUTOFOCUS>",
      "Ситимобайл",
      "HelloWorld!",
      "@econom",
      "Vasya'); DROP TABLE Students;--",
  };

  for (const auto& name : failed_classes) {
    EXPECT_EQ(Classes::kUnknown, ClassesMapper::Parse(name));
  }
}

UTEST(ClassesMapper, ValidateTooLong) {
  const auto too_long_classes =
      "economeconomeconomeconomeconomeconomeconomeconomeconomeconomeconom"
      "economeconomeconomeconomeconomeconomeconomeconomeconomeconomeconom"
      "economeconomeconomeconomeconomeconomeconomeconomeconomeconomeconom"
      "economeconomeconomeconomeconomeconomeconomeconomeconomeconomeconom"
      "economeconomeconomeconomeconomeconomeconomeconomeconomeconomeconom";

  EXPECT_EQ(Classes::kUnknown, ClassesMapper::Parse(too_long_classes));
}

UTEST(Classes, CategoriesLogic) {
  const Classes one({
      "express",
      "econom",
      "business",
      "comfortplus",
      "vip",
  });
  const Classes two({
      "express",
      "business",
      "vip",
  });
  const Classes three({
      "comfortplus",
      "vip",
  });

  EXPECT_EQ(Classes({"comfortplus", "vip"}), (one | ~two) & three);
  EXPECT_EQ(Classes({"express", "business", "vip"}), (one | ~three) & two);
  EXPECT_EQ(Classes({"vip"}), (two | ~one) & three);
  EXPECT_EQ(Classes({"express", "econom", "business", "vip"}),
            (two | ~three) & one);
  EXPECT_EQ(Classes({"vip"}), (three | ~one) & two);
  EXPECT_EQ(Classes({"econom", "comfortplus", "vip"}), (three | ~two) & one);
}
