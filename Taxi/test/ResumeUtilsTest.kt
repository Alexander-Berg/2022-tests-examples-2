package search

import amocrm.assertError
import io.grpc.Status
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import ru.yandex.taxi.crm.masshire.search.checkExternalId
import ru.yandex.taxi.crm.masshire.search.db.PersonalInfo
import ru.yandex.taxi.crm.masshire.search.db.PhoneInfo
import ru.yandex.taxi.crm.masshire.search.patchResume
import ru.yandex.taxi.proto.crm.masshire.JobSite
import ru.yandex.taxi.proto.crm.masshire.Resume

internal class PatchResumeTest {
    private val resume = Resume.newBuilder()

    @AfterEach
    fun teardown() {
        resume.clear()
    }

    @Test
    fun `given new firstName patches resume`() {
        resume.firstName = "Ivan"
        val personalInfo = PersonalInfo(firstName = "Petr")

        assertEquals("Petr", patchResume(resume.build(), personalInfo).firstName)
    }

    @Test
    fun `given null firstName won' patch resume`() {
        resume.firstName = "Ivan"

        assertEquals("Ivan", patchResume(resume.build(), PersonalInfo()).firstName)
    }

    @Test
    fun `given new lastName patches resume`() {
        resume.lastName = "Ivanov"
        val personalInfo = PersonalInfo(lastName = "Petrov")

        assertEquals("Petrov", patchResume(resume.build(), personalInfo).lastName)
    }

    @Test
    fun `given null lastName won't patch resume`() {
        resume.lastName = "Ivanov"

        assertEquals("Ivanov", patchResume(resume.build(), PersonalInfo()).lastName)
    }

    @Test
    fun `given new middleName patches resume`() {
        resume.middleName = "Ivanovich"
        val personalInfo = PersonalInfo(middleName = "Petrovich")

        assertEquals("Petrovich", patchResume(resume.build(), personalInfo).middleName)
    }

    @Test
    fun `given null middleName won't patch resume`() {
        resume.middleName = "Ivanovich"

        assertEquals("Ivanovich", patchResume(resume.build(), PersonalInfo()).middleName)
    }

    @Test
    fun `given email adds it to resume`() {
        resume.contactsBuilder.addEmails("resume-email@test.ru")
        val personalInfo = PersonalInfo(email = "email@email.ru")

        assertEquals(
            listOf("resume-email@test.ru", "email@email.ru"),
            patchResume(resume.build(), personalInfo).contacts.emailsList
        )
    }

    @Test
    fun `given null email won't add it to resume`() {
        resume.contactsBuilder.addEmails("resume-email@test.ru")

        assertEquals(
            listOf("resume-email@test.ru"),
            patchResume(resume.build(), PersonalInfo()).contacts.emailsList
        )
    }

    @Test
    fun `given phone with info adds it`() {
        val personalInfo = PersonalInfo(phone = PhoneInfo(value = "123-45-67", info = "work"))

        val result = patchResume(resume.build(), personalInfo).contacts

        assertEquals("123-45-67", result.phonesList.singleOrNull()?.formatted)
        assertEquals("work", result.phonesList.singleOrNull()?.info)
    }

    @Test
    fun `given phone without info adds phone without info`() {
        val personalInfo = PersonalInfo(phone = PhoneInfo(value = "123-45-67", info = null))

        val result = patchResume(resume.build(), personalInfo).contacts

        assertEquals("123-45-67", result.phonesList.singleOrNull()?.formatted)
        assertEquals("", result.phonesList.singleOrNull()?.info)
    }

    @Test
    fun `given null phone value won't add it to resume`() {
        val personalInfo = PersonalInfo(phone = PhoneInfo(value = null, info = "work"))

        assertTrue(patchResume(resume.build(), personalInfo).contacts.phonesList.isEmpty())
    }

    @Test
    fun `given null phone won't add it to resume`() {
        assertTrue(patchResume(resume.build(), PersonalInfo()).contacts.emailsList.isEmpty())
    }

    @Test
    fun `given null personal info won't patch resume`() {
        resume.firstName = "Ivan"

        assertEquals(resume.build(), patchResume(resume.build(), personalInfo = null))
    }
}

internal class CheckExternalIdTest {
    @Test
    fun `given null external id returns error`() {
        val result = checkExternalId(null)

        assertError(Status.Code.INVALID_ARGUMENT, result)
    }

    @Test
    fun `given hh external id returns hh`() {
        val result = checkExternalId("urn:hh:resume-id")

        assertEquals(JobSite.JOB_SITE_HEAD_HUNTER, result.getOrNull())
    }

    @Test
    fun `given sj external id returns sj`() {
        val result = checkExternalId("urn:sj:resume-id")

        assertEquals(JobSite.JOB_SITE_SUPER_JOB, result.getOrNull())
    }

    @Test
    fun `given unknown external id returns error`() {
        val result = checkExternalId("unknown:resume-id")

        assertError(Status.Code.INVALID_ARGUMENT, result)
    }
}
