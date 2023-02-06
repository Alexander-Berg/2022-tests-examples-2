package tvm

import io.grpc.Status
import io.mockk.Called
import io.mockk.mockk
import io.mockk.verify
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Nested
import org.junit.jupiter.api.Test
import ru.yandex.taxi.crm.masshire.search.tvm.TvmResult

internal class TvmResultTest {
    @Nested
    inner class FlatMapTest {
        @Test
        fun `for result with value calls transformer`() {
            val result = TvmResult.Ok(42).flatMap { TvmResult.Ok(it.toString()) } as? TvmResult.Ok

            assertEquals("42", result?.value)
        }

        @Test
        fun `for result with error won't call transformer`() {
            val transformer = mockk<(Int) -> TvmResult<String>>()

            TvmResult.Error(Status.UNIMPLEMENTED).flatMap(transformer)

            verify { transformer wasNot Called }
        }
    }
}
