#include <gtest/gtest.h>

#include <models/models_fwd.hpp>
#include <radio/spec/spec_view_container.hpp>

#include <set>

namespace hejmdal::radio::spec {

namespace {

struct TestSpec : public ISpec {
  TestSpec(std::string id_, std::set<std::string> deps_)
      : id(std::move(id_)), deps(std::move(deps_)) {}

  std::string id;
  std::set<std::string> deps;

  virtual const std::string& GetId() const override { return id; }
  virtual std::set<std::string> GetDependencies() const override {
    return deps;
  }
};

class TestContainer : public SpecViewContainer<TestSpec> {
 public:
  void Add(std::string id, std::string schema_id, std::vector<int> serv_ids,
           std::set<std::string> deps = {}) {
    std::vector<models::ServiceId> service_ids;
    for (auto&& serv_id : serv_ids) {
      service_ids.push_back(models::ServiceId(serv_id));
    }
    SpecViewContainer<TestSpec>::AddSpecOrUpdateViews(
        std::make_shared<TestSpec>(TestSpec{id, std::move(deps)}), id,
        models::CircuitSchemaId(schema_id), service_ids);
  }
};

void CheckById(const std::string& id, TestContainer& cont) {
  auto spec = cont.GetById(id);
  ASSERT_TRUE(spec != nullptr);
  EXPECT_EQ(spec->id, id);
}

void CheckFindResult(std::set<std::string> result_ids,
                     const std::set<std::shared_ptr<TestSpec>>& specs) {
  EXPECT_EQ(specs.size(), result_ids.size());
  for (const auto& spec : specs) {
    auto it = result_ids.find(spec->id);
    ASSERT_TRUE(it != result_ids.end());
    result_ids.erase(it);
  }
  EXPECT_TRUE(result_ids.empty());
}

void CheckBySchema(const std::string& id, std::set<std::string> result_ids,
                   TestContainer& cont) {
  auto specs = cont.FindBySchemaId(models::CircuitSchemaId(id),
                                   spec::CollectDeps::kFalse);
  CheckFindResult(result_ids, specs);
}

void CheckByService(int id, std::set<std::string> result_ids,
                    TestContainer& cont) {
  auto specs =
      cont.FindByServiceId(models::ServiceId(id), spec::CollectDeps::kFalse);
  CheckFindResult(result_ids, specs);
}

}  // namespace

TEST(TestSpecViewContainer, TestAdd) {
  TestContainer cont;

  cont.Add("id_1", "schema_1", {1, 2, 3});
  cont.Add("id_2", "schema_2", {2, 3, 4});
  cont.Add("id_3", "schema_1", {1, 2, 3});

  CheckById("id_1", cont);
  CheckById("id_2", cont);
  CheckById("id_3", cont);

  EXPECT_TRUE(cont.GetById("no_id") == nullptr);

  CheckBySchema("schema_1", {"id_1", "id_3"}, cont);
  CheckBySchema("schema_2", {"id_2"}, cont);
  CheckBySchema("no_schema", {}, cont);

  CheckByService(1, {"id_1", "id_3"}, cont);
  CheckByService(2, {"id_1", "id_2", "id_3"}, cont);
  CheckByService(3, {"id_1", "id_2", "id_3"}, cont);
  CheckByService(4, {"id_2"}, cont);
  CheckByService(5, {}, cont);
}

TEST(TestSpecViewContainer, TestViewDuplicates) {
  TestContainer cont;
  cont.Add("id_1", "schema_1", {1, 2, 3});
  cont.Add("id_1", "schema_1", {2, 3, 4});
  cont.Add("id_1", "schema_1", {1, 2, 3, 5, 7});

  CheckById("id_1", cont);
  CheckBySchema("schema_1", {"id_1"}, cont);
  CheckByService(1, {"id_1"}, cont);
  CheckByService(2, {"id_1"}, cont);
  CheckByService(3, {"id_1"}, cont);
  CheckByService(4, {"id_1"}, cont);
  CheckByService(5, {"id_1"}, cont);
  CheckByService(7, {"id_1"}, cont);
}

TEST(TestSpecViewContainer, TestDependencies) {
  TestContainer cont;

  cont.Add("a_1", "schema_1", {1});
  cont.Add("a_2", "schema_2", {1});
  cont.Add("b_1", "schema_1", {2}, {"a_2"});
  cont.Add("b_2", "schema_3", {2}, {"a_2"});
  cont.Add("c_1", "schema_5", {3}, {"b_1", "a_1"});

  // By id
  auto result = cont.FindById("c_1", spec::CollectDeps::kTrue);
  CheckFindResult({"c_1"}, result);

  result = cont.FindById("b_1", spec::CollectDeps::kTrue);
  CheckFindResult({"b_1", "c_1"}, result);

  result = cont.FindById("b_2", spec::CollectDeps::kTrue);
  CheckFindResult({"b_2"}, result);

  result = cont.FindById("a_1", spec::CollectDeps::kTrue);
  CheckFindResult({"a_1", "c_1"}, result);

  result = cont.FindById("a_2", spec::CollectDeps::kTrue);
  CheckFindResult({"a_2", "b_1", "b_2", "c_1"}, result);

  // By schema
  result = cont.FindBySchemaId(models::CircuitSchemaId{"schema_1"},
                               spec::CollectDeps::kTrue);
  CheckFindResult({"b_1", "a_1", "c_1"}, result);

  result = cont.FindBySchemaId(models::CircuitSchemaId{"schema_2"},
                               spec::CollectDeps::kTrue);
  CheckFindResult({"a_2", "b_1", "b_2", "c_1"}, result);

  result = cont.FindBySchemaId(models::CircuitSchemaId{"schema_3"},
                               spec::CollectDeps::kTrue);
  CheckFindResult({"b_2"}, result);

  // By service
  result = cont.FindByServiceId(models::ServiceId{1}, spec::CollectDeps::kTrue);
  CheckFindResult({"a_1", "a_2", "b_1", "b_2", "c_1"}, result);

  result = cont.FindByServiceId(models::ServiceId{2}, spec::CollectDeps::kTrue);
  CheckFindResult({"b_1", "b_2", "c_1"}, result);
}

}  // namespace hejmdal::radio::spec
