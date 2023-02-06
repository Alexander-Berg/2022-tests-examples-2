package nuvault_test

import (
	"context"
	"fmt"

	"a.yandex-team.ru/security/gideon/nuvault/pkg/nuvault"
)

func Example_simple() {
	nuc, err := nuvault.NewClient(nuvault.WithMutualAuth("/etc/certs/capi.pem"))
	if err != nil {
		panic(err)
	}
	defer func() { _ = nuc.Close() }()

	secret, err := nuc.GetSecret(context.TODO(), "sec-01ehmc9y69bjkb03wjcxdkn86w")
	if err != nil {
		panic(err)
	}

	fmt.Printf("secret_uid=%q: %s", secret.SecretUuid, secret.Values["some_key"])
}
