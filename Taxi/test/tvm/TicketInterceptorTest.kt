package tvm

import io.grpc.Metadata
import io.grpc.ServerCall
import io.grpc.ServerCallHandler
import io.grpc.Status
import io.mockk.clearAllMocks
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test
import ru.yandex.taxi.crm.masshire.search.UserCredentials
import ru.yandex.taxi.crm.masshire.search.logging.getOrNull
import ru.yandex.taxi.crm.masshire.search.tvm.TicketInterceptor
import ru.yandex.taxi.crm.masshire.search.tvm.TvmFacade
import ru.yandex.taxi.crm.masshire.search.tvm.TvmResult

internal class TicketInterceptorTest {
    private val tvmFacade = mockk<TvmFacade>(relaxed = true)
    private val interceptor = TicketInterceptor(tvmFacade)
    private val call = mockk<ServerCall<Unit, Unit>>(relaxed = true)
    private val next = mockk<ServerCallHandler<Unit, Unit>>(relaxed = true)

    private fun interceptCall(
        metadata: Metadata =
            Metadata().apply {
                put(TicketInterceptor.SERVICE_TICKET_HEADER, "service-ticket")
                put(TicketInterceptor.USER_TICKET_HEADER, "user-ticket")
            }
    ) = interceptor.interceptCall(call, metadata, next)

    @AfterEach fun teardown() = clearAllMocks()

    @Test
    fun `given no service ticket in metadata closes call`() {
        interceptCall(Metadata())

        verify { call.close(any(), any()) }
        verify(exactly = 0) { tvmFacade.checkServiceTicket(any()) }
    }

    @Test
    fun `given service ticket and no user ticket closes call`() {
        interceptCall(
            Metadata().apply { put(TicketInterceptor.SERVICE_TICKET_HEADER, "some-service-ticket") }
        )

        verify { call.close(any(), any()) }
        verify(exactly = 0) { tvmFacade.checkServiceTicket(any()) }
    }

    @Test
    fun `given service ticket and user ticket in metadata passes them to tvmFacade`() {
        every { tvmFacade.checkServiceTicket(any()) } returns TvmResult.Ok(Unit)
        every { tvmFacade.checkUserTicket(any()) } returns TvmResult.Ok("")

        interceptCall(
            Metadata().apply {
                put(TicketInterceptor.SERVICE_TICKET_HEADER, "some-service-ticket")
                put(TicketInterceptor.USER_TICKET_HEADER, "some-user-ticket")
            }
        )

        verify { tvmFacade.checkServiceTicket("some-service-ticket") }
        verify { tvmFacade.checkUserTicket("some-user-ticket") }
    }

    @Test
    fun `when service ticket is not verified closes call`() {
        every { tvmFacade.checkServiceTicket(any()) } returns TvmResult.Error(Status.UNIMPLEMENTED)

        interceptCall()

        verify {
            call.close(
                match { it.code == Status.Code.UNIMPLEMENTED },
                any(),
            )
        }
    }

    @Test
    fun `when service ticket is not verified won't verify user ticket`() {
        every { tvmFacade.checkServiceTicket(any()) } returns TvmResult.Error(Status.UNIMPLEMENTED)

        interceptCall()

        verify(exactly = 0) { tvmFacade.checkUserTicket(any()) }
    }

    @Test
    fun `when user ticket is not verified closes call`() {
        every { tvmFacade.checkServiceTicket(any()) } returns TvmResult.Ok(Unit)
        every { tvmFacade.checkUserTicket(any()) } returns TvmResult.Error(Status.PERMISSION_DENIED)

        interceptCall()

        verify {
            call.close(
                match { it.code == Status.Code.PERMISSION_DENIED },
                any(),
            )
        }
    }

    @Test
    fun `when both service and user tickets are verified won't close call`() {
        every { tvmFacade.checkUserTicket(any()) } returns TvmResult.Ok("42")
        every { tvmFacade.checkServiceTicket(any()) } returns TvmResult.Ok(Unit)

        interceptCall().onMessage(Unit)

        verify(exactly = 0) { call.close(any(), any()) }
    }

    @Test
    fun `when both service and user tickets are verified injects UserCredentials into context`() {
        every { tvmFacade.checkUserTicket(any()) } returns TvmResult.Ok("42")
        every { tvmFacade.checkServiceTicket(any()) } returns TvmResult.Ok(Unit)
        every { next.startCall(any(), any()).onMessage(Unit) } answers
            {
                assertEquals("42", UserCredentials.KEY.getOrNull()?.userUid)
            }

        interceptCall().onMessage(Unit)

        verify { next.startCall(any(), any()).onMessage(Unit) }
    }
}
