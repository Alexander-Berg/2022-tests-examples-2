#include <userver/utest/utest.hpp>

#include <userver/formats/json/value.hpp>
#include <userver/formats/json/value_builder.hpp>

#include <models/requirements.hpp>

TEST(RequirementsCheck, IsTrue) {
  auto rq = models::requirements::Parse(
      formats::json::ValueBuilder("123").ExtractValue(),
      formats::parse::To<models::requirements::ReqValue>{});

  EXPECT_TRUE(rq.index() == 2);
  EXPECT_FALSE(models::requirements::IsTrue(rq));

  rq = "yes";
  EXPECT_TRUE(models::requirements::IsTrue(rq));

  rq = false;
  EXPECT_TRUE(rq.index() == 0);
  EXPECT_FALSE(models::requirements::IsTrue(rq));

  rq = true;
  EXPECT_TRUE(rq.index() == 0);
  EXPECT_TRUE(models::requirements::IsTrue(rq));

  rq = 1;
  EXPECT_TRUE(rq.index() == 1);
  EXPECT_FALSE(models::requirements::IsTrue(rq));
}
