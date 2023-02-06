#pragma once

#include <userver/utest/utest.hpp>

#include <optional>
#include <string>
#include <string_view>
#include <unordered_map>
#include <utility>
#include <vector>

#include <gmock/gmock.h>
#include <userver/formats/json/value.hpp>
#include <userver/formats/json/value_builder.hpp>

#include "smart_rules/draft/repository.hpp"
#include "smart_rules/types/base_types.hpp"

namespace draft = billing_subventions_x::smart_rules::draft;
using RuleId = billing_subventions_x::types::RuleId;
using TimePoint = billing_subventions_x::types::TimePoint;

class StubDraftRepository : public draft::actions::Repository,
                            public draft::repository::Repository {
 public:
  void WithStartsAt(std::string value) { starts_at_ = std::move(value); }
  void WithDraftId(std::string value) { draft_id_ = std::move(value); }
  void WithBudgetId(std::string value) { budget_id_ = std::move(value); }

 protected:
  std::string starts_at_{};
  std::optional<std::string> draft_id_ = std::nullopt;
  std::optional<std::string> budget_id_ = std::nullopt;
};

class NewDraftRepository : public StubDraftRepository {
 public:
  std::optional<draft::Data> GetDraftData(
      std::string_view /*internal_draft_id*/) override {
    return std::nullopt;
  }

  bool AllRulesGenerated(std::string_view) override { return false; }
  bool AllRulesApproved(std::string_view) override { return false; }
  bool HasClashingSpecs(std::string_view) override { return false; }
  std::unordered_map<std::string, int> GetRuleCountPerGeoNode(
      std::string_view) override {
    std::unordered_map<std::string, int> geonodes_stat;
    geonodes_stat["geonode"] = 10;
    return geonodes_stat;
  }
  int GetBulkTotalSpecsCount(std::string_view) override { return 1000; }
  int GetBulkFailedSpecsCount(std::string_view) override { return 50; }
  std::vector<std::string> GetSubDraftSpecErrors(std::string_view) override {
    return {"Error 1", "Error 2"};
  }

  std::optional<std::string> GetBulkDraftSpecIsNotAvailableReason(
      std::string_view) override {
    return std::nullopt;
  }

  std::vector<std::string> FindDraftsWithClashingRules(std::string_view,
                                                       TimePoint) override {
    return {};
  }

  std::vector<std::string> FindApplyingDraftWithClashingRules(
      std::string_view) override {
    return {};
  }

  std::vector<RuleId> SelectActiveClashingRules(std::string_view,
                                                TimePoint) override {
    return {};
  }

  MOCK_METHOD(void, CreateDraftSpec,
              (std::string_view, const formats::json::Value&, std::string_view),
              (override));
  MOCK_METHOD(void, SetApprovedAt, (std::string_view, TimePoint), (override));
  MOCK_METHOD(void, UpdateDraftSpec,
              (std::string_view internal_draft_id, std::string_view draft_id,
               std::string_view tickets, std::string_view approvers,
               std::string_view budget_id),
              (override));
  MOCK_METHOD(void, UpdateState,
              (std::string_view internal_draft_id, std::string_view state,
               std::string_view error),
              (override));
  MOCK_METHOD(std::vector<std::string>, GetScheduleRefsForSubdrafts,
              (std::string_view internal_draft_id,
               std::string_view subdrafts_from, std::string_view subdrafts_to),
              (override));
  MOCK_METHOD(void, ApproveRules,
              (std::string_view internal_draft_id, std::string_view draft_id,
               std::string_view budget_id,
               const std::optional<std::vector<std::string>>& schedule_refs),
              (override));
  MOCK_METHOD(void, GenerateScheduleForMatching,
              (std::string_view internal_draft_id,
               const std::optional<std::vector<std::string>>& schedule_refs),
              (override));
  MOCK_METHOD(void, SaveRulesToClose,
              (std::string_view internal_draft_id,
               const std::vector<std::string>& ids, TimePoint close_at),
              (override));
  MOCK_METHOD(void, CloseOldRules, (std::string_view internal_draft_id),
              (override));

 protected:
  formats::json::Value MakeSpec() {
    formats::json::ValueBuilder spec;
    spec["currency"] = "RUB";
    spec["start"] = starts_at_;
    spec["budget"] = MakeBudget();
    return spec.ExtractValue();
  }

  formats::json::Value MakeBudget() {
    formats::json::ValueBuilder budget;
    budget["weekly"] = "10.0000";
    return budget.ExtractValue();
  }
};

class GeneratingDraftRepository : public NewDraftRepository {
 public:
  std::optional<draft::Data> GetDraftData(
      std::string_view internal_draft_id) override {
    draft::Data data;
    data.internal_draft_id = internal_draft_id;
    data.spec = MakeSpec();
    data.draft_id = draft_id_;
    data.budget_id = budget_id_;
    return data;
  }
};

class GeneratedDraftRepository : public GeneratingDraftRepository {
 public:
  bool AllRulesGenerated(std::string_view) override { return true; }
};

class FailedGeneratingDraftRepository : public GeneratedDraftRepository {
 public:
  std::optional<std::string> GetBulkDraftSpecIsNotAvailableReason(
      std::string_view) override {
    return "Spec is unavailable for whatever reason";
  }
};

class DraftWithSelfClashingSpecsRepository : public GeneratedDraftRepository {
 public:
  bool HasClashingSpecs(std::string_view) override { return true; }
};

class ClashingDraftRepository : public GeneratedDraftRepository {
 public:
  std::vector<std::string> FindDraftsWithClashingRules(std::string_view,
                                                       TimePoint) override {
    return {"12345", "54321"};
  }
};

class GeneratedWithManyErrorsDraftRepository : public GeneratedDraftRepository {
 public:
  int GetBulkFailedSpecsCount(std::string_view) override { return 51; }
};

class ApplyingDraftRepository : public GeneratedDraftRepository {
 public:
  std::optional<draft::Data> GetDraftData(
      std::string_view internal_draft_id) override {
    auto data =
        GeneratedDraftRepository::GetDraftData(internal_draft_id).value();
    data.draft_id = "draft_id";
    return data;
  }
};

class ApprovedDraftRepository : public ApplyingDraftRepository {
 public:
  std::optional<draft::Data> GetDraftData(
      std::string_view internal_draft_id) override {
    auto data =
        ApplyingDraftRepository::GetDraftData(internal_draft_id).value();
    data.approved_at = TimePoint{};
    return data;
  }
};
