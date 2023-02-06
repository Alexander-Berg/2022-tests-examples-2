package amocrm

import io.grpc.Status
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Test
import ru.yandex.taxi.crm.masshire.search.amocrm.statusExceptionOrNull

internal class StatusExceptionOrNullTest {
    @Test
    fun `success result returns null`() {
        assertNull(Result.success(Unit).statusExceptionOrNull())
    }

    @Test
    fun `failure result with status exception returns it`() {
        val exception = Status.UNAUTHENTICATED.asException()

        assertEquals(exception, Result.failure<Unit>(exception).statusExceptionOrNull())
    }

    @Test
    fun `failure result with non status exception returns internal error`() {
        val result = Result.failure<Unit>(Throwable())

        assertEquals(Status.Code.INTERNAL, result.statusExceptionOrNull()?.status?.code)
    }
}
