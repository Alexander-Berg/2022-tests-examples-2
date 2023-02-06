package ad_etl.layer.yt.dds;


import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;

import java.util.stream.Stream;

import static org.junit.jupiter.api.Assertions.assertEquals;


public class FctCaPerformanceEventTest {

   @ParameterizedTest
   @MethodSource
   public void getBrandFromService(String service, String expected) {
      assertEquals(expected, FctCaPerformanceEvent.getBrandFromService(service));
   }

   private static Stream<Arguments> getBrandFromService() {
      return Stream.of(
              Arguments.of(null, null),
              Arguments.of("uber", "uber"),
              Arguments.of("  uber  ", "uber"),
              Arguments.of("hello  uber", "uber"),
              Arguments.of("uber foo", "uber"),
              Arguments.of("uber foo", "uber"),
              Arguments.of("yandex", "yandex"),
              Arguments.of("yango", "yandex"),
              Arguments.of("foo", "unknown")
      );
   }

   @ParameterizedTest
   @MethodSource
   public void fixBrand(String brand, String expected) {
      assertEquals(expected, FctCaPerformanceEvent.fixBrand(brand));
   }

   private static Stream<Arguments> fixBrand() {
      return Stream.of(
              Arguments.of(null, "unknown"),
              Arguments.of("yango", "yandex"),
              Arguments.of("foo", "foo")
      );
   }

}
