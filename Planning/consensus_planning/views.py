import logging
from django.db import IntegrityError
from django.shortcuts import render,redirect

from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth.decorators import login_required, permission_required
from .forms import *

import pandas as pd
from django.http import HttpResponse

from .models import Item
from django.core.exceptions import ValidationError
from django.contrib import messages

#http://127.0.0.1:8000/item_list/items/

# Create your views here.

def Home_view(request):
    template_name = 'consensus_planning/base.html'
    context = {}
    return render(request, template_name, context)

def login_view(request):
    if request.method == 'POST':
        #form = AuthenticationForm(request, data=request.POST)

        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("http://127.0.0.1:8000/permission/upload_excel/")  # Redirect to a success page.
            else:
                form.add_error(None, 'Invalid username or password')
    else:
        form = LoginForm()
    return render(request, 'consensus_planning/login.html', {'form': form})


def user_logout(request):
    # Log the user out
    logout(request)
    # Redirect to a page (e.g., the home page or login page)
    return redirect('http://127.0.0.1:8000/login/log/') 



def handle_uploaded_file(f):
    # Save the uploaded file temporarily
    with open('Item.xlsx', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)



#@permission_required('Consensus_Planning.can_upload', raise_exception=True)

def upload_excel(request):
    if request.method == 'POST' and request.FILES['excel_file']:
        # Handle the uploaded file
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['excel_file'])

            # Read the Excel file using pandas
            df = pd.read_excel('Item.xlsx')

            # Iterate through each row in the dataframe and save data to the Item model
            for index, row in df.iterrows():
                #dc_value = row['Dc'] if pd.notna(row['Dc']) else None
                item = Item(
                    Item_Category_1=row['Item_Category_1'],
                    Item_code=row['Item_code'],
                    Description=row['Description'],
                    Item_Category_2=row['Item_Category_2'],
                    Location=row['Location'],
                    Dc= row['Dc'] ,
                    Supplier=row['Supplier'],
                    ABC_class_Revenue=row['ABC_class_Revenue'],
                    ABC_percentage_Revenue=row['ABC_percentage_Revenue'],
                    On_hand=row['On_hand'],
                    Available_on_hand=row['Available_on_hand'],
                    Days_of_supply=row.get('Days_of_supply', 0) if pd.notna(row['Days_of_supply']) else 0,
                    To_ship=row['To_ship'],
                    To_receive=row['To_receive'],
                    finalized_quantity=row['finalized_quantity'],
                    last_submitted_quantity=row['last_submitted_quantity']
                )
                item.save()

            return redirect('http://127.0.0.1:8000/item_list/items/')

    else:
        form = ExcelUploadForm()

    return render(request, 'consensus_planning/upload_file.html', {'form': form})


def create_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        permission = request.POST.get('permission')  # Get the selected permission

        if form.is_valid():
            # Create the user
            user = form.save()

            # Assign permissions based on the selected permission
            if permission == 'read-only':
                group_name = 'Read-Only'
            elif permission == 'write-only':
                group_name = 'Write-Only'
            elif permission == 'editable':
                group_name = 'Editable'
            else:
                messages.error(request, 'Invalid permission selected.')
                return redirect('http://127.0.0.1:8000/permission/assign_permissions/')

            # Try to fetch the group, if not exist, create it
            group, created = Group.objects.get_or_create(name=group_name)

            # Add the user to the selected group
            user.groups.add(group)

            # Always add the user to the 'Default Group'
            default_group, created = Group.objects.get_or_create(name='Default Group')
            user.groups.add(default_group)

            # Save the user with the assigned groups
            user.save()

            # Provide success message
            messages.success(request, f"User '{user.username}' created successfully with {permission} access.")
            return redirect('http://127.0.0.1:8000/permission/assign_permissions/')  # Redirect to another page after creation

        else:
            # If form is not valid, show error messages
            messages.error(request, 'Please correct the errors below.')

    else:
        # Initialize the empty form for GET request
        form = UserCreationForm()

    # Pass the form to the template for rendering
    return render(request, 'consensus_planning/createuser.html', {'form': form})

def item_list(request):
    # Get all unique categories for the filter dropdown
    item_categories = Item.objects.values_list('Item_Category_2', flat=True).distinct()
    
    # Check if a filter has been applied
    selected_category = request.GET.get('item_category_filter', '')  # Get the selected category from POST data

    # If a filter is selected, filter the items by the selected category
    if selected_category:
        items = Item.objects.filter(Item_Category_2=selected_category)
    else:
        items = Item.objects.all()  # If no filter, get all items
    #items = items.order_by('Item_Category_2', 'finalized_quantity')  # Sorting by Category and Finalized Quantity

    if request.method == 'POST':
        # Loop over the items to check if the finalized_quantity exists in the POST data
        for item in items:
            finalized_quantity_key = f"finalized_quantity_{item.Sr_No}"

            # If the 'finalized_quantity' field for this item is part of the POST data, update the value
            if finalized_quantity_key in request.POST:
                finalized_quantity_value = request.POST[finalized_quantity_key]

                # Ensure the value is converted to an integer if necessary
                try:
                    finalized_quantity_value = int(finalized_quantity_value)
                    # Update the item object and save it
                    item.finalized_quantity = finalized_quantity_value
                    item.user = request.user 
                    item.save()  # Save the updated finalized_quantity
                except ValueError:
                    pass  # Ignore if conversion to integer fails

        # After saving, redirect to the same page to refresh
        return redirect(f'/item_list/items/?item_category_filter={selected_category}')  # Assuming 'item_list' is your URL name  

    # Create a form for each item to update its finalized_quantity
    item_forms = []
    for item in items:
        # Create a form for each item instance
        form = ItemForm(instance=item)
        form.fields['finalized_quantity'].initial = item.finalized_quantity  # Set the initial value

        # Add form to list along with the item
        item_forms.append({'item': item, 'form': form})

    return render(request, 'consensus_planning/item_list.html', {
        'item_forms': item_forms,
        'item_categories': item_categories,  # Pass the categories for filtering in the template
        'selected_category': selected_category  # Pass the selected category to the template
    })


def assign_permissions(request):
    # Initialize flags to track selected permissions
    view_page_selected = False
    edit_selected = False

    if request.method == 'POST':
        form = UserPermissionsForm(request.POST)
        
        if form.is_valid():
            # Get the selected users
            selected_users = form.cleaned_data.get('users')
            
            # Check if checkboxes are checked and assign groups accordingly
            read_only_group, created = Group.objects.get_or_create(name='Read Only')
            edit_group, created = Group.objects.get_or_create(name='Edit')
            view_page_group, created = Group.objects.get_or_create(name='ViewPage')
            
            for user in selected_users:
                if form.cleaned_data.get('read_only'):
                    user.groups.add(read_only_group)
                if form.cleaned_data.get('edit'):
                    user.groups.add(edit_group)
                    edit_selected = True  # Track if the "Edit" permission is selected
                if form.cleaned_data.get('view_page'):
                    user.groups.add(view_page_group)
                    view_page_selected = True  # Track if the "View Page" permission is selected
                
                # Provide feedback to the user
                messages.success(request, f"Permissions updated for {user.username}")

            # Redirect to the same page to update the UI based on selected permissions
            return redirect('http://127.0.0.1:8000/home/')

    else:
        form = UserPermissionsForm()

    # Pass flags to the template to control content based on selected permissions
    return render(request, 'consensus_planning/assign_permissions.html', {
        'form': form,
        'view_page_selected': view_page_selected,
        'edit_selected': edit_selected,
    })


def signout(request):
    pass

def save_finalized_quantities_user(request):
    if request.method == 'POST':
        # Iterate through the submitted finalized quantities
        for key, value in request.POST.items():
            if key.startswith('finalized_quantity_'):  # Check if it's a finalized_quantity field
                # Extract the item ID from the field name
                item_id = key.split('_')[-1]
                try:
                    # Get the item from the database by its ID
                    item = Item.objects.get(Sr_No=item_id)

                    # Update the finalized_quantity for that item
                    item.finalized_quantity = value

                    # Optionally, record the user who made the change (assuming 'user' is a ForeignKey to User)
                    item.changed_by = request.user  # Assuming you have a field 'changed_by' to store the user

                    # Save the item
                    item.save()

                except Item.DoesNotExist:
                    messages.error(request, f"Item with ID {item_id} not found.")
                    return redirect('item_list')  # Redirect back to the item list page with an error

        # Success message
        messages.success(request, "Changes saved successfully!")
        return redirect('item_list')  # Redirect back to the item list page after saving

    # If the request is not POST, render the form again (probably no changes to save)
    return redirect('item_list')














