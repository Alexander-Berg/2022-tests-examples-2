#include <gtest/gtest.h>

#include <mongo/bson/bson.h>
#include <mongo/bson/bsonmisc.h>
#include <mongo/bson/bsontypes.h>
#include <logging/log_extra.hpp>
#include <utils/uuid4.hpp>
#include <views/helpers/order_proc.hpp>

namespace {
::mongo::BSONObj MakeTestDocument() {
  return ::mongo::BSONObjBuilder()
      .append("performer", BSON("candidate_index" << 1))
      .append("candidates", ::mongo::BSONArrayBuilder()
                                .append(BSON("db_id"
                                             << "1"
                                             << "driver_id"
                                             << "1_1"))
                                .append(BSON("db_id"
                                             << "2"
                                             << "driver_id"
                                             << "2_2"))
                                .arr())
      .obj();
}
}  // namespace

TEST(Parsing, GetCandidateIds) {
  LogExtra log_extra{utils::generators::Uuid4()};
  EXPECT_EQ(views::helpers::ParseParkIdDriverIdFromProc(MakeTestDocument(),
                                                        log_extra),
            std::make_pair(std::string("2"), std::string("2")));
}
