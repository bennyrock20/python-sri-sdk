from bill.sri import SRI
from datetime import date
import os


def main():
    """
    Test SRI
    """

    print("Test SRI")

    cert = os.getenv("CERT")
    password = os.getenv("PASSWORD")

    bill = SRI(
        emission_date=date.today(),
        document_type="01",
        environment="1",
        serie="001001",
        company_ruc="0105527386001",
        billing_name="Distribuidora de Suministros Nacional S.A.",
        company_name="Empresa Importadora y Exportadora de Piezas",
        company_address="Av. 6 de Diciembre y Av. 10 de Agosto",
        matriz_address="Av. 6 de Diciembre y Av. 10 de Agosto",
        numeric_code="00000001",
        company_contribuyente_especial="5368",
        company_obligado_contabilidad="SI",
        establishment="001",
        point_emission="001",
        emission_type="1",
        sequential="000000001",
        customer_billing_name="Cliente",
        customer_identification="1792146739001",
        customer_identification_type="04",
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

    print(bill.get_xml())
    bill.get_xml_signed()
    print("validate", bill.validate_sri())


if __name__ == "__main__":
    main()
