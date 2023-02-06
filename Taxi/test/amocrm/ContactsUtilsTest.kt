package amocrm

import io.mockk.every
import io.mockk.mockkObject
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.NullAndEmptySource
import ru.yandex.taxi.crm.masshire.search.Config
import ru.yandex.taxi.crm.masshire.search.amocrm.Contact
import ru.yandex.taxi.crm.masshire.search.amocrm.CustomField
import ru.yandex.taxi.crm.masshire.search.amocrm.EMAIL_FIELD_CODE
import ru.yandex.taxi.crm.masshire.search.amocrm.PHONE_FIELD_CODE
import ru.yandex.taxi.crm.masshire.search.amocrm.TEXT_FIELD_LEN_LIMIT
import ru.yandex.taxi.crm.masshire.search.amocrm.buildContact
import ru.yandex.taxi.crm.masshire.search.amocrm.customField
import ru.yandex.taxi.crm.masshire.search.amocrm.isContactMatched
import ru.yandex.taxi.crm.masshire.search.amocrm.isResumeIdMatched
import ru.yandex.taxi.crm.masshire.search.amocrm.normalizePhone
import ru.yandex.taxi.crm.masshire.search.amocrm.patchContact
import ru.yandex.taxi.proto.crm.masshire.Resume

private fun Contact.resumeId() =
    this.customField(Config.amocrmFields.resumeId)?.values?.singleOrNull()?.value

private fun Contact.emails() = this.customField(EMAIL_FIELD_CODE)?.values?.map { it.value }

private fun Contact.phones() = this.customField(PHONE_FIELD_CODE)?.values?.map { it.value }

internal class NormalizePhoneTest {
    @Test
    fun `given null returns null`() {
        assertNull(normalizePhone(null))
    }

    @Test
    fun `given phone with non digits chars removes them`() {
        assertEquals("1234567", normalizePhone("  123-45-67"))
    }

    @Test
    fun `given russia phone with +7 removes it`() {
        assertEquals("9161234567", normalizePhone("+7 916-123-45-67"))
    }

    @Test
    fun `given phone with 7 at start and length != 11 doesn't remove it`() {
        assertEquals("7111112", normalizePhone("711-11-12"))
    }

    @Test
    fun `given russia phone with 8 at start removes it`() {
        assertEquals("9161234567", normalizePhone("8-916-123-45-67"))
    }

    @Test
    fun `given phone with 8 at start and length != 11 doesn't remove it`() {
        assertEquals("89161245", normalizePhone("891-612-45"))
    }
}

internal class IsResumeIdMatchedTest {
    @BeforeEach
    fun setup() {
        mockkObject(Config)
        every { Config.amocrmFields.resumeId } returns 1
    }

    @Test
    fun `given exactly same resume id returns true`() {
        val contact = contactWithResumeId("resume-id")

        assertTrue(isResumeIdMatched(contact, "resume-id"))
    }

    @Test
    fun `given contact with several resumes ids returns true`() {
        val contact = contactWithResumeId("resume-1 | resume-2")

        assertTrue(isResumeIdMatched(contact, "resume-2"))
    }

    @Test
    fun `given resume-id which is substring of another returns false`() {
        val contact = contactWithResumeId("resume-123 | resume-2")

        assertFalse(isResumeIdMatched(contact, "resume-1"))
    }

    @Test
    fun `given contact without custom_fields returns false`() {
        assertFalse(isResumeIdMatched(Contact(), "resume-id"))
    }

    @Test
    fun `given contact with null resume id returns false`() {
        val contact = contactWithResumeId(null)

        assertFalse(isResumeIdMatched(contact, "resume-id"))
    }
}

internal class IsContactMatchedTest {
    private fun isMatch(
        contact: Contact,
        value: String?,
        normalizeFun: (String?) -> String? = { it }
    ) = isContactMatched(contact, EMAIL_FIELD_CODE, value, normalizeFun)

    @Test
    fun `given exact same value returns true`() {
        val contact = contactWithEmail("some-email")

        assertTrue(isMatch(contact, "some-email"))
    }

    @Test
    fun `when one of values is a match returns true`() {
        val contact = contactWithEmails(listOf("email1", "email2"))

        assertTrue(isMatch(contact, "email2"))
    }

    @Test
    fun `when normalized values are matched returns true`() {
        val contact = contactWithEmail("EMAIL")

        assertTrue(isMatch(contact, "email", normalizeFun = { it?.lowercase() }))
    }

    @Test
    fun `given contact without such custom field and null target value returns true`() {
        val contact = contactWithPhone("1234")

        assertTrue(isMatch(contact, value = null))
    }

    @Test
    fun `given contact with null values and null target value returns true`() {
        val contact = contactWithEmails(emails = null)

        assertTrue(isMatch(contact, value = null))
    }

    @Test
    fun `given contact with null value and null target value returns true`() {
        val contact = contactWithEmail(email = null)

        assertTrue(isMatch(contact, value = null))
    }

    @Test
    fun `given contact with some values and null target value returns false`() {
        val contact = contactWithEmail("email")

        assertFalse(isMatch(contact, value = null))
    }

    @Test
    fun `given different values returns false`() {
        val contact = contactWithEmails(listOf("email1", null))

        assertFalse(isMatch(contact, "email2"))
    }

    @Test
    fun `when contact doesn't have custom fields returns false`() {
        assertFalse(isMatch(Contact(), "email"))
    }

    @Test
    fun `when contact has custom field with null values returns false`() {
        val contact = contactWithEmails(emails = null)

        assertFalse(isMatch(contact, "email"))
    }
}

internal class BuildContactTest {
    private var resume = Resume.newBuilder()

    @BeforeEach
    fun setup() {
        mockkObject(Config)
        every { Config.amocrmFields.resumeId } returns 1
        every { Config.amocrmFields.resumeUrl } returns 2
        every { Config.amocrmFields.age } returns 3
        every { Config.amocrmFields.city } returns 4
    }

    @AfterEach
    fun teardown() {
        resume.clear()
    }

    @Test
    fun `always fills user fields`() {
        val result = buildContact(userId = 1, resume.build())

        assertEquals(1, result.created_by)
        assertEquals(1, result.responsible_user_id)
    }

    @Test
    fun `given non empty names fills contact names`() {
        resume.firstName = "Ivan"
        resume.middleName = "Ivanovich"
        resume.lastName = "Ivanov"

        val result = buildContact(1, resume.build())

        assertEquals("Ivan", result.first_name)
        assertEquals("Ivanov", result.last_name)
        assertEquals("Ivan Ivanov", result.name)
    }

    @Test
    fun `given empty names doesn't fill contact names`() {
        resume.firstName = ""
        resume.lastName = ""

        val result = buildContact(1, resume.build())

        assertNull(result.first_name)
        assertNull(result.last_name)
    }

    @Test
    fun `given non empty email fills custom field`() {
        resume.contactsBuilder.addEmails("email")

        val result = buildContact(1, resume.build())

        assertEquals("email", result.emails()?.singleOrNull())
    }

    @Test
    fun `given empty email won't fill custom field`() {
        resume.contactsBuilder.addEmails("")

        val result = buildContact(1, resume.build())

        assertNull(result.customField(EMAIL_FIELD_CODE))
    }

    @Test
    fun `given non empty phone fills custom field`() {
        resume.contactsBuilder.addPhonesBuilder().formatted = "123-45-67"

        val result = buildContact(1, resume.build())

        assertEquals("123-45-67", result.phones()?.singleOrNull())
    }

    @Test
    fun `given empty phone won't fill custom field`() {
        resume.contactsBuilder.addPhonesBuilder().formatted = ""

        val result = buildContact(1, resume.build())

        assertNull(result.customField(PHONE_FIELD_CODE))
    }

    @Test
    fun `given age fills custom field`() {
        resume.age = 45

        val result = buildContact(1, resume.build()).customField(Config.amocrmFields.age)

        assertEquals("45", result?.values?.singleOrNull()?.value)
    }

    @Test
    fun `given locations fills custom field with first`() {
        resume.addLocations("Moscow")
        resume.addLocations("Spb")

        val result = buildContact(1, resume.build()).customField(Config.amocrmFields.city)

        assertEquals("Moscow", result?.values?.singleOrNull()?.value)
    }

    @Test
    fun `given resume id fills custom field with it`() {
        resume.originBuilder.externalId = "urn:hh:resume-id-1"

        val result = buildContact(1, resume.build())

        assertEquals("resume-id-1", result.resumeId())
    }

    @Test
    fun `given empty resume id won't add custom field`() {
        resume.originBuilder.externalId = ""

        val result = buildContact(1, resume.build())

        assertNull(result.customField(Config.amocrmFields.resumeId))
    }

    @Test
    fun `given no additional info won't fill custom fields`() {
        resume.clearContacts()
        resume.clearLocations()
        resume.clearAge()
        resume.clearOrigin()

        val result = buildContact(1, resume.build()).custom_fields_values

        assertEquals(listOf<CustomField>(), result)
    }
}

internal class PatchContactTest {
    private val resume = Resume.newBuilder()

    @BeforeEach
    fun setup() {
        mockkObject(Config)
        every { Config.amocrmFields.resumeId } returns 1
    }

    @AfterEach
    fun teardown() {
        resume.clear()
    }

    @Test
    fun `given contact with matching resume id returns null`() {
        resume.originBuilder.externalId = "urn:hh:resume-id"
        val contact = contactWithResumeId("resume-id | other-id")

        assertNull(patchContact(contact, resume.build()))
    }

    @Test
    fun `given resume with empty id returns null`() {
        resume.clearOrigin()
        val contact = contactWithResumeId("")

        assertNull(patchContact(contact, resume.build()))
    }

    @Test
    fun `given contact with different resume id returns patched contact`() {
        resume.originBuilder.externalId = "urn:hh:resume-2"
        val contact = contactWithResumeId("resume-id")

        val result = patchContact(contact, resume.build())

        assertEquals("resume-id | resume-2", result?.resumeId())
    }

    @Test
    fun `given overflowed resume id field won't patch contact`() {
        resume.originBuilder.externalId = "urn:hh:resume-2"
        val contact = contactWithResumeId("a".repeat(TEXT_FIELD_LEN_LIMIT))

        assertNull(patchContact(contact, resume.build()))
    }

    @ParameterizedTest
    @NullAndEmptySource
    fun `given empty or null values for resume id field returns patched`(values: List<String?>?) {
        resume.originBuilder.externalId = "urn:hh:resume-1"
        val contact = makeContact(fieldId = Config.amocrmFields.resumeId, values = values)

        val result = patchContact(contact, resume.build())

        assertEquals("resume-1", result?.resumeId())
    }

    @Test
    fun `given contact with null resume id returns patched`() {
        resume.originBuilder.externalId = "urn:hh:resume-1"
        val contact = contactWithResumeId(resumeId = null)

        val result = patchContact(contact, resume.build())

        assertEquals("resume-1", result?.resumeId())
    }

    @Test
    fun `given contact without resume id field returns patched`() {
        resume.originBuilder.externalId = "urn:hh:resume-1"
        val contact = Contact(id = 1)

        val result = patchContact(contact, resume.build())

        assertEquals("resume-1", result?.resumeId())
    }

    @Test
    fun `given contact email equal to resume email returns null`() {
        resume.contactsBuilder.addEmails("email")
        val contact = contactWithEmail("email")

        assertNull(patchContact(contact, resume.build()))
    }

    @Test
    fun `given resume without emails returns null`() {
        resume.clearContacts()
        val contact = contactWithEmail("email")

        assertNull(patchContact(contact, resume.build()))
    }

    @Test
    fun `given different emails returns patched contact`() {
        resume.contactsBuilder.addEmails("email1")
        val contact = contactWithEmail("email2")

        val result = patchContact(contact, resume.build())

        assertEquals(listOf("email2", "email1"), result?.emails())
    }

    @ParameterizedTest
    @NullAndEmptySource
    fun `given empty or null values for email field returns patched contact`(
        values: List<String?>?
    ) {
        resume.contactsBuilder.addEmails("email")
        val contact = contactWithEmails(emails = values)

        val result = patchContact(contact, resume.build())

        assertEquals("email", result?.emails()?.singleOrNull())
    }

    @Test
    fun `given contact without emails returns patched`() {
        resume.contactsBuilder.addEmails("email")
        val contact = Contact(id = 1)

        val result = patchContact(contact, resume.build())

        assertEquals("email", result?.emails()?.singleOrNull())
    }

    @Test
    fun `given contact phone equal to resume phone returns null`() {
        resume.contactsBuilder.addPhonesBuilder().formatted = "123-45-67"
        val contact = contactWithPhone("123-45-67")

        assertNull(patchContact(contact, resume.build()))
    }

    @Test
    fun `given resume without phones returns null`() {
        resume.clearContacts()
        val contact = contactWithPhone("123-45-67")

        assertNull(patchContact(contact, resume.build()))
    }

    @Test
    fun `given different phones returns patched contact`() {
        resume.contactsBuilder.addPhonesBuilder().formatted = "123-45-67"
        val contact = contactWithPhone("999-11-11")

        val result = patchContact(contact, resume.build())

        assertEquals(listOf("999-11-11", "123-45-67"), result?.phones())
    }

    @ParameterizedTest
    @NullAndEmptySource
    fun `given empty or null values for phone field returns patched contact`(
        values: List<String?>?
    ) {
        resume.contactsBuilder.addPhonesBuilder().formatted = "123-45-67"
        val contact = makeContact(fieldCode = PHONE_FIELD_CODE, values = values)

        val result = patchContact(contact, resume.build())

        assertEquals("123-45-67", result?.phones()?.singleOrNull())
    }

    @Test
    fun `given contact without phones returns patched`() {
        resume.contactsBuilder.addPhonesBuilder().formatted = "123-45-67"
        val contact = Contact(id = 1)

        val result = patchContact(contact, resume.build())

        assertEquals("123-45-67", result?.phones()?.singleOrNull())
    }

    @Test
    fun `when patched always sets contact id`() {
        resume.originBuilder.externalId = "urn:hh:resume-1"
        val contact = Contact(id = 1)

        assertEquals(1, patchContact(contact, resume.build())?.id)
    }
}
