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
    ClientTypesEnum,
    DocumentTypeEnum,
    EmmisionTypeEnum,
    TaxCodeEnum,
    PercentageTaxCodeEnum,
    UnitTimeEnum,
    PaymentMethodEnum,
)


class TaxItem(BaseModel):
    """
    Class for handling tax items
    """

    code: TaxCodeEnum
    tax_percentage_code: PercentageTaxCodeEnum
    additional_discount: str
    base: str
    value: str


#  <pago>
#                 <formaPago>01</formaPago>
#                 <total>50.00</total>
#                 <plazo>50.00</plazo>
#                 <unidadTiempo>unidadTiem</unidadTiempo>
#             </pago>


class PaymentItem(BaseModel):
    """
    Class for handling payment items
    """

    payment_method: PaymentMethodEnum
    total: str
    terms: int
    unit_time: UnitTimeEnum


class SRI(BaseModel):
    """
    Class for handling SRI functions
    """

    environment: EnvironmentEnum
    document_type: DocumentTypeEnum = DocumentTypeEnum.INVOICE
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
    customer_identification_type: DocumentTypeEnum
    customer_address: str
    taxes: List[TaxItem]
    payments: List[PaymentItem]

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
                # Info Tributaria
                "companyRuc": self.company_ruc,
                "environment": self.environment,
                "serie": self.serie,
                "razonSocial": self.billing_name,
                "nombreComercial": self.company_name,
                "numeric_code": self.numeric_code,
                "tipoEmision": self.emission_type,
                "claveAcceso": access_key,
                "dirMatriz": "Calle 1",
                "secuencial": "000000000",
                "establecimiento": self.establishment,
                "ptoEmi": self.point_emission,
                "dirEstablecimiento": self.company_address,
                "contribuyenteEspecial": self.company_contribuyente_especial,
                "obligadoContabilidad": self.company_obligado_contabilidad,
                # Info de la factura
                "fechaEmision": self.emission_date,
                "tipoIdentificacionComprador": self.customer_identification_type,
                "razonSocialComprador": self.customer_billing_name,
                "identificacionComprador": self.customer_identification,
                "direccionComprador": self.customer_address,
                # Total Information
                "totalSinImpuestos": 0,
                "totalDescuento": 0,
                "totalConImpuestos": 0,
                "propina": 0,
                "importeTotal": 100,
                "impuestos": self.taxes,
                "pagos": self.payments,
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

    def sign(self):
        """
        Function to sign the electronic invoice
        """
        pass

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

    def get_xml_signed(self):
        """
        Function to get the xml signed of the electronic invoice
        """
        pass
