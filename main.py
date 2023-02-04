from bill.sri import SRI
from datetime import date

def main():
    """
    Test SRI
    """

    print("Test SRI")

    bill = SRI(
        emission_date=date.today(),
        document_type="01",
        environment="1",
        serie="001001",
        company_ruc="0105527386001",
        billing_name="Distribuidora de Suministros Nacional S.A.",
        company_name="Empresa Importadora y Exportadora de Piezas",
        company_address="Av. 6 de Diciembre y Av. 10 de Agosto",
        numeric_code="00000001",
        company_contribuyente_especial="5368",
        company_obligado_contabilidad="SI",
        establishment="001",
        point_emission="001",
        emission_type="1",
        sequential="000000001",
        customer_billing_name="Cliente",
        customer_identification="1792146739001",
        customer_identification_type="01",
        customer_address="Av. 6 de Diciembre y Av. 10 de Agosto",
        taxes=[
            {
                "code": "2",
                "tax": "12",
                "base": "100",
                "value": "12",
            },
        ],
    )

    # Test Validation

    assert bill.get_xml()


if __name__ == "__main__":
    main()
