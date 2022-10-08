import subprocess
from typing import List, TypedDict

"""
References: https://www.youtube.com/watch?v=VH4gXcvkmOY&ab_channel=TheDigitalLife
"""


class ExtFileProps(TypedDict):
    cn: str
    distinguished_name: str
    subjectAltName: List[str]


def generate_local_ssl(location, extfile_props: ExtFileProps):
    rsa_command_resp = subprocess.run(
        ["openssl", "genrsa", "-aes256", "-out", "ca-key.pem", "4096"], text=True
    )
    if rsa_command_resp.stderr:
        raise Exception("Error generating rsa")

    # Generate a public CA Cert
    cert_command_resp = subprocess.run(
        [
            "openssl",
            "req",
            "-new",
            "-x509",
            "-days",
            "365",
            "-key",
            "ca-key.pem",
            "-sha256",
            "-out",
            "ca.pem",
        ],
        text=True,
    )
    if cert_command_resp.stderr:
        raise Exception("Error generating cert")

    # Generate a private key
    key_command_resp = subprocess.run(
        ["openssl", "genrsa", "-out", "server-key.pem", "4096"], text=True
    )
    if key_command_resp.stderr:
        raise Exception("Error generating key")

    # Generate a CSR
    csr_command_resp = subprocess.run(
        [
            "openssl",
            "req",
            "-subj",
            "/CN=localhost",
            "-sha256",
            "-new",
            "-key",
            "server-key.pem",
            "-out",
            "server.csr",
        ],
        text=True,
    )
    if csr_command_resp.stderr:
        raise Exception("Error generating csr")

    # Generate a extfile
    with open("extfile.cnf", "w") as f:
        subjectAltName = ",".join(extfile_props["subjectAltName"])
        f.write(
            "\n".join(
                [
                    "[dn]",
                    f"CN={extfile_props['cn']}",
                    "[req]",
                    f"distinguished_name = {extfile_props['distinguished_name']}",
                    "[EXT]",
                    f"subjectAltName={subjectAltName}",
                    "keyUsage=digitalSignature",
                    "extendedKeyUsage=serverAuth",
                ]
            )
        )

    # Generate a cert
    cert_command_resp = subprocess.run(
        [
            "openssl",
            "x509",
            "-req",
            "-days",
            "365",
            "-sha256",
            "-in",
            "server.csr",
            "-CA",
            "ca.pem",
            "-CAkey",
            "ca-key.pem",
            "-CAcreateserial",
            "-out",
            "server-cert.pem",
            "-extfile",
            "extfile.cnf",
        ],
        text=True,
    )
    if cert_command_resp.stderr:
        raise Exception("Error generating cert")

    # verify the cert
    verify_command_resp = subprocess.run(
        ["openssl", "verify", "-CAfile", "ca.pem", "server-cert.pem"], text=True
    )
    if verify_command_resp.stderr:
        raise Exception("Error verifying cert")

    # Move the files to the location
    mv_command_resp = subprocess.run(
        [
            "mv",
            "ca.pem",
            "ca-key.pem",
            "server-cert.pem",
            "server-key.pem",
            "server.csr",
            "ca.srl",
            "extfile.cnf",
            location,
        ],
        text=True,
    )
    if mv_command_resp.stderr:
        raise Exception("Error moving files")


def add_cert_to_windows(cert_location):
    certutil_command_resp = subprocess.run(
        ["certutil", "-addstore", "-f", "Root", cert_location], text=True
    )
    if certutil_command_resp.stderr:
        raise Exception("Error adding cert to windows")


def add_cert_to_linux(cert_location):
    sudo_command_resp = subprocess.run(
        ["sudo", "cp", cert_location, "/usr/local/share/ca-certificates/"], text=True
    )
    if sudo_command_resp.stderr:
        raise Exception("Error adding cert to linux")

    sudo_command_resp = subprocess.run(["sudo", "update-ca-certificates"], text=True)
    if sudo_command_resp.stderr:
        raise Exception("Error adding cert to linux")


generate_local_ssl(
    "/media/jadson/drive/jadson/docker/traefik/local-ssl",
    {
        "cn": "localhost",
        "distinguished_name": "dn",
        "subjectAltName": ["DNS:localhost", "IP:192.168.50.171"],
    },
)
