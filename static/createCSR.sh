#!/bin/bash

if [ "$REQUEST_METHOD" == "POST" ]; then
  read -n $CONTENT_LENGTH POST_DATA <&0
  QUERY_STRING=$POST_DATA
fi

# Parse the form data from the QUERY_STRING
name=$(echo $QUERY_STRING | sed -n 's/^.*name=\([^&]*\).*$/\1/p' | sed "s/%20/ /g")
email=$(echo $QUERY_STRING | sed -n 's/^.*email=\([^&]*\).*$/\1/p' | sed "s/%40/@/g" | sed "s/%20/ /g")
country=$(echo $QUERY_STRING | sed -n 's/^.*country=\([^&]*\).*$/\1/p' | sed "s/%20/ /g")
state=$(echo $QUERY_STRING | sed -n 's/^.*state=\([^&]*\).*$/\1/p' | sed "s/%20/ /g")
city=$(echo $QUERY_STRING | sed -n 's/^.*city=\([^&]*\).*$/\1/p' | sed "s/%20/ /g")
org=$(echo $QUERY_STRING | sed -n 's/^.*org=\([^&]*\).*$/\1/p' | sed "s/%20/ /g")
unit=$(echo $QUERY_STRING | sed -n 's/^.*unit=\([^&]*\).*$/\1/p' | sed "s/%20/ /g")
cn=$(echo $QUERY_STRING | sed -n 's/^.*cn=\([^&]*\).*$/\1/p' | sed "s/%20/ /g")

openssl genpkey -algorithm RSA -out $cn.key -aes256

# Use the form data to create the CSR using openssl req
openssl req -new -key $cn.key -out $cn.csr -subj "/C=$country/ST=$state/L=$city/O=$org/OU=$unit/CN=$cn" -passout pass:""

# Output the CSR to the response
echo "Content-type: text/plain"
echo ""
cat $cn.csr

