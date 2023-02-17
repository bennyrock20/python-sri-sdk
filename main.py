from src.sri import SRI
from datetime import date, timedelta, datetime
import os


def main():
    """
    Manual Test SRI
    """

    print("Test SRI")

    cert = os.getenv("CERT")
    password = os.getenv("PASSWORD")

    bill = SRI(
        emission_date=date.today() - timedelta(days=38),
        document_type="01",
        environment="1",
        logo="./logo.png",
        company_ruc="0105527386001",
        billing_name="QUILLAY BRAVO VICTOR MANUEL",
        company_name="CREDI-OFERTAS",
        company_address="Manuel Moreno y Canaverales",
        company_phone="2626290073",
        main_address="Manuel Moreno y Canaverales",
        numeric_code="00000001",
        company_contribuyente_especial="5368",
        company_obligado_contabilidad="SI",
        establishment="001",
        point_emission="001",
        emission_type="1",
        sequential="000000006",

        customer_billing_name="Andres Bravo",
        customer_identification="1792146739001",
        customer_identification_type="04",
        customer_email="info@rushdelivery.app",
        customer_phone="0999999999",
        customer_address="Av. 6 de Diciembre y Av. 10 de Agosto",
        taxes=[
            {
                "code": "2",
                "tax_percentage_code": "2",
                "base": "100",
                "tarifa": "12",
                "additional_discount": "0",
                "value": "12",
            },
        ],
        payments=[
            {
                "payment_method": "01",
                "total": "112",
                "terms": 0,
                "unit_time": "dias",
            },
        ],
        lines_items=[
            {
                "code": "0001",
                "aux_code": "ABC-2343",
                "description": "Producto 1",
                "quantity": "1",
                "unit_price": "100",
                "discount": "0",
                "price_total_without_tax": "100",
                "total_price": "112",
                "taxes": [
                    {
                        "code": "2",
                        "tax_percentage_code": "2",
                        "base": "100",
                        "tarifa": "12",
                        "additional_discount": "0",
                        "value": "12",
                    },
                ],
            },
        ],
        total_discount=0,
        tips=0,
        total_without_tax=100,
        grand_total=112,
        certificate=cert,
        password=password,
    )

    # Test Validation
    # res = bill.get_xml()

    # res = bill.get_xml_signed()

    bill.get_pdf(authorization_date=datetime.now())

    # valid, m = bill.validate_sri()
    # print(valid, m)

    # authorized, m = bill.get_authorization()
    # print(authorized, m)


if __name__ == "__main__":
    main()
