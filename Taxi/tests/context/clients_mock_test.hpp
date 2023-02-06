#pragma once

#include <core/context/clients.hpp>

#include <functional>

namespace routestats::test {

template <class T>
using TestClientWrapperHandler = std::function<const T&()>;
template <class T>
class TestClientWrapper;

// Mock client in unittests
// Usage in tests:
//
// context.clients.plus_wallet = MockClient<plus_wallet::Client>([](){
//   return MockPlusWalletClient{};
// });
//
template <class Client>
core::ClientWrapperPtr<Client> MockClient(
    const TestClientWrapperHandler<Client>& handler) {
  return std::make_shared<TestClientWrapper<Client>>(handler);
}

// implementation
template <class Client>
class TestClientWrapper : public core::CodegenClientWrapper<Client> {
 public:
  using Handler = TestClientWrapperHandler<Client>;
  explicit TestClientWrapper(const Handler& handler) : handler_(handler) {}

  const Client& GetClient() const override { return handler_(); }

 private:
  Handler handler_;
};
}  // namespace routestats::test
