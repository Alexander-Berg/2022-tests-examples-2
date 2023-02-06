#include <gtest/gtest.h>

#include <utils/mask_personal_data.hpp>

TEST(MaskPhonesField, Replaces) {
  ASSERT_EQ(signal_device_api_admin::utils::MaskPhonesAndLicenseField(
                "text without phones"),
            "text without phones");
  ASSERT_EQ(signal_device_api_admin::utils::MaskPhonesAndLicenseField(R"=(
               {
                  "some": "text",
                  [
                     {
                         "phones": [],
                         "license_number": "ASDSA"
                     },
                     {
                         "phones": ["123",
                                    "asdasd"],
                     }
                  ]
               }
          )="),
            R"=(
               {
                  "some": "text",
                  [
                     {
                         "phones": "all phones are masked",
                         "license_number": "license_number is masked"
                     },
                     {
                         "phones": "all phones are masked",
                     }
                  ]
               }
          )=");
}
