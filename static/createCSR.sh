#!/bin/bash

name=$1
email=$2
country=$3
state=$4
city=$5
org=$6
unit=$7
cn=$8

# Génération de la paire de clé
openssl genpkey -algorithm RSA -out $cn.key -aes256 -pass pass:"isen"

# Génération du CSR
openssl req -new -key $cn.key -out $cn.csr -subj "/emailAddress=$email/CN=$cn/O=$org/OU=$unit/C=$country/ST=$state/L=$city" -passin pass:"isen"
