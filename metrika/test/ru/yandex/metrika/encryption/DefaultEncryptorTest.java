package ru.yandex.metrika.encryption;

import org.junit.Test;

import ru.yandex.metrika.util.PasswordUtils;

import static org.junit.Assert.assertEquals;

public class DefaultEncryptorTest {

    private Encryptor encryptor = new DefaultEncryptor();

    @Test
    public void encryptDecryptTest() {
        String originValue = "секретное значение";
        String password = PasswordUtils.generatePassword(32);
        String salt = PasswordUtils.generatePassword(16);
        byte[] iv = PasswordUtils.randomBytes(16);

        String encryptedValue = encryptor.encrypt(originValue, password, salt, iv);
        String decryptedValue = encryptor.decrypt(encryptedValue, password, salt, iv);
        assertEquals(originValue, decryptedValue);
    }
}
