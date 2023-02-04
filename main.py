from bill.sri import SRI


def main():
    """
    Test SRI
    """

    print("Test SRI")

    bill = SRI(
        emission_date="04/02/2023",
        type="1",
        environment="testing",
        serie="001",
        company_ruc="1792146739001",
        billing_name="Distribuidora de Suministros Nacional S.A.",
        company_name="Empresa Importadora y Exportadora de Piezas",
        company_address="Av. 6 de Diciembre y Av. 10 de Agosto",
        number="000000001",
        numeric_code="12345678",
        establishment="001",
        point_emission="001",
        emission_type="1",
        sequence="000000001",
    )

    # Test Validation

    assert bill.validate_sri()

if __name__ == "__main__":
    main()