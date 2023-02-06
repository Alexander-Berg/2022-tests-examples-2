package fwimport

import (
	"fmt"
	"io/ioutil"
	"os"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestFormatWhereExpression(t *testing.T) {
	filename := "test_slbfw.tar.gz"
	f, err := os.Open(filename)
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
	defer f.Close()
	data, err := ioutil.ReadAll(f)

	if err != nil {
		t.Fatalf("unable to read %v", filename)
	}
	content, err := ExtractFile(data, "slbfw-cvs/services.yaml")
	if err != nil {
		t.Fatalf("unable to read %v", filename)
	}
	if len(content) == 0 {
		t.Fatalf("empty result %v", filename)
	}

	servicesData, err := parseSlbFwServices(content)
	if err != nil {
		t.Fatalf("parseSlbFwServices %v", err)
	}
	assert.Len(t, servicesData, 9, "wrong lenпер")
}
