from faker import Faker
import random

faker = Faker("ru_RU")

class PointPayloadBuilder:
    @staticmethod
    def point_create():
        return {
            "contacts": [
                {
                    "contact": None,
                    "email": None,
                    "extraPhone": None,
                    "extraSecondPhone": None,
                    "phone": None,
                    "secondPhone": None
                }
            ],
            "addressString": str(faker.address()),
            "title": faker.company(),
            "timezone": "Europe/Moscow",
            "status": random.choice([True, False]),
            "latitude": None,
            "longitude": None,
            "addressType": random.randint(1, 2),
            "loadingType": random.randint(1, 2),
            "liftingCapacityMax": None,
            "maxHeightFromGroundInCm": random.randint(2, 8),
            "comment": faker.sentence(nb_words=6),
            "pointOwnerInn": None,
            "vicinityRadius": None,
            "pointOwnerKpp": None,
            "externalId": None,
            "pointArrivalDuration": None,
            "pointDepartureDuration": None,
            "necessaryPass": 0,
            "statusFlowType": None,
            "cart": 0,
            "isFavorite": 0,
            "elevator": 0
        }