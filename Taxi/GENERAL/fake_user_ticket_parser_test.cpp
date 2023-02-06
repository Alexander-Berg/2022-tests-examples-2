#include <gtest/gtest.h>

#include <logging/log_extra.hpp>

#include <models/tvm2.hpp>
#include <utils/tvm/fake_user_ticket_parser.hpp>

TEST(FakeUserTicketParser, JustTesting) {
  EXPECT_THROW((models::FakeUserContext(models::ContextEnviroment::kYaProd)),
               std::logic_error);
  EXPECT_THROW(
      (models::FakeUserContext(models::ContextEnviroment::kYaTeamProd)),
      std::logic_error);
  EXPECT_NO_THROW(
      (models::FakeUserContext(models::ContextEnviroment::kYaTest)));
  EXPECT_NO_THROW(
      (models::FakeUserContext(models::ContextEnviroment::kYaTeamTest)));
}

using MaybeUid = boost::optional<models::YandexUid>;

TEST(FakeUserTicketParser, Yandex) {
  models::FakeUserContext context(models::ContextEnviroment::kYaTest);
  EXPECT_EQ(boost::none,
            tvm2::helpers::ParseUserTicket(context, "_!fake!_ya-0", {})
                .GetDefaultUid());
  EXPECT_EQ(MaybeUid(100500u),
            tvm2::helpers::ParseUserTicket(context, "_!fake!_ya-100500", {})
                .GetDefaultUid());

  EXPECT_THROW(tvm2::helpers::ParseUserTicket(context, "", {}),
               models::TVMUserTicketInvalidError);
  EXPECT_THROW(tvm2::helpers::ParseUserTicket(context, "1000", {}),
               models::TVMUserTicketInvalidError);
  EXPECT_THROW(tvm2::helpers::ParseUserTicket(context, "_!fake!_ya-team-", {}),
               models::TVMUserTicketInvalidError);
  EXPECT_THROW(tvm2::helpers::ParseUserTicket(context, "_!fake!_ya-", {}),
               models::TVMUserTicketInvalidError);
  EXPECT_THROW(tvm2::helpers::ParseUserTicket(context, "_!fake!_ya--1000", {}),
               models::TVMUserTicketInvalidError);
  EXPECT_THROW(tvm2::helpers::ParseUserTicket(context, "_!fake!_ya-100.0", {}),
               models::TVMUserTicketInvalidError);
  EXPECT_THROW(tvm2::helpers::ParseUserTicket(
                   context, "_!fake!_ya-18446744073709551616", {}),
               models::TVMUserTicketInvalidError);
  EXPECT_THROW(tvm2::helpers::ParseUserTicket(context, "_!fake!_ya-0xff", {}),
               models::TVMUserTicketInvalidError);
}

TEST(FakeUserTicketParser, YandexTeam) {
  models::FakeUserContext context(models::ContextEnviroment::kYaTeamTest);
  EXPECT_EQ(boost::none,
            tvm2::helpers::ParseUserTicket(context, "_!fake!_ya-team-0", {})
                .GetDefaultUid());
  EXPECT_EQ(MaybeUid(100500u), tvm2::helpers::ParseUserTicket(
                                   context, "_!fake!_ya-team-100500", {})
                                   .GetDefaultUid());

  EXPECT_THROW(tvm2::helpers::ParseUserTicket(context, "", {}),
               models::TVMUserTicketInvalidError);
  EXPECT_THROW(tvm2::helpers::ParseUserTicket(context, "1000", {}),
               models::TVMUserTicketInvalidError);
  EXPECT_THROW(tvm2::helpers::ParseUserTicket(context, "_!fake!_ya-", {}),
               models::TVMUserTicketInvalidError);
  EXPECT_THROW(tvm2::helpers::ParseUserTicket(context, "_!fake!_ya-team-", {}),
               models::TVMUserTicketInvalidError);
  EXPECT_THROW(
      tvm2::helpers::ParseUserTicket(context, "_!fake!_ya-team--1000", {}),
      models::TVMUserTicketInvalidError);
  EXPECT_THROW(
      tvm2::helpers::ParseUserTicket(context, "_!fake!_ya-team-100.0", {}),
      models::TVMUserTicketInvalidError);
  EXPECT_THROW(tvm2::helpers::ParseUserTicket(
                   context, "_!fake!_ya-team-18446744073709551616", {}),
               models::TVMUserTicketInvalidError);
  EXPECT_THROW(
      tvm2::helpers::ParseUserTicket(context, "_!fake!_ya-team-0xff", {}),
      models::TVMUserTicketInvalidError);
}
