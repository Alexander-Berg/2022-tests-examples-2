#include <gtest/gtest.h>

#include <handler_util/errors.hpp>
#include "models/user_phones.hpp"

TEST(CleanInternationalPhone, TEST1) {
  models::CountryMap m;
  m["rus"] = {"rus", {}, {},    {},   boost::none, "RU", "_",
              "7",   11, 11,    225,  "1",         "8",  {},
              {},    {}, false, true, boost::none, {}};
  m["ukr"] = {"rus", {}, {},    {},    boost::none, "UA", "_",
              "380", 12, 12,    0,     "1",         "0",  {},
              {},    {}, false, false, boost::none, {}};

  auto f = models::CleanInternationalPhone;
  EXPECT_EQ(f("", std::string("rus"), m, boost::none), boost::none);
  EXPECT_EQ(f(" +7(900)888 77 66 ", std::string("some_country"), m, boost::none)
                .get(),
            "+79008887766");
  EXPECT_EQ(f("79008887766", std::string("rus"), m, boost::none).get(),
            "+79008887766");
  EXPECT_EQ(f("8(900)888-77-66", std::string("rus"), m, boost::none).get(),
            "+79008887766");
  EXPECT_EQ(f("+380937740000", std::string("rus"), m, boost::none).get(),
            "+380937740000");
  EXPECT_EQ(f("0937740000", std::string("ukr"), m, boost::none).get(),
            "+380937740000");
}
