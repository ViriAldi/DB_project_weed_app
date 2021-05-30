from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from .models import *
from datetime import datetime
import pytz


utc=pytz.UTC


@csrf_protect
def login(request):
    if request.method == "GET":
        return render(request, "acidlord/login.html")
    if request.method == "POST":
        if "name_custom" in request.POST and "password_custom" in request.POST:
            name = request.POST["name_custom"]
            password = request.POST["password_custom"]
            try:
                cus = Customer.objects.get(nickname=name, password=password)
                request.session["user"] = cus.id
                return redirect("store")
            except Customer.DoesNotExist:
                return HttpResponse("NO SUCH CUSTOMER")
        elif "name_agro" in request.POST and "password_agro" in request.POST:
            name = request.POST["name_agro"]
            password = request.POST["password_agro"]
            try:
                agr = Agronom.objects.get(nickname=name, password=password)
                request.session["user"] = agr.id
                return redirect("agro")
            except Agronom.DoesNotExist:
                return HttpResponse("NO SUCH AGRONOM")
        raise NotImplementedError


@csrf_protect
def store(request):
    if request.method == "GET":
        if request.session.get("card", None) == None:
            card = ShoppingCart(customer_id=Customer.objects.get(id=request.session["user"]))
            card.save()
            request.session["card"] = card.id
        return render(request, "acidlord/store.html", context={"harvest_list": list(Harvest.objects.all())})
    if request.method == "POST":
        if "card" in request.POST:
            return redirect("card")
        if "orders" in request.POST:
            return redirect("orders")
        if "feedback" in request.POST:
            feedback = Feedback(customer_id=Customer.objects.get(id=request.session["user"]), text=request.POST["feedback"])
            feedback.save()
            return redirect("store")
        for key, q in request.POST.items():
            try:
                if not key.isnumeric():
                    continue
                harvest = Harvest.objects.get(id=int(key))
                item = Harvest2Cart(
                    cart_id=ShoppingCart.objects.get(id=request.session["card"]),
                    harvest_id=harvest,
                    quantity=q,
                    final_price=float(q) * harvest.unit_price
                )
                item.save()
            except Harvest.DoesNotExist:
                continue
        return render(request, "acidlord/store.html", context={"harvest_list": list(Harvest.objects.all())})


@csrf_protect
def card(request):
    if request.method == "GET":
        card = ShoppingCart.objects.get(id=request.session["card"])
        pieces = Harvest2Cart.objects.all().filter(cart_id=card)
        return render(request, "acidlord/card.html", context={"card_list": pieces})
    if request.method == "POST":
        if "address" in request.POST:
            order = Order(
                cart_id=ShoppingCart.objects.get(id=request.session["card"]),
                delivery_address=request.POST["address"]
            )
            order.save()
            request.session["card"] = None
            return redirect("store")

@csrf_protect
def orders(request):
    if request.method == "GET":
        active = Order.objects.all().filter(done=False)
        archive = Order.objects.all().filter(done=True)

        active_with_pieces = [{"card": Harvest2Cart.objects.all().filter(cart_id=order.cart_id), "order": order} for order in active]
        archive_with_pieces = [{"card": Harvest2Cart.objects.all().filter(cart_id=order.cart_id), "order": order} for order in archive]
        return render(request, "acidlord/orders.html", context={
            "active_orders": active_with_pieces,
            "archive": archive_with_pieces
        })
    if request.method == "POST":
        for key in request.POST:
            if key.isnumeric():
                if int(key) > 10**5:
                    order = Order.objects.get(id=int(key) - 100000)
                    order.done = True
                    order.save()
                elif int(key) > 0:
                    order = Order.objects.get(id=int(key))
                    order.done = True
                    order.returned = True
                    order.save()
        return redirect("orders")


@csrf_protect
def agro(request):
    if request.method == "GET":
        return render(request, "acidlord/agro.html")
    if request.method == "POST":
        if "vacations" in request.POST:
            return redirect("vac")
        if "harvest" in request.POST:
            return redirect("harvest")
        if "queries_agro" in request.POST:
            return redirect("queries_agro")
        if "prob" in request.POST:
            return redirect("prob")
        return redirect("agro")


@csrf_protect
def vac(request):
    if request.method == "GET":
        vacations = Vacation.objects.all()
        ids = Agronom2Vacation.objects.all().filter(agronom=Agronom.objects.get(id=request.session["user"]))
        my_vac = Vacation.objects.all().filter(id__in=ids)
        available = Vacation.objects.all().exclude(id__in=ids)
        return render(request, "acidlord/vac.html", context={
                        "vacations": vacations,
                        "my_vacations": my_vac,
                        "available": available
        })
    if request.method == "POST":
        if "vac_date" in request.POST:
            vac = Vacation(
                description=request.POST["vac_description"],
                date=request.POST["vac_date"]
            )
            vac.save()
        if "vac" in request.POST:
            emb = Agronom2Vacation(
                agronom=Agronom.objects.get(id=request.session["user"]),
                vacation=Vacation.objects.get(id=request.POST["vac"])
            )
            emb.save()
        if "back" in request.POST:
            return redirect("agro")
        return redirect("vac")


@csrf_protect
def harvest(request):
    if request.method == "GET":
        return render(request, "acidlord/harvest.html")
    if request.method == "POST":
        if "shelf" in request.POST:
            harvest = Harvest(
                strain_id=Strain.objects.get(name=request.POST["harvest_strain_name"]),
                agronom=Agronom.objects.get(id=request.session["user"]),
                gen_quantity=float(request.POST["quantity"]),
                unit_price=float(request.POST["price"]),
                shelf_life=request.POST["shelf"],
                description=request.POST["description"],
                photo=request.POST["photo"]
            )
            harvest.save()
        if "strain_name" in request.POST:
            strain = Strain(
                name=request.POST["strain_name"],
                sort_description=request.POST["strain_description"]
            )
            strain.save()
        if "back" in request.POST:
            return redirect("agro")
        return redirect("harvest")


@csrf_protect
def prob(request):
    if request.method == "GET":
        return render(request, "acidlord/prob.html", context={"customers": Customer.objects.all(), "harvests": Harvest.objects.all().filter(agronom=Agronom.objects.get(id=request.session["user"]))})
    if request.method == "POST":
        if "cus" in request.POST:
            customer = Customer.objects.get(id=request.POST["cus"])
            harvest = Harvest.objects.get(id=request.POST["harvest"])
            Prob(harvest=harvest, customer=customer, agronom=Agronom.objects.get(id=request.session["user"])).save()
        if "back" in request.POST:
            return redirect("agro")
        return redirect("prob")


@csrf_protect
def queries_agro(request):
    if request.method == "GET":
        return render(request, "acidlord/queries_agro.html", context={"ka": Customer.objects.all(), "ag": Agronom.objects.all()})
    if request.method == "POST":
        if "qu" in request.POST:
            date1 = datetime.strptime(request.POST["first"], "%Y-%M-%d").replace(tzinfo=utc)
            date2 = datetime.strptime(request.POST["second"], "%Y-%M-%d").replace(tzinfo=utc)
            a = int(request.POST["A"])
            c = int(request.POST["C"])
            n = int(request.POST["N"])
            if request.POST["qu"] == "1":
                cards = [x.cart_id for x in Order.objects.all() if x.order_time >= date1 and x.order_time <= date2]
                pieces = [x for x in Harvest2Cart.objects.all() if x.cart_id in cards and x.harvest_id.agronom.id == a]
                customers = [x for x in Customer.objects.all() if len([y for y in pieces if y.cart_id.customer_id == x]) >= n]
                return render(request, "acidlord/queries_agro.html", context={"id": 1, "customers": customers, "ka": Customer.objects.all(), "ag": Agronom.objects.all()})
            if request.POST["qu"] == "2":
                orders = Order.objects.all()
                orders = [x for x in orders if date2 >= x.order_time >= date1]
                cards = [x.cart_id for x in orders if x.cart_id.customer_id.id == c]
                pieces = Harvest2Cart.objects.all().filter(cart_id__in=cards)
                return render(request, "acidlord/queries_agro.html", context={"id": 2, "pieces": pieces, "ka": Customer.objects.all(), "ag": Agronom.objects.all()})
            if request.POST["qu"] == "3":
                probs = [x for x in Prob.objects.all() if date1 <= x.date <= date2 and x.customer.id == c]
                probs_agro = [x.agronom for x in probs]
                agronoms = [x for x in Agronom.objects.all() if probs_agro.count(x) >= n]
                return render(request, "acidlord/queries_agro.html", context={"id": 3, "agronoms": agronoms, "ka": Customer.objects.all(), "ag": Agronom.objects.all()})
            if request.POST["qu"] == "4":
                vacations = Agronom2Vacation.objects.all()
                vacations = [x.vacation for x in vacations if date2 >= x.vacation.date > date1 and x.agronom.id == a]
                agronomes = {x.agronom for x in Agronom2Vacation.objects.all() if x.vacation in vacations}
                return render(request, "acidlord/queries_agro.html", context={"id": 4, "agronomes": agronomes, "ka": Customer.objects.all(), "ag": Agronom.objects.all()})
            if request.POST["qu"] == "5":
                probs_agro = {x.agronom for x in Prob.objects.all() if date1 <= x.date <= date2 and x.customer.id == c}
                cards = [x.cart_id for x in Order.objects.all() if x.cart_id.customer_id.id == c]
                pieces = {x.harvest_id.agronom for x in Harvest2Cart.objects.all() if x.cart_id in cards}
                result = list(probs_agro.intersection(pieces))
                return render(request, "acidlord/queries_agro.html", context={"id": 5, "result": result, "ka": Customer.objects.all(), "ag": Agronom.objects.all()})
            if request.POST["qu"] == "6":
                cards = [x.cart_id for x in Order.objects.all() if date1 <= x.order_time <= date2]
                cards = {x: len(Harvest2Cart.objects.all().filter(cart_id=x)) for x in cards}
                customers = [customer for customer in Customer.objects.all() if sum([value for key, value in cards.items() if key.customer_id == customer]) >= n]
                return render(request, "acidlord/queries_agro.html", context={"id": 6, "customers": customers, "ka": Customer.objects.all(), "ag": Agronom.objects.all()})
            if request.POST["qu"] == "7":
                harvests = [x for x in Harvest.objects.all() if date1 <= x.harvest_time <= date2]
                agronoms = [agronom for agronom in Agronom.objects.all() if len({x.strain_id for x in harvests if x.agronom == agronom}) >= n]
                return render(request, "acidlord/queries_agro.html", context={"id": 7, "agronoms": agronoms, "ka": Customer.objects.all(), "ag": Agronom.objects.all()})
            if request.POST["qu"] == "8":
                probs = [x for x in Prob.objects.all() if date1 <= x.date <= date2 and x.agronom.id == a and x.customer.id == c]
                return render(request, "acidlord/queries_agro.html", context={"id": 8, "probs": probs, "ka": Customer.objects.all(), "ag": Agronom.objects.all()})
            if request.POST["qu"] == "10":
                feedbacks = [x for x in Feedback.objects.all() if
                             x.customer_id.id == c and date1 <= x.feedback_time <= date2]
                month = [(x.feedback_time.month, x.feedback_time.year) for x in feedbacks]
                by_month = {}
                for m in month:
                    by_month[m] = by_month.get(m, 0) + 1
                by_month = [{"month": m[0], "year": m[1], "val": v} for m, v in by_month.items()]
                return render(request, "acidlord/queries_agro.html", context={"id": 10, "by_month": by_month, "ka": Customer.objects.all(), "ag": Agronom.objects.all()})
            if request.POST["qu"] == "11":
                dct = {}
                for strain in Strain.objects.all():
                    harvests = [x for x in Harvest.objects.all() if date1 <= x.harvest_time <= date2 and x.strain_id == strain]
                    harvests_agro = [x.agronom for x in harvests]
                    agronoms = [x for x in Agronom.objects.all() if harvests_agro.count(x) >= n]
                    vacations_agro = [x.agronom for x in Agronom2Vacation.objects.all() if
                                      date1 <= x.vacation.date <= date2]
                    agronoms_count = {agronom: vacations_agro.count(agronom) for agronom in agronoms}
                    if len(agronoms) == 0:
                        continue
                    mean = sum(agronoms_count.values()) / len(agronoms)
                    dct[strain] = mean
                by_mean = sorted([{"strain": s, "mean": dct[s]} for s in dct], key=lambda x: x["mean"], reverse=True)
                return render(request, "acidlord/queries_agro.html", context={"id": 11, "by_mean": by_mean, "ka": Customer.objects.all(), "ag": Agronom.objects.all()})
            if request.POST["qu"] == "12":
                dct = {}
                for harvest in Harvest.objects.all():
                    cards = [x.cart_id for x in Order.objects.all() if date1 <= x.order_time <= date2]
                    pieces = [x for x in Harvest2Cart.objects.all() if x.cart_id in cards and x.harvest_id == harvest]
                    customers = {x.cart_id.customer_id for x in pieces}
                    if len(customers) == 0:
                        continue
                    cards = {y.cart_id for y in pieces}
                    orders = [x for x in Order.objects.all() if x.cart_id in cards]
                    perc = 100 * len([x for x in orders if x.returned]) / len(orders)
                    dct[harvest] = perc
                by_perc = sorted([{"harvest": harvest, "perc": perc} for harvest, perc in dct.items()], key=lambda x: x["perc"], reverse=True)
                return render(request, "acidlord/queries_agro.html", context={"id": 12, "by_perc": by_perc, "ka": Customer.objects.all(), "ag": Agronom.objects.all()})
        if "back" in request.POST:
            return redirect("agro")
        return redirect("queries_agro")