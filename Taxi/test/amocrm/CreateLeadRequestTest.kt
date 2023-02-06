package amocrm

import io.mockk.every
import io.mockk.mockkObject
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import ru.yandex.taxi.crm.masshire.search.AmoCrmSource
import ru.yandex.taxi.crm.masshire.search.Config
import ru.yandex.taxi.crm.masshire.search.amocrm.Contact
import ru.yandex.taxi.crm.masshire.search.amocrm.CreateLeadRequest
import ru.yandex.taxi.proto.crm.masshire.JobSite
import ru.yandex.taxi.proto.crm.masshire.Resume

internal class BuildLeadTest {
    private val resume = Resume.newBuilder()

    @BeforeEach
    fun setup() {
        mockkObject(Config)
        every { Config.amocrmFields.source } returns
            AmoCrmSource(
                id = 1,
                hhSourceId = 2,
                sjSourceId = 3,
            )
        every { Config.amocrmFields.resumeUrl } returns 4
    }

    @AfterEach
    fun teardown() {
        resume.clear()
    }

    private fun build(pipelineId: Int = 1, userId: Int = 2, contact: Contact = Contact()) =
        CreateLeadRequest.build(
            pipelineId = pipelineId,
            userId = userId,
            contact = contact,
            resume = resume.build()
        )

    @Test
    fun `always fills pipeline, user, name and contact`() {
        val contact = Contact(id = 1)
        resume.firstName = "Ivan"
        resume.lastName = "Ivanov"

        val result = build(pipelineId = 1, userId = 2, contact = contact)

        assertEquals("Сделка: Ivan Ivanov", result.name)
        assertEquals(1, result.pipeline_id)
        assertEquals(2, result.created_by)
        assertEquals(2, result.responsible_user_id)
        assertEquals(contact, result._embedded.contacts.singleOrNull())
    }

    @Test
    fun `given jobSite fills custom fields`() {
        resume.originBuilder.jobSite = JobSite.JOB_SITE_SUPER_JOB

        val result = build().custom_fields_values.singleOrNull()

        assertEquals(Config.amocrmFields.source.sjSourceId, result?.values?.singleOrNull()?.enum_id)
        assertEquals(Config.amocrmFields.source.id, result?.field_id)
    }

    @Test
    fun `given unknown jobSite doesn't fill custom fields`() {
        resume.originBuilder.jobSite = JobSite.JOB_SITE_UNSPECIFIED

        val result = build()

        assertTrue(result.custom_fields_values.isEmpty())
    }

    @Test
    fun `given no jobSite doesn't fill custom fields`() {
        resume.clearOrigin()

        val result = build()

        assertTrue(result.custom_fields_values.isEmpty())
    }

    @Test
    fun `given resume url fills custom field with it`() {
        resume.originBuilder.externalUrl = "https://hh.ru/resume-id"

        val result = build().custom_fields_values.singleOrNull()

        assertEquals(Config.amocrmFields.resumeUrl, result?.field_id)
        assertEquals("https://hh.ru/resume-id", result?.values?.singleOrNull()?.value)
    }

    @Test
    fun `given empty resume url won't add custom field`() {
        resume.originBuilder.externalUrl = ""

        val result = build()

        assertTrue(result.custom_fields_values.isEmpty())
    }
}
