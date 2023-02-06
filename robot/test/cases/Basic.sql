SELECT
	Host,
	Path,
	LastAccess,
	TextCRC,
	Acks::PageAcksUnpack(Acknowledgements) as Ack
FROM Input;
