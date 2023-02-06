import config from 'client/config/config';

const isTesting: boolean = process.env.NODE_ENV === config.__TEST__;

export interface TestingAttribute {
    'data-selenium-id': string;
}

interface FromTestingAttributes {
    vacancy?: TestingAttribute;
    fio?: TestingAttribute;
    language_level?: TestingAttribute;
    bdate?: TestingAttribute;
    phone?: TestingAttribute;
    city?: TestingAttribute;
    dr_lic_country?: TestingAttribute;
    dr_lic_number?: TestingAttribute;
    dr_lic_date?: TestingAttribute;
    dr_lic_end_date?: TestingAttribute;
    citizenship?: TestingAttribute;
    date_interview?: TestingAttribute;
    skype_call?: TestingAttribute;
    personal_meeting?: TestingAttribute;
    own_auto?: TestingAttribute;
    car_mark_model?: TestingAttribute;
    vrc?: TestingAttribute;
    vin_car?: TestingAttribute;
    auto_number?: TestingAttribute;
    auto_year?: TestingAttribute;
    auto_color?: TestingAttribute;
    park?: TestingAttribute;
    date_visit?: TestingAttribute;
    date_ytc_visit?: TestingAttribute;
    inline_purpose?: TestingAttribute;
    driver_status?: TestingAttribute;
    reject_reason?: TestingAttribute;
    type_of_activity?: TestingAttribute;
    new_opportunity?: TestingAttribute;
    courier_transport_type?: TestingAttribute;
    advertisement_campaign?: TestingAttribute;
    type_of_employment_form?: TestingAttribute;
    comment?: TestingAttribute;
    recall?: TestingAttribute;
    need_to_resend_sms?: TestingAttribute;
    datetime_scheduled_call?: TestingAttribute;
    time_recall?: TestingAttribute;
    visit_time?: TestingAttribute;
    time_ytc_visit?: TestingAttribute;
    services_offered?: TestingAttribute;
    address_hub?: TestingAttribute;
    induction_training?: TestingAttribute;
}

export const FORM_ATTRIBUTES: FromTestingAttributes = isTesting
    ? {
        vacancy: {
            'data-selenium-id': 'vacancy_input',
        },
        fio: {
            'data-selenium-id': 'name_input',
        },
        language_level: {
            'data-selenium-id': 'languageLevel_input',
        },
        bdate: {
            'data-selenium-id': 'dateBirth_input',
        },
        phone: {
            'data-selenium-id': 'phone_input',
        },
        city: {
            'data-selenium-id': 'city_input',
        },
        dr_lic_country: {
            'data-selenium-id': 'countryLicense_input',
        },
        dr_lic_number: {
            'data-selenium-id': 'driverLicense_input',
        },
        dr_lic_date: {
            'data-selenium-id': 'dateLicenseIssued_input',
        },
        dr_lic_end_date: {
            'data-selenium-id': 'dateLicenseExpires_input',
        },
        citizenship: {
            'data-selenium-id': 'citizenship_input',
        },
        date_interview: {
            'data-selenium-id': 'dateInterview_input',
        },
        skype_call: {
            'data-selenium-id': 'skypeCall_checkbox',
        },
        personal_meeting: {
            'data-selenium-id': 'personalMeeting_checkbox',
        },
        own_auto: {
            'data-selenium-id': 'ownAuto_button',
        },
        car_mark_model: {
            'data-selenium-id': 'carMarkModel_input',
        },
        vrc: {
            'data-selenium-id': 'vrc_input',
        },
        vin_car: {
            'data-selenium-id': 'vinCar_input',
        },
        auto_number: {
            'data-selenium-id': 'carPlate_input',
        },
        auto_year: {
            'data-selenium-id': 'carIssuedYear_input',
        },
        auto_color: {
            'data-selenium-id': 'carColour_input',
        },
        park: {
            'data-selenium-id': 'park_input',
        },
        date_visit: {
            'data-selenium-id': 'dateVisit_input',
        },
        date_ytc_visit: {
            'data-selenium-id': 'dateYTCVisit_input',
        },
        inline_purpose: {
            'data-selenium-id': 'inlinePurpose_input',
        },
        driver_status: {
            'data-selenium-id': 'status_input',
        },
        reject_reason: {
            'data-selenium-id': 'rejectReason_input',
        },
        type_of_activity: {
            'data-selenium-id': 'typeOfActivity_input',
        },
        new_opportunity: {
            'data-selenium-id': 'newOpportunity_input',
        },
        courier_transport_type: {
            'data-selenium-id': 'courierTransportTypeFoot_button',
        },
        advertisement_campaign: {
            'data-selenium-id': 'advertisementCampaign_input',
        },
        type_of_employment_form: {
            'data-selenium-id': 'typeOfEmployment_input',
        },
        comment: {
            'data-selenium-id': 'comment_input',
        },
        recall: {
            'data-selenium-id': 'scheduledCall_checkbox',
        },
        datetime_scheduled_call: {
            'data-selenium-id': 'dateScheduledCall_input',
        },
        time_recall: {
            'data-selenium-id': 'timeScheduledCall_input',
        },
        visit_time: {
            'data-selenium-id': 'taxiparkVisitTime_input',
        },
        time_ytc_visit: {
            'data-selenium-id': 'timeYtcVisit_input',
        },
        services_offered: {
            'data-selenium-id': 'servicesOffered_input',
        },
        address_hub: {
            'data-selenium-id': 'addressHub_input',
        },
        induction_training: {
            'data-selenium-id': 'inductionTraining_input',
        },
        need_to_resend_sms: {
            'data-selenium-id': 'inductionTraining_input',
        },
    }
    : {};
