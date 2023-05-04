import math
import re
import PyPDF2 as PyPDF2
import docx2txt as docx2txt
import nltk
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.conf import settings
import openai
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt
from nltk import SnowballStemmer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from coreapp.models import UserInformation, WebsiteActions

import io
from django.http import FileResponse
from reportlab.pdfgen import canvas
from docx import Document



# Create your views here.
def index(request):
    openai.api_key = "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"
    context = {}

    if request.method == 'POST':
        if 'job_desc' in request.POST.keys():
            job_desc = request.POST.get('job_desc')
            if job_desc == "":
                return redirect('coreapp:index')
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                 messages=[
                    {"role": "system", "content": "You give a summary of a job description"},
                    {"role": "user", "content": job_desc},
                ]
            )
            summary = response['choices'][0]['message']['content']
            context = {'summary': summary}
            try:
                job_summary = WebsiteActions.objects.get(name__iexact="Job Summary")
                job_summary.counter += 1
                job_summary.save()
            except:
                WebsiteActions.objects.create(name="Job Summary",counter = 1)
                pass
        
        elif "cv_for_match" in request.FILES.keys():
            cv_file = request.FILES['cv_for_match']
            job_content = request.POST.get('job_desc_match')

            try:
                pdf_reader = PyPDF2.PdfReader(cv_file)
                cv_content = ''
                for page in range(len(pdf_reader.pages)):
                    cv_content += pdf_reader.pages[page].extract_text()

            except:
                cv_content = docx2txt.process(cv_file)

            cv_text = preprocess_text(cv_content)
            job_text = preprocess_text(job_content)
            
            response1 = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You compare the job description with the CV and provide a percentage match score between 0 and 100%"},
                    {"role": "user", "content": "CV: " + cv_text + "\n\nJob description: " + job_text}
                ]
            )

            output = response1['choices'][0]['message']['content']
            try:
                percentage_result = re.search(r'\d+', output).group()
            except:
                percentage_result = "0"
            context = {'percentage_result': percentage_result}

            try:
                cv_match = WebsiteActions.objects.get(name__iexact="Cv Matching")
                cv_match.counter += 1
                cv_match.save()
            except:
                WebsiteActions.objects.create(name="Cv Matching",counter = 1)
                pass


        elif "cv_for_cover" in request.FILES.keys() or 'cv_content' in request.POST.keys():
            if "cv_for_cover" in request.FILES.keys():
                cv_file = request.FILES['cv_for_cover']
                job_content = request.POST.get('job_desc_cover')

                try:
                    pdf_reader = PyPDF2.PdfReader(cv_file)
                    cv_content = ''
                    for page in range(len(pdf_reader.pages)):
                        cv_content += pdf_reader.pages[page].extract_text()

                except:
                    cv_content = docx2txt.process(cv_file)
            else:
                job_content = request.POST.get('job_desc_cover')
                cv_content = request.POST.get('cv_content')

            response2 = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You generate a cover letter that highlights the candidate's skills and experience, and how they align with the requirements of the job description. The cover letter should be personalized and professional, and should demonstrate the candidate's enthusiasm for the position."},
                    {"role": "user", "content": "CV: " + cv_content + "/n/nJob description: " + job_content}
                ]
            )
            summary = response2['choices'][0]['message']['content']
            
            context = {'job_content': job_content, 'cover_letter': summary, 'cv_content':cv_content}
            try:
                cover_letter = WebsiteActions.objects.get(name__iexact="Cover Letter Generate")
                cover_letter.counter += 1
                cover_letter.save()
            except:
                WebsiteActions.objects.create(name="Cover Letter Generate",counter = 1)


        elif "cv_for_update" in request.FILES.keys():
            cv_file = request.FILES['cv_for_update']
            job_content = request.POST.get('job_desc_update')

            try:
                pdf_reader = PyPDF2.PdfReader(cv_file)
                cv_content = ''
                for page in range(len(pdf_reader.pages)):
                    cv_content += pdf_reader.pages[page].extract_text()

            except:
                cv_content = docx2txt.process(cv_file)

            cv_text = preprocess_text(cv_content)
            job_text = preprocess_text(job_content)
            response3 = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "you enhance a candidate's CV to make it more appealing to potential employers based on the information in the job description."},
                    {"role": "user", "content": "CV: " + cv_text + "/n/nJob description: " + job_text}
         
                ]
            )
            output = response3['choices'][0]['message']['content']
            context = {'output': output}
            try:
                cv_update = WebsiteActions.objects.get(name__iexact="Cv Updating")
                cv_update.counter += 1
                cv_update.save()
            except:
                WebsiteActions.objects.create(name="Cv Updating",counter = 1)
                pass

    if request.GET.get('lang') == 'EN' or request.POST.get('lang') == 'EN':
        return render(request, 'index.html',context)
    
    elif request.GET.get('lang') == 'FR' or request.POST.get('lang')=='FR':
        return render(request, 'index2.html',context)
    return render(request, 'index.html',context)


def generate_word(request):
    document = Document()
    text = request.POST.get('content')
    document.add_paragraph(text)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = 'attachment; filename=example.docx'
    document.save(response)

    return response

@csrf_exempt
def email_verification(request):
    if request.method == 'POST':
        if request.POST.get('email'):
            request.session['email'] = request.POST.get('email')

            try:
                request.session['otp'] = get_random_string(4, allowed_chars='0123456789')
                mail_subject = "OTP for email verification"
                messsage = render_to_string('otp_mail.html', {
                    'email': request.POST.get('email'),
                    'otp': request.session['otp'],
                })
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [request.POST.get('email'), ]
                user, created = UserInformation.objects.get_or_create(email=recipient_list[0])
                e_message = EmailMessage(mail_subject, messsage, email_from, recipient_list)
                e_message.content_subtype = 'html'
                e_message.send()
                
                return HttpResponse("ok", status=200)
            except Exception as e:
                return HttpResponse("no", status=500)

        elif request.POST.get('otp'):
            if request.POST.get('otp') == request.session['otp']:
                del request.session['email']
                del request.session['otp']
                request.session['email_verify'] = "True"
                return HttpResponse("ok",status=200)
            else:
                return HttpResponse("no",status=500)


def preprocess_text(text):
    # Convert to lowercase
    text = text.lower()
    
    # Remove non-alphanumeric characters
    text = re.sub(r'\W+', ' ', text)
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(text)
    text = ' '.join([word for word in tokens if word not in stop_words])
    
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

