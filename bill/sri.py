# -*- coding: utf-8 -*-
"""
@author: Rush Delivery App
"""

import os
import zeep
from datetime import datetime
from jinja2 import Environment, PackageLoader, select_autoescape


class SRI:
    """
    Class for handling SRI functions
    """

    def __init__(self,
                 environment,
                 type,
                 billing_name,
                 company_name,
                 company_ruc,
                 establishment,
                 point_emission,
                 sequence,
                 company_address,
                 company_contribuyente_especial,
                 company_obligado_contabilidad,
                 emission_date,
                 serie, number,
                 numeric_code,
                 emission_type,
                 customer_billing_name,
                 customer_identification,
                 customer_identification_type,
                 customer_address,
                 ):
        """
        @param emission_date: Fecha de emision
        @param type: Tipo de comprobante
        @param ruc: RUC del emisor
        @param environment: Ambiente de trabajo (testing, production)
        @param serie: Serie del comprobante
        @param number: Numero del comprobante
        @param numeric_code: Codigo numerico
        @param emission_type: Tipo de emision
        @param verification_digit: Digito de verificacion
        """
        # Environment information
        self.type = type
        self.environment = environment == "testing" and "1" or "2"
        self.emission_type = emission_type

        # Billing information
        self.company_ruc = company_ruc
        self.billing_name = billing_name
        self.company_name = company_name
        self.company_address = company_address
        self.establishment = establishment
        self.point_emission = point_emission
        self.company_contribuyente_especial = company_contribuyente_especial
        self.company_obligado_contabilidad = company_obligado_contabilidad

        # Invoice information
        self.emission_date = emission_date
        self.serie = serie
        self.number = number
        self.numeric_code = numeric_code
        self.sequence = sequence

        # Customer information
        self.customer_billing_name = customer_billing_name
        self.customer_identification = customer_identification
        self.customer_identification_type = customer_identification_type
        self.customer_address = customer_address

    def __get_reception_url(self):
        """
        Function to get the url of receipt of invoices
        """
        if self.environment == "1":
            return "https://celcer.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl"
        elif self.environment == "2":
            return "https://cel.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl"

    def __get_authorization_url(self):
        """
        Function to get the url of authorization of invoices
        """
        if self.environment == "testing":
            return "https://celcer.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl"
        elif self.environment == "production":
            return "https://cel.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl"

    def __generate_access_key(self):
        """
       Function to generate the access key
        """
        code_number = str(self.numeric_code).zfill(8)

        return (
                str(self.emission_date.replace("/", ""))  # Remove the slashes from the date
                + str(self.type)
                + str(self.company_ruc)
                + str(self.environment)
                + str(self.establishment)
                + str(self.point_emission)
                + str(self.sequence)
                + str(code_number)
                + str(self.emission_type)
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
            loader=PackageLoader("bill", "templates"),
            autoescape=select_autoescape()
        )
        # Generate access key
        key = self.__generate_access_key()

        digit_verifier = SRI.generate_digit_verifier(key)

        access_key = "{}{}".format(key, digit_verifier)

        return loader.get_template("factura_V1.1.0.xml").render({
            # Info Tributaria
            "type": self.type,
            "companyRuc": self.company_ruc,
            "environment": self.environment,
            "serie": self.serie,
            "razonSocial": self.billing_name,
            "nombreComercial": self.company_name,
            "number": self.number,
            "numeric_code": self.numeric_code,
            "emission_type": self.emission_type,
            "claveAcceso": access_key,
            "dirMatriz": "Calle 1",
            "secuencial": "000000000",

            "dirEstablecimiento": self.company_address,
            "contribuyenteEspecial": self.company_contribuyente_especial,
            "obligadoContabilidad": self.company_obligado_contabilidad,

            # Info de la factura

            "fechaEmision": self.emission_date,
            # Customer Information
            # <comercioExterior>{{ comercioExterior  }}</comercioExterior>
            #         <incoTermFactura>A</incoTermFactura>
            #         <lugarIncoTerm>lugarIncoTerm0</lugarIncoTerm>
            #         <paisOrigen>000</paisOrigen>
            #         <puertoEmbarque>puertoEmbarque0</puertoEmbarque>
            #         <puertoDestino>puertoDestino0</puertoDestino>
            #         <paisDestino>000</paisDestino>
            #         <paisAdquisicion>000</paisAdquisicion>
            #         <tipoIdentificacionComprador>04</tipoIdentificacionComprador>
            #         <guiaRemision>000-000-000000000</guiaRemision>
            "tipoIdentificacionComprador": self.customer_identification_type,
            "razonSocialComprador": self.customer_billing_name,
            "identificacionComprador": self.customer_identification,
            "direccionComprador": self.customer_address,

            # Total Information
            # "totalSinImpuestos": self.total_without_taxes,
            # "totalDescuento": self.total_discount,
            # "totalConImpuestos": self.total_taxes,
            # "propina": self.propina,
            # "importeTotal": self.total,
            # "moneda": self.currency,
            # "pagos": self.payments,
            # "detalles": self.details,


        })

    def sign(self):
        """
        Function to sign the electronic invoice
        """
        pass

    def validate_sri(self):
        """
        Function to validate the electronic invoice in the SRI
        """

        from zeep import Client

        client = zeep.Client(wsdl=self.__get_reception_url())
        # transform the xml to bytes
        xml = self.get_xml().encode("utf-8")

        response = client.service.validarComprobante(xml)

        state = response["estado"]
        messages = response["comprobantes"]["comprobante"][0]["mensajes"]

        print(messages)

        return state == "RECIBIDA"

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
