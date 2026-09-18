from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from apps.animals.models import Animal


@login_required
def animal_list(request):
    farm = request.farm
    qs = Animal.objects.filter(farm=farm).select_related("breed", "location") if farm else Animal.objects.none()

    q = request.GET.get("q", "").strip()
    if q:
        from django.db.models import Q
        qs = qs.filter(Q(tag_no__icontains=q) | Q(name__icontains=q))

    gender = request.GET.get("gender")
    if gender:
        qs = qs.filter(gender=gender)

    breed = request.GET.get("breed")
    if breed:
        qs = qs.filter(breed_id=breed)

    status = request.GET.get("status")
    if status:
        qs = qs.filter(status=status)

    location = request.GET.get("location")
    if location:
        qs = qs.filter(location_id=location)

    category = request.GET.get("category")  # all / female / male / kids
    if category == "female":
        qs = qs.filter(gender="FEMALE")
    elif category == "male":
        qs = qs.filter(gender="MALE")
    elif category == "kids":
        qs = [a for a in qs if a.is_kid]

    paginator = Paginator(list(qs) if isinstance(qs, list) else qs, 25)
    page_obj = paginator.get_page(request.GET.get("page"))

    from apps.animals.models import Breed
    from apps.farms.models import Location

    context = {
        "page_obj": page_obj,
        "breeds": Breed.objects.filter(animals__farm=farm).distinct() if farm else [],
        "locations": Location.objects.filter(farm=farm) if farm else [],
        "status_choices": Animal.STATUS_CHOICES,
        "gender_choices": Animal.GENDER_CHOICES,
        "query_params": request.GET,
    }
    return render(request, "animals/animal_list.html", context)


@login_required
def animal_profile(request, pk):
    farm = request.farm
    animal = get_object_or_404(Animal, pk=pk, farm=farm)
    context = {
        "animal": animal,
        "weight_records": animal.weight_records.all()[:20],
        "vaccinations": animal.vaccinations.all()[:20],
        "dewormings": animal.dewormings.all()[:20],
        "treatments": animal.treatments.all()[:20],
        "breeding_records": animal.breeding_records_as_female.all()[:20] if animal.gender == "FEMALE" else [],
        "kidding_records": animal.kidding_records.all()[:20] if animal.gender == "FEMALE" else [],
        "offspring": list(animal.offspring_as_mother.all()) + list(animal.offspring_as_father.all()),
        "movements": animal.movements.all()[:20],
        "sale_record": getattr(animal, "sale_record", None),
        "adg": animal.adg,
    }
    return render(request, "animals/animal_profile.html", context)
