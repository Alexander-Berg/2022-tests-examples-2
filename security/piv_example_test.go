package piv_test

import (
	"crypto"
	"crypto/rand"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"strings"

	"a.yandex-team.ru/security/libs/go/piv"
)

func Example_sign() {
	cards, err := piv.Cards()
	if err != nil {
		panic(err)
	}

	// Find a YubiKey and open the reader.
	var yk *piv.YubiKey
	for _, card := range cards {
		if !strings.Contains(strings.ToLower(card), "yubikey") {
			continue
		}

		if yk, err = piv.Open(card); err != nil {
			panic(err)
		}
		break
	}

	if yk == nil {
		panic("no yk, something very broken")
	}
	defer yk.Close()

	// Generate a private key on the YubiKey.
	key := piv.Key{
		Algorithm:   piv.AlgorithmEC256,
		PINPolicy:   piv.PINPolicyAlways,
		TouchPolicy: piv.TouchPolicyAlways,
	}
	pub, err := yk.GenerateKey(&piv.DefaultManagementKey, piv.SlotAuthentication, key)
	if err != nil {
		panic(err)
	}

	auth := piv.KeyAuth{PIN: piv.DefaultPIN}
	signer, err := yk.PrivateKey(piv.SlotAuthentication, pub, auth)
	if err != nil {
		panic(err)
	}

	data := sha256.Sum256([]byte("foo"))
	signature, err := signer.Sign(rand.Reader, data[:], crypto.SHA256)
	if err != nil {
		panic(err)
	}

	fmt.Printf("sign: %s\n", hex.EncodeToString(signature))
}
