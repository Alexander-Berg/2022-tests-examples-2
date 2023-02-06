import io.grpc.Status
import io.ktor.client.engine.mock.MockEngine
import io.ktor.client.engine.mock.respond
import io.ktor.http.HttpHeaders
import io.ktor.http.HttpStatusCode
import io.ktor.http.headersOf
import io.mockk.clearAllMocks
import io.mockk.every
import io.mockk.mockk
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Test
import ru.yandex.taxi.crm.masshire.search.BlackboxClient
import ru.yandex.taxi.crm.masshire.search.UserCredentials
import ru.yandex.taxi.crm.masshire.search.httpClient
import ru.yandex.taxi.crm.masshire.search.tvm.TvmFacade
import ru.yandex.taxi.crm.masshire.search.tvm.TvmResult

internal class BlackboxClientTest {
    private val tvmFacade =
        mockk<TvmFacade>(relaxed = true) {
            every { getServiceTicketFor(any()) } returns TvmResult.Ok("service-ticket")
        }
    private var responseContent = "{}"
    private var responseStatus = HttpStatusCode.OK

    @AfterEach fun teardown() = clearAllMocks()

    private fun userLogin(): String? {
        val mockEngine = MockEngine { request ->
            assertEquals("service-ticket", request.headers["X-Ya-Service-Ticket"])
            respond(
                content = responseContent,
                status = responseStatus,
                headers = headersOf(HttpHeaders.ContentType, "application/json"),
            )
        }
        return runBlocking {
            BlackboxClient(tvmFacade, httpClient(mockEngine))
                .getUserLogin(
                    UserCredentials(userTicket = "some-user-ticket", userUid = "42"),
                )
        }
    }

    @Test
    fun `when can't fetch service ticket returns null`() {
        every { tvmFacade.getServiceTicketFor(any()) } returns TvmResult.Error(Status.INTERNAL)

        assertNull(userLogin())
    }

    @Test
    fun `given no users in blackbox response returns null`() {
        responseContent = "{}"

        assertNull(userLogin())
    }

    @Test
    fun `given empty users in blackbox response returns null`() {
        responseContent = """{"users": []}"""

        assertNull(userLogin())
    }

    @Test
    fun `given user without login returns null`() {
        responseContent = """{"users": [{}]}"""

        assertNull(userLogin())
    }

    @Test
    fun `given user with login returns it`() {
        responseContent = """{"users": [{"login": "user"}]}"""

        assertEquals("user", userLogin())
    }

    @Test
    fun `when blackbox request fails returns null`() {
        responseContent = """{"grants_status": "ACCESS_DENIED"}"""
        responseStatus = HttpStatusCode.Forbidden

        assertNull(userLogin())
    }

    @Test
    fun `when blackbox returns invalid json returns null`() {
        responseContent = "invalid json"

        assertNull(userLogin())
    }
}
