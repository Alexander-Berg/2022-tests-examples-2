package com.yandex.tv.services.testapp

import android.os.Binder
import android.os.Handler
import android.os.IBinder
import android.os.IInterface
import android.os.Looper
import android.os.Message
import android.os.Parcel
import android.os.RemoteCallbackList
import android.os.RemoteException
import android.util.Log

/**
 * Test IInterface borrowed from quasar-android
 */
interface QuasarBinder : IInterface {
    /**
     * Connects to another QuasarBinder.
     * This allows to receive broadcasts from other QuasarBinder.
     *
     * @param peer QuasarBinder to connect to
     */
    @Throws(RemoteException::class)
    fun connect(peer: QuasarBinder)

    /**
     * Disconnects from another QuasarBinder.
     * This binder will not get broadcast messages from another binder after disconnect.
     *
     * @param peer QuasarBinder to disconnect from
     */
    @Throws(RemoteException::class)
    fun disconnect(peer: QuasarBinder)

    /**
     * Sends a message to this QuasarBinder.
     *
     * @param message - message bytes
     * @param from - QuasarBinder that sent the message
     */
    @Throws(RemoteException::class)
    fun send(message: ByteArray, from: QuasarBinder)

    /**
     * Base implementation of QuasarBinder. Extend this class to use QuasarBinder.
     */
    abstract class Stub<TMessage : Message>(
        private val incomingMessageParser: (ByteArray) -> TMessage,
        private val handler: Handler = Handler(Looper.getMainLooper())
    ) : Binder(), QuasarBinder {

        private val peers = object : RemoteCallbackList<QuasarBinder>() {
            override fun onCallbackDied(callback: QuasarBinder) {
                handler.post {
                    try {
                        onDisconnected(callback)
                    } catch (throwable: Throwable) {
                        Log.e(TAG, "Exception in onCallbackDied: $throwable", throwable)
                    }
                }
            }
        }

        val peersCount = peers.registeredCallbackCount

        init {
            @Suppress("LeakingThis")
            attachInterface(this, DESCRIPTOR)
        }

        /**
         * Called when new peer is connected.
         * At the time, when method is called, peer is already able to receive messages.
         */
        open fun onConnected(peer: QuasarBinder) {
            Log.d(TAG, "onConnected")
        }

        /**
         * Called when peer is disconnected.
         * At the time, when method is called, peer is already disconnected,
         * and thus cannot receive messages anymore.
         */
        open fun onDisconnected(peer: QuasarBinder) {
            Log.d(TAG, "onDisconnected")
        }

        /**
         * Called when some other QuasarBinder sends message to this binder.
         *
         * @param message - incoming message, created with provided incomingMessageParser
         * @param sender - other QuasarBinder, it may or may not be connected to this binder
         */
        abstract fun onIncomingMessage(message: TMessage, sender: QuasarBinder)

        /**
         * Sends message to all connected QuasarBinders.
         *
         * @param message - message to send
         */
        fun broadcast(message: ByteArray) {
            val peersCount = peers.beginBroadcast()
            for (peerIndex in 0 until peersCount) {
                try {
                    peers.getBroadcastItem(peerIndex).send(message, this)
                } catch (exception: RemoteException) {
                    Log.e(TAG, "RemoteException in broadcast: $exception", exception)
                }
            }
            peers.finishBroadcast()
        }

        final override fun connect(peer: QuasarBinder) {
            handler.post {
                try {
                    if (peers.register(peer)) {
                        onConnected(peer)
                    }
                } catch (connect: Throwable) {
                    Log.e(TAG, "Exception in connect: $connect", connect)
                }
            }
        }

        final override fun disconnect(peer: QuasarBinder) {
            handler.post {
                try {
                    if (peers.unregister(peer)) {
                        onDisconnected(peer)
                    }
                } catch (throwable: Throwable) {
                    Log.e(TAG, "Exception in disconnect: $throwable", throwable)
                }
            }
        }

        final override fun send(message: ByteArray, from: QuasarBinder) {
            handler.post {
                try {
                    val protoBufMessage = incomingMessageParser(message)
                    onIncomingMessage(protoBufMessage, from)
                } catch (throwable: Throwable) {
                    Log.e(TAG, "Exception in send: $throwable", throwable)
                }
            }
        }

        final override fun asBinder() = this

        override fun onTransact(code: Int, data: Parcel, reply: Parcel?, flags: Int): Boolean {
            if (super.onTransact(code, data, reply, flags)) {
                return true
            }
            when (code) {
                TRANSACTION_SEND_BYTES -> {
                    val msgSize = data.readInt()
                    val message = ByteArray(msgSize)
                    data.readByteArray(message)
                    send(message, Companion.asInterface(data.readStrongBinder()))
                    reply?.writeNoException()
                    return true
                }
                TRANSACTION_CONNECT -> {
                    connect(Companion.asInterface(data.readStrongBinder()))
                    reply?.writeNoException()
                    return true
                }
                TRANSACTION_DISCONNECT -> {
                    disconnect(Companion.asInterface(data.readStrongBinder()))
                    reply?.writeNoException()
                    return true
                }
            }
            return false
        }

        companion object {
            /**
             * Wraps IBinder in QuasarBinder.
             */
            @JvmStatic
            fun asInterface(binder: IBinder): QuasarBinder {
                val iin = binder.queryLocalInterface(DESCRIPTOR)
                return if (iin is QuasarBinder) iin else Proxy(binder)
            }
        }
    }

    /**
     * Wrapper for IBinder in a remote process.
     */
    private class Proxy(private val remote: IBinder) : QuasarBinder {
        @Throws(RemoteException::class)
        override fun connect(peer: QuasarBinder) {
            runTransaction(TRANSACTION_CONNECT) { parcel ->
                parcel.writeStrongBinder(peer.asBinder())
            }
        }

        @Throws(RemoteException::class)
        override fun disconnect(peer: QuasarBinder) {
            runTransaction(TRANSACTION_DISCONNECT) { parcel ->
                parcel.writeStrongBinder(peer.asBinder())
            }
        }

        @Throws(RemoteException::class)
        override fun send(message: ByteArray, from: QuasarBinder) {
            runTransaction(TRANSACTION_SEND_BYTES) { parcel ->
                parcel.writeInt(message.size)
                parcel.writeByteArray(message)
                parcel.writeStrongBinder(from.asBinder())
            }
        }

        @Throws(RemoteException::class)
        private inline fun runTransaction(code: Int, writeData: (Parcel) -> Unit) {
            val data = Parcel.obtain()
            val reply = Parcel.obtain()
            try {
                writeData(data)
                remote.transact(code, data, reply, 0)
                reply.readException()
            } finally {
                data.recycle()
                reply.recycle()
            }
        }

        override fun asBinder() = remote
    }

    companion object {
        const val TAG = "QuasarBinder"
        const val DESCRIPTOR = "ru.yandex.io.music.ipc.QuasarBinderClient"
        const val TRANSACTION_CONNECT = IBinder.FIRST_CALL_TRANSACTION + 0
        const val TRANSACTION_DISCONNECT = IBinder.FIRST_CALL_TRANSACTION + 1
        const val TRANSACTION_SEND_BYTES = IBinder.FIRST_CALL_TRANSACTION + 2
    }
}
