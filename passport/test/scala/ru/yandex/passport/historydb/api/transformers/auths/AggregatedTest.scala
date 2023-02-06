package scala.ru.yandex.passport.historydb.api.transformers.auths

import org.scalatest._
import ru.yandex.passport.historydb.api.storage.AggregatedAuthValue
import ru.yandex.passport.historydb.api.transformers.auths.Aggregated.parseHistoryDbValue

class AggregatedTest extends FunSuite with Matchers {

  test("Parse HistoryDB value: old version") {
    assert(parseHistoryDbValue("123.45".getBytes()).contains(AggregatedAuthValue(
      timestamp=123.45,
      latitude=None,
      longitude=None,
      accuracy=None,
      precision=None
    )))
  }

  test("Parse HistoryDB value: new version") {
    // формат: version:auth_timestamp:lat:long:accuracy:precision
    val input = List("1", "123.45", "10.0", "20.0", "15000", "district").mkString(":").getBytes()
    assert(parseHistoryDbValue(input).contains(AggregatedAuthValue(
      timestamp=123.45,
      latitude=Some(10.0),
      longitude=Some(20.0),
      accuracy=Some(15000),
      precision=Some("district"))
    ))
  }

  test("Parse HistoryDB value: new version, no laas") {
    // формат: version:auth_timestamp
    assert(parseHistoryDbValue("1:123.45".getBytes()).contains(AggregatedAuthValue(
      timestamp=123.45
    )))
  }

  test("Parse HistoryDB value: new version incomplete / broken 1") {
    assert(parseHistoryDbValue("1:2.2:3.3".getBytes()).isEmpty)
  }

  test("Parse HistoryDB value: new version incomplete / broken 2") {
    assert(parseHistoryDbValue("1:".getBytes()).isEmpty)
  }

  test("Parse HistoryDB value: new version incomplete / broken 3") {
    assert(parseHistoryDbValue("1:::::".getBytes()).isEmpty)
  }

  test("Parse HistoryDB value: new version not a number") {
    assert(parseHistoryDbValue("1:foo:bar:zar:hurr:durr".getBytes()).isEmpty)
  }

}
