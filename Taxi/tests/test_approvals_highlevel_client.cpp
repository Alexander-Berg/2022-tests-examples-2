#include <gtest/gtest.h>

#include <functional>

#include <clients/taxi-approvals/client_mock_base.hpp>

#include <clients/approvals/approvals_highlevel_client.hpp>

namespace hejmdal {

namespace {

namespace ca = ::clients::taxi_approvals;

ca::drafts_create::post::Response ResponseFromRequest(
    const ca::drafts_create::post::Request& request) {
  auto response = ca::drafts_create::post::Response{};
  response.created_by = request.x_yandex_login;
  response.run_manually = request.body.run_manually;
  response.data = ca::ExtendedDraftData{};
  response.data->extra = request.body.data.extra;
  response.service_name = request.body.service_name;
  response.api_path = request.body.api_path;
  response.mode = request.body.mode == ca::CreateDraftRequestMode::kPush
                      ? ca::ExtendedDraftMode::kPush
                      : ca::ExtendedDraftMode::kPoll;
  return response;
}

ca::v2_drafts::get::Response ResponseFromRequest(
    const ca::v2_drafts::get::Request& request) {
  ca::v2_drafts::get::Response response{};
  response.id = std::atoi(request.id.c_str());
  response.mode = ca::ExtendedDraftMode::kPush;

  switch (response.id) {
    case 1: {
      response.status = ca::DraftStatus::kNeedApproval;
      break;
    }
    case 2: {
      response.status = ca::DraftStatus::kApproved;
      break;
    }
    case 3: {
      response.status = ca::DraftStatus::kFailed;
      break;
    }
    case 4: {
      response.status = ca::DraftStatus::kSucceeded;
      break;
    }
    case 5: {
      response.status = ca::DraftStatus::kRejected;
      break;
    }
    case 6: {
      response.status = ca::DraftStatus::kApplying;
      break;
    }
    case 7: {
      response.status = ca::DraftStatus::kPartiallyCompleted;
      break;
    }
    case 8: {
      response.status = ca::DraftStatus::kExpired;
      break;
    }
    default:
      break;
  }

  return response;
}

class MockGenClient : public ::clients::taxi_approvals::ClientMockBase {
 public:
  using CreateRequestCheck =
      std::function<void(const ca::drafts_create::post::Request&)>;

  ca::drafts_create::post::Response draftsCreate(
      const ca::drafts_create::post::Request& request,
      const ca::CommandControl& /*command_control*/ = {}) const override {
    create_check_(request);
    if (create_response_.has_value()) {
      return create_response_.value();
    }

    // Default response
    auto response = ResponseFromRequest(request);
    response.id = 666;
    response.created = "2021-01-11T13:37:20+0300";
    response.change_doc_id =
        "clownductor_ChangeResourcesNannyService_2172_unstable";
    response.status = ca::DraftStatus::kNeedApproval;
    return response;
  }

  ca::v2_drafts::get::Response V2Drafts(
      const ca::v2_drafts::get::Request& request,
      const ca::CommandControl& /*command_control*/ = {}) const override {
    return ResponseFromRequest(request);
  }

  void SetCreateRequestCheck(CreateRequestCheck check) {
    create_check_ = check;
  }
  void SetCreateResponse(
      std::optional<ca::drafts_create::post::Response> resp) {
    create_response_ = resp;
  }

 private:
  CreateRequestCheck create_check_ =
      [](const ca::drafts_create::post::Request&) {};
  std::optional<ca::drafts_create::post::Response> create_response_;
};

std::pair<models::Resource, models::ResourceValue> ResVal(models::Resource res,
                                                          int val) {
  return {res, models::ResourceValue{res, val}};
}

}  // namespace

TEST(TestApprovalsHighLevelClient, CheckCpuRequest) {
  MockGenClient mock_gen_client{};
  clients::detail::ApprovalsClientConfig cfg{1, "test_user_login"};
  clients::ApprovalsHighLevelClient client{mock_gen_client, cfg};

  {
    mock_gen_client.SetCreateRequestCheck(
        [](const ca::drafts_create::post::Request& req) {
          EXPECT_EQ(req.x_yandex_login, "test_user_login");
          EXPECT_EQ(req.body.service_name, "clownductor");
          EXPECT_EQ(req.body.mode, ca::CreateDraftRequestMode::kPush);
          EXPECT_EQ(req.body.run_manually, false);
          EXPECT_EQ(req.body.api_path,
                    "clownductor_change_nanny_service_resources");

          formats::json::ValueBuilder builder;
          builder["branch_id"] = 1;
          builder["parameters"] = formats::json::MakeArray(
              formats::json::MakeObject("name", "cpu", "value", 1000));

          auto body = builder.ExtractValue();
          EXPECT_EQ(req.body.data.extra, body);
        });
    auto draft = client.CreateDraftForChangeResources(
        models::BranchId{1}, {ResVal(models::Resource::kCpu, 1)});
  }
  {
    mock_gen_client.SetCreateRequestCheck(
        [](const ca::drafts_create::post::Request& req) {
          EXPECT_EQ(req.x_yandex_login, "test_user_login");
          EXPECT_EQ(req.body.service_name, "clownductor");
          EXPECT_EQ(req.body.mode, ca::CreateDraftRequestMode::kPush);
          EXPECT_EQ(req.body.run_manually, false);
          EXPECT_EQ(req.body.api_path,
                    "clownductor_change_nanny_service_resources");

          formats::json::ValueBuilder builder;
          builder["branch_id"] = 1;
          builder["parameters"] = formats::json::MakeArray(
              formats::json::MakeObject("name", "cpu", "value", 1000));

          auto body = builder.ExtractValue();
          EXPECT_EQ(req.body.data.extra, body);
        });
    auto draft = client.CreateDraftForChangeResources(
        models::BranchId{1}, {ResVal(models::Resource::kCpu, 1000)});
  }
}

TEST(TestApprovalsHighLevelClient, CheckRamRequest) {
  MockGenClient mock_gen_client{};
  clients::detail::ApprovalsClientConfig cfg{1, "test_user_login"};
  clients::ApprovalsHighLevelClient client{mock_gen_client, cfg};

  {
    mock_gen_client.SetCreateRequestCheck(
        [](const ca::drafts_create::post::Request& req) {
          EXPECT_EQ(req.x_yandex_login, "test_user_login");
          EXPECT_EQ(req.body.service_name, "clownductor");
          EXPECT_EQ(req.body.mode, ca::CreateDraftRequestMode::kPush);
          EXPECT_EQ(req.body.run_manually, false);
          EXPECT_EQ(req.body.api_path,
                    "clownductor_change_nanny_service_resources");

          formats::json::ValueBuilder builder;
          builder["branch_id"] = 1;
          builder["parameters"] = formats::json::MakeArray(
              formats::json::MakeObject("name", "ram", "value", 2048));

          auto body = builder.ExtractValue();
          EXPECT_EQ(req.body.data.extra, body);
        });
    auto draft = client.CreateDraftForChangeResources(
        models::BranchId{1}, {ResVal(models::Resource::kRam, 2)});
  }
  {
    mock_gen_client.SetCreateRequestCheck(
        [](const ca::drafts_create::post::Request& req) {
          EXPECT_EQ(req.x_yandex_login, "test_user_login");
          EXPECT_EQ(req.body.service_name, "clownductor");
          EXPECT_EQ(req.body.mode, ca::CreateDraftRequestMode::kPush);
          EXPECT_EQ(req.body.run_manually, false);
          EXPECT_EQ(req.body.api_path,
                    "clownductor_change_nanny_service_resources");

          formats::json::ValueBuilder builder;
          builder["branch_id"] = 1;
          builder["parameters"] = formats::json::MakeArray(
              formats::json::MakeObject("name", "ram", "value", 2048));

          auto body = builder.ExtractValue();
          EXPECT_EQ(req.body.data.extra, body);
        });
    auto draft = client.CreateDraftForChangeResources(
        models::BranchId{1}, {ResVal(models::Resource::kRam, 2000)});
  }
  {
    EXPECT_ANY_THROW(client.CreateDraftForChangeResources(
        models::BranchId{1}, {ResVal(models::Resource::kRam, 0)}));
  }
  {
    mock_gen_client.SetCreateRequestCheck(
        [](const ca::drafts_create::post::Request& req) {
          EXPECT_EQ(req.x_yandex_login, "test_user_login");
          EXPECT_EQ(req.body.service_name, "clownductor");
          EXPECT_EQ(req.body.mode, ca::CreateDraftRequestMode::kPush);
          EXPECT_EQ(req.body.run_manually, false);
          EXPECT_EQ(req.body.api_path,
                    "clownductor_change_nanny_service_resources");

          formats::json::ValueBuilder builder;
          builder["branch_id"] = 1;
          builder["parameters"] = formats::json::MakeArray(
              formats::json::MakeObject("name", "ram", "value", 10240));

          auto body = builder.ExtractValue();
          EXPECT_EQ(req.body.data.extra, body);
        });
    auto draft = client.CreateDraftForChangeResources(
        models::BranchId{1}, {ResVal(models::Resource::kRam, 10000)});
  }
}

TEST(TestApprovalsHighLevelClient, CheckCreateResponse) {
  MockGenClient mock_gen_client{};
  clients::detail::ApprovalsClientConfig cfg{1, "test_user_login"};
  clients::ApprovalsHighLevelClient client{mock_gen_client, cfg};

  {
    auto draft = client.CreateDraftForChangeResources(
        models::BranchId{5}, {ResVal(models::Resource::kRam, 10000)});
    EXPECT_EQ(draft.approve_status, models::DraftApproveStatus::kNoDecision);
    EXPECT_EQ(draft.apply_status, models::DraftApplyStatus::kNotStarted);
    EXPECT_EQ(draft.apply_status_age, 0u);
    EXPECT_EQ(draft.approve_status_age, 0u);
    EXPECT_EQ(draft.id, models::DraftId{666});
    EXPECT_EQ(draft.branch_id, models::BranchId{5});
    auto changes =
        models::ResourceValueMap{ResVal(models::Resource::kRam, 10240u)};
    EXPECT_EQ(draft.changes, changes);
  }
}

UTEST(TestApprovalsHighLevelClient, CheckGetResponse) {
  MockGenClient mock_gen_client{};
  clients::detail::ApprovalsClientConfig cfg{1, "test_user_login"};
  clients::ApprovalsHighLevelClient client{mock_gen_client, cfg};

  {  // Not changed
    models::ChangeResourcesDraft draft =
        models::ChangeResourcesDraft{models::DraftId{1},
                                     models::BranchId{1},
                                     models::DraftApproveStatus::kNoDecision,
                                     models::DraftApplyStatus::kNotStarted,
                                     0u,
                                     0u,
                                     {}};
    client.UpdateStatuses(draft);

    EXPECT_EQ(draft.approve_status, models::DraftApproveStatus::kNoDecision);
    EXPECT_EQ(draft.apply_status, models::DraftApplyStatus::kNotStarted);
    EXPECT_EQ(draft.approve_status_age, 1u);
    EXPECT_EQ(draft.apply_status_age, 1u);
  }
  {  // Approved
    models::ChangeResourcesDraft draft =
        models::ChangeResourcesDraft{models::DraftId{2},
                                     models::BranchId{1},
                                     models::DraftApproveStatus::kNoDecision,
                                     models::DraftApplyStatus::kNotStarted,
                                     1u,
                                     1u,
                                     {}};
    client.UpdateStatuses(draft);

    EXPECT_EQ(draft.approve_status, models::DraftApproveStatus::kApproved);
    EXPECT_EQ(draft.apply_status, models::DraftApplyStatus::kNotStarted);
    EXPECT_EQ(draft.approve_status_age, 0u);
    EXPECT_EQ(draft.apply_status_age, 2u);
  }
  {  // Failed
    models::ChangeResourcesDraft draft =
        models::ChangeResourcesDraft{models::DraftId{3},
                                     models::BranchId{1},
                                     models::DraftApproveStatus::kNoDecision,
                                     models::DraftApplyStatus::kNotStarted,
                                     1u,
                                     1u,
                                     {}};
    client.UpdateStatuses(draft);

    EXPECT_EQ(draft.approve_status, models::DraftApproveStatus::kApproved);
    EXPECT_EQ(draft.apply_status, models::DraftApplyStatus::kFailed);
    EXPECT_EQ(draft.approve_status_age, 0u);
    EXPECT_EQ(draft.apply_status_age, 0u);
  }
  {  // Succeeded
    models::ChangeResourcesDraft draft =
        models::ChangeResourcesDraft{models::DraftId{4},
                                     models::BranchId{1},
                                     models::DraftApproveStatus::kNoDecision,
                                     models::DraftApplyStatus::kNotStarted,
                                     1u,
                                     1u,
                                     {}};
    client.UpdateStatuses(draft);

    EXPECT_EQ(draft.approve_status, models::DraftApproveStatus::kApproved);
    EXPECT_EQ(draft.apply_status, models::DraftApplyStatus::kSucceeded);
    EXPECT_EQ(draft.approve_status_age, 0u);
    EXPECT_EQ(draft.apply_status_age, 0u);
  }
  {  // Rejected
    models::ChangeResourcesDraft draft =
        models::ChangeResourcesDraft{models::DraftId{5},
                                     models::BranchId{1},
                                     models::DraftApproveStatus::kNoDecision,
                                     models::DraftApplyStatus::kNotStarted,
                                     1u,
                                     1u,
                                     {}};
    client.UpdateStatuses(draft);

    EXPECT_EQ(draft.approve_status, models::DraftApproveStatus::kRejected);
    EXPECT_EQ(draft.apply_status, models::DraftApplyStatus::kNotStarted);
    EXPECT_EQ(draft.approve_status_age, 0u);
    EXPECT_EQ(draft.apply_status_age, 2u);
  }
  {  // Applying
    models::ChangeResourcesDraft draft =
        models::ChangeResourcesDraft{models::DraftId{6},
                                     models::BranchId{1},
                                     models::DraftApproveStatus::kNoDecision,
                                     models::DraftApplyStatus::kNotStarted,
                                     1u,
                                     1u,
                                     {}};
    client.UpdateStatuses(draft);

    EXPECT_EQ(draft.approve_status, models::DraftApproveStatus::kApproved);
    EXPECT_EQ(draft.apply_status, models::DraftApplyStatus::kInProgress);
    EXPECT_EQ(draft.approve_status_age, 0u);
    EXPECT_EQ(draft.apply_status_age, 0u);
  }
  {  // Partially complete
    models::ChangeResourcesDraft draft =
        models::ChangeResourcesDraft{models::DraftId{7},
                                     models::BranchId{1},
                                     models::DraftApproveStatus::kNoDecision,
                                     models::DraftApplyStatus::kNotStarted,
                                     1u,
                                     1u,
                                     {}};
    client.UpdateStatuses(draft);

    EXPECT_EQ(draft.approve_status, models::DraftApproveStatus::kApproved);
    EXPECT_EQ(draft.apply_status, models::DraftApplyStatus::kInProgress);
    EXPECT_EQ(draft.approve_status_age, 0u);
    EXPECT_EQ(draft.apply_status_age, 0u);
  }
  {  // Expired
    models::ChangeResourcesDraft draft =
        models::ChangeResourcesDraft{models::DraftId{8},
                                     models::BranchId{1},
                                     models::DraftApproveStatus::kNoDecision,
                                     models::DraftApplyStatus::kNotStarted,
                                     1u,
                                     1u,
                                     {}};
    client.UpdateStatuses(draft);

    EXPECT_EQ(draft.approve_status, models::DraftApproveStatus::kExpired);
    EXPECT_EQ(draft.apply_status, models::DraftApplyStatus::kNotStarted);
    EXPECT_EQ(draft.approve_status_age, 0u);
    EXPECT_EQ(draft.apply_status_age, 2u);
  }
}

}  // namespace hejmdal
