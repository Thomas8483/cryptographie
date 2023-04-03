from flask import Flask, request
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


def generate_validation_code():
    code = ""
    for i in range(6):
        code += str(random.randint(0, 9))
    return code


@app.route('/', methods=['GET', 'POST'])
def create_csr():
    print(request)
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

        # Envoi d'un code de vérification à l'adresse mail fournie

        # Connexion au serveur SMTP
        server = smtplib.SMTP_SSL(smtp_server, smtp_port, context=context)
        server.login(smtp_username, smtp_password)

        validation_code = generate_validation_code()
        body = "Vous avez fait une demande de CSR, le code de validation est " + validation_code
        message = f"Subject: {subject}\nFrom: {sender_email}\nTo: {email}\n\n{body}"
        server.sendmail(sender_email, email, message)
        server.quit()

        print("Code de vérification envoyé")

        # Création du CSR
        cmd = f"./static/createCSR.sh '{name}' '{email}' '{country}' '{state}' '{city}' '{org}' '{unit}' '{cn}'"
        output = subprocess.check_output(cmd, shell=True)
        return output
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


if __name__ == '__main__':
    app.run()
