# SRI 

SRI provides a simple way to interact with the SRI API.

## Disclaimer

This is not an official SDK, it is a personal project that I use in my company, I am not responsible for any damage that this library may cause.

## SUPPORTED DOCUMENTS

- [x] FACTURA

## Dependencies

- Python 3.7+
- signxml 3.0.0
- pydantic 1.10.4
- zeep 4.2.1
- jinga 3.1.2

## Installation

```shell
pip install sri
```

## Usage

```python
from datetime import date
from sri import SRI

cert_path_file = "certificado.p12"
password = "12345678"

bill = SRI(
        emission_date=date.today(),
        document_type="01",
        environment="1",
        serie="001001",
        company_ruc="010006750001",
        billing_name="Razon Social",
        company_name="Nombre Comercial",
        company_address="Manuel Moreno y Canaverales",
        matriz_address="Manuel Moreno y Canaverales",
        numeric_code="00000001",
        company_contribuyente_especial="5368",
        company_obligado_contabilidad="SI",
        establishment="001",
        point_emission="001",
        emission_type="1",
        sequential="000000005",
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
        certificate=cert_path_file,
        password=password,
    )

# Send the bill to the SRI
valid, m = bill.validate_sri()
print(valid, m)

# Get the authorization
authorized, m = bill.get_authorization()
print(authorized, m)

```
# Features

- [x] FACTURA

# Todo

- [ ] VALIDACIÓN DE TOTAL DE FACTURA
- [ ] ENVÍO POR LOTE
- [ ] COMPROBANTE RETENCIÓN
- [ ] GUÍA DE REMISIÓN
- [ ] NOTA DE CRÉDITO
- [ ] NOTA DE DÉBITO

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)