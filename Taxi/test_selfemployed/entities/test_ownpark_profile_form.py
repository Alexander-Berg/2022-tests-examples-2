from selfemployed.entities import ownpark_profile_form


def test_happy_path():
    form = ownpark_profile_form.FullRegForm.initialize_with_known_phone(
        park_id='old_park',
        contractor_id='old_contractor',
        phone_pd_id='phone_pd_id',
    )
    form = form.set_binding_requested()
    form = form.set_agreements_accepted(
        ownpark_profile_form.Agreements(general=True, gas_stations=True),
    )
    form = form.set_billing_address_filled(
        address='address',
        apartment_number='apartment_number',
        postal_code='postal_code',
    )
    form = form.set_residency_state(
        ownpark_profile_form.ResidencyState.RESIDENT,
    )
    form = form.set_park_creation_started(
        inn_pd_id='inn_pd_id', salesforce_account_id='salesforce_account_id',
    )
    form = form.set_requisites(
        salesforce_requisites_case_id='salesforce_requisites_case_id',
    )
    form = form.set_park_created(
        park_id='new_park', contractor_id='new_contractor',
    )
    assert form.contractor_part == ownpark_profile_form.ContractorFormPart(
        initial_park_id='old_park',
        initial_contractor_id='old_contractor',
        phone_pd_id='phone_pd_id',
        is_phone_verified=True,
        track_id=None,
    )
    assert form.common_part == ownpark_profile_form.CommonFormPart(
        phone_pd_id='phone_pd_id',
        state=ownpark_profile_form.FormState.FINISHED,
        external_id='any-id',  # external_id is auxiliary and not compared
        inn_pd_id='inn_pd_id',
        address='address',
        apartment_number='apartment_number',
        postal_code='postal_code',
        agreements=ownpark_profile_form.Agreements(
            general=True, gas_stations=True,
        ),
        residency_state=ownpark_profile_form.ResidencyState.RESIDENT,
        salesforce_account_id='salesforce_account_id',
        salesforce_requisites_case_id='salesforce_requisites_case_id',
        initial_park_id='old_park',
        initial_contractor_id='old_contractor',
        created_park_id='new_park',
        created_contractor_id='new_contractor',
    )


def test_change_phone_skip_reqs_path():
    form = ownpark_profile_form.FullRegForm.initialize_with_known_phone(
        park_id='old_park',
        contractor_id='old_contractor',
        phone_pd_id='phone_pd_id',
    )
    form = form.set_phone_changed(phone_pd_id='other_phone_pd_id')
    form = form.set_verification_requested(track_id='track_id')
    form = form.set_phone_verified()
    form = form.set_binding_requested()
    form = form.set_agreements_accepted(
        ownpark_profile_form.Agreements(general=True),
    )
    form = form.set_billing_address_filled(
        address='address',
        apartment_number='apartment_number',
        postal_code='postal_code',
    )
    form = form.set_residency_state(
        ownpark_profile_form.ResidencyState.NON_RESIDENT,
    )
    form = form.set_park_creation_started(
        inn_pd_id='inn_pd_id', salesforce_account_id='salesforce_account_id',
    )
    form = form.set_park_created(
        park_id='new_park', contractor_id='new_contractor',
    )
    assert form.contractor_part == ownpark_profile_form.ContractorFormPart(
        initial_park_id='old_park',
        initial_contractor_id='old_contractor',
        phone_pd_id='other_phone_pd_id',
        is_phone_verified=True,
        track_id=None,
    )
    assert form.common_part == ownpark_profile_form.CommonFormPart(
        phone_pd_id='other_phone_pd_id',
        state=ownpark_profile_form.FormState.FINISHED,
        external_id='any-id',  # external_id is auxiliary and not compared
        inn_pd_id='inn_pd_id',
        address='address',
        apartment_number='apartment_number',
        postal_code='postal_code',
        agreements=ownpark_profile_form.Agreements(
            general=True, gas_stations=False,
        ),
        residency_state=ownpark_profile_form.ResidencyState.NON_RESIDENT,
        salesforce_account_id='salesforce_account_id',
        salesforce_requisites_case_id=None,
        initial_park_id='old_park',
        initial_contractor_id='old_contractor',
        created_park_id='new_park',
        created_contractor_id='new_contractor',
    )
