#include <gtest/gtest.h>

#include <clients/sticker/models/digest_elems.hpp>
#include <clients/sticker/sticker_highlevel_client.hpp>

namespace hejmdal {

namespace {

struct Buffer : public clients::StickerClient {
 public:
  void SendEmail(const clients::models::StickerEmail& email,
                 const std::string& address) const override {
    email_ = email;
    address_ = address;
  }

  mutable clients::models::StickerEmail email_;
  mutable std::string address_;
};

}  // namespace

TEST(TestStickerHighlevelClient, TestEmptyDigestEmptyDescription) {
  auto buffer = std::make_shared<Buffer>();
  auto hl_client = clients::StickerHighLevelClient(buffer, "Source <s@s.s>");
  {
    clients::models::StickerDigest digest("test digest",
                                          "hello@yandex-team.ru");

    hl_client.Send(digest);
    EXPECT_EQ(buffer->email_.from, "Source <s@s.s>");
    EXPECT_EQ(buffer->email_.subject, "Digest: test digest");
    EXPECT_EQ(buffer->email_.body,
              "\n___________________\nStay OK,\nHejmdal\n");
  }
  { EXPECT_ANY_THROW(auto _ = clients::models::Text::Create("   \n\n\n\t")); }
}

TEST(TestStickerHighlevelClient, TestDigestDescription) {
  auto buffer = std::make_shared<Buffer>();
  auto hl_client = clients::StickerHighLevelClient(buffer, "Source <s@s.s>");

  clients::models::StickerDigest digest("test digest", "hello@yandex-team.ru");
  digest.PushElement(
      clients::models::Text::Create("Some\ncool\ndescription\n\n\n"));
  digest.PushElement(clients::models::Splitter::Create());

  hl_client.Send(digest);
  EXPECT_EQ(buffer->email_.from, "Source <s@s.s>");
  EXPECT_EQ(buffer->email_.subject, "Digest: test digest");
  EXPECT_EQ(buffer->email_.body,
            "\nSome\ncool\ndescription\n\n"
            "===============================================\n"
            "\n___________________\nStay OK,\nHejmdal\n");
}

TEST(TestStickerHighlevelClient, TestFormat) {
  auto buffer = std::make_shared<Buffer>();
  auto hl_client = clients::StickerHighLevelClient(buffer, "Source <s@s.s>");

  clients::models::StickerDigest digest("test digest", "hello@yandex-team.ru");
  auto table = clients::models::DataTable::Create(
      std::vector<std::string>{"Circuit out point id", "Incidents"});
  digest.PushElement(table);

  EXPECT_ANY_THROW(table->AddRow({""}));

  table->AddRow({"hello", "world"});
  table->AddRow({"foo", "bar"});
  table->AddRow({"foo-and-null", std::nullopt});
  table->AddRow(
      {"baz",
       "very long "
       "striiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiing\nand "
       "looooooooooooooooooooooonger\nand looooooooooooooonger"});

  hl_client.Send(digest);

  EXPECT_EQ(buffer->email_.from, "Source <s@s.s>");
  EXPECT_EQ(buffer->email_.subject, "Digest: test digest");
  std::string body(
      "\n - Circuit out point id: hello\n - Incidents: "
      "world\n-----------------------------------------------\n - Circuit out "
      "point id: foo\n - Incidents: "
      "bar\n-----------------------------------------------\n"
      " - Circuit out point id: "
      "foo-and-null\n-----------------------------------------------\n"
      " - Circuit out "
      "point id: baz\n - Incidents:\n     very long "
      "striiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiing\n     and "
      "looooooooooooooooooooooonger\n     and "
      "looooooooooooooonger\n-----------------------------------------------"
      "\n\n___________________\nStay OK,\nHejmdal\n");
  EXPECT_EQ(buffer->email_.body, body);
}

TEST(TestStickerClient, TestCreateRequestBody) {
  clients::models::StickerEmail email;
  email.subject = "J<3C++";
  email.from = "H&J <mail@mail.com>";
  auto body = clients::StickerClient::CreateRequestBody(email);
  EXPECT_EQ(
      body,
      "<?xml version=\"1.0\" encoding=\"UTF-8\"?><mails><mail><from>H&amp;J "
      "&lt;mail@mail.com&gt;</from><subject encoding=\"base64\">J&lt;3C++"
      "</subject><body><![CDATA[]]></body></mail></mails>");
}

}  // namespace hejmdal
