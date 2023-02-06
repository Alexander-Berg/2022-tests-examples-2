import com.google.protobuf.Empty
import io.grpc.Status
import io.grpc.StatusException
import io.grpc.stub.StreamObserver
import io.mockk.MockKAnnotations
import io.mockk.impl.annotations.MockK
import io.mockk.verify
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Nested
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows
import ru.yandex.taxi.crm.masshire.search.DEFAULT_ERROR_MESSAGE
import ru.yandex.taxi.crm.masshire.search.grpcCheck
import ru.yandex.taxi.crm.masshire.search.grpcCheckNotNull
import ru.yandex.taxi.crm.masshire.search.grpcRequire
import ru.yandex.taxi.crm.masshire.search.grpcRequireNotNull
import ru.yandex.taxi.crm.masshire.search.runObserving

internal class GrpcUtilsKtTest {

    var messageCalled = false

    @BeforeEach
    fun setup() {
        messageCalled = false
    }

    fun message(): String {
        messageCalled = true
        return "message() was called"
    }

    @Test
    fun `grpcCheck(true) doesn't call lazyMessage and doesn't throw`() {
        grpcCheck(true) { message() }
        assertFalse(messageCalled)
    }

    @Test
    fun `grpcCheck(false) calls lazyMessage and throws INTERNAL`() {
        val ex = assertThrows<StatusException> { grpcCheck(false) { message() } }

        assertTrue(messageCalled)
        assertEquals(Status.INTERNAL.code, ex.status.code)
    }

    @Test
    fun `grpcRequire(true) doesn't call lazyMessage and doesn't throw`() {
        grpcRequire(true) { message() }
        assertFalse(messageCalled)
    }

    @Test
    fun `grpcRequire(false) calls lazyMessage and throws INVALID_ARGUMENT`() {
        val ex = assertThrows<StatusException> { grpcRequire(false) { message() } }

        assertTrue(messageCalled)
        assertEquals(Status.INVALID_ARGUMENT.code, ex.status.code)
    }

    @Test
    fun `grpcRequireNotNull on not null value doesn't call lazyMessage and returns value`() {
        val optional: Int? = 1

        assertEquals(1, grpcRequireNotNull(optional) { message() })
        assertFalse(messageCalled)
    }

    @Test
    fun `grpcRequireNotNull on null value calls lazyMessage and throws`() {
        val optional: Int? = null

        val ex = assertThrows<StatusException> { grpcRequireNotNull(optional) { message() } }

        assertTrue(messageCalled)
        assertEquals(Status.INVALID_ARGUMENT.code, ex.status.code)
    }

    @Test
    fun `grpcCheckNotNull on not null value doesn't call lazyMessage and returns value`() {
        val optional: Int? = 1

        val value = optional.grpcCheckNotNull { message() }

        assertFalse(messageCalled)
        assertEquals(optional!!, value)
    }

    @Test
    fun `grpcCheckNotNull on null value calls lazyMessage and throws INTERNAL`() {
        val optional: Int? = null

        val ex = assertThrows<StatusException> { optional.grpcCheckNotNull { message() } }

        assertTrue(messageCalled)
        assertEquals(Status.INTERNAL.code, ex.status.code)
    }

    @Nested
    inner class RunObservingTest {
        @MockK(relaxUnitFun = true) private lateinit var responseObserver: StreamObserver<Empty>

        @BeforeEach
        private fun setup() {
            MockKAnnotations.init(this)
        }

        // Empty string is contained in any other string
        private fun verifyStatus(status: Status, message: String = "") {
            verify {
                responseObserver.onError(
                    match {
                        (it as? StatusException)?.status?.code == status.code &&
                            it.message?.contains(message) == true
                    }
                )
            }
        }

        @Test
        fun `for no exception calls onNext and completes`() {
            runObserving(responseObserver) { Empty.getDefaultInstance() }

            verify { responseObserver.onNext(any()) }
            verify { responseObserver.onCompleted() }
        }

        @Test
        fun `for StatusExceptions returns it`() {
            runObserving(responseObserver) { throw Status.DEADLINE_EXCEEDED.asException() }

            verifyStatus(Status.DEADLINE_EXCEEDED)
        }

        @Test
        fun `for IllegalArgumentException returns invalid argument error`() {
            val message = "Illegal argument value"
            runObserving(responseObserver) {
                require(false) { message }
                Empty.getDefaultInstance()
            }

            verifyStatus(Status.INVALID_ARGUMENT, message)
        }

        @Test
        fun `for IllegalStateException returns invalid argument error`() {
            val message = "Some special message here"
            runObserving(responseObserver) {
                check(false) { message }
                Empty.getDefaultInstance()
            }

            verifyStatus(Status.INTERNAL, message)
        }

        @Test
        fun `for unknown exception returns internal error`() {
            val message = "Some special message here"
            runObserving(responseObserver) { throw RuntimeException(message) }

            verifyStatus(Status.INTERNAL, DEFAULT_ERROR_MESSAGE)
        }
    }
}
