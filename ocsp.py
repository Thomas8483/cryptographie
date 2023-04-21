import subprocess
import multiprocessing
import time


# Define a function to start the OCSP responder as a separate process
def start_ocsp_responder():
    # Run the openssl ocsp command to start the OCSP responder
    subprocess.run(["openssl", "ocsp", "-port", "8888", "-index", "OCSP/index.txt", "-rsigner", "OCSP/ocsp.crt", "-rkey", "OCSP/ocsp.key", "-CA", "ACI_old/intermediate_ca.crt", "-ndays", "365"])


def send_ocsp_request():
    cmd = "openssl ocsp -issuer chain.crt -cert certs/test13@mailfence.com.crt -text -url http://localhost:8888"
    output = subprocess.Popen(cmd, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # Use communicate() to capture the output and error streams
    stdout, stderr = output.communicate()
    print(stdout)
    print(stderr)
    print("Requete envoyee")

start_ocsp_responder()

# if __name__ == '__main__':
#     # Check if the script is being run as a frozen executable
#     if hasattr(multiprocessing, 'freeze_support'):
#         multiprocessing.freeze_support()
#
#     # Start the OCSP responder in a separate process
#     ocsp_process = multiprocessing.Process(target=start_ocsp_responder)
#     ocsp_process.start()
#
#     # Sleep for a short duration to allow the OCSP responder to start
#     time.sleep(2)
#
#     # Call the function to send OCSP request
#     send_ocsp_request()
#
#     # Wait for the OCSP responder process to complete
#     ocsp_process.join()
