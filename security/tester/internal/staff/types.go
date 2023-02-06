package staff

type Key struct {
	Fingerprint string `json:"fingerprint_sha256"`
}

type staffErrResult struct {
	Msg string `json:"error_message"`
}
