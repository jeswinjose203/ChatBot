import google.generativeai as genai
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import render
import PyPDF2
import os
from django.conf import settings
from difflib import get_close_matches  # For similarity checking
from chatbot.models import Jeswin
from vanna.remote import VannaDefault

# Define your PostgreSQL connection parameters
postgres_config = {
    'host': 'localhost',
    'port': 5432,
    'database': 'postgres',
    'user': 'postgres',
    'password': 'Jeswin@123'
}

# Initialize VannaDefault with the PostgreSQL configuration
vn = VannaDefault(model='chinook', api_key='3998531b47dd4a95ab264c824b7cfe71')
ddl = 'TABLE name is Chatbot_Jeswin,Column names are id,employee_name'
try:
    # Connect to PostgreSQL database
    vn.connect_to_postgres(**postgres_config)
    
   
except Exception as e:
    print(f"Error: {str(e)}")


# Configure the API key
genai.configure(api_key="AIzaSyD_w-A54eylWKzXv-YHFMJ9AUZXTiqFLy8")
GOOGLE_API_KEY = "AIzaSyD_w-A54eylWKzXv-YHFMJ9AUZXTiqFLy8"

def index(request):
    # Retrieve all records
    # records = Jeswin.objects.all()
    # for record in records:
    #     print(record.id, record.employee_name)

    # # Filter data by conditions
    # employee = Jeswin.objects.filter(employee_name='John Doe').first()
    # if employee is not None:
    #     print(employee.id, employee.employee_name)
    # else:
    #     print("No employee found with the name 'John Doe'")


    response = vn.ask("what is the employee name of the employee with id 1"+ddl)
    print(response)
    response = vn.ask("List all employees whose name starts with J"+ddl)
    print(response)
    return render(request, 'chatbot/index.html')

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


# def handle_query(user_message):
#     """
#     Handle specific user queries and map them to corresponding SQL-like statements.
#     Use similarity matching for fuzzy queries.
#     """
#     query_map = {
#         # Execution-related queries
#         "how many test cases passed": "ExecutionTopology.objects.filter(run_result='Pass').count()",
#         "how many test cases failed": "ExecutionTopology.objects.filter(run_result='Fail').count()",
#         "get test cases by execution status": "ExecutionTopology.objects.values('tc_name', 'execution_status')",
#         "list test cases with pass or fail result": "ExecutionTopology.objects.values('tc_name', 'run_result')",
#         "get average execution time": "ExecutionTopology.objects.aggregate(avg_time=Avg(F('finished_date') - F('started_date')))",
#         "get recent execution logs": "ExecutionTopology.objects.order_by('-started_date').values('log_path', 'tc_name')[:10]",
        
#         # Test scenario-related queries
#         "how many test scenarios are public": "TestScenario.objects.filter(public='True').count()",
#         "how many test scenarios are private": "TestScenario.objects.filter(public='False').count()",
#         "list all test scenarios": "TestScenario.objects.all()",
#         "list test scenarios by category": "TestScenario.objects.values('scenario_category').distinct()",
#         "find scenarios created by a specific user": "TestScenario.objects.filter(user__username='USERNAME')",
#         "get scenario details by name": "TestScenario.objects.filter(scenario_name='SCENARIO_NAME').values()",
        
#         # Script-related queries
#         "list all scripts": "ScriptInfo.objects.all()",
#         "get script details by name": "ScriptInfo.objects.filter(script_name='SCRIPT_NAME').values()",
#         "list scripts with testbed information": "ScriptInfo.objects.prefetch_related('script_testbeds').all()",
#         "count scripts associated with a testbed": "ScriptInfo.objects.annotate(testbed_count=Count('script_testbeds')).values()",
#         "list scripts modified after a specific date": "ScriptInfo.objects.filter(last_modified__gte='YYYY-MM-DD')",
        
#         # Testbed-related queries
#         "list all testbeds": "TestbedTopology.objects.all()",
#         "get testbed details by name": "TestbedTopology.objects.filter(name='TESTBED_NAME').values()",
#         "count testbeds used in executions": "ExecutionTopology.objects.values('tc_id__script_testbeds').distinct().count()",
        
#         # Test case-specific queries
#         "list all test cases": "TestCaseInfo.objects.all()",
#         "get test case by name": "TestCaseInfo.objects.filter(testcase_name='TESTCASE_NAME').values()",
#         "list test cases in a specific scenario": "TestCaseInfo.objects.filter(scenario_id__scenario_name='SCENARIO_NAME').values()",
#         "find test cases with a specific keyword in description": "TestCaseInfo.objects.filter(description__icontains='KEYWORD').values()",
        
#         # Group runs and execution metrics
#         "list all group runs": "GroupRun.objects.all()",
#         "get group run details by name": "GroupRun.objects.filter(group_run_name='GROUP_NAME').values()",
#         "get test cases in a group run": "GroupRun.objects.filter(group_run_name='GROUP_NAME').values('ordered_testcase_ids')",
#         "list group runs by email": "GroupRun.objects.filter(email='EMAIL_ADDRESS')",
#         "count group runs with specific topology": "GroupRun.objects.filter(topology_id='TOPOLOGY_ID').count()",
        
#         # Miscellaneous
#         "get all unique execution statuses": "ExecutionTopology.objects.values_list('execution_status', flat=True).distinct()",
#         "list all topologies used in execution": "ExecutionTopology.objects.values('tc_id__script_testbeds__name').distinct()",
#         "list recent executions by start date": "ExecutionTopology.objects.order_by('-started_date')[:10]",
#         "find execution log paths by result": "ExecutionTopology.objects.filter(run_result='RESULT').values('log_path')",
#         "list all scenarios with scripts": "TestScenario.objects.prefetch_related('script_info_set').all()",
#     }


#     # Use similarity matching to find the closest query
#     possible_queries = query_map.keys()
#     closest_match = get_close_matches(user_message, possible_queries, n=1, cutoff=0.5)

#     if closest_match:
#         matched_query = closest_match[0]
#         return query_map[matched_query]

#     return None








@csrf_exempt
def chatbot_response(request):
    if request.method == 'POST':
        try:
            # Get the user's message
            user_message = request.POST.get('message').strip().lower()

            # Check for greetings
            greetings = ["hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening", "good night", "howdy"]
            if user_message in greetings:
                return JsonResponse({'response': 'Hello! I am your assistant to help navigate through the Intelligent Automation Framework. How can I assist you today?'})
            




             # Check if the message appears to be a data query
            data_query_indicators = [
                'show me', 'find', 'search', 'query', 'get', 'select',
                'list', 'display', 'what are', 'how many', 'count'
            ]
           
            is_data_query = any(indicator in user_message for indicator in data_query_indicators)
 
            if is_data_query:
                # Try to convert to SQL first
                sql_query = vn.ask(user_message+ddl)
                if sql_query:
                    return JsonResponse({
                        'response': f"I've converted your question into SQL:\n```sql\n{sql_query}\n```\n\nWould you like me to explain this query or execute it for you?"
                    })
 
            # If not a data query or SQL conversion failed, use Gemini
            if not GOOGLE_API_KEY:
                return JsonResponse({
                    'error': 'Google API key not configured'
                }, status=500)
 
            # # Check for specific SQL-like queries
            # query = handle_query(user_message)
            # if query:
            #     return JsonResponse({'response': f"The appropriate query is: `{query}`"})

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





