#include <gtest/gtest.h>

#include "classes.hpp"

using namespace models;

namespace {

struct ClassMeta {
  const char* name;
  uint16_t id;
};

static const ClassMeta kClassList[] = {
    {"express", Classes::Express},   {"econom", Classes::Econom},
    {"business", Classes::Business}, {"comfortplus", Classes::ComfortPlus},
    {"vip", Classes::Vip},           {"minivan", Classes::Minivan}};

}  // namespace

TEST(ClassesMapper, Parse_Valid) {
  for (ClassMeta c : kClassList) {
    EXPECT_EQ(c.id, ClassesMapper::Parse(c.name));
  }
}

TEST(ClassesMapper, Parse_Invalid) {
  EXPECT_EQ(Classes::Unknown, ClassesMapper::Parse(""));
  EXPECT_EQ(Classes::Unknown, ClassesMapper::Parse("qwerty"));
  EXPECT_EQ(Classes::Unknown, ClassesMapper::Parse("unknown"));
}

TEST(ClassesMapper, Validate_Valid) {
  for (ClassMeta c : kClassList) {
    EXPECT_EQ(c.id, ClassesMapper::Validate(c.id));
  }
}

TEST(ClassesMapper, Validate_Invalid) {
  EXPECT_EQ(Classes::Unknown, ClassesMapper::Validate(Classes::Unknown));
  EXPECT_EQ(Classes::Unknown, ClassesMapper::Validate(-1));
  EXPECT_EQ(Classes::Unknown, ClassesMapper::Validate(256));
}

TEST(Classes, Add_Str) {
  Classes classes;

  // prepare
  for (ClassMeta c : kClassList) {
    classes.Add(c.name);
  }

  // check
  EXPECT_FALSE(classes.Empty());
  for (ClassMeta c : kClassList) {
    EXPECT_TRUE(classes.Provides(c.id));
  }
}

TEST(Classes, Add_Id) {
  Classes classes;

  // prepare
  for (ClassMeta c : kClassList) {
    classes.Add(c.id);
  }

  // check
  EXPECT_FALSE(classes.Empty());
  for (ClassMeta c : kClassList) {
    EXPECT_TRUE(classes.Provides(c.id));
  }
}

TEST(Classes, Add_Class) {
  Classes classes0;
  Classes classes1;

  // prepare
  int i = 0;
  for (ClassMeta c : kClassList) {
    (i++ % 2 ? classes0 : classes1).Add(c.id);
  }
  classes0.Add(classes1);

  // check
  EXPECT_FALSE(classes0.Empty());
  for (ClassMeta c : kClassList) {
    EXPECT_TRUE(classes0.Provides(c.id));
  }
}

TEST(Classes, Remove_Str) {
  Classes classes;

  // prepare
  for (ClassMeta c : kClassList) {
    classes.Add(c.id);
  }

  int i = 0;
  for (ClassMeta c : kClassList) {
    if (i++ % 2) classes.Remove(c.name);
  }

  // check
  EXPECT_FALSE(classes.Empty());
  i = 0;
  for (ClassMeta c : kClassList) {
    EXPECT_NE(static_cast<bool>(i++ % 2), classes.Provides(c.id));
  }
}

TEST(Classes, Remove_Id) {
  Classes classes;

  // prepare
  for (ClassMeta c : kClassList) {
    classes.Add(c.id);
  }

  int i = 0;
  for (ClassMeta c : kClassList) {
    if (i++ % 2) classes.Remove(c.id);
  }

  // check
  EXPECT_FALSE(classes.Empty());
  i = 0;
  for (ClassMeta c : kClassList) {
    EXPECT_NE(static_cast<bool>(i++ % 2), classes.Provides(c.id));
  }
}

TEST(Classes, Remove_Classes) {
  Classes classes0;
  Classes classes1;

  // prepare
  int i = 0;
  for (ClassMeta c : kClassList) {
    classes0.Add(c.id);
    if (i++ % 2) classes1.Add(c.id);
  }
  classes0.Remove(classes1);

  // check
  EXPECT_FALSE(classes0.Empty());
  i = 0;
  for (ClassMeta c : kClassList) {
    EXPECT_NE(static_cast<bool>(i++ % 2), classes0.Provides(c.id));
  }
}

TEST(Classes, AndMask) {
  Classes classes0;
  Classes classes1;

  // prepare
  int i = 0;
  for (ClassMeta c : kClassList) {
    classes0.Add(c.id);
    if (i++ % 2) classes1.Add(c.id);
  }
  classes0.AndMask(classes1);

  // check
  EXPECT_FALSE(classes0.Empty());
  i = 0;
  for (ClassMeta c : kClassList) {
    EXPECT_EQ(static_cast<bool>(i % 2), classes0.Provides(c.id));
    ++i;
  }
}

TEST(Classes, Provides_Id) {
  Classes classes;

  // prepare
  int i = 0;
  for (ClassMeta c : kClassList) {
    if (i++ % 2) classes.Add(c.id);
  }

  // check
  i = 0;
  for (ClassMeta c : kClassList) {
    EXPECT_EQ(static_cast<bool>(i % 2), classes.Provides(c.id));
    ++i;
  }
}

TEST(Classes, Provides_Classes) {
  Classes classes0;
  Classes classes1;

  // prepare 0
  int i = 0;
  for (ClassMeta c : kClassList) {
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

TEST(Classes, Empty) {
  Classes classes;

  // check 0
  EXPECT_TRUE(classes.Empty());

  // prepare 1
  classes.Add(Classes::Unknown);

  // check 1
  EXPECT_TRUE(classes.Empty());

  // prepare 2
  classes.Add(Classes::Econom);

  // check 2
  EXPECT_FALSE(classes.Empty());
}

TEST(Classes, GetFirstActive) {
  Classes classes;

  // check 0
  EXPECT_EQ(Classes::Unknown, classes.GetFirstActive());

  // prepare 1
  classes.Add(Classes::Business);
  classes.Add(Classes::Vip);
  classes.Add(Classes::Minivan);

  // check 1
  EXPECT_EQ(Classes::Business, classes.GetFirstActive());
}

TEST(Classes, IterateNonEmpty) {
  Classes classes;

  classes.Add(Classes::Business);
  classes.Add(Classes::Vip);
  classes.Add(Classes::Minivan);

  std::array<ClassType, 3> expected_types{{
      Classes::Business,
      Classes::Vip,
      Classes::Minivan,
  }};

  uint8_t i = 0;
  for (ClassType t : classes) {
    EXPECT_EQ(t, expected_types[i++]);
  }
  EXPECT_EQ(3, i);
  i = 0;
  for (const auto& t : classes) {
    EXPECT_EQ(t, expected_types[i++]);
  }
  EXPECT_EQ(3, i);
}

TEST(Classes, NewClass) {
  EXPECT_EQ(Classes::MaxClassType, 52)
      << "In order to register new class "
         "you have to add it into driver-categories-api database. "
         "Please ensure you have it in both places. "
         "This class categories and driver-categories-api "
         "have to be synced manually some time. "
         "See also TAXIMETERBACK-8336. Ask: @azinoviev, @unpaleness.";
}

TEST(Classes, IterateEmpty) {
  Classes classes;
  EXPECT_FALSE(classes.begin() != classes.end());
}

TEST(ClassesGrade, Constructor) {
  ClassesGrade grade;
  for (ClassMeta c : kClassList) {
    EXPECT_EQ(ClassesGrade::Default, grade.Get(c.id));
  }
}

TEST(ClassesGrade, Set_Get_Name) {
  ClassesGrade grade;

  // prepare
  for (ClassMeta c : kClassList) {
    // id as grade
    grade.Set(c.name, static_cast<ClassesGrade::value_t>(c.id));
  }

  // check
  for (ClassMeta c : kClassList) {
    EXPECT_EQ(static_cast<ClassesGrade::value_t>(c.id), grade.Get(c.name));
  }
}

TEST(ClassesGrade, Set_Get_Id) {
  ClassesGrade grade;

  // prepare
  for (ClassMeta c : kClassList) {
    // id as grade
    grade.Set(c.id, static_cast<ClassesGrade::value_t>(c.id));
  }

  // check
  for (ClassMeta c : kClassList) {
    EXPECT_EQ(static_cast<ClassesGrade::value_t>(c.id), grade.Get(c.id));
  }
}

TEST(ClassesGrade, Fill) {
  ClassesGrade grade;

  // check 0
  for (ClassMeta c : kClassList) {
    EXPECT_EQ(ClassesGrade::Default, grade.Get(c.id));
  }

  // prepare 1
  grade.Fill(1);

  // check 1
  for (ClassMeta c : kClassList) {
    EXPECT_EQ(1, grade.Get(c.id));
  }
}

TEST(ClassesGrade, GetEnabledClasses) {
  ClassesGrade grade;

  // check 0
  EXPECT_FALSE(grade.GetEnabledClasses().Empty());

  // prepare 1
  int i = 0;
  for (ClassMeta c : kClassList) {
    if (i++ % 2) grade.Set(c.id, ClassesGrade::Disabled);
  }

  // check 1
  const Classes& greadeClasses = grade.GetEnabledClasses();
  EXPECT_FALSE(greadeClasses.Empty());
  for (ClassMeta c : kClassList) {
    EXPECT_NE(static_cast<bool>(i++ % 2), greadeClasses.Provides(c.id));
  }
}

TEST(ClassesGrade, GetDisabledClasses) {
  ClassesGrade grade;

  // check 0
  EXPECT_TRUE(grade.GetDisabledClasses().Empty());

  // prepare 1
  int i = 0;
  for (ClassMeta c : kClassList) {
    if (i++ % 2) grade.Set(c.id, ClassesGrade::Disabled);
  }

  // check 1
  const Classes& greadeClasses = grade.GetDisabledClasses();
  EXPECT_FALSE(greadeClasses.Empty());
  for (ClassMeta c : kClassList) {
    EXPECT_EQ(static_cast<bool>(i % 2), greadeClasses.Provides(c.id));
    ++i;
  }
}
