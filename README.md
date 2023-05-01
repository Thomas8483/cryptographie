<div align="center">
  <h1>Certificate creation</h1>
  <p>
    <strong>A website to create x509 certificates</strong>
  </p>
</div>


Download your certificate in .crt and your key pair generated with our intermediate certification authority.

## Documentation

- ACR/ contains all the files related to the root Certificaton Authority.
- ACI/ contains all the files related to the intermediate Certificaton Authority.
- templates/ contains the HTML.
- static contains the CSS and the createCSR script used by our server.


## Using

Open a terminal within the "cryptographie" folder:

```bash
python3 app.py
```
Connect to http://127.0.0.1:5000 with a Web browser

- Fill in the form:
  - The email field is used to send the verification code.
  - The common name one is the name which will be certified.

## Collaborators

- Thomas JAXEL
- Hugo SAVY
