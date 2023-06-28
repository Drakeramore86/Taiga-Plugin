from datetime import datetime, timedelta
from django.http import JsonResponse
from .taiga_api import TaigaManager
from django.shortcuts import render
from functools import reduce

# Function to format the duration
def format_duration(duration):
    total_seconds = duration.total_seconds()
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    return f"{int(hours)} hours {int(minutes):02d} minutes"

# Main view function
def my_view(request):
    # Taiga Manager Initialization and Login
    taiga = TaigaManager('https://taiga.itd.pub/api/v1')
    taiga.login('username', 'password')

    # Getting the project by slug
    project = taiga.get_project_by_slug('taiga-api-integration')
    if not project:
        return JsonResponse({"error": "Project not found"}, status=404)

    # Get list of sprints for the project
    sprints = taiga.get_sprints_for_project(project['id'])

    # Sprint filter processing
    sprint_filter = request.GET.get('sprint')
    user_stories = taiga.get_user_stories_for_project(project['id']) if not sprint_filter else \
        taiga.get_user_stories_for_sprint(taiga.get_sprint_by_name(project['id'], sprint_filter)['id'])
    if not user_stories:
        return JsonResponse({"error": "User stories not found"}, status=404)

    entries = []

    # Process user stories
    for us in user_stories:
        tasks = taiga.get_tasks_for_story(us['id'])
        if tasks:
            entries.extend(process_tasks(tasks, taiga, project))

    # User filter processing
    user_filter = request.GET.get('user')
    if user_filter:
        entries = [entry for entry in entries if entry['user_full_name'] == user_filter]

    # Calculate the total spent time
    total_time = reduce(lambda sum, entry: sum + timedelta(hours=int(entry['spent_time'].split(" hours ")[0]),
            minutes=int(entry['spent_time'].split(" hours ")[1].split(" minutes")[0])), entries, timedelta())

    # Formatting total time
    total_time_str = f"{total_time.days * 24 + total_time.seconds // 3600} hours {(total_time.seconds // 60) % 60} minutes"

    context = {
        'time_entries': entries,
        'total_time': total_time_str,
        'users': list(set(entry['user_full_name'] for entry in entries)),
        'sprints': [sprint['name'] for sprint in sprints],
    }

    return render(request, 'main.html', context)

# Helper function to process tasks
def process_tasks(tasks, taiga, project):
    entries = []
    for task in tasks:
        if not task['status_extra_info']['is_closed']:
            spent_time = taiga.get_custom_attributes_for_task(task['id'])
            hours, minutes = map(int, spent_time.split(':'))
            work_time = timedelta(hours=hours, minutes=minutes)
            formatted_work_time = format_duration(work_time)

            task_status = taiga.get_task_status(task['status'])

            user = taiga.get_user(task['assigned_to'])
            user_full_name = user['full_name'] if user else "Unknown"

            entry = {
                'user_id': task['assigned_to'],
                'task_id': task['id'],
                'work_date': datetime.today().date(),
                'entry_date': datetime.today().date(),
                'spent_time': formatted_work_time,
                'task_title': task['subject'],
                'project_title': project['name'],
                'user_full_name': user_full_name,
                'task_status': task_status['name'] if task_status else 'unknown',
            }
            entries.append(entry)
    return entries