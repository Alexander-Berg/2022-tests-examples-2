package com.yandex.tv.services.testjava

import android.os.Parcel
import android.os.Parcelable
import com.yandex.tv.services.common.annotations.AidlProps
import com.yandex.tv.services.common.annotations.AndroidService

@AndroidService
interface TestJavaServiceApi {

    class Dump() : Parcelable {
        constructor(parcel: Parcel) : this() {
        }

        override fun writeToParcel(parcel: Parcel, flags: Int) {

        }

        override fun describeContents(): Int {
            return 0
        }

        companion object CREATOR :
            Parcelable.Creator<Dump> {
            override fun createFromParcel(parcel: Parcel): Dump {
                return Dump(parcel)
            }

            override fun newArray(size: Int): Array<Dump?> {
                return arrayOfNulls(size)
            }
        }
    }


    @AidlProps(uid = 666)
    fun dummy()

    @AidlProps
    fun dummyByte(): Byte

    fun dummyChar(): Char

    fun dummyShort(): Short

    fun dummyInt(): Int

    fun dummyLong(): Long

    fun dummyFloat(): Float

    fun dummyDouble(): Double

    fun dummyBoolean(): Boolean

    fun dummyString(): String

    fun dummyParcelable(): Dump

    fun dummyInAll(aByte: Byte, aChar: Char, aShort: Short, anInt: Int, aLong: Long,
                   aFloat: Float, aDouble: Double, aBoolean: Boolean, string: String, dump: Dump)

}
