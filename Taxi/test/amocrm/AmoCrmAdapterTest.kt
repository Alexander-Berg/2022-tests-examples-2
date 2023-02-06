package amocrm

import RequestsHelper
import io.grpc.Status
import io.ktor.client.features.ClientRequestException
import io.ktor.http.HttpHeaders
import io.ktor.http.HttpStatusCode
import io.mockk.clearAllMocks
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.every
import io.mockk.justRun
import io.mockk.mockkConstructor
import io.mockk.mockkObject
import io.mockk.mockkStatic
import io.mockk.spyk
import io.mockk.verify
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Nested
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows
import org.junit.jupiter.api.fail
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ValueSource
import ru.yandex.taxi.crm.masshire.search.AmoCrmFields
import ru.yandex.taxi.crm.masshire.search.AmoCrmSource
import ru.yandex.taxi.crm.masshire.search.Config
import ru.yandex.taxi.crm.masshire.search.amocrm.AmoCrmAdapter
import ru.yandex.taxi.crm.masshire.search.amocrm.Contact
import ru.yandex.taxi.crm.masshire.search.amocrm.CreateLeadRequest
import ru.yandex.taxi.crm.masshire.search.amocrm.Lead
import ru.yandex.taxi.crm.masshire.search.amocrm.patchContact
import ru.yandex.taxi.crm.masshire.search.amocrm.statusExceptionOrNull
import ru.yandex.taxi.crm.masshire.search.db.Application
import ru.yandex.taxi.crm.masshire.search.db.ApplicationTokenInfoDAO
import ru.yandex.taxi.crm.masshire.search.db.TokenInfo
import ru.yandex.taxi.crm.masshire.search.httpClient
import ru.yandex.taxi.proto.crm.masshire.Resume

internal fun <T> assertError(expected: Status.Code, actual: Result<T>) {
    assertEquals(expected, actual.statusExceptionOrNull()?.status?.code)
}

internal class AmoCrmAdapterTest {
    private val requests = RequestsHelper()

    @BeforeEach
    fun setup() {
        mockkObject(Config)
        every { Config.amocrmFields } returns
            AmoCrmFields(
                age = 1,
                city = 2,
                resumeId = 3,
                resumeUrl = 4,
                source =
                    AmoCrmSource(
                        id = 5,
                        hhSourceId = 6,
                        sjSourceId = 7,
                    )
            )

        mockkConstructor(ApplicationTokenInfoDAO::class)
        every { anyConstructed<ApplicationTokenInfoDAO>().read(Application.AMOCRM) } returns
            TokenInfo(accessToken = "access_token", refreshToken = "refresh", expiresIn = 1111)
    }

    @AfterEach
    fun teardown() {
        clearAllMocks()
        requests.clear()
    }

    private fun amocrm() =
        AmoCrmAdapter(
            url = "yandex.amocrm.ru",
            clientId = "client-id",
            clientSecret = "client-secret",
            httpClient = httpClient(requests.engine()),
        )

    private fun expiredAmo(response: String): AmoCrmAdapter {
        requests.addResponse(status = HttpStatusCode.Unauthorized) {
            assertEquals("Bearer access_token", headers[HttpHeaders.Authorization])
        }
        requests.addResponse(content = response) {
            assertEquals("Bearer new_token", headers[HttpHeaders.Authorization])
        }

        val amo = spyk(amocrm())
        coEvery { amo.refreshAccessToken(any()) } returns
            TokenInfo(accessToken = "new_token", refreshToken = "new_refresh", expiresIn = 123)

        return amo
    }

    @Nested
    inner class GetContactsTest {
        private fun getContacts(
            query: String,
            adapter: AmoCrmAdapter = amocrm(),
        ) = runBlocking { adapter.getContacts(query) }

        @ParameterizedTest
        @ValueSource(
            strings =
                [
                    "{}",
                    """{"_embedded": {}}""",
                    """{"_embedded": {"contacts": []}}""",
                ]
        )
        fun `given response without contacts return empty`(response: String) {
            requests.addResponse(content = response) {
                assertEquals("some-query", url.parameters["query"])
            }

            assertEquals(listOf<Contact>(), getContacts("some-query").getOrNull())
        }

        @Test
        fun `given empty response returns empty`() {
            requests.addResponse(status = HttpStatusCode.NoContent, content = "")

            assertEquals(listOf<Contact>(), getContacts("query").getOrNull())
        }

        @Test
        fun `given invalid json returns error`() {
            requests.addResponse(content = "invalid json")

            assertError(Status.Code.INTERNAL, getContacts("some query"))
        }

        @Test
        fun `given valid response returns contacts`() {
            requests.addResponse(
                content = """{"_embedded": {"contacts": [{"id": 1}, {"id": 2}]}}"""
            )

            val result = getContacts("some query")

            assertEquals(listOf(Contact(id = 1), Contact(id = 2)), result.getOrNull())
        }

        @Test
        fun `when amocrm responds with 5xx returns unavailable error`() {
            requests.addResponse(status = HttpStatusCode.BadGateway)

            assertError(Status.Code.UNAVAILABLE, getContacts("some query"))
        }

        @Test
        fun `given expired token retries with new token`() {
            val amo = expiredAmo("""{"_embedded": {"contacts": [{"id": 1}]}}""")

            val result = getContacts("some query", adapter = amo)
            assertEquals(listOf(Contact(id = 1)), result.getOrNull())
        }
    }

    @Nested
    inner class FindContactTest {
        private val resume = Resume.newBuilder()
        private val amo = spyk(amocrm())

        @AfterEach
        fun teardown() {
            resume.clear()
        }

        private fun findContact(resume: Resume) = runBlocking { amo.findContact(resume) }

        @Test
        fun `when contact is found by resume id returns it`() {
            val contact = contactWithResumeId("resume-id")
            coEvery { amo.getContacts("resume-id") } returns Result.success(listOf(contact))

            resume.originBuilder.externalId = "urn:hh:resume-id"

            assertEquals(contact, findContact(resume.build()).getOrNull())
            coVerify(exactly = 1) { amo.getContacts(any()) }
        }

        @Test
        fun `when getContacts by resume id fails won't search by email or phone`() {
            val exception = Throwable("smth bad happened")
            coEvery { amo.getContacts("resume-id") } returns Result.failure(exception)

            resume.originBuilder.externalId = "urn:hh:resume-id"

            assertEquals(exception, findContact(resume.build()).exceptionOrNull())
            coVerify(exactly = 1) { amo.getContacts(any()) }
        }

        @Test
        fun `when no contact has matching resume id searches by email`() {
            val contactByResumeId = contactWithResumeId("resume-id-2")
            val contactByEmail = contactWithEmail("email")
            coEvery { amo.getContacts("resume-id-1") } returns
                Result.success(listOf(contactByResumeId))
            coEvery { amo.getContacts("email") } returns Result.success(listOf(contactByEmail))

            resume.originBuilder.externalId = "urn:hh:resume-id-1"
            resume.contactsBuilder.addEmails("email")

            assertEquals(contactByEmail, findContact(resume.build()).getOrNull())
            coVerify(exactly = 2) { amo.getContacts(any()) }
        }

        @Test
        fun `when no contact was found by resume id searches by email`() {
            val contact = contactWithEmail("email")
            coEvery { amo.getContacts(any()) } returns Result.success(listOf())
            coEvery { amo.getContacts("email") } returns Result.success(listOf(contact))

            resume.contactsBuilder.addEmails("email")

            assertEquals(contact, findContact(resume.build()).getOrNull())
            coVerify(exactly = 2) { amo.getContacts(any()) }
        }

        @Test
        fun `when emails differ returns null`() {
            val contact = contactWithEmail("another-email")
            coEvery { amo.getContacts(any()) } returns Result.success(listOf())
            coEvery { amo.getContacts("email") } returns Result.success(listOf(contact))

            resume.contactsBuilder.addEmails("email")

            val result = findContact(resume.build())
            assertTrue(result.isSuccess)
            assertNull(result.getOrNull())
        }

        @Test
        fun `when email is missing searches by normalized phone`() {
            val contact = contactWithPhone("1234567")
            coEvery { amo.getContacts(any()) } returns Result.success(listOf())
            coEvery { amo.getContacts("1234567") } returns Result.success(listOf(contact))

            resume.contactsBuilder.addPhonesBuilder().formatted = "123-45-67"

            assertEquals(contact, findContact(resume.build()).getOrNull())
            coVerify(exactly = 2) { amo.getContacts(any()) }
        }

        @Test
        fun `when phones differ returns null`() {
            val contact = contactWithPhone("1234567890")
            coEvery { amo.getContacts(any()) } returns Result.success(listOf())
            coEvery { amo.getContacts("1234567") } returns Result.success(listOf(contact))

            resume.contactsBuilder.addPhonesBuilder().formatted = "1234567"

            val result = findContact(resume.build())
            assertTrue(result.isSuccess)
            assertNull(result.getOrNull())
        }

        @Test
        fun `when second getContacts fails returns error`() {
            val exception = Throwable("smth bad happened")
            coEvery { amo.getContacts(any()) } returns Result.success(listOf())
            coEvery { amo.getContacts("email") } returns Result.failure(exception)

            resume.contactsBuilder.addEmails("email")

            assertEquals(exception, findContact(resume.build()).exceptionOrNull())
        }
    }

    @Nested
    inner class UpdateContactTest {
        private fun updateContact(contact: Contact, adapter: AmoCrmAdapter = amocrm()) =
            runBlocking {
                adapter.updateContact(contact)
            }

        @Test
        fun `given contact with id updates it`() {
            requests.addResponse(status = HttpStatusCode.OK)

            assertTrue(updateContact(Contact(id = 1)).isSuccess)
        }

        @Test
        fun `given contact without id does nothing`() {
            requests.addResponse { fail { "Shouldn't make any requests" } }

            assertTrue(updateContact(Contact(id = null)).isSuccess)
        }

        @Test
        fun `when amo returns 5xx returns unavailable error`() {
            requests.addResponse(status = HttpStatusCode.BadGateway)

            assertError(Status.Code.UNAVAILABLE, updateContact(Contact(id = 1)))
        }

        @Test
        fun `given expired token retries with new token`() {
            val amo = expiredAmo("{}")

            val result = updateContact(Contact(id = 1), adapter = amo)

            assertTrue(result.isSuccess)
        }
    }

    @Nested
    inner class CreateNoteTest {
        private fun createNote(
            userId: Int,
            leadId: Int,
            text: String,
            adapter: AmoCrmAdapter = amocrm()
        ) = runBlocking { adapter.createNote(userId, leadId, text) }

        @Test
        fun `when request is ok returns success`() {
            requests.addResponse(status = HttpStatusCode.OK)

            assertTrue(createNote(userId = 1, leadId = 2, "some test").isSuccess)
        }

        @Test
        fun `when amo returns 5xx returns unavailable error`() {
            requests.addResponse(status = HttpStatusCode.BadGateway)

            val result = createNote(userId = 1, leadId = 2, "some text")

            assertError(Status.Code.UNAVAILABLE, result)
        }

        @Test
        fun `given expired token retries with new token`() {
            val result = createNote(userId = 1, leadId = 2, "some text", expiredAmo(""))
            assertTrue(result.isSuccess)
        }
    }

    @Nested
    inner class CreateLeadTest {
        private val request =
            CreateLeadRequest(
                name = "name",
                pipeline_id = 123,
                created_by = 123,
                responsible_user_id = 123,
                _embedded = CreateLeadRequest.Embedded(contacts = listOf()),
                custom_fields_values = listOf(),
            )

        private fun createLead(adapter: AmoCrmAdapter = amocrm()) = runBlocking {
            adapter.createLead(request)
        }

        @ParameterizedTest
        @ValueSource(strings = ["[]", """[{}]"""])
        fun `when response is invalid returns error`(response: String) {
            requests.addResponse(content = response)

            assertError(Status.Code.INTERNAL, createLead())
        }

        @Test
        fun `when response is ok returns first lead`() {
            requests.addResponse(content = """[{"id": 1}, {"id": 2}]""")

            assertEquals(1, createLead().getOrNull()?.id)
        }

        @Test
        fun `given expired token retries with new token`() {
            val amo = expiredAmo("""[{"id": 1}]""")

            assertEquals(1, createLead(amo).getOrNull()?.id)
        }
    }

    @Nested
    inner class CreateApplicationTest {
        private val resume = Resume.newBuilder()
        private val amo = spyk(amocrm())

        private fun createApplication() = runBlocking {
            amo.createApplication(userId = 1, pipelineId = 123, resume = resume.build())
        }

        @BeforeEach
        fun setup() {
            resume.contactsBuilder.addEmails("email")
            mockkStatic(::patchContact)
            every { patchContact(any(), any()) } returns null
        }

        @AfterEach
        fun teardown() {
            resume.clear()
        }

        @Test
        fun `given resume without contacts returns error`() {
            resume.clearContacts()

            val result = createApplication()

            assertError(Status.Code.INTERNAL, result)
        }

        @Test
        fun `when findContact fails returns error`() {
            val exception = Throwable("Smth bad happened")
            coEvery { amo.findContact(any()) } returns Result.failure(exception)

            assertEquals(exception, createApplication().exceptionOrNull())
        }

        @Test
        fun `when findContact returns null createLead is called with new contact`() {
            coEvery { amo.findContact(any()) } returns Result.success(null)
            coEvery { amo.createLead(any()) } returns Result.success(Lead(id = 123))

            resume.firstName = "Ivan"

            createApplication()

            coVerify(exactly = 1) {
                amo.createLead(match { it._embedded.contacts.singleOrNull()?.first_name == "Ivan" })
            }
        }

        @Test
        fun `when findContact returns contact with null id createLead is called with new contact`() {
            coEvery { amo.findContact(any()) } returns Result.success(Contact(id = null))
            coEvery { amo.createLead(any()) } returns Result.success(Lead(id = 123))

            resume.firstName = "Ivan"

            createApplication()

            coVerify(exactly = 1) {
                amo.createLead(match { it._embedded.contacts.singleOrNull()?.first_name == "Ivan" })
            }
        }

        @Test
        fun `when findContact is ok createLead is called with old contact`() {
            coEvery { amo.findContact(any()) } returns Result.success(Contact(id = 1))
            coEvery { amo.createLead(any()) } returns Result.success(Lead(id = 123))

            createApplication()

            coVerify(exactly = 1) {
                amo.createLead(match { it._embedded.contacts.singleOrNull()?.id == 1 })
            }
        }

        @Test
        fun `when contact differs patches and updates it`() {
            coEvery { amo.findContact(any()) } returns Result.success(Contact(id = 1))
            every { patchContact(any(), any()) } returns contactWithResumeId("resume-id-1")
            coEvery { amo.updateContact(any()) } returns Result.success(Unit)
            coEvery { amo.createLead(any()) } returns Result.success(Lead(id = 123))

            createApplication()

            coVerify(exactly = 1) {
                amo.updateContact(match { it.custom_fields_values?.isNotEmpty() == true })
            }
        }

        @Test
        fun `when contact update fails returns error`() {
            coEvery { amo.findContact(any()) } returns Result.success(Contact(id = 1))
            every { patchContact(any(), any()) } returns Contact()

            val exception = Throwable("smth bad happened")
            coEvery { amo.updateContact(any()) } returns Result.failure(exception)

            assertEquals(exception, createApplication().exceptionOrNull())
        }

        @Test
        fun `when createLead fails returns error`() {
            coEvery { amo.findContact(any()) } returns Result.success(Contact(id = 1))

            val exception = Throwable("smth bad happened")
            coEvery { amo.createLead(any()) } returns Result.failure(exception)

            assertEquals(exception, createApplication().exceptionOrNull())
        }

        @Test
        fun `when work experience is set createNote is called`() {
            coEvery { amo.findContact(any()) } returns Result.success(Contact(id = 1))
            coEvery { amo.createLead(any()) } returns Result.success(Lead(id = 123))
            coEvery { amo.createNote(any(), any(), any()) } returns Result.success(Unit)

            resume.experienceBuilder.totalMonths = 12

            createApplication()

            coVerify(exactly = 1) { amo.createNote(any(), 123, "Опыт работы: 1 год") }
        }

        @Test
        fun `when work experience is not set createNote is not called`() {
            coEvery { amo.findContact(any()) } returns Result.success(Contact(id = 1))
            coEvery { amo.createLead(any()) } returns Result.success(Lead(id = 123))
            coEvery { amo.createNote(any(), any(), any()) } returns Result.success(Unit)

            resume.clearExperience()

            createApplication()

            coVerify(exactly = 0) { amo.createNote(any(), any(), any()) }
        }

        @Test
        fun `when createNote fails returns success`() {
            coEvery { amo.findContact(any()) } returns Result.success(Contact(id = 1))
            coEvery { amo.createLead(any()) } returns Result.success(Lead(id = 123))
            coEvery { amo.createNote(any(), any(), any()) } returns Result.failure(Throwable())

            resume.experienceBuilder.totalMonths = 12

            val result = createApplication()

            coVerify(exactly = 1) { amo.createNote(any(), any(), any()) }
            assertEquals("yandex.amocrm.ru/leads/detail/123", result.getOrNull())
        }
    }

    @Nested
    inner class RefreshAccessTokenTest {

        private fun refresh() = runBlocking { amocrm().refreshAccessToken("token") }

        @Test
        fun `when refresh is successful returns it`() {
            requests.addResponse(
                """{"access_token": "access", "refresh_token": "refresh", "expires_in": 123}""",
            )

            justRun { anyConstructed<ApplicationTokenInfoDAO>().update(any(), any()) }

            val expected =
                TokenInfo(
                    accessToken = "access",
                    refreshToken = "refresh",
                    expiresIn = 123,
                )

            assertEquals(expected, refresh())
            verify(exactly = 1) {
                anyConstructed<ApplicationTokenInfoDAO>().update(Application.AMOCRM, expected)
            }
        }

        @Test
        fun `when can't refresh token for some reason throws`() {
            requests.addResponse(status = HttpStatusCode.Forbidden)

            assertThrows<ClientRequestException> { refresh() }
        }
    }
}
