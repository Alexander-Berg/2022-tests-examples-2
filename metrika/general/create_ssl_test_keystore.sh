#!/bin/bash

# Author: Styopochkin

KEY_DIR=.
PKEY_FILE=$KEY_DIR/test_pk.key
CERT_FILE=$KEY_DIR/test.cer
# keystore file should be the same as specified for "sslConnector.keystore" property
KEY_STORE_FILE=$KEY_DIR/test.keystore
PKCS12_FILE=/tmp/$RANDOM

# this password should be the same as specified for "sslConnector.keyPassword" property
read -s -p "Enter destination keystore password: " KS_PASS
echo

echo "Generate PKCS12"
openssl pkcs12 -inkey $PKEY_FILE -passin pass:test -in $CERT_FILE -export -out $PKCS12_FILE -password pass:$KS_PASS
echo "Import PKCS12 into keystore"
keytool -importkeystore -srckeystore $PKCS12_FILE -srcstorepass $KS_PASS -srcstoretype PKCS12 \
  -destkeystore $KEY_STORE_FILE -deststorepass $KS_PASS -noprompt
rm $PKCS12_FILE