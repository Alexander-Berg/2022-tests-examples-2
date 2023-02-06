#include <gmock/gmock.h>

#include <userver/utils/datetime.hpp>

#include "smart_rules/types/base_types.hpp"
#include "smart_rules/usecases/clean_drafts.hpp"

namespace {

namespace usecase = billing_subventions_x::smart_rules::usecases::clean_drafts;
using TimePoint = billing_subventions_x::types::TimePoint;

static TimePoint kMockNow =
    utils::datetime::Stringtime("2021-06-20T19:00:00+0300");

class DraftsSpy final : public usecase::Repository {
 public:
  MOCK_METHOD(void, RemoveStaleUnapprovedDrafts,
              (TimePoint, unsigned, unsigned), (final));
  MOCK_METHOD(void, CleanApprovedDrafts, (TimePoint, unsigned), (final));
};

class Request {
 public:
  Request& WithRemoveStale(bool value) {
    remove_stale_ = value;
    return *this;
  }

  Request& WithCleanApproved(bool value) {
    clean_approved_ = value;
    return *this;
  }

  Request& WithNow(TimePoint value) {
    now_ = value;
    return *this;
  }

  Request& WithDaysToKeep(unsigned value) {
    days_to_keep_ = value;
    return *this;
  }

  Request& WithChunkSize(unsigned value) {
    chunk_size_ = value;
    return *this;
  }

  usecase::Request Build() const {
    usecase::Request req;
    req.remove_stale = remove_stale_;
    req.clean_approved = clean_approved_;
    req.now = now_;
    req.days_to_keep = days_to_keep_;
    req.chunk_size = chunk_size_;
    return req;
  }

 private:
  bool remove_stale_ = false;
  bool clean_approved_ = false;
  TimePoint now_;
  unsigned days_to_keep_ = 0;
  unsigned chunk_size_ = 0;
};

class CleanDraftsUseCase : public testing::Test {
 public:
  CleanDraftsUseCase() : repo_{DraftsSpy()}, uc_{usecase::UseCase(&repo_)} {}

 protected:
  DraftsSpy repo_;
  usecase::UseCase uc_;
};

TEST_F(CleanDraftsUseCase, DoesNotRemoveStaleUnapprovedDraftsWhenDisabled) {
  EXPECT_CALL(repo_,
              RemoveStaleUnapprovedDrafts(testing::_, testing::_, testing::_))
      .Times(0);
  auto request = Request().WithRemoveStale(false).Build();
  uc_.Execute(std::move(request));
}

TEST_F(CleanDraftsUseCase, RemovesStaleUnapprovedDraftsWhenEnabled) {
  EXPECT_CALL(repo_, RemoveStaleUnapprovedDrafts(kMockNow, 5, 10)).Times(1);
  auto request = Request()
                     .WithRemoveStale(true)
                     .WithNow(kMockNow)
                     .WithDaysToKeep(5)
                     .WithChunkSize(10)
                     .Build();
  uc_.Execute(std::move(request));
}

TEST_F(CleanDraftsUseCase, DoesNotCleanApprovedDraftsWhenDisabled) {
  EXPECT_CALL(repo_, CleanApprovedDrafts(testing::_, testing::_)).Times(0);
  auto request = Request().WithCleanApproved(false).Build();
  uc_.Execute(std::move(request));
}

TEST_F(CleanDraftsUseCase, CleansApprovedDraftsWhenEnabled) {
  EXPECT_CALL(repo_, CleanApprovedDrafts(kMockNow, 10)).Times(1);
  auto request = Request()
                     .WithCleanApproved(true)
                     .WithNow(kMockNow)
                     .WithChunkSize(10)
                     .Build();
  uc_.Execute(std::move(request));
}

}  // namespace
