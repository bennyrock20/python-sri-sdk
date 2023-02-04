from enum import Enum, IntEnum


class EnvironmentEnum(str, Enum):
    TESTING = "1"
    PRODUCTION = "2"


class EmmisionTypeEnum(str, Enum):
    NORMAL = "1"


class ClientTypesEnum(str, Enum):
    RUC = "04"
    CEDULA = "05"
    PASAPORTE = "06"
    CONSUMIDOR_FINAL = "07"
    IDENTIFICACION_EXTERIOR = "08"


class DocumentTypeEnum(str, Enum):
    INVOICE = "01"
    NOTA_CREDITO = "04"
    NOTA_DEBITO = "05"
    GUIA_REMISION = "06"
    RETENCION = "07"


class StatusEnum(str, Enum):
    STATUS_PROCESSING = "PPR"
    STATUS_AUTHORIZED = "AUT"
    STATUS_NOT_AUTHORIZED = "NAT"


class TaxCodeEnum(str, Enum):
    IVA = "2"
    ICE = "3"
    IRBPNR = "5"


class PercentageTaxCodeEnum(str, Enum):
    ZERO = "0"
    TWELVE = "2"
    FOURTEEN = "3"
    NO_TAX = "6"
    TAX_EXEMPT = "7"
