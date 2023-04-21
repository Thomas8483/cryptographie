import random
import smtplib
import ssl
import subprocess
import re
import zipfile

from flask import Flask, request, redirect, render_template, send_file

app = Flask(__name__, static_folder='static')

# Mail
sender_email = 'projetcrypto1@mailfence.com'
smtp_server = 'smtp.mailfence.com'
smtp_port = 465
smtp_username = 'projetcrypto1'
smtp_password = 'doqro3-Roqtis-coxvop'
context = ssl.create_default_context()
subject = "CSR"

liste_info = []
liste_info_revoke = []
user_info = []


def ocsp_launch():
    cmd = f"openssl ocsp -port 8888 -index OCSP/index.txt -rsigner OCSP/ocsp.crt -rkey OCSP/ocsp.key -CA ACI_old/intermediate_ca.crt -ndays 365"
    subprocess.check_output(cmd, shell=True)
    print("Serveur OSCP: lancé")


def ocsp_revokation():
    cmd = f"openssl ca -config openssl.cnf -revoke"
    subprocess.check_output(cmd, shell=True)
    print("Serveur OSCP: revocation effectué")


def ocsp_renew():
    cmd = f"openssl ca -config openssl.cnf -renew -keyfile server.key -cert server.crt -out new_server.crt"
    subprocess.check_output(cmd, shell=True)
    print("Serveur OSCP: renouvellement effectué")


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

        # Ouvrir le flux de vérification
        file = open("validation_codes.txt", "r")

        for line in file:
            email_file, code_file = line.strip().split(", ")
            print(email_file + ", " + code_file)
            if email == email_file:
                find = True
                print("Email trouvé")
                if code == code_file:
                    find_code = True
                    print("Code de validation correct")

                    certificate_name = "certs/" + email + ".crt"

                    # Ouvre le serveur de l'OCSP
                    cmd = f"openssl ocsp -port 8888 -index OCSP/index.txt -rsigner OCSP/ocsp.crt -rkey OCSP/ocsp.key -CA ACI_old/intermediate_ca.crt -ndays 365"
                    subprocess.check_output(cmd, shell=True)
                    print("Serveur OSCP lancé")

                    print("Certificat révoqué")

                    # Stockage de la revocation
                    file = open("revoke_list.txt", "a")
                    file.write(email + ", " + code + ", " + reason + "\n")
                    file.close()

                    return render_template('revoke_success.html')

                else:
                    print("Faux code de validation")

        if not find or not find_code:
            return render_template('revoke_error.html')

        file.close()

    else:
        return render_template('revoke.html')


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

        # TODO: a tester
        if user_code == validation_code and validation_code.isdigit():

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
            cmd = "openssl x509 -req -in " + csr_file + " -CA ACI_old/intermediate_ca.crt -CAkey ACI_old/intermediate_ca.key -CAcreateserial -out " + crt_file + " -days 365 -sha256 -passin pass:" + "isen"
            subprocess.check_output(cmd, shell=True)

            # TODO: Ajouter le certificat créé dans l'OCSP
            cmd = "OCSP/ocsp.sh"

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
    certificate_name = "certs/" + liste_info[7] + ".crt"
    archive_name = "key_and_certificate.zip"

    # Création de l'archive contenant le certificat de l'utilisateur, sa paire de clé, l'ACR, l'ACI_old
    with zipfile.ZipFile(archive_name, mode='w') as myzip:
        myzip.write(certificate_name, certificate_name)
        myzip.write(key_name, key_name)
        myzip.write("ACR/root_ca.crt", "root_ca.crt")
        myzip.write("ACI_old/intermediate_ca.crt", "intermediate_ca.crt")
        myzip.close()

    print("ZIP envoyé")

    return send_file(archive_name, as_attachment=True)


if __name__ == '__main__':
    app.run()
