#include <gtest/gtest.h>

#include <clients/juggler/models/juggler_raw_event.hpp>

namespace hejmdal::clients::models {
TEST(TestJugglerRawEvent, ValidateTruncateDescription) {
  JugglerRawEvent event;
  event.host = "some_host";
  event.service = "some_service";
  event.description = std::string(1025, 'x');

  TruncateTooLongDescription(event);

  std::string expected_description = "[cut]";
  EXPECT_EQ(expected_description, event.description);

  event.description = std::string(1024, 'x');
  expected_description = event.description;

  TruncateTooLongDescription(event);
  EXPECT_EQ(expected_description, event.description);
}

TEST(TestJugglerRawEvent, SmartTruncateDescription) {
  JugglerRawEvent event;
  event.host = "some_host";
  event.service = "some_service";
  event.description = "xxxx xx x\n" + std::string(1025, 'x') + "\t xxxxx";

  TruncateTooLongDescription(event);
  std::string expected_description = "xxxx xx x[cut]";
  EXPECT_EQ(expected_description, event.description);
}

}  // namespace hejmdal::clients::models
