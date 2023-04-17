import random
import smtplib
import ssl
import subprocess
import re
import zipfile

from flask import Flask, request, redirect, render_template, send_file

app = Flask(__name__, static_folder='static')

# Mail
sender_email = 'test13@mailfence.com'
smtp_server = 'smtp.mailfence.com'
smtp_port = 465
smtp_username = 'test13'
smtp_password = 'suwtov-zuFza6-mokhus'
context = ssl.create_default_context()
subject = "CSR"

liste_info = []
liste_info_revoke = []
user_info = []


def generate_validation_code():
    code = ""
    for i in range(6):
        code += str(random.randint(0, 9))
    return code


@app.route('/', methods=['GET'])
def main():
    return render_template('/home.html')


@app.route('/home.html', methods=['GET'])
def home():
    return render_template('home.html')


# TODO: Révoquer le certificat(Faire une liste de certificats valides(OCSP))
@app.route('/revoke.html', methods=['GET', 'POST'])
def revoke():
    print(request.form)
    if request.method == 'POST':
        request.environ['CONTENT_TYPE'] = 'application/json'
        email = request.form['Email']
        code = request.form['Code']
        reason = request.form['Reason']

        liste_info_revoke.clear()
        liste_info_revoke.extend([email, code, reason])
        find = False
        find_code = False

        # Ouvrir le flux de verification
        file = open("validation_codes.txt.txt", "r")
        for line in file:
            email_file, code_file = line.strip().split(", ")
            print(email_file + ", " + code_file)
            if email == email_file:
                find = True
                if code == code_file:
                    find_code = True

                    # Révoquer le certificat
                    #cmd =  f"openssl ca -config {config_file} -revoke {cert_file}"
                    #subprocess.check_output(cmd, shell=True)
                    print("Certificat révoqué")

                    # stockage de la revocation
                    file = open("revoke_list.txt", "a")
                    file.write(email + ", " + code + ", " + reason + "\n")
                    file.close()

                    return render_template('revoke_success.html')

                else:
                    print("Erreur : mauvais code saisie")

        if not find:
                print("Erreur : email sans correspondance")
                print("Erreur : Certificat non révoqué")
                return render_template('revoke_error.html')

        if not find_code:
            print("Erreur : code sans correspondance")
            print("Erreur : Certificat non révoqué")
            return render_template('revoke_error.html')

        file.close()





@app.route('/form.html', methods=['GET', 'POST'])
def form():
    print(request.form)
    if request.method == 'POST':
        request.environ['CONTENT_TYPE'] = 'application/json'
        name = request.form['Name']
        email = request.form['Email']
        country = request.form['Country']
        state = request.form['State']
        city = request.form['City']
        org = request.form['Organization']
        unit = request.form['Unit']
        cn = request.form['Email']

        liste_info.clear()
        liste_info.extend([name, email, country, state, city, org, unit, cn])

        # Envoi d'un code de vérification à l'adresse mail fournie
        # Connexion au serveur SMTP
        server = smtplib.SMTP_SSL(smtp_server, smtp_port, context=context)
        server.login(smtp_username, smtp_password)

        validation_code = generate_validation_code()
        liste_info.append(validation_code)
        body = "Vous avez fait une demande de certificat pour " + cn + ". \nLe code de validation est " + validation_code + ".\nConservez-le."
        message = f"Subject: {subject}\nFrom: {sender_email}\nTo: {email}\n\n{body}"
        server.sendmail(sender_email, email, message)
        server.quit()

        print("Code de vérification envoyé")

        return redirect('verification.html')

    else:
        return render_template('form.html')


@app.route('/verification.html', methods=['GET', 'POST'])
def verify():
    print(request.form)
    if request.method == 'POST':
        request.environ['CONTENT_TYPE'] = 'application/json'
        user_code = request.form['code']

        name = liste_info[0]
        email = liste_info[1]
        country = liste_info[2]
        state = liste_info[3]
        city = liste_info[4]
        org = liste_info[5]
        unit = liste_info[6]
        cn = liste_info[7]
        validation_code = liste_info[8]

        user_info.clear()
        user_info.extend([country, state, city, org, unit, cn])

        # Si l'utilisateur a saisi le bon code
        if user_code == validation_code:

            print("Code de validation correct")

            # Écriture du code de validation dans validations_codes.txt
            fichier = open("validation_codes.txt", "a")
            fichier.write(email + ", " + validation_code + "\n")
            fichier.close()

            # Création du CSR
            cmd = f"./static/createCSR.sh '{name}' '{email}' '{country}' '{state}' '{city}' '{org}' '{unit}' '{cn}'"
            subprocess.check_output(cmd, shell=True)
            print("CSR créé")

            # Vérification du CSR
            csr_file = cn + ".csr"
            cmd = "openssl req -noout -subject -in {}".format(csr_file)
            subject_line = subprocess.check_output(cmd, shell=True).decode().strip()

            # Analyse du CSR
            matches = re.findall(r'/(\w+)=([\w.@\s-]+)', subject_line)
            print(matches)
            dict_matches = dict(matches)

            # Comparaison du CSR et des valeurs demandées
            if all(value in dict_matches.values() for value in user_info):
                print("CSR correct")
            else:
                print("Erreur(s) dans le CSR")
                return render_template('error.html')

            # Création du CRT
            crt_file = "certs/" + cn + ".crt"
            cmd = "openssl x509 -req -in " + csr_file + " -CA ACI/intermediate_ca.crt -CAkey ACI/intermediate_ca.key -CAcreateserial -out " + crt_file + " -days 365 -sha256 -passin pass:" + "isen"
            subprocess.check_output(cmd, shell=True)

            print("CRT créé")

            return render_template('success.html')

        else:
            print("Code de vérification erroné")
            return render_template('error.html')

    else:
        return render_template('verification.html')


@app.route('/download', methods=['GET'])
def download():
    key_name = liste_info[7] + ".key"
    certificate_name = liste_info[7] + ".crt"
    archive_name = "key_and_certificate.zip"

    # Création de l'archive contenant le certificat de l'utilisateur, sa paire de clé, l'ACR, l'ACI
    with zipfile.ZipFile(archive_name, mode='w') as myzip:
        myzip.write(certificate_name, certificate_name)
        myzip.write(key_name, key_name)
        myzip.write("ACR/root_ca.crt", "root_ca.crt")
        myzip.write("ACI/intermediate_ca.crt", "intermediate_ca.crt")
        myzip.close()

    print("ZIP envoyé")

    return send_file(archive_name, as_attachment=True)


if __name__ == '__main__':
    app.run()
