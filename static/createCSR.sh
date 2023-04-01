#!/bin/bash


# Parse the form data from the QUERY_STRING
name=$1
email=$2
country=$3
state=$4
city=$5
org=$6
unit=$7
cn=$8

openssl genpkey -algorithm RSA -out $cn.key -aes256 -pass pass:"isen"

# Use the form data to create the CSR using openssl req
#openssl req -new -key $cn.key -out $cn.csr -subj "/C=$country/ST=$state/L=$city/O=$org/OU=$unit/CN=$cn" -passout pass:"isen"
