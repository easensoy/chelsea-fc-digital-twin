class ChelseaFCException(Exception):
    pass

class PlayerNotFoundError(ChelseaFCException):
    pass

class MatchNotFoundError(ChelseaFCException):
    pass

class FormationError(ChelseaFCException):
    pass

class DataExportError(ChelseaFCException):
    pass

class AnalyticsError(ChelseaFCException):
    pass

class ValidationError(ChelseaFCException):
    pass

class PowerBIConnectionError(ChelseaFCException):
    pass

class InsufficientDataError(ChelseaFCException):
    pass