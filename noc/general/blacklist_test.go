package cauth

import (
	"testing"
)

func TestIsRestrictedProjectID(t *testing.T) {

	restrictedProjectIDs = map[uint32]bool{0x80004096: true}
	restrictedMacros = map[string]bool{"_VAULTNETS_": true}

	if !IsRestrictedProjectID(0x80004096) {
		t.Errorf("0x80004096 is restricted, please check out PUNCHER-1011")
		t.Fail()
	}

	if IsRestrictedProjectID(0x696) {
		t.Errorf("0x696 should not be restricted")
		t.Fail()
	}

	if !IsRestrictedMacros("_VAULTNETS_") {
		t.Errorf("_VAULTNETS_ is restricted, please check out PUNCHER-1011")
		t.Fail()
	}

	if IsRestrictedMacros("_SEARCHSAND_") {
		t.Errorf("_SEARCHSAND_ should not be restricted")
		t.Fail()
	}
}
