#include "add_meta_data.hpp"

#include <candidates/filters/test/add_meta_data_info.hpp>
#include <candidates/filters/test/add_meta_data_params.hpp>

namespace candidates::filters::test {

AddMetaData::AddMetaData(const FilterInfo& info,
                         const formats::json::Value& meta_data)
    : Filter(info), meta_data_(meta_data) {}

Result AddMetaData::Process([[maybe_unused]] const GeoMember& member,
                            Context& context) const {
  context.meta[name()] = meta_data_;
  return Result::kAllow;
}

AddMetaDataFactory::AddMetaDataFactory() : Factory(info::kAddMetaData) {}

std::unique_ptr<Filter> AddMetaDataFactory::Create(
    const formats::json::Value& params,
    [[maybe_unused]] const FactoryEnvironment& env) const {
  const auto& fparams = params.As<add_meta_data::Params>();
  if (!fparams.meta_data) return {};

  return std::make_unique<AddMetaData>(info(), fparams.meta_data->extra);
}

}  // namespace candidates::filters::test
