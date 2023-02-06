package tvm

import io.grpc.Status
import io.mockk.clearAllMocks
import io.mockk.every
import io.mockk.mockk
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Nested
import org.junit.jupiter.api.Test
import ru.yandex.passport.tvmauth.CheckedServiceTicket
import ru.yandex.passport.tvmauth.TicketStatus
import ru.yandex.passport.tvmauth.TvmClient
import ru.yandex.taxi.crm.masshire.search.tvm.TvmFacade
import ru.yandex.taxi.crm.masshire.search.tvm.TvmResult
import ru.yandex.taxi.crm.masshire.search.tvm.TvmToolApi
import ru.yandex.taxi.crm.masshire.search.tvm.TvmToolResponse
import ru.yandex.taxi.crm.masshire.search.tvm.User

internal class TvmFacadeTest {
    private val tvmClient = mockk<TvmClient>(relaxed = true)
    private val tvmToolApi = mockk<TvmToolApi>(relaxed = true)

    private fun tvm() = TvmFacade(tvmClient, tvmToolApi)

    @AfterEach fun teardown() = clearAllMocks()

    @Nested
    inner class CheckUserTicketTest {
        @Test
        fun `when TvmToolApi throws returns unauthenticated`() {
            every { tvmToolApi.check(any()) } throws Exception()

            val result = tvm().checkUserTicket("some ticket") as? TvmResult.Error

            assertEquals(Status.Code.UNAUTHENTICATED, result?.status?.code)
        }

        @Test
        fun `when TvmToolApi returns ok with default uid returns it`() {
            every { tvmToolApi.check(any()) } returns
                TvmToolResponse(user = User(status = "OK", default_uid = "42"))

            val result = tvm().checkUserTicket("some ticket") as? TvmResult.Ok

            assertEquals("42", result?.value)
        }

        @Test
        fun `when TvmToolApi returns ok without uid returns empty string`() {
            every { tvmToolApi.check(any()) } returns
                TvmToolResponse(user = User(status = "OK", default_uid = null))

            val result = tvm().checkUserTicket("some ticket") as? TvmResult.Ok

            assertEquals("", result?.value)
        }

        @Test
        fun `when TvmToolApi return no user returns unauthenticated`() {
            every { tvmToolApi.check(any()) } returns TvmToolResponse(user = null)

            val result = tvm().checkUserTicket("some ticket") as? TvmResult.Error

            assertEquals(Status.Code.UNAUTHENTICATED, result?.status?.code)
        }

        @Test
        fun `when TvmToolApi return no status returns unauthenticated`() {
            every { tvmToolApi.check(any()) } returns TvmToolResponse(user = User(status = null))

            val result = tvm().checkUserTicket("some ticket") as? TvmResult.Error

            assertEquals(Status.Code.UNAUTHENTICATED, result?.status?.code)
        }

        @Test
        fun `when TvmToolApi return NO_ROLES status returns permission denied`() {
            every { tvmToolApi.check(any()) } returns
                TvmToolResponse(user = User(status = "NO_ROLES"))

            val result = tvm().checkUserTicket("some ticket") as? TvmResult.Error

            assertEquals(Status.Code.PERMISSION_DENIED, result?.status?.code)
        }
    }

    @Nested
    inner class CheckServiceTicketTest {
        @Test
        fun `when TvmClient returns OK returns no error`() {
            every { tvmClient.checkServiceTicket(any()) } returns
                CheckedServiceTicket(TicketStatus.OK, "", 0, 0)

            val result = tvm().checkServiceTicket("service ticket")

            assertTrue(result is TvmResult.Ok)
        }

        @Test
        fun `when TvmClient returns null status returns unauthenticated`() {
            every { tvmClient.checkServiceTicket(any()) } returns null

            val result = tvm().checkServiceTicket("service ticket") as? TvmResult.Error

            assertEquals(Status.Code.UNAUTHENTICATED, result?.status?.code)
        }

        @Test
        fun `when TvmClient returns non-OK status returns unauthenticated`() {
            every { tvmClient.checkServiceTicket(any()) } returns
                CheckedServiceTicket(TicketStatus.EXPIRED, "", 0, 0)

            val result = tvm().checkServiceTicket("service ticket") as? TvmResult.Error

            assertEquals(Status.Code.UNAUTHENTICATED, result?.status?.code)
        }

        @Test
        fun `when TvmClient throws returns unauthenticated`() {
            every { tvmClient.checkServiceTicket(any()) } throws Exception()

            val result = tvm().checkServiceTicket("service ticket") as? TvmResult.Error

            assertEquals(Status.Code.UNAUTHENTICATED, result?.status?.code)
        }
    }

    @Nested
    inner class GetServiceTicketForTest {
        @Test
        fun `when TvmClient returns service ticket returns no error`() {
            every { tvmClient.getServiceTicketFor(any<String>()) } returns "service-ticket"

            val result = tvm().getServiceTicketFor("") as? TvmResult.Ok<String>

            assertEquals("service-ticket", result?.value)
        }

        @Test
        fun `when TvmClient returns null ticket returns internal error`() {
            every { tvmClient.getServiceTicketFor(any<String>()) } returns null

            val result = tvm().getServiceTicketFor("") as? TvmResult.Error

            assertEquals(Status.Code.INTERNAL, result?.status?.code)
        }

        @Test
        fun `when TvmClient throws returns internal error`() {
            every { tvmClient.getServiceTicketFor(any<String>()) } throws Exception()

            val result = tvm().getServiceTicketFor("") as? TvmResult.Error

            assertEquals(Status.Code.INTERNAL, result?.status?.code)
        }
    }
}
