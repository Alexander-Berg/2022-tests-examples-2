#include <string>

#include <userver/dynamic_config/storage_mock.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/mock_now.hpp>

#include <clients/localizations-replica/client_gmock.hpp>
#include <taxi_config/variables/GROCERY_LOCALIZATION_USED_KEYSETS.hpp>
#include <utils/update_keysets.hpp>

namespace grocery_l10n {

namespace {

std::vector<dynamic_config::KeyValue> ToUsedKeysets(
    const taxi_config::grocery_localization_used_keysets::VariableType& value) {
  return {{taxi_config::GROCERY_LOCALIZATION_USED_KEYSETS, value}};
}

class UpdateKeysetsContext {
 protected:
  UpdateKeysetsContext()
      : current_snapshot_{},
        next_snapshot_{},
        storage_mock_{},
        mock_l10_replica_client_{},
        call_expectation_(EXPECT_CALL(mock_l10_replica_client_, V1Keyset)) {}

  void AddKeyset(const models::Keyset& keyset) {
    AddKeyset(keyset, current_snapshot_);
  }

  void UpdateKeyset(const models::Keyset& keyset) {
    AddKeyset(keyset, next_snapshot_);
    call_expectation_.WillOnce(::testing::Return(
        clients::localizations_replica::v1_keyset::get::Response200{
            clients::localizations_replica::Convert(
                keyset,
                grocery_shared::utils::To<clients::localizations_replica::
                                              UpdatedKeysetResponse>{})}));
  }

  void KeepKeyset(const std::string& keyset_name) {
    AddKeyset(current_snapshot_.at(keyset_name), next_snapshot_);
    call_expectation_.WillOnce(::testing::Return(
        clients::localizations_replica::v1_keyset::get::Response304{}));
  }

  void MakeKeysetNotFound(const std::string& keyset_name) {
    call_expectation_.WillOnce(::testing::Throw(
        clients::localizations_replica::v1_keyset::get::Response404{
            clients::localizations_replica::NotFound{
                clients::localizations_replica::NotFoundError{
                    clients::localizations_replica::NotFoundErrorCode::
                        kNotfound,
                    fmt::format("Keyset {} not found.", keyset_name)}}}));
  }

  const models::Keysets& ExpectedKeysetsSnapshot() const {
    return next_snapshot_;
  }

  const models::Keysets* CurrentKeysetsSnapshot() const {
    return &current_snapshot_;
  }

  const clients::localizations_replica::ClientGMock&
  LocalizationReplicaClientMock() const {
    return mock_l10_replica_client_;
  }

  void SetUsedKeysets(
      const taxi_config::grocery_localization_used_keysets::VariableType&
          used_keysets) {
    storage_mock_.Extend(ToUsedKeysets(used_keysets));
  }

  dynamic_config::Snapshot ConfigSnapshot() const {
    return storage_mock_.GetSnapshot();
  }

 private:
  using Func = clients::localizations_replica::v1_keyset::get::Response(
      const clients::localizations_replica::v1_keyset::get::Request&,
      const clients::codegen::CommandControl&);
  using CallExpectation = ::testing::internal::TypedExpectation<Func>;

  models::Keysets current_snapshot_;
  models::Keysets next_snapshot_;
  dynamic_config::StorageMock storage_mock_;
  clients::localizations_replica::ClientGMock mock_l10_replica_client_;
  CallExpectation& call_expectation_;

  void AddKeyset(const models::Keyset& keyset, models::Keysets& keysets) {
    keysets.insert({keyset.Name(), keyset});
  }
};

}  // namespace

class UpdateKeysetsTest : public ::testing::Test,
                          protected UpdateKeysetsContext {};

UTEST_F(UpdateKeysetsTest, InitUpdate) {
  UpdateKeyset(models::Keyset{
      "keyset-1", ::utils::datetime::MockNow(),
      models::KeysetTranslations{
          {"key-1",
           models::Translations{
               {"ru", {{models::PluralForm::kOne, "translation"}}}}}}});
  SetUsedKeysets({"keyset-1"});

  const auto next_snapshot = utils::TryUpdateKeysets(
      ConfigSnapshot(), nullptr, LocalizationReplicaClientMock());

  ASSERT_TRUE(next_snapshot.has_value());
  EXPECT_EQ(next_snapshot.value(), ExpectedKeysetsSnapshot());
}

UTEST_F(UpdateKeysetsTest, RegularUpdate) {
  using namespace std::literals;
  const auto now = ::utils::datetime::MockNow();
  AddKeyset(models::Keyset{
      "keyset-1", now - 24h,
      models::KeysetTranslations{
          {"key-1",
           models::Translations{
               {"ru", {{models::PluralForm::kOne, "translation"}}}}}}});
  UpdateKeyset(models::Keyset{
      "keyset-1", now,
      models::KeysetTranslations{
          {"key-1",
           models::Translations{
               {"ru", {{models::PluralForm::kOne, "updated-translation"}}}}}}});
  SetUsedKeysets({"keyset-1"});

  const auto next_snapshot =
      utils::TryUpdateKeysets(ConfigSnapshot(), CurrentKeysetsSnapshot(),
                              LocalizationReplicaClientMock());

  ASSERT_TRUE(next_snapshot.has_value());
  EXPECT_EQ(next_snapshot.value(), ExpectedKeysetsSnapshot());
}

UTEST_F(UpdateKeysetsTest, NotModified) {
  AddKeyset(models::Keyset{
      "keyset-1", ::utils::datetime::MockNow(),
      models::KeysetTranslations{
          {"key-1",
           models::Translations{
               {"ru", {{models::PluralForm::kOne, "translation"}}}}}}});
  KeepKeyset("keyset-1");
  SetUsedKeysets({"keyset-1"});

  const auto next_snapshot =
      utils::TryUpdateKeysets(ConfigSnapshot(), CurrentKeysetsSnapshot(),
                              LocalizationReplicaClientMock());

  EXPECT_FALSE(next_snapshot.has_value());
}

UTEST_F(UpdateKeysetsTest, NotFound) {
  MakeKeysetNotFound("keyset-1");
  SetUsedKeysets({"keyset-1"});

  EXPECT_THROW(
      {
        utils::TryUpdateKeysets(ConfigSnapshot(), nullptr,
                                LocalizationReplicaClientMock());
      },
      std::exception);
}

UTEST_F(UpdateKeysetsTest, PartialUpdate) {
  using namespace std::literals;

  const auto now = ::utils::datetime::MockNow();
  AddKeyset(models::Keyset{
      "keyset-1", now - 24h,
      models::KeysetTranslations{
          {"key-1",
           models::Translations{
               {"ru", {{models::PluralForm::kOne, "translation"}}}}}}});
  AddKeyset(models::Keyset{
      "keyset-2", now - 24h,
      models::KeysetTranslations{
          {"key-2",
           models::Translations{
               {"ru", {{models::PluralForm::kOne, "translation"}}}}}}});
  KeepKeyset("keyset-1");
  UpdateKeyset(models::Keyset{
      "keyset-2", now,
      models::KeysetTranslations{
          {"key-2",
           models::Translations{
               {"ru", {{models::PluralForm::kOne, "updated-translation"}}}}}}});
  SetUsedKeysets({"keyset-1", "keyset-2"});

  const auto next_snapshot =
      utils::TryUpdateKeysets(ConfigSnapshot(), CurrentKeysetsSnapshot(),
                              LocalizationReplicaClientMock());

  ASSERT_TRUE(next_snapshot.has_value());
  EXPECT_EQ(next_snapshot.value(), ExpectedKeysetsSnapshot());
}

UTEST_F(UpdateKeysetsTest, AddKeyset) {
  using namespace std::literals;
  const auto now = ::utils::datetime::MockNow();
  AddKeyset(models::Keyset{
      "keyset-1", now - 24h,
      models::KeysetTranslations{
          {"key-1",
           models::Translations{
               {"ru", {{models::PluralForm::kOne, "translation"}}}}}}});
  KeepKeyset("keyset-1");
  UpdateKeyset(models::Keyset{
      "keyset-2", now,
      models::KeysetTranslations{
          {"key-2",
           models::Translations{
               {"ru", {{models::PluralForm::kOne, "translation"}}}}}}});
  SetUsedKeysets({"keyset-1", "keyset-2"});

  const auto next_snapshot =
      utils::TryUpdateKeysets(ConfigSnapshot(), CurrentKeysetsSnapshot(),
                              LocalizationReplicaClientMock());

  ASSERT_TRUE(next_snapshot.has_value());
  EXPECT_EQ(next_snapshot.value(), ExpectedKeysetsSnapshot());
}

UTEST_F(UpdateKeysetsTest, RemoveKeyset) {
  const auto now = ::utils::datetime::MockNow();
  AddKeyset(models::Keyset{
      "keyset-1", now,
      models::KeysetTranslations{
          {"key-1",
           models::Translations{
               {"ru", {{models::PluralForm::kOne, "translation"}}}}}}});
  AddKeyset(models::Keyset{
      "keyset-2", now,
      models::KeysetTranslations{
          {"key-2",
           models::Translations{
               {"ru", {{models::PluralForm::kOne, "translation"}}}}}}});
  KeepKeyset("keyset-1");
  SetUsedKeysets({"keyset-1"});

  auto next_snapshot =
      utils::TryUpdateKeysets(ConfigSnapshot(), CurrentKeysetsSnapshot(),
                              LocalizationReplicaClientMock());

  ASSERT_TRUE(next_snapshot.has_value());
  EXPECT_EQ(next_snapshot.value(), ExpectedKeysetsSnapshot());
}

}  // namespace grocery_l10n
