# -*- coding: utf-8 -*-
"""
@author: @bennyrock20
"""

import os

from datetime import date
from typing import List, Literal

import zeep
from OpenSSL import crypto
from jinja2 import Environment, PackageLoader, select_autoescape
from lxml import etree
from pydantic import BaseModel, constr
from signxml import DigestAlgorithm
from signxml.xades import (
    XAdESDataObjectFormat,
)

from .XAdESSigner import MyXAdESSigner

from .enum import (
    EnvironmentEnum,
    DocumentTypeEnum,
    EmmisionTypeEnum,
    TaxCodeEnum,
    PercentageTaxCodeEnum,
    UnitTimeEnum,
    PaymentMethodEnum,
    IdentificationTypeEnum,
)


class TaxItem(BaseModel):
    """
    Class for handling tax items
    """

    code: TaxCodeEnum
    tax_percentage_code: PercentageTaxCodeEnum
    additional_discount: str
    tarifa: str
    base: str
    value: str


class PaymentItem(BaseModel):
    """
    Class for handling payment items
    """

    payment_method: PaymentMethodEnum
    total: str
    terms: int
    unit_time: UnitTimeEnum


class LineItem(BaseModel):
    """
    Class for handling line items
    """

    code: str
    aux_code: str
    description: str
    quantity: str
    unit_price: str
    discount: str
    price_total_without_tax: str
    taxes: List[TaxItem]


class SRI(BaseModel):
    """
    Class for handling SRI functions
    """

    environment: EnvironmentEnum
    document_type: DocumentTypeEnum = DocumentTypeEnum.INVOICE
    matriz_address: str
    billing_name: constr(min_length=3, max_length=300)
    company_name: constr(min_length=3, max_length=300)
    company_ruc: constr(min_length=13, max_length=13)
    establishment: constr(min_length=3, max_length=3)
    point_emission: constr(min_length=3, max_length=3)
    company_address: str
    company_contribuyente_especial: str
    company_obligado_contabilidad: Literal["SI", "NO"]
    emission_date: date
    serie: constr(min_length=6, max_length=6)
    sequential: constr(min_length=9, max_length=9)
    numeric_code: constr(min_length=8, max_length=8)
    emission_type: EmmisionTypeEnum = EmmisionTypeEnum.NORMAL
    customer_billing_name: str
    customer_identification: str
    customer_identification_type: IdentificationTypeEnum
    customer_address: str
    taxes: List[TaxItem]
    payments: List[PaymentItem]
    lines_items: List[LineItem]
    total_without_tax: float
    total_discount: float
    tips: float
    grand_total: float
    certificate: str
    password: str

    def __init__(self, **data):
        super().__init__(**data)

    def __get_reception_url(self):
        """
        Function to get the url of receipt of invoices
        """
        if self.environment.value == "1":
            return "https://celcer.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl"
        elif self.environment.value == "2":
            return "https://cel.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl"

    def __get_authorization_url(self):
        """
        Function to get the url of authorization of invoices
        """
        if self.environment.value == "1":
            return "https://celcer.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl"
        elif self.environment.value == "2":
            return "https://cel.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl"

    def __get_access_key(self):
        """
        Function to generate the access key
        """
        code_number = str(self.numeric_code).zfill(8)

        key = (
                str(self.emission_date.strftime("%d%m%Y"))
                + str(self.document_type.value)
                + str(self.company_ruc)
                + str(self.environment.value)
                + str(self.establishment)
                + str(self.point_emission)
                + str(self.sequential)
                + str(code_number)
                + str(self.emission_type.value)
        )

        digit_verifier = SRI.generate_digit_verifier(key)

        return "{}{}".format(key, digit_verifier)

    @staticmethod
    def generate_digit_verifier(key):
        """
        Function to generate the verification digit
        """
        assert int(key), "The key must be an integer"

        x = len(key)
        factor = 2
        total = 0

        while x > 0:
            x = x - 1
            number = int(key[x: x + 1])
            total = total + (number * factor)

            if factor == 7:
                factor = 2
            else:
                factor = factor + 1

        module = total % 11
        validator = 11 - module

        if validator == 11:
            validator = 0

        if validator == 10:
            validator = 1

        return validator

    def get_xml(self):
        """
        Function to get the xml of the electronic invoice
        """

        loader = Environment(
            loader=PackageLoader("bill", "templates"), autoescape=select_autoescape()
        )

        access_key = self.__get_access_key()

        render = loader.get_template("factura_V1.1.0.xml").render(
            {
                "bill": self,
                "claveAcceso": access_key,
                "fechaEmision": self.emission_date.strftime("%d/%m/%Y"),
            }
        )

        return render.replace("\n", "")

    def get_xml_signed(self):
        """
        Function to sign the electronic invoice
        """

        p12 = crypto.load_pkcs12(open(self.certificate, "rb").read(), self.password.encode("utf-8"))

        # PEM formatted private key
        key = crypto.dump_privatekey(crypto.FILETYPE_PEM, p12.get_privatekey())

        # PEM formatted certificate
        cert = crypto.dump_certificate(crypto.FILETYPE_PEM, p12.get_certificate())

        data_object_format = XAdESDataObjectFormat(
            Description="contenido comprobante",
            MimeType="text/xml",
        )
        signer = MyXAdESSigner(
            data_object_format=data_object_format,
            c14n_algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315",
            signature_algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1",
            digest_algorithm=DigestAlgorithm.SHA1,

        )

        doc = self.get_xml().encode("utf-8")

        data = etree.fromstring(doc)

        signed_doc = signer.sign(
            data,
            key=key,
            cert=cert,
            reference_uri=["#comprobante"],
        )

        path_xml = os.path.join(os.getcwd(), 'signed.xml')
        with open(path_xml, 'w') as f:
            f.write(etree.tostring(signed_doc, pretty_print=True, encoding="unicode", method='xml'))

        return open(path_xml, 'r').read()

    def validate_sri(self):
        """
        Function to validate the electronic invoice in the SRI
        """

        client = zeep.Client(wsdl=self.__get_reception_url())
        # transform the xml to bytes
        xml = self.get_xml_signed().encode("utf-8")

        response = client.service.validarComprobante(xml)

        is_valid = response["estado"] == "RECIBIDA"

        return is_valid, response

    def get_authorization(self):
        """
        Function to get the authorization of the electronic invoice in the SRI
        """

        client = zeep.Client(wsdl=self.__get_authorization_url())

        access_key = self.__get_access_key()

        response = client.service.autorizacionComprobante(access_key)

        authorized = response["autorizaciones"]["autorizacion"][0]["estado"] == "AUTORIZADO"

        return authorized, response

    def get_qr(self):
        """
        Function to get the qr of the electronic invoice
        """
        pass
