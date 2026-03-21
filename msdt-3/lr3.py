import re
import csv

reg_patterns = {
    'telephone' : r"^\+7-\(\d{3}\)-\d{3}-\d{2}-\d{2}$",
    'height'    : r"^[012]\.\d{2}$",
    'inn'       : r"^\d{12}$",
    'identifier': r"^\d+-\d+\/\d+$",
    'occupation': r"^[A-Za-zА-Яа-яЁё\s-]+$",
    'latitude'  : r"^(-?(90(\.0{1,6})?|([0-9]|[1-8]\d)(\.\d{1,6})?))$",
    'blood_type': r"^(?:AB|A|O|B)[+−]$",
    'issn'      : r"^\d{4}-\d{4}$",
    'uuid'      : r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    'date'      : r"^(?:19|20)\d{2}-(?:0[1-9]|1[012])-(?:0[1-9]|[12]\d|3[01])$"
}

def is_row_valid(row):
    for col, pattern in reg_patterns.items():
        if not re.match(pattern, row[col]):
            return False
    return True

def main(filename):
    with open(filename, mode='r', encoding='utf-16') as file:
        reader = csv.DictReader(file, delimiter=';')

        invalid_rows_numbers = []

        for row_number, row in enumerate(reader, start=2):
            if not is_row_valid(row):
                invalid_rows_numbers.append(row_number - 2)

    return(invalid_rows_numbers)
