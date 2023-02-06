package logging

import io.grpc.Context
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Test
import ru.yandex.taxi.crm.masshire.search.logging.GrpcMDC

private val STRING_KEY = Context.key<String>("TheAnswer")
private val INT_KEY = Context.key<Int>("TheAnswer")

internal class GrpcMDCTest {

    @Test
    fun `get when no value is stored returns null`() {
        assertNull(GrpcMDC()[STRING_KEY])
    }

    @Test
    fun `get after set returns value`() {
        val mdc = GrpcMDC()

        mdc[STRING_KEY] = "42"
        mdc[INT_KEY] = 42

        assertEquals("42", mdc[STRING_KEY])
        assertEquals(42, mdc[INT_KEY])
    }
}
