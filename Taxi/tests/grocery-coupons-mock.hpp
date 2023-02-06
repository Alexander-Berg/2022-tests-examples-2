#include <clients/grocery-coupons/client_mock_base.hpp>

namespace clients::grocery_coupons {

namespace GroceryCouponsValidate = internal_v1_coupons_validate::post;

enum class ClientBehaviour { kOk, kInvalid, kErr400, kNotCalled };

class MyGroceryCouponsClient : public ClientMockBase {
 public:
  ClientBehaviour behaviour = ClientBehaviour::kNotCalled;

  GroceryCouponsValidate::Response Validate(
      const GroceryCouponsValidate::Request& /*request*/,
      const CommandControl& /*command_control*/ = {}) const override {
    switch (behaviour) {
      case ClientBehaviour::kOk:
        return GroceryCouponsValidate::Response{{true, true, {}, {}}};
        break;
      case ClientBehaviour::kInvalid:
        return GroceryCouponsValidate::Response{{false, false, {}, {}}};
        break;
      case ClientBehaviour::kErr400:
        throw GroceryCouponsValidate::Response400{
            {BadRequestCode::kBadRequest, "Err"}};
        break;
      case ClientBehaviour::kNotCalled:
        throw std::runtime_error("Should not be called");
        break;
    }
  }
};

}  // namespace clients::grocery_coupons
