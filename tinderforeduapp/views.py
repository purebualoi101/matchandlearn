from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from .forms import SignUpForm, CommentForm, AdditionalForm, Editprofileform, profilepicture
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.shortcuts import render
from .tokens import account_activation_token
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django import db
from datetime import datetime


# Create your views here.


# this function renders home page.
@login_required
def home(request):
    return render(request, 'tinder/home.html')


def test_redirect(request):
    return HttpResponseRedirect("/")


# function for signup.
def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            # collect user information.
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            user.refresh_from_db()
            user.profile.first_name = form.cleaned_data.get('first_name')
            user.profile.last_name = form.cleaned_data.get('last_name')
            user.profile.email = form.cleaned_data.get('email')
            user.profile.college = form.cleaned_data.get('college')
            user.profile.age = form.cleaned_data.get('age')
            user.profile.gender = form.cleaned_data.get('gender')
            new_user = Userinfo.objects.create(name=user.username, school=user.profile.college,
                                               school_keyword=stringforschool(user.profile.college),
                                               age=user.profile.age, first_name=user.profile.first_name,
                                               last_name=user.profile.last_name, gender=user.profile.gender)
            Profilepic.objects.create(user=new_user, images='default.png')
            new_user.save()
            user.save()
            # send verify link to E-mail user.
            current_site = get_current_site(request)
            mail_subject = 'Please verify your email address.'
            message = render_to_string('tinder/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user), })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            db.connection.close()
            return render(request, 'tinder/email_sent.html')

    else:
        form = SignUpForm()
    return render(request, 'tinder/signup.html', {'form': form})


# confirm E-mail.
def activate_user(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.profile.email_confirmed = True
        user.save()
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return render(request, 'tinder/Activation_success.html')
    else:
        return HttpResponse('''Activation link is invalid! <META HTTP-EQUIV="Refresh" CONTENT="5;URL=/login">''')


# function for see user profile.
def user_profile(request, user_id):
    User = Userinfo.objects.get(name=request.user.username)
    comments = Comment.objects.filter(post=User)
    pic = Profilepic.objects.get(user=User)
    # add expert subject.
    if request.POST.get('subject_good'):
        subject = Subject.objects.create(subject_name=request.POST['subject_good'],
                                         subject_keyword=stringforsearch(request.POST['subject_good']))
        user_add = Userinfo.objects.get(name=request.user.username)
        user_add.expert_subject.add(subject)
        user_add.save()
        return render(request, 'tinder/your_subject.html',
                      {'comments': comments, 'pic': pic, 'name': Userinfo.objects.get(id=user_id),
                       'subject': Userinfo.objects.get(name=request.user.username).expert_subject.all()})
    return render(request, 'tinder/your_subject.html',
                  {'comments': comments, 'pic': pic, 'name': Userinfo.objects.get(id=user_id),
                   'subject': Userinfo.objects.get(name=request.user.username).expert_subject.all(),
                   'test': Userinfo.objects.get(name=request.user.username).match.all()})


# this function used when user login.
def successlogin(request):
    if request.POST.get('login'):
        return render(request, 'tinder/home.html', {'name': request.user.username})


# function for see another profile.
def another_profile(request, user_id):
    pic = Profilepic.objects.get(user=user_id)
    modelget = get_object_or_404(Userinfo, id=user_id)
    match_guy = Userinfo.objects.get(id=user_id)
    Username = Userinfo.objects.get(name=request.user.username)
    comments = Comment.objects.filter(post=match_guy)
    url_name_list = [Username.name, match_guy.name]
    url_name_list_sort = sorted(url_name_list)
    url_chat = url_name_list_sort[0] + "_" + url_name_list_sort[1]
    # add a comment and can comment once.
    if request.POST.get('comment_input'):
        comment_text = Comment.objects.create(comment=request.POST['comment_input'])
        # create new comment if user never comment to this profile.
        if not Comment.objects.filter(whocomment=Username, commentto=match_guy):
            create_comment = Comment.objects.create(comment_value=comment_text, whocomment=Username,
                                                    commentto=match_guy)
            create_comment.save()
        # edit comment if user ever comment to this profile.
        else:
            edit_comment = Comment.objects.get(whocomment=Username, commentto=match_guy)
            edit_comment.comment_value = comment_text
            edit_comment.save()
    # add a score, can add it once and can give a score of one to five.
    if request.POST.get('star_input'):
        star_score = Comment.objects.create(comment=request.POST['star_input'])
        # create new score if user never give it to this profile.
        if not Comment.objects.filter(whocomment=Username, commentto=match_guy):
            create_score = Comment.objects.create(comment_value=star_score, whocomment=Username, commentto=match_guy)
            create_score.save()
        # edit score if user ever give it to this profile.
        else:
            edit_score = Comment.objects.get(whocomment=Username, commentto=match_guy)
            edit_score.comment_value = star_score
            edit_score.save()
    # if user is student or tutor of this profile. he can chat.
    if match_guy.request.filter(sender=Username.name).exists():
        return render(request, 'tinder/profile.html',
                      {'comments': comments, 'pic': pic, 'name': Userinfo.objects.get(name=request.user.username),
                       'subject': Userinfo.objects.get(id=user_id).expert_subject.all(),
                       'test': Userinfo.objects.get(
                           name=request.user.username).match.all(),
                       'profile': Userinfo.objects.get(id=user_id), 'check': 1, "chat_room_name": url_chat})
    return render(request, 'tinder/profile.html',
                  {'comments': comments, 'pic': pic, 'profile': modelget, 'subject': modelget.expert_subject.all(),
                   'name': Userinfo.objects.get(name=request.user.username), "chat_room_name": url_chat})


# if user sign in with Facebook. he have to add his school.
def add_school(request):
    if request.method == "POST":
        form = AdditionalForm(request.POST)
        if form.is_valid():
            school = form.cleaned_data.get('school')
            adddata = Userinfo.objects.get(name=request.user.username)
            adddata.school = school
            adddata.school_keyword = stringforschool(school)
            adddata.save()
            return HttpResponseRedirect('/')
    else:
        form = AdditionalForm()
    return render(request, 'tinder/adddata.html', {'form': form})


# function for show home page.
def home_page(request):
    tutor_list = []
    sendPOST = 0
    # check that user has loged in.
    if (Userinfo.objects.filter(name=request.user.username).count() == 0):
        return HttpResponseRedirect('/login')
    # check that dose user have school data ?
    if Userinfo.objects.get(name=request.user.username).school == '':
        return HttpResponseRedirect('/add_school')
    # subject finding.
    if request.POST.get('subject_find'):
        sendPOST = 1
        result = {}
        what_sub = stringforsearch(request.POST['subject_find'])
        # user uses subject name to find tutor.
        if request.POST['filter'] != "" and request.POST['location_school'] != " ":
            tutor_list = Userinfo.objects.filter(expert_subject__subject_keyword=what_sub,
                                                 school_keyword=stringforschool(request.POST['location_school']),
                                                 gender=request.POST['filter'])
            for key in tutor_list:
                result[key] = Profilepic.objects.get(user=key)
        # user uses gender to find tutor.
        elif request.POST['filter'] != "":
            tutor_list = Userinfo.objects.filter(expert_subject__subject_keyword=what_sub,
                                                 gender=request.POST['filter'])
            for key in tutor_list:
                result[key] = Profilepic.objects.get(user=key)
        # user uses school name to find tutor.
        elif request.POST['location_school'] != "":
            tutor_list = Userinfo.objects.filter(expert_subject__subject_keyword=what_sub,
                                                 school_keyword=stringforschool(request.POST['location_school']))
            for key in tutor_list:
                result[key] = Profilepic.objects.get(user=key)
        # user use school name and gender to find tutor.
        else:
            tutor_list = Userinfo.objects.filter(expert_subject__subject_keyword=what_sub)
            for key in tutor_list:
                result[key] = Profilepic.objects.get(user=key)
        return render(request, 'tinder/home.html',
                      {'infoma': result, 'name': Userinfo.objects.get(name=request.user.username),
                       "search_result": tutor_list, "search_size": len(tutor_list), 'sendPOST': sendPOST,
                       "what_sub": request.POST['subject_find']})

    return render(request, 'tinder/home.html',
                  {'name': Userinfo.objects.get(name=request.user.username), "search_size": len(tutor_list),
                   'sendPOST': sendPOST, 'test': Userinfo.objects.get(name=request.user.username).request.all()})


# function for delete expert subject.
def select_delete(request, user_id):
    User1 = Userinfo.objects.get(id=user_id)
    modelget = get_object_or_404(Userinfo, id=user_id)
    num = request.POST.getlist("subject_list")
    # user press remove button but he has no selected subject.
    if len(num) == 0:
        pass
    # user select subject to remove it.
    else:
        for i in num:
            select = modelget.expert_subject.get(pk=i)
            select.delete()

    return HttpResponseRedirect(reverse('tinder:your_subject', args=(User1.id,)))


# student request page.
def student_request(request, user_id):
    match_list_id = Userinfo.objects.get(name=request.user.username).request.all()
    list_match = []
    username = Userinfo.objects.get(name=request.user.username)
    username.read()  # read function will make notification is 0 .
    username.save()
    # show list of people who send request to user.
    for i in match_list_id:
        list_match.append(Userinfo.objects.get(name=i.sender))
    return render(request, 'tinder/student_request.html', {'name': Userinfo.objects.get(name=request.user.username),
                                                           'student_request': Userinfo.objects.get(
                                                               name=request.user.username).request.all(),
                                                           'list_match': list_match})


# this function for send request.
def send_request(request, user_id):
    Username = Userinfo.objects.get(name=request.user.username)
    pic = Profilepic.objects.get(user=user_id)
    comments = Comment.objects.filter(post=request.user.id)
    match_guy = Userinfo.objects.get(id=user_id)
    url_name_list = [Username.name, match_guy.name]
    url_name_list_sort = sorted(url_name_list)
    url_chat = url_name_list_sort[0] + "_" + url_name_list_sort[1]
    already_match = 0
    if request.method == "POST":
        # they are already paired.
        if match_guy.request.filter(sender=Username.name, receiver=match_guy.name) or Username.request.filter(
                sender=match_guy.name, receiver=Username.name):
            already_match = 1
            return render(request, 'tinder/profile.html',
                          {'already_match': already_match, 'comments': comments, 'pic': pic,
                           'name': Userinfo.objects.get(name=request.user.username),
                           'subject': Userinfo.objects.get(id=user_id).expert_subject.all(),
                           'test': Userinfo.objects.get(name=request.user.username).match.all(), 'check': 1,
                           'profile': Userinfo.objects.get(id=user_id), 'chat_room_name': url_chat})
        # send request.
        else:
            user_name = RequestSend.objects.create(sender=Username.name, request_message=request.POST['text_request'],
                                                   receiver=match_guy.name)
            match_guy.request.add(user_name)
            Userinfo.objects.get(id=user_id).notify()  # notify function will +1 student request notification.
            Userinfo.objects.get(id=user_id).save()
            return render(request, 'tinder/profile.html',
                          {'already_match': already_match, 'comments': comments, 'pic': pic,
                           'name': Userinfo.objects.get(name=request.user.username),
                           'subject': Userinfo.objects.get(id=user_id).expert_subject.all(),
                           'test': Userinfo.objects.get(name=request.user.username).match.all(), 'check': 1,
                           'profile': Userinfo.objects.get(id=user_id), 'chat_room_name': url_chat})


# this function for cancel send request.
def cancel_send_request(request, user_id):
    Username = Userinfo.objects.get(name=request.user.username)
    pic = Profilepic.objects.get(user=user_id)
    comments = Comment.objects.filter(post=request.user.id)
    match_guy = Userinfo.objects.get(id=user_id)
    url_name_list = [Username.name, match_guy.name]
    url_name_list_sort = sorted(url_name_list)
    url_chat = url_name_list_sort[0] + "_" + url_name_list_sort[1]
    # cancel sent request
    if request.POST.get('cancel_send_request'):
        Username = Userinfo.objects.get(name=request.user.username)
        match_guy = Userinfo.objects.get(id=user_id)
        remove_match = match_guy.request.get(sender=Username.name, receiver=match_guy.name)
        match_guy.request.remove(remove_match)
        Userinfo.objects.get(id=user_id).denotify()  # denotify function will -1 student request notification.
        Userinfo.objects.get(id=user_id).save()
        return render(request, 'tinder/profile.html',
                      {'comments': comments, 'pic': pic, 'name': Userinfo.objects.get(name=request.user.username),
                       'subject': Userinfo.objects.get(id=user_id).expert_subject.all(),
                       'test': Userinfo.objects.get(
                           name=request.user.username).match.all(),
                       'profile': Userinfo.objects.get(id=user_id), 'chat_room_name': url_chat})
    return render(request, 'tinder/profile.html',
                  {'comments': comments, 'pic': pic, 'name': Userinfo.objects.get(name=request.user.username),
                   'subject': Userinfo.objects.get(id=user_id).expert_subject.all(),
                   'test': Userinfo.objects.get(name=request.user.username).match.all(),
                   'profile': Userinfo.objects.get(id=user_id), 'chat_room_name': url_chat})


# this function for accept and decline request.
def accept_or_not_request(request, user_id):
    Username = Userinfo.objects.get(name=request.user.username)
    pic = Profilepic.objects.get(user=user_id)
    match_guy = Userinfo.objects.get(id=user_id)
    url_name_list = [Username.name, match_guy.name]
    url_name_list_sort = sorted(url_name_list)
    comments = Comment.objects.filter(post=user_id)
    chat_room_name = url_name_list_sort[0] + "_" + url_name_list_sort[1]
    # accept student request.
    if request.POST.get('accept'):
        Username = Userinfo.objects.get(name=request.user.username)
        match_guy = Userinfo.objects.get(id=user_id)
        match_obj = MatchedName.objects.create(match=match_guy.name, myself=Username.name)
        Username.match.add(match_obj)
        request_obj = Username.request.get(sender=match_guy.name, receiver=Username.name)
        Username.request.remove(request_obj)
        match_obj2 = MatchedName.objects.create(match=Username.name, myself=match_guy.name)
        match_guy.match.add(match_obj2)
        return HttpResponseRedirect(reverse('tinder:student_request', args=(Username.id,)))
    # decline student request.
    if request.POST.get('decline'):
        Username = Userinfo.objects.get(name=request.user.username)
        match_guy = Userinfo.objects.get(id=user_id)
        request_obj = Username.request.get(sender=match_guy.name, receiver=Username.name)
        Username.request.remove(request_obj)
        return HttpResponseRedirect(reverse('tinder:student_request', args=(Username.id,)))
    return render(request, 'tinder/accept_or_not_request.html',
                  {'comments': comments, 'pic': pic, 'name': Userinfo.objects.get(name=request.user.username),
                   'chat_room_name': chat_room_name, 'name': Userinfo.objects.get(name=request.user.username),
                   'profile': Userinfo.objects.get(id=user_id),
                   'subject': Userinfo.objects.get(id=user_id).expert_subject.all(),
                   'request': Username.request.get(sender=match_guy.name)})


# this function for show student and tutor list.
def student_tutor_list(request, user_id):
    match_list_id = Userinfo.objects.get(name=request.user.username).match.all()
    list_match = {}
    for i in match_list_id:
        list_sort = []
        key = Userinfo.objects.get(name=i.match)
        list_sort = sorted(
            [Userinfo.objects.get(name=request.user.username).name, Userinfo.objects.get(name=i.match).name])
        value = list_sort[0] + "_" + list_sort[1]
        list_match[key] = value
    return render(request, 'tinder/students_tutor_list.html', {"name": Userinfo.objects.get(name=request.user.username),
                                                               'tutor_list': Userinfo.objects.get(
                                                                   id=user_id).match.all(), 'list_match': list_match})


# see matched profile.
def watch_profile(request, user_id):
    match_guy = Userinfo.objects.get(id=user_id)
    post = get_object_or_404(Userinfo, name=match_guy.name)
    pic = Profilepic.objects.get(user=user_id)
    comments = post.comments.filter(active=True)
    new_comment = None
    reviewed = 0
    if len(post.comments.filter(active=True, name=request.user.username)) == 1:
        reviewed = 1

    if request.POST.get('send_review'):
        comment_form = CommentForm(data=request.POST)
        if len(post.comments.filter(active=True, name=request.user.username)) == 0:
            if comment_form.is_valid():
                # Create Comment object but don't save to database yet
                new_comment = comment_form.save(commit=False)
                # Assign the current post to the comment
                new_comment.post = post
                new_comment.name = request.user.username
                # Save the comment to the database
                new_comment.save()
        else:
            now = datetime.now()
            dt_string = now.strftime("%B %d, %Y, %I:%M %p")
            edit_comment = post.comments.get(active=True, name=request.user.username)
            edit_comment.comment = request.POST['comment'] + "  (edited on : " + dt_string + ')'
            edit_comment.star = request.POST['star']
            edit_comment.save()

    else:
        comment_form = CommentForm()

    # cancel being student or tutor.
    if request.POST.get('unmatch'):
        username = Userinfo.objects.get(name=request.user.username)
        match_guy = Userinfo.objects.get(id=user_id)
        unmatch_obj = username.match.get(match=match_guy.name, myself=username.name)
        username.match.remove(unmatch_obj)
        unmatch_obj2 = match_guy.match.get(match=username.name, myself=match_guy.name)
        match_guy.match.remove(unmatch_obj2)
        return HttpResponseRedirect(reverse('tinder:students_tutor_list', args=(username.id,)))

    # remove review.
    if request.POST.get('remove_review'):
        remove_review = post.comments.get(active=True, name=request.user.username)
        Comment.delete(remove_review)
        return HttpResponseRedirect(reverse('tinder:watch_profile', args=(match_guy.id,)))

    return render(request, 'tinder/watch_profile.html',
                  {'reviewed': reviewed, 'pic': pic, 'name': Userinfo.objects.get(name=request.user.username),
                   'profile': Userinfo.objects.get(id=user_id), 'post': post, 'comments': comments,
                   'new_comment': new_comment, 'comment_form': comment_form})


# this function for edit profile.
def edit_profile(request, user_id):
    User = Userinfo.objects.get(name=request.user.username)
    Pic = Profilepic.objects.get(user=User)
    if request.method == "POST":
        form = Editprofileform(request.POST, instance=User)
        formpic = profilepicture(request.POST, request.FILES, instance=Pic)
        if form.is_valid() and formpic.is_valid():
            form.save()
            formpic.save()
            return HttpResponseRedirect(reverse('tinder:your_subject', args=(user_id,)))

    else:
        form = Editprofileform(instance=User)
        formpic = profilepicture(instance=Pic)
    return render(request, 'tinder/edit_profile.html', {"pic": Pic, 'form': form, 'formpic': formpic})


# this function for make searching easy
def stringforsearch(keyword):
    keyword = keyword.lower()
    keyword = keyword.replace(' ', '')
    return keyword


# this function for make searching easy
def stringforschool(keyword):
    keyword = keyword.upper()
    keyword = keyword.replace(' ', '')
    return keyword
