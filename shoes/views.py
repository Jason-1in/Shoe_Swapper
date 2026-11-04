from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import Http404
from .models import Shoe, SwapRequest, Postcode
from .forms import ShoeForm, SwapRequestForm, RespondForm, BrowseFilterForm
from .geo import haversine_km
# Create your views here.
def index(request):
    """Home Page"""
    return render (request, 'shoes/index.html')


@login_required
def my_shoes(request):
    """Show the logged-in user's own shoes."""
    shoes = Shoe.objects.filter(owner=request.user).order_by('-date_added')
    context = {'shoes': shoes}
    return render(request, 'shoes/my_shoes.html', context)


@login_required
def new_shoe(request):
    """Add a new shoe."""
    if request.method != 'POST':
        form = ShoeForm()
    else:
        form = ShoeForm(
            data=request.POST,
            files=request.FILES
            )
        if form.is_valid():
            shoe = form.save(commit=False)
            shoe.owner = request.user
            shoe.save()
            return redirect('shoes:my_shoes')

    context = {'form': form, 'heading': 'Add a shoe'}
    return render(request, 'shoes/shoe_form.html', context)


@login_required
def edit_shoe(request, shoe_id):
    """Edit one of your own shoes."""
    # Filtering by owner means anyone else gets a 404.
    shoe = get_object_or_404(Shoe, id=shoe_id, owner=request.user)

    if request.method != 'POST':
        form = ShoeForm(instance=shoe)
    else:
        form = ShoeForm(instance=shoe, 
                        data=request.POST,
                        files=request.FILES)
        if form.is_valid():
            form.save()
            return redirect('shoes:my_shoes')

    context = {'form': form, 'heading': 'Edit shoe'}
    return render(request, 'shoes/shoe_form.html', context)

#Now for the browsing page 

@login_required
def browse(request):
    """Show available shoes from other users"""
    
    shoes = (Shoe.objects
             .filter(is_available=True)
             .exclude(owner=request.user)
             .select_related('owner')
             .order_by('-date_added'))
    form = BrowseFilterForm(request.GET or None)
    data = form.cleaned_data if form.is_valid() else {}


    # Database filters
    if data.get('brand'):
        shoes = shoes.filter(brand=data['brand'])
    if data.get('model_name'):
        shoes = shoes.filter(model_name__icontains=data['model_name'])
    if data.get('size_min') is not None:
        shoes = shoes.filter(size_us__gte=data['size_min'])
    if data.get('size_max') is not None:
        shoes = shoes.filter(size_us__lte=data['size_max'])

    shoes = list(shoes)

    #Distance filter and sorting - after database filters 
    postcode = data.get('postcode')

    if postcode:
        origin = Postcode.objects.filter(code=postcode).first()
        print(f'Lat: {origin.latitude}')
        print(f'Long: {origin.longitude}')
        if origin is None:
            form.add_error('postcode', "We don't recognise that postcode.")
        else:
            codes = {s.postcode for s in shoes}
            coords = {p.code: p for p in Postcode.objects.filter(code__in=codes)}

            for shoe in shoes:
                p = coords.get(shoe.postcode)
                print (shoe.postcode)
                if p is None:
                    shoe.distance_km = None
                    shoe.distance_label = ''
                else:
                    d = haversine_km(origin.latitude, origin.longitude,
                                     p.latitude, p.longitude)
                    shoe.distance_km = d
                    shoe.distance_label = 'Same area' if d < 1 else f'About {round(d)} km away'

            if data.get('radius'):
                limit = int(data['radius'])
                shoes = [s for s in shoes
                         if s.distance_km is not None and s.distance_km <= limit]

            shoes.sort(key=lambda s: (s.distance_km is None, s.distance_km or 0))
    context = {'shoes':shoes, 'form': form}
    return render(request, 'shoes/browse.html', context)





@login_required
def shoe_detail(request, shoe_id):
    """Show one shoe."""
    shoe = get_object_or_404(Shoe, id=shoe_id)

    # Unavailable shoes are only visible to their owner.
    if not shoe.is_available and shoe.owner != request.user:
        raise Http404

    context = {'shoe': shoe, 'is_owner': shoe.owner == request.user}
    return render(request, 'shoes/shoe_detail.html', context)


@login_required
def request_swap(request, shoe_id):
    """Ask the owner of a shoe for a swap."""
    shoe = get_object_or_404(Shoe, id=shoe_id)

    # You can't request your own shoe, or one that's no longer available.
    if shoe.owner == request.user or not shoe.is_available:
        raise Http404

    already = SwapRequest.objects.filter(
        shoe=shoe, requester=request.user, status='pending').exists()
    if already:
        messages.info(request, 'You already have a pending request for this pair.')
        return redirect('shoes:my_requests')

    if request.method != 'POST':
        form = SwapRequestForm()
    else:
        form = SwapRequestForm(data=request.POST)
        if form.is_valid():
            swap = form.save(commit=False)
            swap.shoe = shoe
            swap.requester = request.user
            swap.save()
            messages.success(request, 'Swap request sent.')
            return redirect('shoes:my_requests')

    context = {'form': form, 'shoe': shoe}
    return render(request, 'shoes/request_swap.html', context)


@login_required
def incoming_requests(request):
    """Requests other people have made on my shoes."""
    swaps = (SwapRequest.objects
             .filter(shoe__owner=request.user)
             .select_related('shoe', 'requester')
             .order_by('-date_added'))
    return render(request, 'shoes/incoming_requests.html', {'swaps': swaps})


@login_required
def my_requests(request):
    """Requests I've made on other people's shoes."""
    swaps = (SwapRequest.objects
             .filter(requester=request.user)
             .select_related('shoe', 'shoe__owner')
             .order_by('-date_added'))
    return render(request, 'shoes/my_requests.html', {'swaps': swaps})


@login_required
def respond_request(request, request_id):
    """Accept or decline a pending request on one of my shoes."""
    # Only the shoe's owner can find this, and only while it's pending.
    swap = get_object_or_404(
        SwapRequest, id=request_id, shoe__owner=request.user, status='pending')

    if request.method != 'POST':
        form = RespondForm(instance=swap)
    else:
        form = RespondForm(instance=swap, data=request.POST)
        action = request.POST.get('action')
        if form.is_valid() and action in ('accept', 'decline'):
            with transaction.atomic():
                swap = form.save(commit=False)
                if action == 'accept':
                    swap.status = 'accepted'
                    swap.save()
                    shoe = swap.shoe
                    shoe.is_available = False
                    shoe.save()
                    # Decline everyone else who asked for this pair.
                    (SwapRequest.objects
                     .filter(shoe=shoe, status='pending')
                     .exclude(id=swap.id)
                     .update(status='declined'))
                else:
                    swap.status = 'declined'
                    swap.owner_contact_details = ''
                    swap.save()
            return redirect('shoes:incoming_requests')

    context = {'form': form, 'swap': swap}
    return render(request, 'shoes/respond_request.html', context)


@login_required
def delete_shoe(request, shoe_id):
    """Confirm and delete one of your own shoes."""
    shoe = get_object_or_404(Shoe, id=shoe_id, owner=request.user)

    if request.method == 'POST':
        shoe.delete()
        messages.success(request, 'Shoe deleted.')
        return redirect('shoes:my_shoes')

    return render(request, 'shoes/delete_shoe.html', {'shoe': shoe})
