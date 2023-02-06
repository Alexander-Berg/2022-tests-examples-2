package tvmapi

import (
	"testing"
)

func TestCrypto(t *testing.T) {
	ts := "100500"
	dst := "15,85"
	secret := "6zQnNi5BpraJplR-EFtfVA"
	actualSign, err := signRequest(ts, dst, secret)
	if err != nil {
		t.Fatal(err)
	}

	expectedSign := "XAcYCIajePAYi8QYhXCQasOkcr0-CjVBrJ2IfJyrGyI"

	if expectedSign != actualSign {
		t.Fatal("Expected sign: " + expectedSign + ". Actual: " + actualSign)
	}

	if _, err := signRequest(ts, dst, "   "); err != errorSecretDecode {
		t.Fatalf("signRequest: %s", err)
	}
}
