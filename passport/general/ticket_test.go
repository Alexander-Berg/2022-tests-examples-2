package tvmcontext

import (
	"errors"
	"testing"
)

const (
	testTicket1 = "3:serv:CgYIDRCUkQYQDBgcIgdiYjpzZXNzIghiYjpzZXNzMg:ERmeH_yzC7K_QsoHTyw7llCsyExEz3CoEopPIuivA0ZAtTaFq_Pa0l9Fhhx_NX9WpOp2CPyY5cFc4PXhcO83jCB7-EGvHNxGN-j2NQalERzPiKqkDCO0Q5etLzSzrfTlvMz7sXDvELNBHyA0PkAQnbz4supY0l-0Q6JBYSEF3zOVMjjE-HeQIFL3ats3_PakaUMWRvgQQ88pVdYZqAtbDw9PlTla7ommygVZQjcfNFXV1pJKRgOCLs-YyCjOJHLKL04zYj0X6KsOCTUeqhj7ml96wLZ-g1X9tyOR2WAr2Ctq7wIEHwqhxOLgOSKqm05xH6Vi3E_hekf50oe2jPfKEA"

	testTicket3          = "3:serv:CM0PELvKidAFIgcIyYp6EN8B:OsBR9E9tg_p6QbQt6EAaNluWZhJvidyr16fBf__QSxzuX9zLAOersvipSxHkQg_2_QoQGp3v3pL5SgZvyo2TqV06c01PaeZsmletxExPXu_7W68Y2X0nSwnUTTTMkNEISYvHEWIKvfbBnxMcgMQpfZpHImb52dq-_6Fsi7HkWrg"
	testTicket3Msg       = "3:serv:CM0PELvKidAFIgcIyYp6EN8B:"
	testTicket3Signature = "OsBR9E9tg_p6QbQt6EAaNluWZhJvidyr16fBf__QSxzuX9zLAOersvipSxHkQg_2_QoQGp3v3pL5SgZvyo2TqV06c01PaeZsmletxExPXu_7W68Y2X0nSwnUTTTMkNEISYvHEWIKvfbBnxMcgMQpfZpHImb52dq-_6Fsi7HkWrg"
	testTicket3Proto     = "CM0PELvKidAFIgcIyYp6EN8B"
)

func TestTicketsErrs(t *testing.T) {
	if _, err := parseFromStr(testTicket1); err == nil {
		t.Fatal(err)
	}

	if _, err := parseFromStr("12:2345"); err != errorMalformed {
		t.Fatal(err)
	}
	if _, err := parseFromStr("1:usr:1234:234"); err != errorUnsupportedVersion {
		t.Fatal(err)
	}
	if _, err := parseFromStr("3:usr:1234:234"); err != errorUnsupportedType {
		t.Fatal(err)
	}
	if _, err := parseFromStr("3:user:++++:234"); err != errorInvalidBase64 {
		t.Fatal(err)
	}
	if _, err := parseFromStr("3:user:asdf:234"); err != errorInvalidProtobuf {
		t.Fatal(err)
	}
	if _, err := parseFromStr("3:serv:CAsQ__________9_Gg4KAgh7EHsg0oXYzAQoAA:N8"); err != errorWrongTicketTypeSrv {
		t.Fatal(err)
	}
	if _, err := parseFromStr("3:user:CM0PELvKidAFIgcIyYp6EN8B:Os"); err != errorWrongTicketTypeUsr {
		t.Fatal(err)
	}
	if _, err := parseFromStr("3:serv:CAAQACIFCHsQyAM:Os"); err != errorMissingKeyid {
		t.Fatal(err)
	}
	if _, err := parseFromStr("3:serv:CCoQACIFCHsQyAM:Os"); err != errorMissingExpTime {
		t.Fatal(err)
	}
}

func TestParseFromStrFields(t *testing.T) {
	parsed, err := parseFromStr(testTicket3)
	if err != nil {
		t.Fatal(err)
	}

	if parsed.Msg != testTicket3Msg {
		t.Fatal(errors.New("incorrect msg"))
	}

	if parsed.Signature != testTicket3Signature {
		t.Fatal(errors.New("incorrect signature"))
	}

	if parsed.Type != TicketTypeServiceTicket {
		t.Fatal(errors.New("incorrect ticket type"))
	}

	if parsed.Version != TvmTicketsVersion3 {
		t.Fatal(errors.New("incorrect ticket version"))
	}

	if parsed.Proto != testTicket3Proto {
		t.Fatal(errors.New("incorrect ticket proto"))
	}

	if parsed.Ticket == nil {
		t.Fatal(errors.New("incorrect protobuf"))
	}

	if parsed.Ticket.Service == nil {
		t.Fatal(errors.New("incorrect protobuf"))
	}
}
