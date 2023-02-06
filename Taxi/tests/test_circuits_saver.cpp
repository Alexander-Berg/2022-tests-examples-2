#include <gtest/gtest.h>

#include <models/circuit_state.hpp>
#include <radio/saver/circuits_saver_impl.hpp>

#include "tools/testutils.hpp"

namespace hejmdal {
const auto MockTime = testutils::MockTime;
using AlertStatus = models::CircuitStatus;
using JugglerStatus = clients::models::JugglerRawEventStatus;

static formats::json::Value kMetaData = [] {
  formats::json::ValueBuilder builder;
  builder["hello"] = "world";
  return builder.ExtractValue();
}();

TEST(TestCircuitsSaverProcessCircuit, NoData) {
  auto result = radio::circuits_saver::impl::ProcessCircuit(
      {"circuit1", "state", {}, kMetaData, MockTime(1)});
  models::CircuitState expected_state{
      "circuit1", "state",  AlertStatus::kNoData, MockTime(1), MockTime(1),
      "",         kMetaData};
  EXPECT_EQ(result.new_state, expected_state);
  EXPECT_FALSE(result.new_incident.has_value());
}

TEST(TestCircuitsSaverProcessCircuit, NoDataOk) {
  auto old_state = models::CircuitState{
      "circuit1",     "state",  AlertStatus::kNoData, MockTime(1), MockTime(1),
      "description1", kMetaData};
  auto result = radio::circuits_saver::impl::ProcessCircuit(
      {"circuit1",
       "state",
       {radio::blocks::State::kOk, "description2"},
       kMetaData,
       MockTime(2)},
      old_state);
  models::CircuitState expected_state{
      "circuit1",  "state",        AlertStatus::kOk, std::nullopt,
      MockTime(2), "description2", kMetaData};
  EXPECT_EQ(result.new_state, expected_state);
  EXPECT_TRUE(result.new_incident.has_value());

  models::Incident expected_incident{
      "circuit1",           "state",        {},       MockTime(1), MockTime(2),
      AlertStatus::kNoData, "description1", kMetaData};
  EXPECT_EQ(expected_incident, *result.new_incident);
}

TEST(TestCircuitsSaverProcessCircuit, OkNoData) {
  auto old_state = models::CircuitState{
      "circuit1",  "state",        AlertStatus::kOk, std::nullopt,
      MockTime(1), "description1", kMetaData};
  auto result = radio::circuits_saver::impl::ProcessCircuit(
      {"circuit1", "state", {}, kMetaData, MockTime(2)}, old_state);
  models::CircuitState expected_state{
      "circuit1", "state",  AlertStatus::kNoData, MockTime(2), MockTime(2),
      "",         kMetaData};
  EXPECT_EQ(result.new_state, expected_state);
  EXPECT_FALSE(result.new_incident.has_value());
}

TEST(TestCircuitsSaverProcessCircuit, FirstOk) {
  auto result = radio::circuits_saver::impl::ProcessCircuit(
      {"circuit1",
       "state",
       {radio::blocks::State::kOk, "description1"},
       kMetaData,
       MockTime(1)});
  models::CircuitState expected_state{"circuit1", "state",     AlertStatus::kOk,
                                      {},         MockTime(1), "description1",
                                      kMetaData};
  EXPECT_EQ(result.new_state, expected_state);
  EXPECT_FALSE(result.new_incident.has_value());
}

TEST(TestCircuitsSaverProcessCircuit, FirstWarn) {
  auto result = radio::circuits_saver::impl::ProcessCircuit(
      {"circuit1",
       "state",
       {radio::blocks::State::kWarn, "description1"},
       kMetaData,
       MockTime(1)});
  models::CircuitState expected_state{
      "circuit1",  "state",        AlertStatus::kWarn, MockTime(1),
      MockTime(1), "description1", kMetaData};
  EXPECT_EQ(result.new_state, expected_state);
  EXPECT_FALSE(result.new_incident.has_value());
}

TEST(TestCircuitsSaverProcessCircuit, OkOk) {
  auto old_state =
      models::CircuitState{"circuit1",  "state",        AlertStatus::kOk, {},
                           MockTime(1), "description1", kMetaData};
  auto result = radio::circuits_saver::impl::ProcessCircuit(
      {"circuit1",
       "state",
       {radio::blocks::State::kOk, "description1"},
       kMetaData,
       MockTime(2)},
      old_state);
  EXPECT_FALSE(result.new_state.has_value());
  EXPECT_FALSE(result.new_incident.has_value());
}

TEST(TestCircuitsSaverProcessCircuit, OkWarn) {
  auto old_state =
      models::CircuitState{"circuit1",  "state",        AlertStatus::kOk, {},
                           MockTime(1), "description1", kMetaData};
  auto result = radio::circuits_saver::impl::ProcessCircuit(
      {"circuit1",
       "state",
       {radio::blocks::State::kWarn, "description2"},
       kMetaData,
       MockTime(2)},
      old_state);
  models::CircuitState expected_state{
      "circuit1",  "state",        AlertStatus::kWarn, MockTime(2),
      MockTime(2), "description2", kMetaData};
  EXPECT_EQ(result.new_state, expected_state);
  EXPECT_FALSE(result.new_incident.has_value());
}

TEST(TestCircuitsSaverProcessCircuit, WarnCrit) {
  auto old_state = models::CircuitState{
      "circuit1",  "state",        AlertStatus::kWarn, MockTime(1),
      MockTime(2), "description1", kMetaData};
  auto result = radio::circuits_saver::impl::ProcessCircuit(
      {"circuit1",
       "state",
       {radio::blocks::State::kCritical, "description2"},
       kMetaData,
       MockTime(3)},
      old_state);
  models::CircuitState expected_state{
      "circuit1",  "state",     AlertStatus::kCritical,
      MockTime(1), MockTime(3), "description2",
      kMetaData};
  EXPECT_EQ(result.new_state, expected_state);
  EXPECT_FALSE(result.new_incident.has_value());
}

TEST(TestCircuitsSaverProcessCircuit, OkCrit) {
  auto old_state =
      models::CircuitState{"circuit1",  "state",        AlertStatus::kOk, {},
                           MockTime(1), "description1", kMetaData};
  auto result = radio::circuits_saver::impl::ProcessCircuit(
      {"circuit1",
       "state",
       {radio::blocks::State::kCritical, "description2"},
       kMetaData,
       MockTime(2)},
      old_state);
  models::CircuitState expected_state{
      "circuit1",  "state",     AlertStatus::kCritical,
      MockTime(2), MockTime(2), "description2",
      kMetaData};
  EXPECT_EQ(result.new_state, expected_state);
  EXPECT_FALSE(result.new_incident.has_value());
}

TEST(TestCircuitsSaverProcessCircuit, CritWarn) {
  auto old_state =
      models::CircuitState{"circuit1",  "state",     AlertStatus::kCritical,
                           MockTime(1), MockTime(2), "description1",
                           kMetaData};
  auto result = radio::circuits_saver::impl::ProcessCircuit(
      {"circuit1",
       "state",
       {radio::blocks::State::kWarn, "description2"},
       kMetaData,
       MockTime(3)},
      old_state);
  EXPECT_FALSE(result.new_state.has_value());
  EXPECT_FALSE(result.new_incident.has_value());
}

TEST(TestCircuitsSaverProcessCircuit, WarnOk) {
  auto old_state = models::CircuitState{
      "circuit1",  "state",        AlertStatus::kWarn, MockTime(1),
      MockTime(2), "description1", kMetaData};
  auto result = radio::circuits_saver::impl::ProcessCircuit(
      {"circuit1",
       "state",
       {radio::blocks::State::kOk, "description2"},
       kMetaData,
       MockTime(3)},
      old_state);
  models::CircuitState expected_state{"circuit1", "state",     AlertStatus::kOk,
                                      {},         MockTime(3), "description2",
                                      kMetaData};
  EXPECT_EQ(result.new_state, expected_state);
  EXPECT_TRUE(result.new_incident.has_value());
  models::Incident expected_incident{
      "circuit1",         "state",        {},       MockTime(1), MockTime(3),
      AlertStatus::kWarn, "description1", kMetaData};
  EXPECT_EQ(expected_incident, *result.new_incident);
};

TEST(TestCircuitsSaverProcessCircuit, CritOk) {
  auto old_state =
      models::CircuitState{"circuit1",  "state",     AlertStatus::kCritical,
                           MockTime(1), MockTime(2), "description1",
                           kMetaData};
  auto result = radio::circuits_saver::impl::ProcessCircuit(
      {"circuit1",
       "state",
       {radio::blocks::State::kOk, "description2"},
       kMetaData,
       MockTime(3)},
      old_state);
  models::CircuitState expected_state{"circuit1", "state",     AlertStatus::kOk,
                                      {},         MockTime(3), "description2",
                                      kMetaData};
  EXPECT_EQ(result.new_state, expected_state);
  EXPECT_TRUE(result.new_incident.has_value());
  models::Incident expected_incident{
      "circuit1",     "state",     {},
      MockTime(1),    MockTime(3), AlertStatus::kCritical,
      "description1", kMetaData};
  EXPECT_EQ(expected_incident, *result.new_incident);
};

TEST(TestCircuitsSaverProcessCircuit, OkOkDescriptionChanged) {
  auto old_state =
      models::CircuitState{"circuit1",  "state",        AlertStatus::kOk, {},
                           MockTime(1), "description1", kMetaData};
  auto result = radio::circuits_saver::impl::ProcessCircuit(
      {"circuit1",
       "state",
       {radio::blocks::State::kOk, "description2"},
       kMetaData,
       MockTime(2)},
      old_state);
  models::CircuitState expected_state{"circuit1", "state",     AlertStatus::kOk,
                                      {},         MockTime(2), "description2",
                                      kMetaData};
  EXPECT_EQ(result.new_state, expected_state);
  EXPECT_FALSE(result.new_incident.has_value());
}

TEST(TestCircuitsSaverProcessCircuit, WarnWarnDescriptionChanged) {
  auto old_state = models::CircuitState{
      "circuit1",  "state",        AlertStatus::kWarn, MockTime(1),
      MockTime(2), "description1", kMetaData};
  auto result = radio::circuits_saver::impl::ProcessCircuit(
      {"circuit1",
       "state",
       {radio::blocks::State::kWarn, "description2"},
       kMetaData,
       MockTime(3)},
      old_state);
  models::CircuitState expected_state{
      "circuit1",  "state",        AlertStatus::kWarn, MockTime(1),
      MockTime(3), "description2", kMetaData};
  EXPECT_EQ(result.new_state, expected_state);
  EXPECT_FALSE(result.new_incident.has_value());
}

TEST(TestCircuitsSaverProcessCircuit, NoIncidentStartTime) {
  auto old_state = models::CircuitState{
      "circuit1",  "state",        AlertStatus::kWarn, std::nullopt,
      MockTime(2), "description1", kMetaData};
  const auto prepare_result = radio::circuits_saver::impl::ProcessCircuit(
      {"circuit1",
       "state",
       {radio::blocks::State::kOk, "description2"},
       kMetaData,
       MockTime(3)},
      old_state);
  ASSERT_FALSE(prepare_result.new_incident.has_value());
};

TEST(TestCircuitsSaverProcessCircuit, IncidentEndTimeLessThanStartTime) {
  auto old_state = models::CircuitState{
      "circuit1",  "state",        AlertStatus::kWarn, std::nullopt,
      MockTime(5), "description1", kMetaData};
  const auto prepare_result = radio::circuits_saver::impl::ProcessCircuit(
      {"circuit1",
       "state",
       {radio::blocks::State::kOk, "description2"},
       kMetaData,
       MockTime(3)},
      old_state);
  ASSERT_FALSE(prepare_result.new_incident.has_value());
};

TEST(TestCircuitsSaver, UpdateCircuitsChunkTest1) {
  const std::vector<models::CircuitStateInfo> new_states_info{
      {"circuit1",
       "state",
       {radio::blocks::State::kOk, "description1"},
       kMetaData,
       MockTime(2)},
      {"circuit2",
       "state",
       {radio::blocks::State::kWarn, "description2"},
       kMetaData,
       MockTime(2)}};
  std::vector<models::CircuitState> db_states{
      {"circuit1", "state", AlertStatus::kWarn, MockTime(1), MockTime(1),
       "description1_2", kMetaData}};
  const auto prepare_result = radio::circuits_saver::impl::PrepareChunk(
      new_states_info.begin(), new_states_info.end(), std::move(db_states));

  ASSERT_EQ(2u, prepare_result.new_states.size());
  ASSERT_EQ(1u, prepare_result.new_incidents.size());

  models::CircuitState expected_state1{
      "circuit1",  "state",        AlertStatus::kOk, {},
      MockTime(2), "description1", kMetaData};
  models::CircuitState expected_state2{
      "circuit2",  "state",        AlertStatus::kWarn, MockTime(2),
      MockTime(2), "description2", kMetaData};
  EXPECT_EQ(expected_state2, prepare_result.new_states.at(1));

  models::Incident expected_incident{
      "circuit1",         "state",          {},       MockTime(1), MockTime(2),
      AlertStatus::kWarn, "description1_2", kMetaData};
  EXPECT_EQ(expected_incident, prepare_result.new_incidents.front());
};

TEST(TestCircuitsSaver, UpdateCircuitsChunkTest2) {
  /* Test cases:
   * 1. Ok -> Ok = skip
   * 2. Warn -> Warn = skip
   * 3. Warn -> Err = Err
   * 4. Err -> Warn = skip
   * 5. Err -> Ok = Ok + incident
   * 6. Ok -> Ok + new description = Ok + new description
   * 7. Err -> Err + new description = Err + new description
   * 8. Ok -> NoData = NoData
   * 9. NoData -> Ok = Ok + incident
   * 10. <no info> -> Ok = Ok
   */
  std::vector<models::CircuitState> db_states{
      {"circuit1", "state", AlertStatus::kOk, std::nullopt, MockTime(1), "ok",
       kMetaData},
      {"circuit2", "state", AlertStatus::kWarn, MockTime(1), MockTime(1),
       "warning", kMetaData},
      {"circuit3", "state", AlertStatus::kWarn, MockTime(1), MockTime(1),
       "warning", kMetaData},
      {"circuit4", "state", AlertStatus::kError, MockTime(1), MockTime(1),
       "error", kMetaData},
      {"circuit5", "state", AlertStatus::kError, MockTime(1), MockTime(1),
       "error", kMetaData},
      {"circuit6", "state", AlertStatus::kOk, std::nullopt, MockTime(1), "ok 1",
       kMetaData},
      {"circuit7", "state", AlertStatus::kError, MockTime(1), MockTime(1),
       "error 1", kMetaData},
      {"circuit8", "state", AlertStatus::kOk, std::nullopt, MockTime(1), "ok",
       kMetaData},
      {"circuit9", "state", AlertStatus::kNoData, MockTime(1), MockTime(1),
       "no data", kMetaData}};
  const std::vector<models::CircuitStateInfo> new_states_info{
      {"circuit1",
       "state",
       {radio::blocks::State::kOk, "ok"},
       kMetaData,
       MockTime(2)},
      {"circuit2",
       "state",
       {radio::blocks::State::kWarn, "warning"},
       kMetaData,
       MockTime(2)},
      {"circuit3",
       "state",
       {radio::blocks::State::kError, "error"},
       kMetaData,
       MockTime(2)},
      {"circuit4",
       "state",
       {radio::blocks::State::kWarn, "warning"},
       kMetaData,
       MockTime(2)},
      {"circuit5",
       "state",
       {radio::blocks::State::kOk, "ok"},
       kMetaData,
       MockTime(2)},
      {"circuit6",
       "state",
       {radio::blocks::State::kOk, "ok 2"},
       kMetaData,
       MockTime(2)},
      {"circuit7",
       "state",
       {radio::blocks::State::kError, "error 2"},
       kMetaData,
       MockTime(2)},
      {"circuit8",
       "state",
       {radio::blocks::State::kNoData, "no data"},
       kMetaData,
       MockTime(2)},
      {"circuit9",
       "state",
       {radio::blocks::State::kOk, "ok"},
       kMetaData,
       MockTime(2)},
      {"circuit10",
       "state",
       {radio::blocks::State::kOk, "ok"},
       kMetaData,
       MockTime(2)}};

  const auto prepare_result = radio::circuits_saver::impl::PrepareChunk(
      new_states_info.begin(), new_states_info.end(), std::move(db_states));

  const std::vector<models::CircuitState> expected_states{
      {"circuit3", "state", AlertStatus::kError, MockTime(1), MockTime(2),
       "error", kMetaData},
      {"circuit5", "state", AlertStatus::kOk, std::nullopt, MockTime(2), "ok",
       kMetaData},
      {"circuit6", "state", AlertStatus::kOk, std::nullopt, MockTime(2), "ok 2",
       kMetaData},
      {"circuit7", "state", AlertStatus::kError, MockTime(1), MockTime(2),
       "error 2", kMetaData},
      {"circuit8", "state", AlertStatus::kNoData, MockTime(2), MockTime(2),
       "no data", kMetaData},
      {"circuit9", "state", AlertStatus::kOk, std::nullopt, MockTime(2), "ok",
       kMetaData},
      {"circuit10", "state", AlertStatus::kOk, std::nullopt, MockTime(2), "ok",
       kMetaData}};
  const std::vector<models::Incident> expected_incidents{
      {"circuit5", "state", "", MockTime(1), MockTime(2), AlertStatus::kError,
       "error", kMetaData},
      {"circuit9", "state", "", MockTime(1), MockTime(2), AlertStatus::kNoData,
       "no data", kMetaData}};

  ASSERT_EQ(expected_states.size(), prepare_result.new_states.size());
  ASSERT_EQ(expected_incidents.size(), prepare_result.new_incidents.size());

  for (std::size_t i = 0; i < expected_states.size(); i++) {
    ASSERT_EQ(prepare_result.new_states[i], expected_states[i]);
  }

  for (std::size_t i = 0; i < expected_incidents.size(); i++) {
    ASSERT_EQ(prepare_result.new_incidents[i], expected_incidents[i]);
  }
};

}  // namespace hejmdal
