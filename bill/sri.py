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

    def __init__(self, emission_date, type, ruc, environment, establishment, point_emission, serie, number, sequence, numeric_code, emission_type,
                 verification_digit):
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
        self.emission_date = emission_date
        self.type = type
        self.ruc = ruc
        self.environment = environment == "testing" and "1" or "2"
        self.establishment = establishment
        self.point_emission = point_emission
        self.serie = serie
        self.number = number
        self.numeric_code = numeric_code
        self.emission_type = emission_type
        self.verification_digit = verification_digit
        self.sequence = sequence

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
                str(self.emission_date.replace("/", "")) # Remove the slashes from the date
                + str(self.type)
                + str(self.ruc)
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

        return loader.get_template("factura_V2.1.0.xml").render({
            "fechaEmision": self.emission_date,
            "type": self.type,
            "ruc": self.ruc,
            "environment": self.environment,
            "serie": self.serie,
            "number": self.number,
            "numeric_code": self.numeric_code,
            "emission_type": self.emission_type,
            "verification_digit": self.verification_digit,
            "claveAcceso": access_key,
            "dirMatriz": "Calle 1",
            "secuencial": "000000000",
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

        return  state == "RECIBIDA"

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



