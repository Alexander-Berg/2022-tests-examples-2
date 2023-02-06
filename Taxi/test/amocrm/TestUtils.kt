package amocrm

import ru.yandex.taxi.crm.masshire.search.Config
import ru.yandex.taxi.crm.masshire.search.amocrm.Contact
import ru.yandex.taxi.crm.masshire.search.amocrm.CustomField
import ru.yandex.taxi.crm.masshire.search.amocrm.CustomFieldValue
import ru.yandex.taxi.crm.masshire.search.amocrm.EMAIL_FIELD_CODE
import ru.yandex.taxi.crm.masshire.search.amocrm.PHONE_FIELD_CODE

internal fun makeContact(
    id: Int? = null,
    fieldId: Int? = null,
    fieldCode: String? = null,
    values: List<String?>? = null
) =
    Contact(
        id = id,
        custom_fields_values =
            listOf(
                CustomField(
                    field_id = fieldId,
                    field_code = fieldCode,
                    values = values?.map { CustomFieldValue(value = it) }
                )
            )
    )

internal fun contactWithResumeId(resumeId: String?) =
    makeContact(id = 1, fieldId = Config.amocrmFields.resumeId, values = listOf(resumeId))

internal fun contactWithEmails(emails: List<String?>?) =
    makeContact(id = 1, fieldCode = EMAIL_FIELD_CODE, values = emails)

internal fun contactWithEmail(email: String?) = contactWithEmails(listOf(email))

internal fun contactWithPhone(phone: String) =
    makeContact(id = 1, fieldCode = PHONE_FIELD_CODE, values = listOf(phone))
