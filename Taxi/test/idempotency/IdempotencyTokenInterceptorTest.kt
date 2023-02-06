package idempotency

import io.grpc.Metadata
import io.grpc.ServerCall
import io.grpc.ServerCallHandler
import io.mockk.clearAllMocks
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows
import ru.yandex.taxi.crm.masshire.search.idempotency.IdempotencyTokenInterceptor
import ru.yandex.taxi.crm.masshire.search.idempotency.getIdempotencyToken

internal class IdempotencyTokenInterceptorTest {
    private val interceptor = IdempotencyTokenInterceptor()
    private val call = mockk<ServerCall<Unit, Unit>>(relaxed = true)
    private val next = mockk<ServerCallHandler<Unit, Unit>>(relaxed = true)

    private fun interceptCall(metadata: Metadata) = interceptor.interceptCall(call, metadata, next)

    @AfterEach fun teardown() = clearAllMocks()

    @Test
    fun `given no idempotency token header won't set context key and will continue call`() {
        every { next.startCall(call, any()).onMessage(Unit) } answers
            {
                assertThrows<IllegalArgumentException> { getIdempotencyToken() }
            }

        interceptCall(Metadata()).onMessage(Unit)

        verify { next.startCall(call, any()).onMessage(Unit) }
    }

    @Test
    fun `given idempotency token header adds it to context and continues call`() {
        every { next.startCall(any(), any()).onMessage(Unit) } answers
            {
                assertEquals("idempotency-token", getIdempotencyToken())
            }

        val headers =
            Metadata().apply {
                put(IdempotencyTokenInterceptor.IDEMPOTENCY_TOKEN_HEADER, "idempotency-token")
            }
        interceptCall(headers).onMessage(Unit)

        verify { next.startCall(any(), any()).onMessage(Unit) }
    }
}
