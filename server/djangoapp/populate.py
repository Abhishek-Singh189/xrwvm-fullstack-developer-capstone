import json
from pathlib import Path

from djangoapp.models import CarMake, CarModel


def initiate():
    data_file = Path(__file__).resolve().parent.parent / "database" / "data" / "car_records.json"
    with data_file.open("r", encoding="utf-8") as file:
        records = json.load(file).get("cars", [])

    for record in records:
        make, _ = CarMake.objects.get_or_create(
            name=record["make"],
            defaults={"description": f"{record['make']} vehicles"},
        )
        CarModel.objects.get_or_create(
            make=make,
            name=record["model"],
            year=record["year"],
            defaults={"type": record.get("bodyType", "SEDAN").upper()},
        )

    print(f"Populated {len(records)} car records")
