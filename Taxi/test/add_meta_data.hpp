#pragma once

#include <candidates/filters/filter.hpp>

namespace candidates::filters::test {

class AddMetaData : public Filter {
 public:
  AddMetaData(const FilterInfo& info, const formats::json::Value& meta_data);

  Result Process(const GeoMember& member, Context& context) const override;

 private:
  const formats::json::Value meta_data_;
};

class AddMetaDataFactory : public Factory {
 public:
  AddMetaDataFactory();

  std::unique_ptr<Filter> Create(const formats::json::Value& params,
                                 const FactoryEnvironment& env) const override;
};

}  // namespace candidates::filters::test
