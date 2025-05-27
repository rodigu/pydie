# Converter

Converts data from a REST API response into valid SQL data using type conversions specified by input.

The dictionary should have each possible attribute returned as a key, and their respective SQL data types as values (strings).

## Special data types

Some data types require further specifications to be properly converted.

### Datetime

Datetimes may come in a variety of formats.
These should be specified for conversion using the following convention:

```json
{
    "object.datesample": "datetime[FORMATTING]"
}
```

A full list of formatting codes may be found at the
[Python datetime library documentation](https://docs.python.org/3/library/datetime.html#format-codes).

## Lists

### Inconsistent

Inconsistent lists should receive a `varchar` with a reasonable length.

### Consistent

If the list has consistent objects that follow the same formatting,
set its value to a dictionary that follows the same formatting presented here.
A new table with the name of the property will be created, and the values for the list will be inserted into it.

## Example

An API keeps track of customers.
Here is an example response for the users endpoint:

```json
{
    "users": [
        {
            "id": "001",
            "name": "John",
            "height": 2.1,
            "purchaseHistory": [
                {
                    "id": "00",
                    "cost": 1.2,
                    "date": "2025-01-15 14:29:03"
                }
            ],
            "aliases": ["johnny", "j"]
        }
    ]
}
```

Here is what the SQL converter specification would look like:

```json
{
    "id": "varchar(3)",
    "name": "varchar(100)",
    "height": "decimal",
    "aliases": "varchar(100)",
    "purchaseHistory": {
        "id": "varchar(2)",
        "cost": "money",
        "date": "smalldatetime[%Y-%m-%d %H:%M:%S]"
    }
}
```

For the property `"purchaseHistory"`,
a table with the same name will be created (if it doesn't already exists) using the specifications given.
Any new users with a `"purchaseHistory"` will have such property used to update the new table.
