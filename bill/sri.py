# -*- coding: utf-8 -*-
"""
@author: Rush Delivery App
"""

import os
import zeep

from datetime import datetime
from jinja2 import Environment, PackageLoader, select_autoescape
from typing import Set, Tuple, List, Union, Literal
from pydantic import BaseModel, Field, constr
from datetime import date, datetime, time, timedelta
from .enum import (
    EnvironmentEnum,
    StatusEnum,
    DocumentTypeEnum,
    EmmisionTypeEnum,
    TaxCodeEnum,
    PercentageTaxCodeEnum,
    UnitTimeEnum,
    PaymentMethodEnum,
    IdentificationTypeEnum,
)
from signxml import DigestAlgorithm
from signxml.xades import (
    XAdESSigner,
    XAdESVerifier,
    XAdESVerifyResult,
    XAdESSignaturePolicy,
    XAdESDataObjectFormat,
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
        if self.environment.value == "testing":
            return "https://celcer.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl"
        elif self.environment.value == "production":
            return "https://cel.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl"

    def __generate_access_key(self):
        """
        Function to generate the access key
        """
        code_number = str(self.numeric_code).zfill(8)

        return (
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

        loader = Environment(
            loader=PackageLoader("bill", "templates"), autoescape=select_autoescape()
        )
        # Generate access key
        key = self.__generate_access_key()

        digit_verifier = SRI.generate_digit_verifier(key)

        access_key = "{}{}".format(key, digit_verifier)

        return loader.get_template("factura_V1.1.0.xml").render(
            {
                "bill": self,
                "claveAcceso": access_key,
                "fechaEmision": self.emission_date.strftime("%d/%m/%Y"),
            }
        )

    def validate_sri(self):
        """
        Function to validate the electronic invoice in the SRI
        """

        from zeep import Client

        client = zeep.Client(wsdl=self.__get_reception_url())
        # transform the xml to bytes
        xml = self.get_xml().encode("utf-8")

        response = client.service.validarComprobante(xml)

        is_valid = response["estado"] == "RECIBIDA"

        if not is_valid:
            messages = response["comprobantes"]["comprobante"][0]["mensajes"]
            print(messages)

        return is_valid

    def get_xml_signed(self):
        """
        Function to sign the electronic invoice
        """

        from OpenSSL import crypto

        p12 = crypto.load_pkcs12(open(self.certificate, "rb").read(), self.password)

        # PEM formatted private key
        key = crypto.dump_privatekey(crypto.FILETYPE_PEM, p12.get_privatekey())

        # PEM formatted certificate
        cert = crypto.dump_certificate(crypto.FILETYPE_PEM, p12.get_certificate())

        from lxml import etree
        from signxml import XMLSigner, XMLVerifier

        data_to_sign = self.get_xml().encode("utf-8")
        root = etree.fromstring(data_to_sign)
        signed_root = XMLSigner().sign(root, key=key, cert=cert)
        verified_data = XMLVerifier().verify(signed_root, x509_cert=cert).signed_xml

        print(signed_root)

    def get_authorization(self):
        """
        Function to get the authorization of the electronic invoice in the SRI
        """
        pass

    def get_qr(self):
        """
        Function to get the qr of the electronic invoice
        """
        pass
