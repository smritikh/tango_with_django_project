from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm
from rango.forms import UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

def index(request):

    # Query the database for a list of ALL categories currently stored.
    # Order the categories by no. likes in descending order.
    # Retrieve the top 5 only - or all if less than 5.
    # Place the list in our context_dict dictionary
    # that will be passed to the template engine.

    category_list = Category.objects.order_by('-likes')[:5]
    page_list= Page.objects.order_by('-views')[:5]
    context_dict = {'categories': category_list, 'pages': page_list}

    # Render the response and send it back!
    return render(request, 'rango/index.html', context=context_dict)

def about(request):
    context_dict = {'yourname': "Smriti"}
    return HttpResponse('Rango says here is about page')
    #return render(request, 'rango/about.html', context = context_dict )

def show_category(request, category_name_slug):

    #Create a context dictionary which we can pass
    #to the template rendering engine

    context_dict = {}
    try:
        category = Category.objects.get(slug=category_name_slug)

        pages = Page.objects.filter(category=category)

        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        context_dict['category'] = None
        context_dict['pages'] = None

    return render(request, 'rango/category.html', context_dict)

def add_category(request):
    form = CategoryForm()

    # A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database.
            cat = form.save(commit=True)
            print(cat,cat.slug)
            # Now that the category is saved
            # We could give a confirmation message
            # But since the most recent category added is on the index page
            # Then we can direct the user back to the index page.
            return index(request)
        else:
            # The supplied form contained errors
            # just print them to the terminal.
            print(form.errors)

    # Will handle the bad form, new form, or no form supplied cases.
    # Render the form with error messages (if any).
    return render(request,'rango/add_category.html', {'form': form})

def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    form = PageForm()
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                return show_category(request, category_name_slug)
        else:
            print(form.errors)

    context_dict = {'form':form, 'category':category}
    return render(request, 'rango/add_page.html',context_dict)

def register(request):
    registered = False

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()

            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save()

            registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request, 'rango/register.html',{
        'user_form': user_form,
        'profile_form': profile_form,
        'registered': registered
         })

def user_login(request):

    # If the request is HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':

        # This information is obtained from the login form.

        username = request.POST.get('username')
        password = request.POST.get('password')

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.

        user = authenticate(username=username, password=password)

        # If we have a user object, the details are correct
        # If not, no user with matching credentials found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                # An inactive account was used - no logging in.
                return  HttpResponse("Your Rango account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            print("Invalid login details: {0}, {1}".format(username,password))
            return HttpResponse("Invalid login details supplied.")

        # The request is not HTTP POST, do display the login form
        # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank directory object...
        return render(request, 'rango/login.html', {})

@login_required
def restricted(request):
    return HttpResponse("Since you're logged in, you can see this text!")

@login_required
def user_logout(request):
    # Since we know the user is logged in, we can log them out
    logout(request)
    # Take the user back to the homepage.
    return HttpResponseRedirect(reverse('index'))








