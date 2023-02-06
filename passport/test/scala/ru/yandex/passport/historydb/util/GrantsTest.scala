package ru.yandex.passport.historydb.util

import java.util

import collection.JavaConverters._
import com.google.common.net.InetAddresses
import org.scalatest.FunSuite
import ru.yandex.passport.util.Grants
import ru.yandex.passport.util.net.Subnet

import scala.collection.mutable.ArrayBuffer


class GrantsTest extends FunSuite {
  val grantAX = "a.X"
  val grantAY = "a.Y"
  val grantAZ = "a.Z"
  val grantBX = "b.X"

  val grants = new Grants()
  grants.add(
    "A",
    1,
    ArrayBuffer(
      "fe80::863a:4bff:fece:e9c4/64",
      "2a02:6b8:0:803::8805",
      "192.168.0.0/24",
      "10.10.0.0/17",
      "172.16.0.1"
    ).asJava,
    ArrayBuffer("a.X", "a.Y", "b.X").asJava
  )
  grants.add(
    "B",
    1,
    ArrayBuffer(
      "2a02:6b8:0:803::8805"
    ).asJava,
    ArrayBuffer("a.X", "a.Y", "b.X").asJava
  )
  grants.add(
    "C",
    1,
    ArrayBuffer(
      "fe80::fece:e9c4/96",
      "4130@2a02:6b8:c000::/40",
      "2130@2a02:6b8:c000::/40"
    ).asJava,
    ArrayBuffer("a.X", "a.Y", "b.X").asJava
  )

  def ip(ip: String) = InetAddresses.forString(ip)

  test("unknown consumer") {
    assert(!grants.checkGrant("C", grantAX, ip("192.168.0.0")))
  }

  test("consumer has got grant") {
    for (grant <- List(grantAX, grantAY, grantBX)) {
      assert(grants.checkGrant("A", grant, ip("fe80::")))
      assert(grants.checkGrant("A", grant, ip("fe80:0000:0000:0000:ffff:ffff:ffff:ffef")))
      assert(grants.checkGrant("A", grant, ip("fe80:0000:0000:0000:ffff:ffff:ffff:ffff")))
      assert(grants.checkGrant("A", grant, ip("fe80:0000:0000:0000:0000:0000:ffff:ffff")))
      assert(grants.checkGrant("C", grant, ip("fe80:0000:0000:0000:0000:0000:ffff:ffff")))
      assert(grants.checkGrant("C", grant, ip("2a02:6b8:c000:0000:0000:4130:ffff:ffff")))
      assert(grants.checkGrant("A", grant, ip("2a02:6b8:0:803::8805")))
      assert(grants.checkGrant("B", grant, ip("2a02:6b8:0:803::8805")))

      assert(grants.checkGrant("A", grant, ip("192.168.0.0")))
      assert(grants.checkGrant("A", grant, ip("192.168.0.255")))

      assert(grants.checkGrant("A", grant, ip("10.10.0.0")))
      assert(grants.checkGrant("A", grant, ip("10.10.0.255")))
      assert(grants.checkGrant("A", grant, ip("10.10.127.0")))
      assert(grants.checkGrant("A", grant, ip("10.10.127.255")))

      assert(grants.checkGrant("A", grant, ip("172.16.0.1")))
    }
  }

  test("consumer has got grant for the other networks") {
    for (userIp <- List(
      ip("fe80:1000:0000:0000:ffff:ffff:ffff:ffff"), ip("2a02:6b8:0:803::8806"),
      ip("192.168.1.0"), ip("10.10.128.255"), ip("172.16.0.0"))
    ) {
      for (grant <- List(grantAX, grantAY, grantBX)) {
        assert(!grants.checkGrant("A", grant, userIp))
        assert(!grants.checkGrant("A", grant, userIp))
        assert(!grants.checkGrant("A", grant, userIp))
        assert(!grants.checkGrant("B", grant, userIp))
      }
    }
  }

  test("consumer hasn't got grant") {
    assert(!grants.checkGrant("A", grantAZ, ip("192.168.0.0")))
    assert(!grants.checkGrant("A", grantAZ, ip("2a02:6b8:0:803::8805")))
    assert(!grants.checkGrant("C", grantAZ, ip("2a02:6b8:00c0:0000:0000:4130:ffff:ffff")))
  }

  test("0.0.0.0/0; ::/0") {
    val grants = new Grants()
    grants.add(
      "A",
      1,
      ArrayBuffer("::/0", "0.0.0.0/0").asJava,
      ArrayBuffer("a.X", "a.Y", "b.X").asJava
    )
    for (userIp <- List(
      ip("fe80:1000:0000:0000:ffff:ffff:ffff:ffff"), ip("2a02:6b8:0:803::8806"),
      ip("192.168.1.0"), ip("10.10.128.255"), ip("172.16.0.0"))
    ) {
      for (grant <- List(grantAX, grantAY, grantBX)) {
        assert(grants.checkGrant("A", grant, userIp))
      }
    }
  }
}
