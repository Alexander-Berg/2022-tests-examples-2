#include <gtest/gtest.h>
#include <boost/uuid/string_generator.hpp>

#include "uuid.hpp"

boost::uuids::string_generator parse;

TEST(Uuid, ToString) {
  boost::uuids::uuid uuid = parse("acfc69c8-afe9-47ba-887f-d6404428b31c");
  ASSERT_EQ("acfc69c8afe947ba887fd6404428b31c", utils::uuid::ToString(uuid));
}

TEST(Uuid, FromString) {
  boost::uuids::uuid uuid = parse("f728fffb-d334-4908-56d8-5ab5b1b6639a");
  ASSERT_EQ(uuid, utils::uuid::FromString("f728fffbd334490856d85ab5b1b6639a"));
}
