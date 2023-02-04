from bill.sri import SRI


def test_sri_xml():
    """
    Test the SRI SDK
    """

    bill = SRI(
        emission_date="2019-01-01",
        type="01",
        ruc="0999999999001",
        environment="testing",
        establishment="001",
        point_emission="001",
        serie="001",
        number="000000001",
        numeric_code="12345678",
        emission_type="1",
        verification_digit="1",
    )

    # Test XML generation

    xml = bill.get_xml()

    assert "0999999999001" in xml

    # 5.1Los contribuyentes generarán sus comprobantes electrónicos en formato .xml conforme a los esquemas .xsd que
    # están disponibles en el portal web del SRI, a través de sus propios
    # aplicativos informáticos o mediante el facturador electrónico que el SRI dispone gratuitamente
    # para los contribuyentes.

    # 5.2 Cada comprobante generado contendrá una clave de acceso única que estará compuesta por 49
    # dígitos numéricos, el aplicativo a utilizar por el contribuyente deberá
    # generar de manera automática esta clave, la cual constituye un
    # requisito obligatorio que le dará el CARACTER de único a cada
    # comprobante y a la vez se constituirá en el número de autorización
    # del mismo; en base a esta clave el SRI generará la respuesta de
    # autorizado o no; a continuación, se describe su conformación:

    # 5.3 El código que conformará el tipo de emisión según la clave
    # de acceso generada se detalla a continuación:

    # 1. Emisión Normal (Emisor y Receptor en el mismo país)
