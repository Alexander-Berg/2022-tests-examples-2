package softattest

func NewAttestator(priv, pub []byte, userName, machineID func() (string, error)) *Attestator {
	out := newAttestator(priv, pub)
	if userName != nil {
		out.username = userName
	}

	if machineID != nil {
		out.machineID = machineID
	}

	return out
}
