import zipfile
key_name = "test13@mailfence.com.key"
certificate_name = "test13@mailfence.com.crt"
archive_name = "key_and_certificate.zip"

# Création de l'archive qui contient les deux fichiers
with zipfile.ZipFile(archive_name, mode="w") as myzip:
    myzip.write(certificate_name, certificate_name)
    myzip.write(key_name, key_name)
    myzip.close()

print("ZIP envoyé")
