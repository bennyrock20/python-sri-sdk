from sri.enum import TaxCodeEnum, PercentageTaxCodeEnum, PaymentMethodEnum


class TestSRI:
    def test_totals(self):
        """
        Test the SRI SDK
        """

        from sri import SRI
        from datetime import date, datetime

        bill = SRI(
            emission_date=date.today(),
            document_type="01",
            environment="1",
            serie="001001",
            company_ruc="0100067500001",
            billing_name="Rush Soft",
            company_name="Rush Delivery",
            company_address="Manuel Moreno y Canaverales",
            main_address="Manuel Moreno y Canaverales",
            numeric_code="00000001",
            company_contribuyente_especial="5368",
            company_obligado_contabilidad="SI",
            company_phone="+59398888888",
            establishment="001",
            point_emission="001",
            emission_type="1",
            sequential="000000005",
            customer_billing_name="Jhon Doe",
            customer_identification="1792146739001",
            customer_identification_type="04",
            customer_address="Av. 6 de Diciembre y Av. 10 de Agosto",
            customer_email="info@rushdelivery.app",
            customer_phone="+59398569277",
            lines_items=[
                {
                    "code": "0001",
                    "aux_code": "ABC-2343",
                    "description": "Producto 1 - No aplica IVA",
                    "quantity": 1,
                    "unit_price": 110,
                    "discount": 10,
                    "price_total_without_tax": 100,
                    "total_price": 100,
                    "taxes": [
                        {
                            "code": TaxCodeEnum.IVA,
                            "tax_percentage_code": PercentageTaxCodeEnum.ZERO,
                            "base": 100,
                            "additional_discount": 0,
                            "value": 0,
                        },
                    ],
                },
                {
                    "code": "0002",
                    "aux_code": "ABC-2344",
                    "description": "Producto 2 (12%)",
                    "quantity": 5,
                    "unit_price": 4.50,
                    "discount": 0,
                    "price_total_without_tax": 22.50,
                    "total_price": 25.50,
                    "taxes": [
                        {
                            "code": TaxCodeEnum.IVA,
                            "tax_percentage_code": PercentageTaxCodeEnum.TWELVE,
                            "base": 22.50,
                            "additional_discount": 0,
                            "value": 2.70,
                        },
                    ],
                },
                {
                    "code": "0003",
                    "aux_code": "ABC-2345",
                    "description": "Producto 3 (14%)",
                    "quantity": 15,
                    "unit_price": 2.50,
                    "discount": 0,
                    "price_total_without_tax": 37.50,
                    "total_price": 42.50,
                    "taxes": [
                        {
                            "code": TaxCodeEnum.IVA,
                            "tax_percentage_code": PercentageTaxCodeEnum.FOURTEEN,
                            "base": 37.50,
                            "additional_discount": 0,
                            "value": 5.25,
                        },
                    ],
                },
                {
                    "code": "0004",
                    "aux_code": "ABC-2346",
                    "description": "Producto 4 - No aplica IVA",
                    "quantity": 10,
                    "unit_price": 1.50,
                    "discount": 0,
                    "price_total_without_tax": 15,
                    "total_price": 15,
                    "taxes": [
                        {
                            "code": TaxCodeEnum.IVA,
                            "tax_percentage_code": PercentageTaxCodeEnum.NO_TAX,
                            "base": 15,
                            "additional_discount": 0,
                            "value": 0,
                        },
                    ]
                },

                {
                    "code": "0005",
                    "aux_code": "ABC-2347",
                    "description": "Producto 5 - Tax Exempt",
                    "quantity": 10,
                    "unit_price": 3,
                    "discount": 0,
                    "price_total_without_tax": 30,
                    "total_price": 30,
                    "taxes": [
                        {
                            "code": TaxCodeEnum.IVA,
                            "tax_percentage_code": PercentageTaxCodeEnum.TAX_EXEMPT,
                            "base": 30,
                            "additional_discount": 0,
                            "value": 0,
                        },
                    ]
                }
            ],
            payments=[
                {
                    "payment_method": PaymentMethodEnum.CASH,
                    "total": 212.95,
                    "terms": 0,
                    "unit_time": "dias",
                },
            ],
            tips=0,
        )

        # Test Total Tax 0%
        assert bill.get_subtotal_0() == 100

        # Test Total Tax 12%
        assert bill.get_subtotal_12() == 22.50

        # Test Total Tax 14%
        assert bill.get_subtotal_14() == 37.50

        # Test Total No Tax
        assert bill.get_subtotal_tax_exempt() == 30

        # Test Total Tax Exempt
        assert bill.get_subtotal_no_tax() == 15

        # Validate total without tax (Sum all price_total_without_tax 100 + 22)

        assert bill.total_without_tax == 205

        # Validate  total_tax

        assert bill.total_tax == 7.95

        # Validate grand total sum total_without_tax + total_tax (205 + 7.95)

        assert bill.grand_total == 212.95

        assert bill.total_discount == 10

        pdf_bytes = bill.get_pdf(
            logo="logo.png",
            authorization_date=datetime.now())

        with open("test.pdf", "wb") as f:
            f.write(pdf_bytes)
