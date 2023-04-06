import random
import smtplib
import ssl
import subprocess
import re

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
    return redirect('/home.html')


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
        id_certificate = request.form['Id']
        otp = request.form['OTP']

        liste_info_revoke.clear()
        liste_info_revoke.extend([email, id_certificate, otp])

        # Révoquer le certificat

        print("Certificat révoqué")

        return render_template('revoke_success.html')

    else:
        return render_template('revoke.html')


@app.route('/form.html', methods=['GET', 'POST'])
def formulaire():
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
        cn = request.form['CN']

        liste_info.clear()
        liste_info.extend([name, email, country, state, city, org, unit, cn])

        # Envoi d'un code de vérification à l'adresse mail fournie
        # Connexion au serveur SMTP
        server = smtplib.SMTP_SSL(smtp_server, smtp_port, context=context)
        server.login(smtp_username, smtp_password)

        validation_code = generate_validation_code()
        liste_info.append(validation_code)
        body = "Vous avez fait une CSR pour " + cn + ". \nLe code de validation est " + validation_code
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

            # Création du CSR
            cmd = f"./static/createCSR.sh '{name}' '{email}' '{country}' '{state}' '{city}' '{org}' '{unit}' '{cn}'"
            subprocess.check_output(cmd, shell=True)
            print("CSR créé")

            # Vérification du CSR
            csr_file = cn + ".csr"
            cmd = "openssl req -noout -subject -in {}".format(csr_file)
            subject_line = subprocess.check_output(cmd, shell=True).decode().strip()

            # Analyse du CSR
            matches = re.findall(r'/(\w+)=([\w.]+)', subject_line)
            dict_matches = dict(matches)

            # Comparaison du CSR et des valeurs demandées
            if all(value in dict_matches.values() for value in user_info):
                print("CSR correct")
            else:
                print("Erreur(s) dans le CSR")
                return render_template('error.html')

            # Création du CRT
            crt_file = cn + ".crt"
            cmd = "openssl x509 -req -in " + csr_file + " -CA ACI/intermediateCA.crt -CAkey ACI/intermediate.key -CAcreateserial -out " + crt_file + " -days 365 -sha256 -passin pass:" + "isen"
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
    certificate_name = liste_info[7] + ".crt"
    return send_file(certificate_name, as_attachment=True)


if __name__ == '__main__':
    app.run()
