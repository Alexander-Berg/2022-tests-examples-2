package ru.yandex.passport.historydb.api.storage

import java.util.Base64

import org.scalatest.FunSuite


class HistoryDBUtilPackUnpackTest extends FunSuite {

  test("unpack BE usigned int to long") {
    assert(HistoryDBUtil.packedUnsignedBEIntToLong(Array[Byte](0, 0, 0, 0)) == 0)
    assert(HistoryDBUtil.packedUnsignedBEIntToLong(Array[Byte](0, 0, 0, 255.toByte)) == 255)
    assert(HistoryDBUtil.packedUnsignedBEIntToLong(Array[Byte](255.toByte, 0, 0, 0)) == 4278190080L)
    // 2 ** 32 - 1
    assert(HistoryDBUtil.packedUnsignedBEIntToLong(Array[Byte](255.toByte, 255.toByte, 255.toByte, 255.toByte)) == 4294967295L)
    assert(HistoryDBUtil.packedUnsignedBEIntToLong(Array[Byte](7, 91, 205.toByte, 21)) == 123456789)
  }

  test("unpack BE usigned long to BigInt") {
    val ff = 255.toByte
    assert(HistoryDBUtil.packedUnsignedBELongToBigInt(Array[Byte](0, 0, 0, 0, 0, 0, 0, 0)) == 0)
    // 2 ** 64 - 1
    assert(HistoryDBUtil.packedUnsignedBELongToBigInt(Array[Byte](ff, ff, ff, ff, ff, ff, ff, ff)) == BigInt("18446744073709551615"))
    assert(HistoryDBUtil.packedUnsignedBELongToBigInt(Array[Byte](17.toByte, 25.toByte, 107.toByte, 137.toByte, 250.toByte, 149.toByte, 157.toByte, 183.toByte)) == BigInt("1232134213421342135"))
  }

  test("test pack/unpack long") {
    assert(HistoryDBUtil.packedUnsignedBELongToBigInt(HistoryDBUtil.longToPackedBEUnsignedLong(0L)) == BigInt(0))
    assert(HistoryDBUtil.packedUnsignedBELongToBigInt(HistoryDBUtil.longToPackedBEUnsignedLong(1131234567899876L)) == BigInt(1131234567899876L))
    assert(HistoryDBUtil.packedUnsignedBELongToBigInt(HistoryDBUtil.longToPackedBEUnsignedLong(9223372036854775807L)) == BigInt(9223372036854775807L))
  }

}


class HistoryDBUtilAggregatedAuthTest extends FunSuite {

  test("parseAggregatedAuthKey") {
    var bytes = Array[Int](53, 53, 52, 0, 0, 0, 0, 3, 79, 181, 226, 255, 255, 255, 254, 119, 101, 98).map(_.toByte)
    val (uidPrefix1, uid1, hours1, tail1, suffix1) = HistoryDBUtil.parseAggregatedAuthKey(bytes)

    assert((uidPrefix1, uid1, hours1, tail1) == (554, 55555554L, 1, "web"))
    assert(suffix1 sameElements Array[Int](255, 255, 255, 254, 119, 101, 98).map(_.toByte))
    // uid = 1131234567899876; ts = 1905873659.051203; tail = web
    // 876\x00\x04\x04\xda\x12\x93\xca\xe4\xff\xf7\xeb\xfeweb

    bytes = Array[Int](56, 55, 54, 0, 4, 4, 218, 18, 147, 202, 228, 255, 247, 235, 254, 119, 101, 98).map(_.toByte)
    val (uidPrefix2, uid2, hours2, tail2, suffix2) = HistoryDBUtil.parseAggregatedAuthKey(bytes)
    assert((uidPrefix2, uid2, hours2, tail2)  == (876, 1131234567899876L, 529409, "web"))
    assert(suffix2 sameElements Array[Int](255, 247, 235, 254, 119, 101, 98).map(_.toByte))
  }

  test("parseAggregatedAuthKeyTail") {
    val key = "//fr/ndlYg==" // 529409, "web" in Base64
    val bytes = Array[Int](255, 247, 235, 254, 119, 101, 98).map(_.toByte)
    val (tailBytes, hours, tail) = HistoryDBUtil.parseAggregatedAuthKeyTail(key)
    assert((hours, tail) == (529409, "web"))
    assert(tailBytes sameElements bytes)
  }

  test("getNextAggregatedAuthKeyTail") {
    val incrementedBytes = HistoryDBUtil.getNextAggregatedAuthKeyTail(Array[Int](1, 127).map(_.toByte))
    assert(incrementedBytes == Base64.getEncoder.encodeToString(Array[Int](1, 128).map(_.toByte)))
  }

  test("getNextAggregatedAuthKeyTailBorder") {
    val incrementedBytes = HistoryDBUtil.getNextAggregatedAuthKeyTail(Array[Int](255, 255).map(_.toByte))
    assert(incrementedBytes == Base64.getEncoder.encodeToString(Array[Int](1, 0, 0).map(_.toByte)))
  }

  test("buildAggregatedAuthKeyRangeFromOnly") {
    val uid = 1131234567899876L
    val expectedStartRow = Array[Int](56, 55, 54, 0, 4, 4, 218, 18, 147, 202, 228, 255, 247, 235, 254, 119, 101, 98).map(_.toByte)
    val expectedStopRow = Array[Int](56, 55, 54).map(_.toByte) ++ HistoryDBUtil.longToPackedBEUnsignedLong(uid + 1)
    val (startRow, stopRow) = HistoryDBUtil.buildAggregatedAuthKeyRange(uid, None, Some("//fr/ndlYg=="))  // 529409, "web" in Base64
    assert(startRow sameElements expectedStartRow)
    assert(stopRow sameElements expectedStopRow)
  }

  test("buildAggregatedAuthKeyRangeFromAndHoursLimit") {
    val uid = 1131234567899876L
    val expectedStartRow = Array[Int](56, 55, 54, 0, 4, 4, 218, 18, 147, 202, 228, 255, 247, 235, 254, 119, 101, 98).map(_.toByte)
    val expectedStopRow = Array[Int](56, 55, 54, 0, 4, 4, 218, 18, 147, 202, 228).map(_.toByte) ++ HistoryDBUtil.longToPackedBEUnsignedInt(HistoryDBUtil.MAX_UINT - (529409 - 1))
    val (startRow, stopRow) = HistoryDBUtil.buildAggregatedAuthKeyRange(uid, Some(1), Some("//fr/ndlYg==")) // 529409, "web" in Base64
    assert(startRow sameElements expectedStartRow)
    assert(stopRow sameElements expectedStopRow)
  }

  test("buildAggregatedAuthKeyRangeDefault") {
    val uid = 1131234567899876L
    val expectedStartRow = Array[Int](56, 55, 54).map(_.toByte) ++ HistoryDBUtil.longToPackedBEUnsignedLong(uid)
    val expectedStopRow = Array[Int](56, 55, 54).map(_.toByte) ++ HistoryDBUtil.longToPackedBEUnsignedLong(uid + 1)
    val (startRow, stopRow) = HistoryDBUtil.buildAggregatedAuthKeyRange(uid, None, None)
    assert(startRow sameElements expectedStartRow)
    assert(stopRow sameElements expectedStopRow)
  }
}


class HistoryDBUtilEventTest extends  FunSuite {

  test("simple") {
    assert(HistoryDBUtil.buildBaseEventKey(123, 0) == "123_9223372036854775807.000000")
    assert(HistoryDBUtil.buildBaseEventKey(123, 1) == "123_9223372036854775806.000000")
    assert(HistoryDBUtil.buildBaseEventKey(123, 1.123) == "123_9223372036854775806.877000")
  }

  test("negativeValue") {
    intercept[IllegalArgumentException] {
      HistoryDBUtil.buildBaseEventKey(123, -1)
    }
  }

}
