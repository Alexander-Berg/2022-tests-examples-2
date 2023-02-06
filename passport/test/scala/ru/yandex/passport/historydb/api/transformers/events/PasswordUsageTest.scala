package ru.yandex.passport.historydb.api.transformers.events


import org.scalatest._
import ru.yandex.passport.historydb.api.storage.{Event, HistoryDBUtil}


class PasswordUsageEntryTest extends FunSuite with Matchers {

  test("addVersionPrefixToPasswordHash") {
    assert(PasswordUsageEntry.addVersionPrefixToPasswordHash("a") == "1:a")
    assert(PasswordUsageEntry.addVersionPrefixToPasswordHash("1:a") == "1:a")
    assert(PasswordUsageEntry.addVersionPrefixToPasswordHash("2:a") == "2:a")
    assert(PasswordUsageEntry.addVersionPrefixToPasswordHash("123:a") == "123:a")
  }

  def buildPasswordEvent(timestamp: Double, passwordHash: String) = {
    Event(timestamp, Map("name" -> HistoryDBUtil.CHANGE_PASSWORD_EVENT_NAME, "value" -> passwordHash))
  }

  test("groupPasswordByActiveRanges: with removed, unknown passwords") {
    val events = List(
      buildPasswordEvent(150, "a"),
      buildPasswordEvent(140, "*"),
      buildPasswordEvent(130, "b"),
      Event(125, Map("name" -> HistoryDBUtil.CHANGE_PASSWORD_EVENT_NAME)),
      buildPasswordEvent(120, "c"),
      Event(110, Map("name" -> HistoryDBUtil.CHANGE_PASSWORD_EVENT_NAME)),
      buildPasswordEvent(100, "d")
    )
    val expected = Map(
      "1:a" -> (150.0, None),
      "1:b" -> (130.0, Some(140.0)),
      "1:c" -> (120.0, Some(125.0)),
      "1:d" -> (100.0, Some(110.0))
    )
    PasswordUsageEntry.groupPasswordByActiveRanges(events) should equal (expected)
  }

  test("groupPasswordByActiveRanges: bad event") {
    intercept[IllegalArgumentException] {
      PasswordUsageEntry.groupPasswordByActiveRanges(List(Event(1, Map("name" -> "badname"))))
    }
  }

}