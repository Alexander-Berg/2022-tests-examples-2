package jobsite.headhunter

import RequestsHelper
import io.grpc.Status
import io.ktor.client.request.HttpRequestData
import io.ktor.http.HttpStatusCode
import io.mockk.clearAllMocks
import io.mockk.every
import io.mockk.mockk
import io.mockk.mockkConstructor
import io.mockk.mockkObject
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Nested
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ValueSource
import ru.yandex.taxi.crm.masshire.search.UserCredentials
import ru.yandex.taxi.crm.masshire.search.db.TokenInfo
import ru.yandex.taxi.crm.masshire.search.db.TokenInfoDAO
import ru.yandex.taxi.crm.masshire.search.dictionary.DictionaryStorage
import ru.yandex.taxi.crm.masshire.search.httpClient
import ru.yandex.taxi.crm.masshire.search.jobsite.JobSiteResult
import ru.yandex.taxi.crm.masshire.search.jobsite.headhunter.createHeadHunterAdapter
import ru.yandex.taxi.proto.crm.masshire.JobSite
import ru.yandex.taxi.proto.crm.masshire.ResumeQuery

internal class AdapterTest {
    private val requests = RequestsHelper()
    private val storage = mockk<DictionaryStorage>()

    @BeforeEach
    fun setup() {
        mockkObject(UserCredentials)
        every { UserCredentials.get() } returns
            UserCredentials(userUid = "123", userTicket = "user-ticket")

        mockkConstructor(TokenInfoDAO::class)
        every { anyConstructed<TokenInfoDAO>().read(any(), any()) } returns
            TokenInfo(accessToken = "access_token", refreshToken = "refreshToken", expiresIn = 222)
    }

    @AfterEach
    fun teardown() {
        clearAllMocks()
        requests.clear()
    }

    private fun adapter() =
        createHeadHunterAdapter(
            clientId = "clientId",
            clientSecret = "clientSecret",
            httpClient = httpClient(requests.engine()),
            storage = storage,
        )

    @Test
    fun `always returns HEAD_HUNTER job site`() {
        assertEquals(JobSite.JOB_SITE_HEAD_HUNTER, adapter().jobSite)
    }

    @Nested
    inner class RequestAccessTokenTest {

        private fun requestAccessToken(authCode: String = "authCode") = runBlocking {
            adapter().requestAccessToken(authCode)
        }

        @Test
        fun `when response is valid returns token info`() {
            val authCode = "authCode"

            requests.addResponse(
                content =
                    """{"access_token": "access", "refresh_token": "refresh", "expires_in": 123}"""
            ) {
                assertEquals("clientId", url.parameters["client_id"])
                assertEquals("clientSecret", url.parameters["client_secret"])
                assertEquals(authCode, url.parameters["code"])
            }

            val result = requestAccessToken(authCode)

            assertEquals(
                TokenInfo(accessToken = "access", refreshToken = "refresh", expiresIn = 123),
                result
            )
        }

        @ParameterizedTest
        @ValueSource(strings = ["", "{}"])
        fun `when response is invalid returns null`(content: String) {
            requests.addResponse(content = content)

            assertNull(requestAccessToken())
        }

        @Test
        fun `when job site returns 5xx returns null`() {
            requests.addResponse(status = HttpStatusCode.BadGateway)

            assertNull(requestAccessToken())
        }
    }

    @Nested
    inner class OpenResumeContactsTest {
        private fun openContacts(externalId: String = "urn:hh:resume-id") = runBlocking {
            adapter().openResumeContacts(externalId)
        }

        private fun resumeWithActionUrl(url: String = "some-url"): String {
            return """{"id": "1", "actions": {"get_with_contact": {"url": "$url"}}}"""
        }

        @ParameterizedTest
        @ValueSource(
            strings =
                [
                    """{"id": "1"}""",
                    """{"id": "1", "actions": {}}""",
                    """{"id": "1", "actions": {"get_with_contact": {}}}""",
                ]
        )
        fun `when resume doesn't have url for buying contacts returns internal error`(
            content: String
        ) {
            requests.addResponse(content = content)

            val result = openContacts() as? JobSiteResult.Error

            assertEquals(Status.Code.INTERNAL, result?.toStatus()?.code)
        }

        @Test
        fun `when get resume request returns 5xx returns unavailable error`() {
            requests.addResponse(status = HttpStatusCode.BadGateway)

            val result = openContacts() as? JobSiteResult.Error

            assertEquals(Status.Code.UNAVAILABLE, result?.toStatus()?.code)
        }

        @Test
        fun `when buy contact request returns 5xx returns unavailable error`() {
            val url = "https://api.hh.ru/resumes/1?with_contacts=fdfd"
            requests.addResponse(content = resumeWithActionUrl(url))
            requests.addResponse(status = HttpStatusCode.BadGateway) {
                assertEquals(url, this.url.toString())
            }

            val result = openContacts() as? JobSiteResult.Error

            assertEquals(Status.Code.UNAVAILABLE, result?.toStatus()?.code)
        }

        @Test
        fun `when job site returns valid contacts returns them`() {
            val resume =
                """
                    {
                        "id": "1",
                        "first_name": "Ivan",
                        "last_name": "Ivanov",
                        "middle_name": "Ivanovich",
                        "contact": [
                            {
                                "type": {"id": "cell"},
                                "value": {"formatted": "8-911-222-33-44"}
                            }
                        ]
                    }
                """.trimIndent()
            requests.addResponse(content = resumeWithActionUrl())
            requests.addResponse(content = resume)

            val result = openContacts() as? JobSiteResult.Ok
            val contacts = result?.value?.first

            assertNotNull(result)
            assertEquals(resume, result?.value?.second)
            assertEquals("Ivan", contacts?.firstName)
            assertEquals("Ivanov", contacts?.lastName)
            assertEquals("Ivanovich", contacts?.middleName)
            assertEquals(
                "8-911-222-33-44",
                contacts?.contacts?.phonesList?.singleOrNull()?.formatted
            )
        }

        @Test
        fun `when buy contacts response is invalid returns internal error`() {
            requests.addResponse(content = resumeWithActionUrl())
            requests.addResponse(content = "{}")

            val result = openContacts() as? JobSiteResult.Error

            assertEquals(Status.Code.INTERNAL, result?.toStatus()?.code)
        }
    }

    @Nested
    inner class GetResumeTest {
        private fun getResume(externalId: String = "urn:hh:1") = runBlocking {
            adapter().getResume(externalId)
        }

        @Test
        fun `when job site returns valid json returns resume`() {
            val resume = """{"id": "123"}"""

            requests.addResponse(content = resume)

            val result = getResume("urn:hh:123") as? JobSiteResult.Ok

            assertNotNull(result)
            assertEquals(resume, result?.value?.second)
            assertEquals("urn:hh:123", result?.value?.first?.origin?.externalId)
        }

        @ParameterizedTest
        @ValueSource(strings = ["", "{}"])
        fun `when job site returns invalid response returns internal error`(content: String) {
            requests.addResponse(content = content)

            val result = getResume() as? JobSiteResult.Error

            assertEquals(Status.Code.INTERNAL, result?.toStatus()?.code)
        }

        @Test
        fun `when job site returns 5xx return unavailable error`() {
            requests.addResponse(status = HttpStatusCode.BadGateway)

            val result = getResume() as? JobSiteResult.Error

            assertEquals(Status.Code.UNAVAILABLE, result?.toStatus()?.code)
        }
    }

    @Nested
    inner class ListResumesTest {
        private val query = ResumeQuery.newBuilder()

        @AfterEach
        fun teardown() {
            query.clear()
        }

        private fun listResumes(pageNumber: Int = 0, pageSize: Int = 10) = runBlocking {
            adapter().listResumes(query.build(), pageNumber, pageSize)
        }

        private fun verifyFilter(
            pageNumber: Int = 0,
            pageSize: Int = 10,
            block: HttpRequestData.() -> Unit
        ) {
            requests.addResponse(content = """{"items": [{"id": "1"}]}""") { this.block() }

            val result = listResumes(pageNumber, pageSize) as? JobSiteResult.Ok

            assertEquals(listOf("urn:hh:1"), result?.value?.map { it.origin.externalId })
        }

        @Test
        fun `given pageNumber adds it`() {
            verifyFilter(pageNumber = 20) {
                assertEquals(listOf("20"), url.parameters.getAll("page"))
            }
        }

        @Test
        fun `given pageSize greater than zero adds it`() {
            verifyFilter(pageSize = 20) {
                assertEquals(listOf("20"), url.parameters.getAll("per_page"))
            }
        }

        @Test
        fun `given zero pageSize won't add it`() {
            verifyFilter(pageSize = 0) { assertFalse(url.parameters.contains("per_page")) }
        }

        @Test
        fun `given valid response returns resumes`() {
            requests.addResponse(content = """{"items": [{"id": "1"}, {"id": "2"}]}""")

            val result = listResumes() as? JobSiteResult.Ok

            assertEquals(
                listOf("urn:hh:1", "urn:hh:2"),
                result?.value?.map { it.origin.externalId }
            )
        }

        @ParameterizedTest
        @ValueSource(strings = ["", "{}", """{"items": [{}]}"""])
        fun `given invalid response returns error`(content: String) {
            requests.addResponse(content = content)

            val result = listResumes() as? JobSiteResult.Error

            assertEquals(Status.Code.INTERNAL, result?.toStatus()?.code)
        }

        @Test
        fun `when job site returns 5xx returns unavailable error`() {
            requests.addResponse(status = HttpStatusCode.BadGateway)

            val result = listResumes() as? JobSiteResult.Error

            assertEquals(Status.Code.UNAVAILABLE, result?.toStatus()?.code)
        }
    }
}
