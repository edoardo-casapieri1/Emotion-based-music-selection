"""Modulo contenente le eccezioni del Sistema di elaborazione degli impulsi."""


class JSONSchemaValidationException(Exception):
    """Eccezione lanciata se il JSON fornito non rispetta lo schema di validazione."""


class TooManyNaNsException(Exception):
    """Eccezione lanciata quando il numero di valori nulli nella time series di un canale
    supera la soglia definita nel JSON di configurazione.
    """


class SessionNotFoundException(Exception):
    """Eccezione lanciata quando non viene passata una sessione in fase operativa."""
