"""
Sets up a ready-to-explore farm: an owner login, one farm, a few sheds,
breeds, animals with weight/health/breeding history, feed stock, and a
sale/expense, so the handed-over project can be opened and demoed
immediately rather than staring at an empty database.

Usage:
    python manage.py seed_demo_data
"""

from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import Permission
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = "Seed the database with a demo organization, farm, staff, and animal records."

    @transaction.atomic
    def handle(self, *args, **options):
        from apps.accounts.models import Role, User
        from apps.animals.models import Animal, AnimalWeight, Breed, Species
        from apps.breeding.models import BreedingRecord, Kid, KiddingRecord
        from apps.farms.models import Farm, Location
        from apps.feed.models import Feed, FeedConsumption
        from apps.finance.models import Expense
        from apps.health.models import Deworming, Treatment, Vaccination
        from apps.procurement.models import Purchase, Supplier
        from apps.sales.models import AnimalSale, Customer
        from apps.staff.models import StaffMembership
        from apps.tenants.models import Organization

        self.stdout.write("Seeding demo data...")

        org, _ = Organization.objects.get_or_create(name="Green Valley Farms", slug="green-valley-farms")
        farm, _ = Farm.objects.get_or_create(
            organization=org, code="gv-main",
            defaults={"name": "Green Valley Main Farm", "address": "West Bengal, India"},
        )

        shed_a, _ = Location.objects.get_or_create(farm=farm, name="Shed A", defaults={"capacity": 50})
        shed_b, _ = Location.objects.get_or_create(farm=farm, name="Shed B - Kids", defaults={"capacity": 30})

        # Roles
        role_defs = Role.DEFAULT_ROLE_CHOICES
        roles = {}
        for code, name in role_defs:
            role, _ = Role.objects.get_or_create(code=code, defaults={"name": name})
            if not role.permissions.exists():
                role.permissions.set(Permission.objects.all() if code in (Role.OWNER, Role.ADMIN) else [])
            roles[code] = role

        # Owner user
        if not User.objects.filter(username="owner").exists():
            owner = User.objects.create_superuser(
                username="owner", email="owner@greenvalley.example", password="ChangeMe123!",
                first_name="Farm", last_name="Owner",
            )
        else:
            owner = User.objects.get(username="owner")
        StaffMembership.objects.get_or_create(
            user=owner, farm=farm,
            defaults={"role": roles[Role.OWNER], "designation": "Owner", "joining_date": date.today() - timedelta(days=700)},
        )

        # A vet staff member
        if not User.objects.filter(username="vet_amit").exists():
            vet = User.objects.create_user(
                username="vet_amit", email="amit.vet@greenvalley.example", password="ChangeMe123!",
                first_name="Amit", last_name="Singh", is_staff=True,
            )
        else:
            vet = User.objects.get(username="vet_amit")
        StaffMembership.objects.get_or_create(
            user=vet, farm=farm,
            defaults={"role": roles[Role.VETERINARY], "designation": "Farm Veterinarian", "joining_date": date.today() - timedelta(days=400)},
        )

        # Species / breeds
        goat, _ = Species.objects.get_or_create(name="Goat")
        breed_boer, _ = Breed.objects.get_or_create(species=goat, name="Boer")
        breed_jamuna, _ = Breed.objects.get_or_create(species=goat, name="Jamunapari")

        # Animals
        doe, _ = Animal.objects.get_or_create(
            farm=farm, tag_no="G-001",
            defaults=dict(
                name="Ganga", gender="FEMALE", breed=breed_boer,
                date_of_birth=date.today() - timedelta(days=900),
                color="White", birth_weight=Decimal("3.2"), current_weight=Decimal("42.0"),
                source="BORN_ON_FARM", location=shed_a, status=Animal.STATUS_ACTIVE,
            ),
        )
        buck, _ = Animal.objects.get_or_create(
            farm=farm, tag_no="G-002",
            defaults=dict(
                name="Raja", gender="MALE", breed=breed_jamuna,
                date_of_birth=date.today() - timedelta(days=1100),
                color="Brown", birth_weight=Decimal("3.5"), current_weight=Decimal("58.0"),
                source="PURCHASED", purchase_date=date.today() - timedelta(days=1000),
                purchase_price=Decimal("15000.00"), location=shed_a, status=Animal.STATUS_ACTIVE,
            ),
        )

        for i, w in enumerate([38.0, 40.0, 42.0]):
            AnimalWeight.objects.get_or_create(
                farm=farm, animal=doe, weight_date=date.today() - timedelta(days=(3 - i) * 30),
                defaults={"weight_kg": Decimal(str(w)), "weight_method": "SCALE"},
            )

        Vaccination.objects.get_or_create(
            farm=farm, animal=doe, vaccine="PPR Vaccine", date=date.today() - timedelta(days=60),
            defaults={"dose": "1ml", "next_due_date": date.today() + timedelta(days=3), "administered_by": vet},
        )
        Deworming.objects.get_or_create(
            farm=farm, animal=doe, medicine="Albendazole", date=date.today() - timedelta(days=45),
            defaults={"dose": "5ml", "body_weight": Decimal("41.0"), "next_due_date": date.today() + timedelta(days=5), "administered_by": vet},
        )
        Treatment.objects.get_or_create(
            farm=farm, animal=buck, date=date.today() - timedelta(days=10),
            defaults={
                "symptoms": "Mild lameness", "diagnosis": "Hoof rot", "medicine": "Antiseptic spray",
                "vet": vet, "follow_up_date": date.today() + timedelta(days=4),
            },
        )

        breeding, _ = BreedingRecord.objects.get_or_create(
            farm=farm, female_animal=doe, male_animal=buck,
            heat_date=date.today() - timedelta(days=170), mating_date=date.today() - timedelta(days=165),
            defaults={"mating_method": "NATURAL", "pregnancy_status": "CONFIRMED"},
        )

        kidding, created = KiddingRecord.objects.get_or_create(
            farm=farm, breeding_record=breeding, female_animal=doe,
            kidding_date=date.today() - timedelta(days=20),
            defaults={"number_of_kids": 2, "male_kids": 1, "female_kids": 1, "birth_assistance": "NONE"},
        )
        if created:
            k1 = Kid.objects.create(farm=farm, kidding_record=kidding, tag_no="G-003", gender="MALE", birth_weight=Decimal("3.0"))
            k1.create_animal_record(breed=breed_boer)
            k2 = Kid.objects.create(farm=farm, kidding_record=kidding, tag_no="G-004", gender="FEMALE", birth_weight=Decimal("2.8"))
            k2.create_animal_record(breed=breed_boer)
            Animal.objects.filter(tag_no__in=["G-003", "G-004"], farm=farm).update(location=shed_b)

        # Feed
        supplier, _ = Supplier.objects.get_or_create(farm=farm, name="AgroFeed Suppliers", defaults={"phone": "9876543210"})
        napier, _ = Feed.objects.get_or_create(
            farm=farm, feed_name="Napier", defaults={"unit": "KG", "purchase_price": Decimal("3.0"), "supplier": supplier, "stock_quantity": Decimal("500"), "minimum_stock": Decimal("100")},
        )
        maize, _ = Feed.objects.get_or_create(
            farm=farm, feed_name="Maize Crushed", defaults={"unit": "KG", "purchase_price": Decimal("22.0"), "supplier": supplier, "stock_quantity": Decimal("40"), "minimum_stock": Decimal("50")},
        )
        FeedConsumption.objects.get_or_create(
            farm=farm, feed=napier, date=date.today() - timedelta(days=1),
            defaults={"quantity": Decimal("15"), "animal_category": "ALL", "number_of_animals": 4},
        )
        Purchase.objects.get_or_create(
            farm=farm, supplier=supplier, purchase_date=date.today() - timedelta(days=20),
            item_type="FEED", item_name="Maize Crushed", quantity=Decimal("100"), unit_price=Decimal("22.0"),
            defaults={"payment_status": "PAID"},
        )

        # Commercial
        customer, _ = Customer.objects.get_or_create(farm=farm, name="Local Meat Trader", defaults={"phone": "9123456780"})
        sold_animal, _ = Animal.objects.get_or_create(
            farm=farm, tag_no="G-099",
            defaults=dict(
                name="Sold Kid", gender="MALE", breed=breed_boer,
                date_of_birth=date.today() - timedelta(days=200),
                current_weight=Decimal("28.0"), source="BORN_ON_FARM",
                location=shed_a, status=Animal.STATUS_ACTIVE,
            ),
        )
        AnimalSale.objects.get_or_create(
            farm=farm, animal=sold_animal, buyer=customer, sale_date=date.today() - timedelta(days=5),
            defaults={"live_weight": Decimal("28.0"), "rate_per_kg": Decimal("450.0"), "payment_mode": "CASH"},
        )
        Expense.objects.get_or_create(
            farm=farm, expense_date=date.today() - timedelta(days=3), category="FEED",
            defaults={"description": "Monthly feed purchase", "amount": Decimal("2200.00"), "payment_mode": "CASH"},
        )
        Expense.objects.get_or_create(
            farm=farm, expense_date=date.today() - timedelta(days=2), category="LABOUR",
            defaults={"description": "Staff wages", "amount": Decimal("8000.00"), "payment_mode": "BANK_TRANSFER"},
        )

        self.stdout.write(self.style.SUCCESS(
            "Demo data ready.\n"
            "  Owner login   -> username: owner     password: ChangeMe123!\n"
            "  Vet login     -> username: vet_amit   password: ChangeMe123!\n"
            "Change these passwords immediately after first login."
        ))
