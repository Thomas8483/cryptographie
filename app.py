from flask import Flask, request, redirect
import subprocess
import smtplib
import ssl
import random

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


def generate_validation_code():
    code = ""
    for i in range(6):
        code += str(random.randint(0, 9))
    return code


@app.route('/', methods=['GET', 'POST'])
def create_csr():
    print(request.form)
    if request.method == 'POST':
        request.environ['CONTENT_TYPE'] = 'application/json'
        name = request.form['name']
        email = request.form['email']
        country = request.form['country']
        state = request.form['state']
        city = request.form['city']
        org = request.form['org']
        unit = request.form['unit']
        cn = request.form['cn']

        liste_info.extend([name, email, country, state, city, org, unit, cn])

        # Envoi d'un code de vérification à l'adresse mail fournie
        # Connexion au serveur SMTP
        server = smtplib.SMTP_SSL(smtp_server, smtp_port, context=context)
        server.login(smtp_username, smtp_password)

        validation_code = generate_validation_code()
        liste_info.append(validation_code)
        body = "Vous avez fait une demande de CSR, le code de validation est " + validation_code
        message = f"Subject: {subject}\nFrom: {sender_email}\nTo: {email}\n\n{body}"
        server.sendmail(sender_email, email, message)
        server.quit()

        print("Code de vérification envoyé")

        return redirect('/static/verification.html')

    else:
        return '''
            <form method="post">
                <label for="name">Name:</label>
                <input type="text" id="name" name="name"><br><br>

                <label for="email">Email:</label>
                <input type="text" id="email" name="email"><br><br>

                <label for="country">Country:</label>
                <input type="text" id="country" name="country"><br><br>

                <label for="state">State:</label>
                <input type="text" id="state" name="state"><br><br>

                <label for="city">City:</label>
                <input type="text" id="city" name="city"><br><br>

                <label for="org">Organization:</label>
                <input type="text" id="org" name="org"><br><br>

                <label for="unit">Organizational Unit:</label>
                <input type="text" id="unit" name="unit"><br><br>

                <label for="cn">Common Name:</label>
                <input type="text" id="cn" name="cn"><br><br>

                <input type="submit" value="Submit">
            </form>
        '''


@app.route('/static/verification.html', methods=['POST'])
def verify():
    if request.method == 'POST':
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
        # Compare user_code with the validation_code generated earlier
        if user_code == validation_code:
            # Création du CSR
            cmd = f"./static/createCSR.sh '{name}' '{email}' '{country}' '{state}' '{city}' '{org}' '{unit}' '{cn}'"
            output = subprocess.check_output(cmd, shell=True)
            return output


if __name__ == '__main__':
    app.run()
