package ru.yandex.metrika.cdp.proto;

import java.time.Instant;
import java.time.LocalDate;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

import org.junit.Test;

import ru.yandex.metrika.cdp.dto.core.Client;
import ru.yandex.metrika.cdp.dto.core.ClientType;
import ru.yandex.metrika.cdp.dto.core.EntityStatus;
import ru.yandex.metrika.util.StringUtil;

import static org.junit.Assert.assertEquals;

public class ClientProtoSerializerTest {

    @Test
    public void testE2E() {
        Set<String> emails = Set.of("test@example.com", "test@yandex.ru");
        Set<String> emailsMd5 = emails.stream()
                .map(StringUtil::stringMd5)
                .collect(Collectors.toSet());
        Set<String> phones = Set.of("+79001000000", "+79002000000", "+79003000000");
        Set<String> phonesMd5 = phones.stream()
                .map(StringUtil::stringMd5)
                .collect(Collectors.toSet());

        var client = new Client(
                1,
                2,
                "externalHardId",
                "Bob",
                LocalDate.now().minusDays(10),
                Instant.now().minusMillis(TimeUnit.DAYS.toMillis(10)),
                Instant.now().minusMillis(TimeUnit.DAYS.toMillis(5)),
                Set.of(1L, 2L, 3L, -1L),
                Set.of("client_user_id", "test"),
                emails,
                phones,
                emailsMd5,
                phonesMd5,
                EntityStatus.ACTIVE,
                Map.of("test", Set.of("val1", "val2")),
                ClientType.CONTACT,
                null
        );

        var serializer = new ClientProtoSerializer();

        assertEquals(client, serializer.deserialize(serializer.serialize(client)));
    }

}
