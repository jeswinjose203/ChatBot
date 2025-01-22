import google.generativeai as genai
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import render
import PyPDF2
import os
from django.conf import settings

class DocumentContext:
    def __init__(self, file_path):
        self.file_path = file_path
        self._content = None
    
    @property
    def content(self):
        if self._content is None:
            try:
                with open(self.file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text_content = []
                    for page in pdf_reader.pages:
                        text_content.append(page.extract_text())
                    self._content = "\n".join(text_content)
            except Exception as e:
                print(f"Error reading PDF: {e}")
                self._content = ""
        return self._content

# Initialize the PDF context
pdf_path = os.path.join(settings.BASE_DIR, 'easyauto_dashboard_overview.pdf')
doc_context = DocumentContext(pdf_path)

def create_prompt(user_message):
    """
    Create a prompt that enforces documentation-based responses
    """
    return f"""
    Website Documentation Context:
    {doc_context.content}

    User Question: {user_message}

    Instructions:
    1. First, check if the user's question is related to any content in the website documentation provided above.
    2. If the topic exists in the documentation:
       - Begin by explaining how it's used or implemented in this specific website
       - Then, you may provide additional relevant technical information to enhance understanding
       - Always connect any additional information back to how it relates to this website
    3. If the topic is NOT found in the documentation:
        
       - Clearly state that the topic or question is not covered in the website documentation
       - Do not provide general information unrelated to the website
       - Suggest consulting the website documentation for supported features and functionality
    
    Remember: Only provide information that's relevant to or connected with the website documentation.
    For general queries not related to the website, indicate that they're outside the scope of the documentation.
    """

def index(request):
    return render(request, 'chatbot/index.html')

# Configure the API key
genai.configure(api_key="AIzaSyD_w-A54eylWKzXv-YHFMJ9AUZXTiqFLy8")

@csrf_exempt
def chatbot_response(request):
    if request.method == 'POST':
        try:
            # Get the user's message
            user_message = request.POST.get('message').strip().lower()
            
            # Check for greetings
            greetings = ["hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening"]
            if user_message in greetings:
                return JsonResponse({'response': 'Hello! I am your assistant to help navigate through the Intelligent Automation Framework. How can I assist you today?'})
            
            # Create documentation-focused prompt
            full_prompt = create_prompt(user_message)
            
            # Generate response using Gemini
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(full_prompt)
            
            return JsonResponse({'response': response.text})
            
        except Exception as e:
            print(f"Error in chatbot_response: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
