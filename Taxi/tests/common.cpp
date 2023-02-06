#include "common.hpp"

predicate_evaluator::KwargsMap BuildKwargsMap(const std::string& car_number,
                                              const std::string& car_id,
                                              const std::string& park_id,
                                              const std::string& uuid,
                                              const std::string& license_id) {
  predicate_evaluator::KwargsMap mp;
  mp[predicate_evaluator::KwargWrapper::Parse(kCarNumber)] = car_number;
  mp[predicate_evaluator::KwargWrapper::Parse(kCarId)] = car_id;
  mp[predicate_evaluator::KwargWrapper::Parse(kParkId)] = park_id;
  mp[predicate_evaluator::KwargWrapper::Parse(kUuid)] = uuid;
  mp[predicate_evaluator::KwargWrapper::Parse(kLicenseId)] = license_id;
  return mp;
}

clients::blocklist::IndexableBlocksItem CreateItem(
    std::string id, std::vector<std::string> keys,
    std::vector<std::string> values, std::vector<bool> indexes,
    std::string predicate_id, bool is_active, std::string mechanics,
    std::string updated, std::int64_t revision) {
  clients::blocklist::IndexableBlocksItem item;
  item.block_id = std::move(id);
  item.data = clients::blocklist::IndexableBlocksItemData{};
  item.data->keys = std::move(keys);
  item.data->values = std::move(values);
  item.data->indexable_keys = std::move(indexes);
  item.data->predicate_id = std::move(predicate_id);
  item.data->is_active = is_active;
  item.data->revision = revision;
  item.data->mechanics = std::move(mechanics);
  item.data->updated = std::move(updated);
  return item;
}
