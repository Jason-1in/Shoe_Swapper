from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Shoe
from .forms import ShoeForm

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
        form = ShoeForm(data=request.POST)
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
        form = ShoeForm(instance=shoe, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('shoes:my_shoes')

    context = {'form': form, 'heading': 'Edit shoe'}
    return render(request, 'shoes/shoe_form.html', context)