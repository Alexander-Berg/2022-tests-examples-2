#pragma once

#include <functional>
#include <string>
#include <vector>

#include <eventus/common/operation_argument.hpp>
#include <eventus/operations/mapper_base.hpp>

namespace eventus::operations::details::test_helpers {

using OperationArgsV = std::vector<eventus::common::OperationArgument>;
using StringV = std::vector<std::string>;

template <typename T, typename... Args>
typename T::BaseTypePtr MakeOperation(Args&&... args) {
  return std::make_shared<T>(std::forward<Args>(args)...);
}

template <typename T, typename... Args>
typename T::BaseTypePtr MakeOperationWithHook(
    std::function<void(std::shared_ptr<T> operation)> hook, Args&&... args) {
  auto operation = std::make_shared<T>(std::forward<Args>(args)...);
  hook(operation);
  return std::move(operation);
}

std::string PrintOperationArg(const eventus::common::OperationArgument& data,
                              const int idx);
std::string PrintOperationArgs(const OperationArgsV& data);

}  // namespace eventus::operations::details::test_helpers
