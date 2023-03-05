
from base64 import b64encode

from OpenSSL.crypto import FILETYPE_ASN1, FILETYPE_PEM, X509, dump_certificate, load_certificate
from lxml.etree import SubElement
from signxml import XMLSigner
from signxml.util import SigningSettings, add_pem_header, ds_tag, xades_tag
from signxml.xades import (
    XAdESSigner,
)


class MyXAdESSigner(XAdESSigner, XMLSigner):

    def _add_reference_to_signed_info(self, sig_root, node_to_reference):
        signed_info = self._find(sig_root, "SignedInfo")
        reference = SubElement(signed_info, ds_tag("Reference"), nsmap=self.namespaces)
        reference.set("URI", f"#{node_to_reference.get('Id')}")
        reference.set("Type", "http://uri.etsi.org/01903#SignedProperties")
        reference.set("Id", f"Reference-{node_to_reference.get('Id')}")
        SubElement(reference, ds_tag("DigestMethod"), nsmap=self.namespaces, Algorithm=self.digest_alg.value)
        digest_value_node = SubElement(reference, ds_tag("DigestValue"), nsmap=self.namespaces)
        node_to_reference_c14n = self._c14n(node_to_reference, algorithm=self.c14n_alg)
        digest = self._get_digest(node_to_reference_c14n, algorithm=self.digest_alg)
        digest_value_node.text = b64encode(digest).decode()

    def add_signing_certificate(self, signed_signature_properties, sig_root, signing_settings: SigningSettings):
        signing_cert_v2 = SubElement(
            signed_signature_properties, xades_tag("SigningCertificate"), nsmap=self.namespaces
        )
        for cert in signing_settings.cert_chain:  # type: ignore
            if isinstance(cert, X509):
                loaded_cert = cert
            else:
                loaded_cert = load_certificate(FILETYPE_PEM, add_pem_header(cert))
            der_encoded_cert = dump_certificate(FILETYPE_ASN1, loaded_cert)
            cert_digest_bytes = self._get_digest(der_encoded_cert, algorithm=self.digest_alg)
            cert_node = SubElement(signing_cert_v2, xades_tag("Cert"), nsmap=self.namespaces)
            cert_digest = SubElement(cert_node, xades_tag("CertDigest"), nsmap=self.namespaces)
            SubElement(cert_digest, ds_tag("DigestMethod"), nsmap=self.namespaces, Algorithm=self.digest_alg.value)
            digest_value_node = SubElement(cert_digest, ds_tag("DigestValue"), nsmap=self.namespaces)
            digest_value_node.text = b64encode(cert_digest_bytes).decode()

            # Issue Serial V2
            issuer_serial_v2 = SubElement(cert_node, xades_tag("IssuerSerial"), nsmap=self.namespaces)

            # Add Issuer Name
            issuer_name = SubElement(issuer_serial_v2, ds_tag("X509IssuerName"), nsmap=self.namespaces)

            issuer_name_bytes = loaded_cert.get_issuer()

            cn = issuer_name_bytes.__getattr__("CN")
            ou = issuer_name_bytes.__getattr__("OU")
            o = issuer_name_bytes.__getattr__("O")
            c = issuer_name_bytes.__getattr__("C")

            issuer_name.text = f"CN={cn},OU={ou},O={o},C={c}"

            # Add Issuer Serial Number
            issuer_serial_number = loaded_cert.get_serial_number()
            issuer_name = SubElement(issuer_serial_v2, ds_tag("X509SerialNumber"), nsmap=self.namespaces)
            issuer_name.text = str(issuer_serial_number)

    def check_deprecated_methods(self):
        pass