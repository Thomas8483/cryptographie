from flask import Flask, request
import subprocess

app = Flask(__name__, static_folder='static')


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
