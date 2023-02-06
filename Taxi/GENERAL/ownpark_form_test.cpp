#include <gtest/gtest.h>

#include <models/contractors.hpp>
#include <models/ownpark_form.hpp>
#include <userver/utest/utest.hpp>

namespace {

namespace models = selfemployed_fns_profiles::models;

}  // namespace

TEST(DirectForms, happy_path) {
  models::OwnparkContractorPart contractor_part;
  contractor_part.initial_park_id = "selfreg";
  contractor_part.initial_contractor_id = "selfreg_id";
  contractor_part.phone_pd_id = "phone_pd_id";
  contractor_part.is_phone_verified = false;
  contractor_part.last_step = "intro";
  contractor_part.profession = "market-courier";

  auto form = models::OwnparkForm(contractor_part);

  EXPECT_EQ(form.GetState(), "INITIAL");
  EXPECT_EQ(form.GetInitialParkContractorId(),
            (models::ParkContractorId{"selfreg", "selfreg_id"}));
  EXPECT_EQ(form.GetPhonePdId(), "phone_pd_id");
  EXPECT_EQ(form.GetProfession(), "market-courier");
  EXPECT_EQ(form.IsFromSelfreg(), true);
  EXPECT_EQ(form.GetSelfregId(), "selfreg_id");
  EXPECT_EQ(form.IsViaPassport(), false);
  EXPECT_EQ(form.GetPassportUid(), std::nullopt);

  form.SetPhone("phone_pd_id2");
  EXPECT_EQ(form.GetPhonePdId(), "phone_pd_id2");

  form.SetVerificationRequested("track_id");
  EXPECT_EQ(form.GetTrackId(), "track_id");

  form.SetPhoneVerified();
  EXPECT_TRUE(form.IsPhoneVerified());

  models::OwnparkCommonPart common_part;
  common_part.phone_pd_id = "phone_pd_id2";
  common_part.state = "INITIAL";
  common_part.external_id = "external_id";

  form = models::OwnparkForm(form.GetContractorPart(), common_part);

  form.SetBindingRequested();
  EXPECT_EQ(form.GetState(), "FILLING");
  EXPECT_EQ(form.GetExternalId(), "external_id");

  form.AssignAgreements(formats::json::FromString(
      "{\"agreement1\": true, \"agreement2\": false}"));
  EXPECT_EQ(form.GetCommonPart()->agreements,
            formats::json::FromString(
                "{\"agreement1\": true, \"agreement2\": false}"));

  form.SetBillingAddressFilled("address", "221B", "123456");
  EXPECT_EQ(form.GetAddress(), "address");
  EXPECT_EQ(form.GetApartmentNumber(), "221B");
  EXPECT_EQ(form.GetPostalCode(), "123456");

  form.SetParkCreationStarted("inn_pd_id", "sf_acc_id",
                              std::string(models::residency_states::kResident));
  EXPECT_EQ(form.GetInnPdId(), "inn_pd_id");
  EXPECT_EQ(form.GetSalesforceAccountId(), "sf_acc_id");
  EXPECT_EQ(form.GetResidencyState(), models::residency_states::kResident);
  EXPECT_EQ(form.GetState(), "FILLED");

  form.SetParkCreated(
      models::ParkContractorId{"new_park_id", "new_contractor_id"});
  EXPECT_EQ(form.GetCreatedParkContractorId(),
            (models::ParkContractorId{"new_park_id", "new_contractor_id"}));
  EXPECT_EQ(form.GetState(), "FINISHED");
  EXPECT_TRUE(form.IsParkCreated());
}

TEST(DirectForms, incorrect_transition) {
  models::OwnparkContractorPart contractor_part;
  contractor_part.initial_park_id = "selfreg";
  contractor_part.initial_contractor_id = "selfreg_id";
  contractor_part.phone_pd_id = "phone_pd_id";
  contractor_part.is_phone_verified = false;
  contractor_part.last_step = "intro";
  contractor_part.profession = "profession";

  auto form = models::OwnparkForm(std::move(contractor_part));
  EXPECT_THROW(form.SetParkCreated(models::ParkContractorId{
                   "new_park_id", "new_contractor_id"}),
               models::IncorrectStepTransition);
}
