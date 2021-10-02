"""Modulo che consente il caricamento delle impostazioni
di configurazione del sistema di elaborazione degli impulsi.
"""

import json
from os.path import join, dirname
from validatore_json import validate_json_files
import settings
from Sistema_di_elaborazione_degli_impulsi.exceptions import JSONSchemaValidationException


def load_config() -> dict:
    """Valida lo schema del file JSON di configurazione del sistema di elaborazione dei dati.
    Ritorna:
        Dizionario contenente i parametri di configurazione.

    Lancia:
        JSONSchemaViolationException: se il JSON in input non soddisfa lo schema di validazione."""

    schema_path = join(dirname(dirname(__file__)), 'JsonSchemas',
                       'DataPrepConfigurationSchema.json')
    conf_path = settings.DATA_PREP_CONFIG_PATH
    if validate_json_files(conf_path, schema_path):
        with open(conf_path, 'r') as conf_file:
            conf = json.load(conf_file)
            return conf
    raise JSONSchemaValidationException('[ERRORE] JSON di configurazione in formato errato.')
