#include <gtest/gtest.h>

#include <userver/formats/json/inline.hpp>
#include <userver/utest/utest.hpp>

#include <radio/circuit_states_cache.hpp>

namespace hejmdal::radio {

template <class T>
void CheckPtrVectorEquality(const std::vector<std::shared_ptr<T>>& v1,
                            const std::vector<std::shared_ptr<T>>& v2,
                            const char* fail_msg) {
  ASSERT_EQ(v1.size(), v2.size()) << fail_msg;
  for (std::size_t i = 0; i < v1.size(); ++i) {
    EXPECT_EQ(*v1[i], *v2[i]) << fail_msg << " at index " << i;
  }
}

TEST(TestCircuitStatesCache, GetStatesLike) {
  RunInCoro([]() {
    CircuitStatesCacheModel model;

    model.UpsertState({"circuit_id_1",
                       "out_point_id_1",
                       models::CircuitStatus::kOk,
                       {},
                       {},
                       {},
                       {}});

    model.UpsertState({"circuit_id_2",
                       "out_point_id_1",
                       models::CircuitStatus::kOk,
                       {},
                       {},
                       {},
                       formats::json::MakeObject("service_id", 1)});

    model.UpsertState({"circuit_id_2",
                       "out_point_id_2",
                       models::CircuitStatus::kOk,
                       {},
                       {},
                       {},
                       formats::json::MakeObject("service_id", 1)});

    model.UpsertState({"circuit_id_4",
                       "out_point_id_1",
                       models::CircuitStatus::kOk,
                       {},
                       {},
                       {},
                       formats::json::MakeObject("service_id", 2)});

    model.RemoveExpiredFromViews();

    auto states = model.GetStatesLike(
        [](const auto& id) { return id.out_point_id == "out_point_id_1"; },
        models::ServiceId{1});

    models::CircuitState expected_state{
        "circuit_id_2",
        "out_point_id_1",
        models::CircuitStatus::kOk,
        {},
        {},
        {},
        formats::json::MakeObject("service_id", 1)};

    std::vector<models::CircuitStateCPtr> expected_states = {
        std::make_shared<const models::CircuitState>(
            std::move(expected_state))};

    CheckPtrVectorEquality(expected_states, states, "case 1");
  });
}

}  // namespace hejmdal::radio
