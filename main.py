from bill.sri import SRI


def main():
    """
    Test SRI
    """

    print("Test SRI")

    bill = SRI(
        emission_date="03/02/2023",
        document_type="01",
        environment="testing",
        serie="001",
        company_ruc="0105527386001",
        billing_name="Distribuidora de Suministros Nacional S.A.",
        company_name="Empresa Importadora y Exportadora de Piezas",
        company_address="Av. 6 de Diciembre y Av. 10 de Agosto",
        number="000000001",
        numeric_code="12345678",
        company_contribuyente_especial="5368",
        company_obligado_contabilidad="SI",
        establishment="001",
        point_emission="001",
        emission_type="1",
        sequence="000000001",
        customer_billing_name="Cliente",
        customer_identification="1792146739001",
        customer_identification_type="04",
        customer_address="Av. 6 de Diciembre y Av. 10 de Agosto",
    )

    # Test Validation

    assert bill.validate_sri()


if __name__ == "__main__":
    main()
