# -*- coding: utf-8 -*-
"""
@author: @bennyrock20
"""

import base64
import os
from datetime import date, datetime
from io import BytesIO

import zeep
from OpenSSL import crypto
from barcode import Code39
from barcode.writer import SVGWriter
from jinja2 import Environment, select_autoescape, FileSystemLoader
from lxml import etree
from pydantic import BaseModel, constr
from signxml import DigestAlgorithm
from signxml.xades import (
    XAdESDataObjectFormat,
)
from typing import List, Optional

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

from weasyprint import HTML

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

loader = FileSystemLoader(
    [os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")]
)

loader = Environment(loader=loader, autoescape=select_autoescape())


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
    total_price: str


class SRI(BaseModel):
    """
    Class for handling SRI functions
    """

    environment: EnvironmentEnum
    document_type: DocumentTypeEnum = DocumentTypeEnum.INVOICE
    main_address: str
    logo: str
    billing_name: constr(min_length=3, max_length=300)
    company_name: constr(min_length=3, max_length=300)
    company_ruc: constr(min_length=13, max_length=13)
    company_phone: Optional[str] = None
    customer_email: Optional[str] = None
    establishment: constr(min_length=3, max_length=3)
    point_emission: constr(min_length=3, max_length=3)
    company_address: str
    company_contribuyente_especial: str
    company_obligado_contabilidad: Literal["SI", "NO"]
    emission_date: date
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

    def get_serie(self):
        """
        Function to get the serie
        """
        return "{}{}".format(self.establishment, self.point_emission)

    def get_access_key(self):
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
            number = int(key[x : x + 1])
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
        access_key = self.get_access_key()

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

        p12 = crypto.load_pkcs12(
            open(self.certificate, "rb").read(), self.password.encode("utf-8")
        )

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

        path_xml = os.path.join(os.getcwd(), "signed.xml")
        with open(path_xml, "w") as f:
            f.write(
                etree.tostring(
                    signed_doc, pretty_print=True, encoding="unicode", method="xml"
                )
            )

        return open(path_xml, "r").read()

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

        access_key = self.get_access_key()

        response = client.service.autorizacionComprobante(access_key)

        authorized = (
            response["autorizaciones"]["autorizacion"][0]["estado"] == "AUTORIZADO"
            if response["autorizaciones"]
            else False
        )

        return authorized, response

    @staticmethod
    def get_tmp_dir():
        """
        Function to get the temporary directory
        """
        tmp = os.path.join(os.getcwd(), "tmp")
        if not os.path.exists(tmp):
            os.mkdir(tmp)

        return tmp

    def get_barcode_image(self):
        """
        Function to get the barcode image of the electronic invoice
        """
        rv = BytesIO()
        Code39(str(self.get_access_key()), writer=SVGWriter()).write(rv)

        return base64.b64encode(rv.getvalue()).decode("utf-8")

    def get_logo_base64(self):
        """
        Function to get the logo of the electronic invoice
        """

        with open(self.logo, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())

        return encoded_string.decode("utf-8")

    def get_subtotal_12(self):
        """
        Function to get the subtotal 12 of the electronic invoice
        """
        return sum(
            [
                float(i.value)
                for i in self.taxes
                if i.tax_percentage_code == PercentageTaxCodeEnum.TWELVE
            ]
        )

    def get_subtotal_0(self):
        """
        Function to get the subtotal 0 of the electronic invoice
        """
        return sum(
            [
                float(i.value)
                for i in self.taxes
                if i.tax_percentage_code == PercentageTaxCodeEnum.ZERO
            ]
        )

    def get_subtotal_no_tax(self):
        """
        Function to get the subtotal no iva of the electronic invoice
        """
        return sum(
            [
                float(i.value)
                for i in self.taxes
                if i.tax_percentage_code == PercentageTaxCodeEnum.NO_TAX
            ]
        )

    def get_total_tax(self):
        """
        Function to get the total tax of the electronic invoice
        """
        return sum([float(i.value) for i in self.taxes])

    def get_pdf(self, authorization_date: datetime):
        """
        Function to get the pdf of the electronic invoice
        """
        html = loader.get_template("ride.html").render(
            {
                "bill": self,
                "authorization_date": authorization_date,
                # "barcode_image": self.get_barcode_image(),
            }
        )

        file = os.path.join(self.get_tmp_dir(), f"{self.get_access_key()}.pdf")

        HTML(string=html).write_pdf(file)

        return file

    def get_qr(self):
        """
        Function to get the qr of the electronic invoice
        """
        raise NotImplementedError
