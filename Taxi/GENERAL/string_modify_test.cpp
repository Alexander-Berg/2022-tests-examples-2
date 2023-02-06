#include "string_modify.hpp"

#include <userver/engine/run_in_coro.hpp>
#include <userver/utest/utest.hpp>

namespace {

void AssertDescription(const std::string& str, const std::string& expected,
                       const std::vector<std::string>& tags_to_delete) {
  EXPECT_EQ(eats_products::utils::DeleteFromString(str, tags_to_delete),
            expected);
}

}  // namespace

TEST(DeleteTags, DeleteBolds) {
  RunInCoro([]() {
    std::string description =
        "<b>Состав:</b> груша <br><b>Срок годности:</b> 30сут<br>";
    std::string expected = "Состав: груша <br>Срок годности: 30сут<br>";
    std::vector<std::string> tags_to_delete = {"<b>", "</b>"};

    AssertDescription(description, expected, tags_to_delete);
  });
}

TEST(DeleteTags, DeleteBoldsAndBreaks) {
  RunInCoro([]() {
    std::string description =
        "<b>Состав:</b> груша <br><b>Срок годности:</b> 30сут<br>";
    std::string expected = "Состав: груша Срок годности: 30сут";
    std::vector<std::string> tags_to_delete = {"<b>", "</b>", "<br>"};

    AssertDescription(description, expected, tags_to_delete);
  });
}

TEST(DeleteTags, EmptyDescription) {
  RunInCoro([]() {
    std::string description = "";
    std::string expected = "";
    std::vector<std::string> tags_to_delete = {"<b>", "</b>", "<br>"};

    AssertDescription(description, expected, tags_to_delete);
  });
}

TEST(DeleteTags, EmptyTagsToDelete) {
  RunInCoro([]() {
    std::string description =
        "<b>Состав:</b> груша <br><b>Срок годности:</b> 30сут<br>";
    std::string expected =
        "<b>Состав:</b> груша <br><b>Срок годности:</b> 30сут<br>";
    AssertDescription(description, expected, {});
  });
}

TEST(DeleteTags, TagIsMissingInDescription) {
  RunInCoro([]() {
    std::string description =
        "<b>Состав:</b> груша <br><b>Срок годности:</b> 30сут<br>";
    ;
    std::string expected =
        "<b>Состав:</b> груша <br><b>Срок годности:</b> 30сут<br>";
    ;
    std::vector<std::string> tags_to_delete = {"<p>"};

    AssertDescription(description, expected, tags_to_delete);
  });
}

TEST(DeleteTags, EmptyTag) {
  RunInCoro([]() {
    std::string description =
        "<b>Состав:</b> груша <br><b>Срок годности:</b> 30сут<br>";
    std::string expected =
        "<b>Состав:</b> груша <br><b>Срок годности:</b> 30сут<br>";
    std::vector<std::string> tags_to_delete = {""};
    AssertDescription(description, expected, tags_to_delete);
  });
}

TEST(DeleteTags, DoubleTag) {
  RunInCoro([]() {
    std::string description =
        "<b>Состав:</b> груша <br><b>Срок годности:</b> 30сут<br>";
    std::string expected = "<b>Состав:</b> груша <b>Срок годности:</b> 30сут";
    std::vector<std::string> tags_to_delete = {"<br>", "<br>"};
    AssertDescription(description, expected, tags_to_delete);
  });
}
