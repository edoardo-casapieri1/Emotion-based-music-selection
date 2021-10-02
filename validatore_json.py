import json
import jsonschema


def validate_json_data(data, schema) -> bool:
    try:
        jsonschema.validate(instance=data, schema=schema)
    except jsonschema.exceptions.ValidationError as err:
        print("INVALID JSON: ", err.message)
        return False
    except jsonschema.exceptions.SchemaError as err:
        print("INVALID JSON: ", err.message)
        return False
    return True


# passare i path per il file json da validare e il path per lo schema con cui validarlo
def validate_json_files(json_data_path, json_schema_path) -> bool:
    with open(json_data_path, 'r') as json_file:
        data = json.load(json_file)

    with open(json_schema_path, 'r') as json_file:
        schema = json.load(json_file)

    return validate_json_data(data, schema)


def validate_json_with_schema_path(data, json_schema_path) -> bool:
    with open(json_schema_path, 'r') as json_file:
        schema = json.load(json_file)

    return validate_json_data(data, schema)
